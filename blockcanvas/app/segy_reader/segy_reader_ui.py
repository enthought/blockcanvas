""" UI for a generic Segy file reader.
"""

# Enthought lib imports
from traitsui.api import View, Item, Group, HGroup, VGrid, \
     RangeEditor, Handler, Tabbed
from traitsui.menu import OKCancelButtons

#------------------------------------------------------------------------------
#  SegyReaderUIHandler class
#------------------------------------------------------------------------------

class SegyReaderUIHandler(Handler):
    """ Handler class that takes care of cleaning up after the UI is closed.
    """

    def closed(self, info, is_ok):
        """ Once the UI is closed, close the file handle.
        """

        file_handle = info.object.file_handle
        if  file_handle and not file_handle.closed:
             file_handle.close()
        return

#------------------------------------------------------------------------------
#  segy_reader_view variable
#------------------------------------------------------------------------------

segy_reader_view = View(
      Tabbed(
           Group(
              Item('filename', label = 'File'),
              HGroup(
                 Item('samples_per_trace', style = 'readonly', width=50),
                 Item('trace_count', style='readonly', width=50),
                 Item('sample_rate'),
                 label = 'Header info',
                 show_border = True,
              ),
              VGrid(
                 HGroup(
                     Item('inline_bytes',
                          editor = RangeEditor(mode = 'spinner',
                                               low = 1, high = 240)),
                     Item('crossline_bytes',
                          editor = RangeEditor(mode = 'spinner',
                                               low = 1, high = 240)),
                 ),
                 HGroup(
                     Item('x_location_bytes',
                          editor = RangeEditor(mode = 'spinner',
                                               low = 1, high = 240)),
                     Item('y_location_bytes',
                          editor = RangeEditor(mode = 'spinner',
                                               low = 1, high = 240)),
                     Item('xy_scale_bytes',
                          label = 'XY Scale Bytes',
                          editor = RangeEditor(mode = 'spinner',
                                               low = 1, high = 240)),
                 ),
                 label = 'Byte offsets',
                 show_border = True,
              ),
              HGroup(
                 Item('data_type'),
                 # FIXME: This is needed only when UI supports tabular view of
                 #        the header data.
                 #Item('view_data_bytes', enabled_when = 'False'),
                 Item('byte_order', style = 'readonly'),
                 label = 'Data format',
                 show_border = True,
              ),
              label = 'File Format'
           ),
           Group(Item('active_traceheader', style='custom', show_label=False),
                 label = 'Trace Header'),
      ),
      resizable = True,
      close_result = False,
      handler = SegyReaderUIHandler,
      buttons = OKCancelButtons,
   )

### EOF -----------------------------------------------------------------------
