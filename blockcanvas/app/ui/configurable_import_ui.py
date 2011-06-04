""" Composable UI for imports
"""

# Standard imports
import os

# Enthought library imports
from enthought.block_canvas.app.utils import create_geo_context
from enthought.contexts.data_context import DataContext
from pyface.api import FileDialog
from traits.api import HasTraits, Any, Str, Instance, Trait
from traitsui.api import View, Item, Tabbed, Group, HGroup, VGrid, \
     RangeEditor, Handler, InstanceEditor
from traitsui.menu import OKButton, CancelButton, Action

# Geo library imports/ dependencies
try:
    has_geo = True
    from enthought.block_canvas.app.segy_reader.segy_reader import SegyReader
    from geo.io.ui.file_log_reader_ui import FileLogReaderUI
except ImportError:
    has_geo = False

#------------------------------------------------------------------------------
#  ConfigurableImportUIHandler class
#------------------------------------------------------------------------------

class ConfigurableImportUIHandler(Handler):
    """ Handler for UI to perform back operations, as well as close operations
    """

    def show_file_dialog(self, info):
        """ Operation to show the parent file dialog when the back button is
            clicked
        """

        file_dialog = FileDialog(action = 'open',
                                 default_path = info.object.filename,
                                 wildcard = info.object.wildcard
                                 )
        file_dialog.open()

        # Check if the UI has to be reset.
        if file_dialog.path != '':
            filename = file_dialog.path
            filesplit = os.path.splitext(filename)
            if filesplit[1] != '' :
                info.object.reset_view(filename)

        return


    def closed(self, info, is_ok):
        """ Finalize the context in the importer
        """

        if is_ok:
            info.object.get_context()
        return

#------------------------------------------------------------------------------
#  ConfigurableImportUI class
#------------------------------------------------------------------------------

class ConfigurableImportUI(HasTraits):
    """ Import UI which will compose the view depending on the reader used.
    """

    # File reader used; SegyReader or FileLogReaderUI
    model    = Any

    # Name of the file being read
    filename = Str('')

    # Final context
    context  = Instance(DataContext)

    # Options to save the new context
    save_choice = Trait(
        'Add to the active context',
        {
         'Add to the active context': 'add',
         'Substitute the active context': 'substitute',
         # XXX: to be implemented.
         #'Add as a subcontext to the active context': 'subcontext',
         #'Add as a new context': 'new',
        },
        cols = 2)

    # Wildcard character to be used for subsequent file searches
    wildcard    = Str('All files (*.*)|*.*')

    # Proxy for refreshing UI
    _view_proxy = Any


    #---------------------------------------------------------------------------
    # HasTraits methods
    #---------------------------------------------------------------------------

    def __init__(self, **traits):
        """ Construct a view proxy to be able to refresh view when model changes
        """

        super(ConfigurableImportUI, self).__init__(**traits)
        self._view_proxy = self

    def _filename_changed(self):
        """ Reset the model when filename changes
        """

        filesplit = os.path.splitext(self.filename)
        if filesplit[1] == '.sgy' or filesplit[1] == '.segy':
            self.model = SegyReader(filename = self.filename)
        elif filesplit[1] == '.pickle':
            self.model = None
        else:
            self.model = FileLogReaderUI(file_name = self.filename)

        return

    def trait_view(self, name=None, view_element=None):
        """ Use proxy views when the UI has to refresh
        """

        # Static view
        if name != 'actual_view':
            filename = os.path.split(self.filename)
            settings = {'buttons': [Action(name='Back',
                                           action='show_file_dialog'),
                                    OKButton, CancelButton],
                        'title': 'Importing Data as Context',
                        'width':700,
                        'height':600,
                        'resizable':True,
                        'close_result': False,
                        'handler':ConfigurableImportUIHandler,
                        }

            return View(Item(name='_view_proxy', show_label = False,
                             editor=InstanceEditor(view='actual_view'),
                             style='custom'),
                        **settings)

        # Dynamic view
        items = []
        if has_geo and self.model:
            if isinstance(self.model, FileLogReaderUI):
                items = [
                    Tabbed(
                      Group(
                        Group(
                           Item('object.model.log_reader_info',
                                show_label=False,
                                style='custom', height=375),
                           ),
                        '_',
                        HGroup(Item('object.model.select_deselect_all',
                                    label='Select/deselect all'
                                    ),
                               '_',
                               Item('object.model.lower_case'),
                               ),
                        label='Select Curves',
                        ),
                      Group(Item('object.model.text_view',
                                 style='custom',
                                 show_label=False
                                ),
                            label='File View',
                            ),
                      )
                   ]
            else:
                items = [
                    Tabbed(
                       Group(
                          HGroup(
                             Item('object.model.samples_per_trace',
                                  style = 'readonly', width=50),
                             Item('object.model.trace_count',
                                  style='readonly', width=50),
                             Item('object.model.sample_rate'),
                             label = 'Header info',
                             show_border = True,
                          ),
                          VGrid(
                             HGroup(
                                Item('object.model.inline_bytes',
                                     editor = RangeEditor(mode = 'spinner',
                                                          low = 1, high = 240)),
                                Item('object.model.crossline_bytes',
                                     editor = RangeEditor(mode = 'spinner',
                                                          low = 1, high = 240)),
                             ),
                             HGroup(
                                Item('object.model.x_location_bytes',
                                     editor = RangeEditor(mode = 'spinner',
                                                          low = 1, high = 240)),
                                Item('object.model.y_location_bytes',
                                     editor = RangeEditor(mode = 'spinner',
                                                          low = 1, high = 240)),
                                Item('object.model.xy_scale_bytes',
                                     label = 'XY Scale Bytes',
                                     editor = RangeEditor(mode = 'spinner',
                                                          low = 1, high = 240)),
                             ),
                             label = 'Byte offsets',
                             show_border = True,
                          ),
                          HGroup(
                             Item('object.model.data_type'),
                             Item('object.model.byte_order', style='readonly'),
                             label = 'Data format',
                             show_border = True,
                          ),
                          label = 'File Format'
                       ),
                       Group(
                          Item('object.model.active_traceheader',
                               style='custom', show_label=False),
                          label = 'Trace Header'
                       ),
                )]

        # Insert file name at the begin; and save options in the end.
        items.insert(0, Group(Item('filename', style='readonly',
                                   show_label=False),
                              show_border = True, label = 'File'))
        items.append(Group(Item('save_choice', style='custom',
                                show_label=False),
                           show_border = True,
                           label = 'Save new context as',
                           ))
        return View(Group(*items))

    #---------------------------------------------------------------------------
    #  ConfigurableImportUI methods
    #---------------------------------------------------------------------------

    def get_context(self):
        """ Finalize the context
        """

        self.context = None
        if os.path.splitext(self.filename)[1] == '.pickle':
            self.context = DataContext.load_context_from_file(self.filename)

        elif self.model:
            if isinstance(self.model, FileLogReaderUI):
                reader = self.model.active_reader
                if reader:
                    log_info = reader.read_info(self.filename)
                    self.context = create_geo_context(
                        reader.read_data(self.filename, log_info),
                        log_info.well_name)
            else:
                self.context = self.model.read_data()

        return

    def reset_view(self, filename):
        """ Reset view proxy whenever model changes to fire events for UI to
            refresh
        """

        self._view_proxy = None
        self.filename = filename
        self._view_proxy = self

        return


# Local test
if __name__ == '__main__':
    c = ConfigurableImportUI()
    c.configure_traits()

### EOF -----------------------------------------------------------------------
