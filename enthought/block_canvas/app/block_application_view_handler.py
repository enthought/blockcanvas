""" This is the GUI "Controller" or "Handler" for the Application.  It
    primary purpose is to set up/call actions for menu items.

"""
from enthought.block_canvas.context.data_context import DataContext

# Standard imports
import os, logging

# Enthought library imports
from enthought.traits.api import on_trait_change
from enthought.traits.ui.api import Controller
from enthought.traits.ui.menu import MenuBar, Menu, Action
from enthought.pyface.action.api import Group
from enthought.pyface.api import DirectoryDialog, FileDialog
import enthought.pyface.api as pyface
from enthought.etsconfig.api import ETSConfig

# Local imports
from ui.configurable_import_ui import ConfigurableImportUI
from ui.project_folder_ui import ProjectFolderUI
from utils import create_unique_project_name
from enthought.block_canvas.plot.context_plot import ContextPlot

# Global logger
logger = logging.getLogger(__name__)

##########################################################################
# Menu Bar and Action definitions
##########################################################################

CloseAction = Action(
    name   = 'Close',
    action = '_on_close',
)

ImportDataFileAction = Action(
    name   = 'Import Data',
    action = '_on_import_data_file',
)

SaveDataAction = Action(
    name = 'Save Data',
    action = '_on_save_data',
)

ClearContextAction = Action(
    name = "Clear Context",
    action = "_on_clear_context",
)



OpenAction = Action(
    name   = 'Open Script',
    action = '_on_open',
)

SaveAction = Action(
    name   = 'Save Script',
    action = '_on_save',
)

SaveAsAction = Action(
    name   = 'Save Script As',
    action = '_on_save_as',
)


OpenProjectAction = Action(
    name   = 'Open Project',
    action = '_on_open_project',
)

SaveProjectAction = Action(
    name = 'Save Project',
    action = '_on_save_project',
)

SaveProjectAsAction = Action(
    name = 'Save Project As',
    action = '_on_save_project_as',
)

SetToolbarHideAction = Action(
    name = "Hide Toolbar",
    action = "_on_toggle_hide",
)

PlotAction = Action(
    name='Plot',
    action = '_on_plot',
)

RunCustomUIAction = Action(
    name = "Run Custom UI Script",
    action = "_on_run_custom_ui",
)

BlockApplicationMenuBar = \
        MenuBar(
            Menu( Group(
                        OpenProjectAction,
                        OpenAction,
                        ImportDataFileAction,
                        RunCustomUIAction,
                  ),
                  Group(
                        SaveProjectAction,
                        SaveProjectAsAction,
                        #SaveDataAction,
                        SaveAction,
                        SaveAsAction,
                  ),
                  Group(
                        CloseAction,
                  ),
                  name = 'File' ),
            Menu( Group(
                        PlotAction,
                        ),
                  name='Plot'),
                  
            #Menu( Group(ClearContextAction),
            #      name = "Data" ),
            Menu( Group(
                        SetToolbarHideAction,
                  ),
                  name = "Preferences" ),
        )


##########################################################################
# Handler class
##########################################################################

class BlockApplicationViewHandler(Controller):
    """ Defines methods for handling menu actions in the BlockApplication.

        fixme: This is very much a temporary solution to test saving and
               loading of blocks.  Don't put much work in here because we
               will be using Envisage for the real deal...
    """

    def _on_import_data_file(self, info):
        """ Loading data files to import data for data contexts.

            File formats supported are ASCII, LAS, CSV, pickled files.
            ASCII files can be tab- or whitespace- delimited.
            If geo cannot be imported, only the pickled files can be
            used.
        """

        try:
            import geo
            wildcard = 'All files (*.*)|*.*|' + \
                       'ASCII files (*.asc)|*.asc|' + \
                       'Text files (*.txt)|*.txt|' + \
                       'CSV files (*.csv)|*.csv|' + \
                       'LAS files (*.las)|*.las|' + \
                       'Pickled files (*.pickle)|*.pickle|'+ \
                       'Segy files (*.segy)|*.segy'
        except ImportError:
            wildcard = 'Pickled files (*.pickle)|*.pickle'
        
        app = info.object
        file_dialog = FileDialog(action = 'open',
                                 default_directory = app.data_directory,
                                 wildcard = wildcard,
                                 )
        file_dialog.open()

        data_context, filename = None, file_dialog.path
        if file_dialog.path != '':
            filesplit = os.path.splitext(filename)
            if filesplit[1] != '': 
                configurable_import = ConfigurableImportUI(filename = filename,
                                                           wildcard = wildcard)
                ui = configurable_import.edit_traits(kind='livemodal')
                if ui.result and configurable_import.context:
                    data_context = configurable_import.context
                    app.load_context(
                        data_context, mode=configurable_import.save_choice_)

                    filename = configurable_import.filename

        if data_context:
            logger.debug('Loading data from %s' % filename)
        else:
            logger.error('Unidentified file format for data import: %s' %
                         filename)
        return

    def _on_plot(self, info):
        from cp.plot.simple_datacontext_plot import SimpleDataContextPlot
        context = info.object.project.active_experiment.context
