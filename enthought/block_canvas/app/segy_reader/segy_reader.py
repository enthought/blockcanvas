""" A generic Segy file reader
"""

# Standard imports
from numpy import array
import logging, os, struct, string

# Enthought lib imports
from enthought.contexts.data_context import DataContext
from enthought.pyface.api import ProgressDialog
from enthought.traits.api import HasTraits, File, Int, Enum, Float, Property, \
     Any, Instance, on_trait_change
from enthought.units.quantity_traits import QuantityTrait
from enthought.units.time import msec

# Geo imports
from geo.io.segy.segy import Segy
from geo.io.segy.binary_header import BinaryHeader
from geo.io.segy.trace_header import TraceHeader

# Local imports
from segy_reader_ui import segy_reader_view
from utils import ibm2ieee
from trace_header_ui import TraceHeaderView

# Global logger
logger = logging.getLogger(__name__)

# Global translator to ensure that log-context names are python-friendly
trans_table = string.maketrans('/.\\@#$%^&*()-+=<>', '_________________')

#------------------------------------------------------------------------------
#  SegyReader class
#------------------------------------------------------------------------------

class SegyReader(HasTraits):
    """ Support for reading all segy files.
    """

    # File details
    filename            = File('')

    # Header info
    samples_per_trace   = Int(0)
    trace_count         = Int(0)
    sample_rate         = QuantityTrait(0.0, msec, 'time')

    # Byte offsets
    inline_bytes        = Int(17)
    crossline_bytes     = Int(21)
    x_location_bytes    = Int(73)
    y_location_bytes    = Int(77)
    xy_scale_bytes      = Int(71)

    # Data formatting for reading
    data_type           = Enum('IBM', 'IEEE')
    #view_data_bytes     = Enum(4, 2)
    byte_order          = Enum('Big Endian', 'Little Endian')

    # Default view
    trait_view          = segy_reader_view

    # Miscellaneous traits
    samples             = Int(901)
    active_traceheader  = Instance(TraceHeaderView, ())
    file_handle         = Any
    x_format            = Property(depends_on = ['x_location_bytes',
                                                 'byte_order'])
    y_format            = Property(depends_on = ['y_location_bytes',
                                                 'byte_order'])
    inline_format       = Property(depends_on = ['inline_bytes',
                                                 'byte_order'])
    crossline_format    = Property(depends_on = ['crossline_bytes',
                                                 'byte_order'])
    scale_format        = Property(depends_on = ['xy_scale_bytes',
                                                 'byte_order'])
    byte_order_char     = Property(depends_on = ['byte_order'])
    data_format         = Property(depends_on = ['data_type', 'byte_order',
                                                 'samples'])

    #---------------------------------------------------------------------------
    # HasTraits interface
    #---------------------------------------------------------------------------

    ### trait methods ----------------------------------------------------------

    def _get_byte_order_char(self):
        """ Property getter for byte order char
        """
        if self.byte_order == 'Big Endian':
            return '>'
        else:
            return '<'

    def _get_crossline_format(self):
        """ Property getter for crossline_format
        """
        return self.byte_order_char + 'x'*(self.crossline_bytes-1) + 'I' + \
               'x'*(237-self.crossline_bytes)

    def _get_data_format(self):
        """ Property getter for data_format
        """
        if self.data_type == 'IBM':
            return self.byte_order_char + 'i'*(self.samples/4)
        else:
            return self.byte_order_char + 'f'*(self.samples/4)

    def _get_inline_format(self):
        """ Property getter for inline_format
        """
        return self.byte_order_char + 'x'*(self.inline_bytes-1) + 'I' + \
               'x'*(237-self.inline_bytes)

    def _get_x_format(self):
        """ Property getter for x_format
        """
        return self.byte_order_char + 'x'*(self.x_location_bytes-1) + 'I' + \
               'x'*(237-self.x_location_bytes)

    def _get_scale_format(self):
        """ Property getter for scale_format
        """
        if self.xy_scale_bytes > 0:
            return self.byte_order_char + 'x'*(self.xy_scale_bytes-1) + 'I' + \
                   'x'*(237-self.xy_scale_bytes)
        else:
            return ''

    def _get_y_format(self):
        """ Property getter for y_format
        """
        return self.byte_order_char + 'x'*(self.y_location_bytes-1) + 'I' + \
               'x'*(237-self.y_location_bytes)

    def _filename_changed(self):
        """ Change binary header and update inline_byte_data,
            crossline_byte_data, samples_per_trace,
            trace_count, sample_rate, etc. from binary header.
        """

        # Reset the file_handle
        if self.file_handle and not self.file_handle.closed:
            self.file_handle.close()

        if self.filename == '':
            self.file_handle = None
            return

        self.file_handle = file(self.filename, 'rb')

        # Ignoring card-image-header; 3200 bytes of EBCDIC data
        self.file_handle.read(Segy.CARD_IMAGE_HEADER_LEN)

        # Read in the binary header; 400 bytes of binary header data
        data = self.file_handle.read(Segy.BINARY_HEADER_LEN)

        # Find out if the byte format is Big Endian or Little Endian.
        # FIXME: should make this portion independent; as change in byte order
        #        can change the binary header information.
        byte_format = getattr(Segy, self.byte_order.replace(' ', '_').upper())
        binary_header = BinaryHeader(data, byte_format)

        # File settings
        self.samples = 4*binary_header.samples
        self._inspect_traces()

        return

    #---------------------------------------------------------------------------
    # SegyFileReader interface
    #---------------------------------------------------------------------------

    ### private methods --------------------------------------------------------

    @on_trait_change('active_traceheader.trace_header_number')
    def _change_active_traceheader(self):
        """ Change the trace header being viewed
        """

        offset = Segy.CARD_IMAGE_HEADER_LEN + Segy.BINARY_HEADER_LEN + \
                 (self.active_traceheader.trace_header_number-1)* \
                 (Segy.TRACE_HEADER_LEN+self.samples)
        self.file_handle.seek(offset)
        header_data = self.file_handle.read(Segy.TRACE_HEADER_LEN)
        byte_format = getattr(Segy, self.byte_order.replace(' ', '_').upper())
        del self.active_traceheader.model
        self.active_traceheader.model = TraceHeader(header_data, byte_format)

    def _inspect_traces(self):
        """ Inspect all the traces, save the first trace-header
        """

        # Get trace header data of 240 bytes.
        header_data = self.file_handle.read(Segy.TRACE_HEADER_LEN)
        # FIXME: there should be a provision to change byte-order.
        byte_format = getattr(Segy, self.byte_order.replace(' ', '_').upper())
        traceheader = TraceHeader(header_data, byte_format)

        # Find trace counts
        trace_count = 0
        while header_data != '':
            self.file_handle.seek(self.samples, 1)
            trace_count += 1
            header_data = self.file_handle.read(Segy.TRACE_HEADER_LEN)

        # Set all the UI fields.
        self.trace_count = trace_count
        self.active_traceheader.model = traceheader
        self.active_traceheader.total_headers = self.trace_count

        self.samples_per_trace = traceheader.samplesInTrace
        # Convert sample rate from microseconds to milliseconds.
        self.sample_rate = 0.001*traceheader.sampleInterval

        return

    def _read_trace(self, header_data, check_length):
        """ Read a trace successfully from its header data and return a trace.

            Returns:
            --------
            x: float
              x location of trace
            y: float
              y location of trace
            inline: float
              inline location of trace
            crossline: float
              crossline location of trace
            scale_factor: float
              factor by which x and y are scaled
            trace: array
              samples constituting the trace

        """

        if len(header_data) != check_length:
            logger.error('SegyReader: Mismatch in trace header data length')
            return None

        x_val = float(struct.unpack(self.x_format, header_data)[0])
        y_val = float(struct.unpack(self.y_format, header_data)[0])
        inline_val = float(struct.unpack(self.inline_format, header_data)[0])
        crossline_val = float(struct.unpack(self.crossline_format,
                                            header_data)[0])

        scale_factor = 1.0
        if self.scale_format != '':
            scale_factor = float(struct.unpack(self.scale_format,
                                               header_data)[0])
            if scale_factor != 0:
                if scale_factor < 0 :
                    scale_factor = -1.0/scale_factor
                x_val *= scale_factor
                y_val *= scale_factor
            else:
                scale_factor = 1.0

        # Read the trace data.
        raw_data = self.file_handle.read(self.samples)

        if self.data_type == 'IBM':
            trace = ibm2ieee(array(struct.unpack(self.data_format, raw_data)))
        else:
            trace = array(struct.unpack(self.data_format, raw_data))

        return x_val, y_val, inline_val, crossline_val, scale_factor, trace


    ### public methods ---------------------------------------------------------

    def read_data(self):
        """ Obtain x_locations, y_locations, data_locations, traces in a context

            Returns:
            ---------
            context: DataContext

        """

        # Check if the filename is valid for reading data
        if not self.file_handle:
            return None

        # Set the file reader at the first char.
        if self.file_handle.closed:
            self.file_handle = file(self.filename, 'rb')

        # Setup a progress dialog
        progress = ProgressDialog(title='Reading Segy Files',
                                  message='Reading Segy Files',
                                  max=100, show_time=True, can_cancel=True)
        progress.open()

        # Skip the card_image_header and binary header
        self.file_handle.seek(Segy.CARD_IMAGE_HEADER_LEN +
                              Segy.BINARY_HEADER_LEN)
        progress.update(1)

        # Check if data lengths are correct.
        x_data_len = struct.calcsize(self.x_format)
        y_data_len = struct.calcsize(self.y_format)
        inline_data_len = struct.calcsize(self.inline_format)
        crossline_data_len = struct.calcsize(self.crossline_format)

        if not (x_data_len == y_data_len and
                y_data_len == inline_data_len and
                inline_data_len == crossline_data_len):
            logger.error('SegyReader: Mismatch in format lengths')
            return None

        if self.scale_format != '':
            scale_data_len = struct.calcsize(self.scale_format)
            if scale_data_len != x_data_len:
                logger.error('SegyReader: Mismatch in format lengths')
                return None

        # Get trace header data of 240 bytes.
        header_data = self.file_handle.read(Segy.TRACE_HEADER_LEN)
        traces, read_error = [], False
        previous_update = 1
        while header_data != '' and not read_error:
            trace = self._read_trace(header_data, x_data_len)
            if trace is None:
                logger.error('SegyReader: Error in reading a trace')
                read_error = True
            else:
                traces.append(trace)
                header_data = self.file_handle.read(Segy.TRACE_HEADER_LEN)

            progress_pc = 1 + int(98.0*float(len(traces))/
                                  float(self.trace_count))
            if progress_pc - previous_update > 1:
                cont_val, skip_val = progress.update(progress_pc)
                previous_update = progress_pc

                # If the user has cancelled the action then stop the import
                # immediately
                if skip_val or not cont_val:
                    del traces
                    self.file_handle.close()
                    return None

        self.file_handle.close()
        progress.update(100)

        if read_error:
            del traces
            return None
        else:
            arr_descriptor = {'names': ('x','y','inline','crossline',
                                        'scale_factor', 'trace'),
                              'formats': ('f4', 'f4', 'f4', 'f4', 'f4',
                                          str(self.samples_per_trace)+'f4')
                              }
            traces = array(traces, dtype=arr_descriptor)
            filesplit = os.path.split(self.filename)
            name = str(os.path.splitext(filesplit[1])[0]).translate(trans_table)
            return DataContext(
                name=name,
                _bindings={'traces':traces['trace'],
                           'x_locations':traces['x'],
                           'y_locations':traces['y'],
                           'inline_values':traces['inline'],
                           'crossline_values':traces['crossline'],
                           'scale_factors':traces['scale_factor']})
        return


# Local test
if __name__ == '__main__':
    sr = SegyReader()
    ui = sr.edit_traits(kind = 'livemodal')
    if ui.result:
        context = sr.read_data()

### EOF ------------------------------------------------------------------------