#        plot_window = ContextPlot(context=context)
#        plot_window.edit_traits()
        index = None
        candidates = ['depth', 'DEPTH', 'Depth', 'time', 'TWT', 'twt', 'dbm',
                      ]
        for candidate in candidates:
            if candidate in context.keys():
                index = candidate
                break
            
        p = SimpleDataContextPlot(data_context=context, index=index)
    
    #------------------------------------------------------------------------
    # Script loading/saving
    #------------------------------------------------------------------------

    def _on_open(self, info):
        """ Menu action to load a script from file.  """
        print '_on_open(%r)' % info
        file_dialog = FileDialog(action='open',
                                 default_directory=info.object.file_directory,
                                 wildcard='All files (*.*)|*.*')
        print 'file_dialog'
        file_dialog.open()
        print 'open'

        if file_dialog.path != '':
            info.object.load_code_from_file(file_dialog.path)
        return

    def _on_save(self, info):
        """ Save script to file """
        if os.path.exists(info.object.file_path):
            info.object.save_block_to_file(info.object.file_path)
            msg = 'Saving script at ', info.object.file_path
            logger.debug(msg)
        else:
            self._on_save_as(info)
        return


    def _on_save_as(self, info):
        """ Menu action to save script to file of different name """
        file_dialog = FileDialog(action='save as',
                                 default_path=info.object.file_path,
                                 wildcard='All files (*.*)|*.*')
        file_dialog.open()

        if file_dialog.path != '':
            info.object.save_code_to_file(file_dialog.path)
            msg = 'Saving script at ', file_dialog.path
            logger.debug(msg)
        return

    def _on_run_custom_ui(self, info):
        """ Run a custom UI on top of the context.
        """
        wildcard = FileDialog.WILDCARD_PY.rstrip('|')
        file_dialog = FileDialog(action='open',
                                 default_directory=info.object.file_directory,
                                 wildcard=wildcard)
        file_dialog.open()

        if file_dialog.path != '':
            info.object.run_custom_ui(file_dialog.path, live=False)
        return


    #------------------------------------------------------------------------
    # Project persistence
    #------------------------------------------------------------------------

    def _get_current_project_dir(self, project):
        """ Returns a best guess of where the "current" directory is, based on
        the project_save_path of the current project.  Can be used for loading
        and saving projects.
        """
        if os.path.exists(project.project_save_path):
            dir_path = os.path.split(project.project_save_path)
            project_dir = dir_path[0]
        else:
            project_dir = ETSConfig.user_data
        return project_dir
    
    def _save_project_graphically(self, parent, project, dirname):
        """ Saves the given project to a name **dirname**.  Gives the user
        graphical feedback.
        """
        # FIXME: pop up a progress bar
        try:
            project.save(dirname)
        except Exception, e:
            pyface.error(parent=parent, message='Error while saving project:\n%s' % str(e))
            raise
        pyface.information(parent=parent, message='Project saved to %s' % dirname)


    def _on_open_project(self, info):
        """ Open and load a project
        """
        app = info.object
        project_dir = self._get_current_project_dir(app.project)
        dir_dialog = DirectoryDialog(action='open', default_path=project_dir,
                                     size=(500,400))
        dir_dialog.open()
        if dir_dialog.path != '':
            try:
                app.load_project(dir_dialog.path)
            except IOError, e:
                pyface.error(parent=info.ui.control, message=e)
        return

    def _on_save_project(self, info):
        """ Save the project where it was loaded from.

            This should handle the case when the project is new.
        """
        # Check to see if we need to pop up the save_project_as dialog.
        project = info.object.project
        if project.project_save_path == "":
            self._on_save_project_as(info)
        else:
            self._save_project_graphically(info.ui.control, project, project.project_save_path)
        return

    def _on_save_project_as(self, info):
        """ Saving project as a folder containing pickled data, and script
        """
        project = info.object.project
        base_dir = self._get_current_project_dir(project)
        project_name = create_unique_project_name(base_dir, 'Converge Project')
        pfui = ProjectFolderUI(base_dir = base_dir,
                               project_name = project_name)
        ui = pfui.edit_traits(kind = 'livemodal')
        if ui.result:
            project_dir = os.path.join(pfui.base_dir, pfui.project_name)
            self._save_project_graphically(info.ui.control, project, project_dir)
        return

    #------------------------------------------------------------------------
    # Misc actions
    #------------------------------------------------------------------------

    def _on_toggle_hide(self, info):
        """ Sets whether or not the Auto-Hide Feature should be activated/deactivated
        """
        viewport = info.object.project.active_experiment.controller.canvas.viewports[0]
        if viewport.auto_hide:
            viewport.auto_hide = False
            SetToolbarHideAction.name = "Hide Toolbar"
        else:
            viewport.auto_hide = True
            SetToolbarHideAction.name = "Show Toolbar"

    #------------------------------------------------------------------------
    # Deprecated actions
    #------------------------------------------------------------------------

#    def _on_save_data(self, info):
#        """ Saving data context to a pickled file.
#        """
#        file_dialog = FileDialog(action='save as',
#                                 default_path=info.object.file_path,
#                                 wildcard= 'Pickled files (*.pickle)|*.pickle')
#        file_dialog.open()
#
#        if file_dialog.path != '' and info.object.block_unit.data_context is not None:
#            info.object.block_unit.data_context.save_context_to_file(file_dialog.path)
#            msg = 'Saving Data Context at ' + file_dialog.path
#            logger.debug(msg)
#
#        return
#
#
#    
#    def _on_clear_context(self, info):
#        """ Clears the active context
#        """
#
#        info.object.clear_active_context()
#

# We are not using dimming for the moment.
#    @on_trait_change('model:context_viewer:table_selection')
#    def context_selection_changed(self, object, name, old, new):
#        """ When the user changes their selection in the context viewer.
#
#        Dim all of the nodes which are not affected by the selected variables.
#        """
#        self.model.project.controller.undim_all()
#        if len(new) > 0:
#            names = [row.name for row in new]
#            restricted = self.model.project.exec_model.restricted(inputs=names)
#            affected_uuids = set([stmt.uuid for stmt in restricted.statements])
#            self.model.project.controller.dim_not_active(affected_uuids)

    @on_trait_change('model.context_viewer.variables',
                     'model.project.active_experiment.exec_model.statements.inputs.binding',
                     'model.project.active_experiment.exec_model.statements.outputs.binding')
    def context_variables_changed(self, object, name, old, new):
        """ When the list of variables in the context changes.
        """
        # XXX: should this listen to the context instead of
        # context_viewer.variables? I've had problems with that elsewhere.

        # Flag all nodes which cannot be executed with the given context.
        experiment = self.model.project.active_experiment

        exec_model = experiment.exec_model
        available_names = experiment.context.keys()
        required_names, satisfied_names = exec_model.mark_unsatisfied_inputs(
            available_names)
        experiment.controller.unflag_all()
        if len(required_names) == 0:
            # Early out to avoid unnecessary work.
            return
        restricted = exec_model.restricted(inputs=required_names)
        for stmt in restricted.statements:
            experiment.controller.flag_node(stmt)



### EOF ------------------------------------------------------------------------
