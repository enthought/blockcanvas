# Enthought library imports.
from traits.api import Instance, on_trait_change, List, Callable

from pyface.workbench.api import Perspective, PerspectiveItem
from pyface.action.api import Action, Group, MenuManager
from pyface.workbench.api import WorkbenchWindow
from pyface.workbench.action.api import MenuBarManager
from pyface.workbench.action.api import ToolBarManager
from pyface.workbench.action.api import ViewMenuManager
from apptools.undo.action.api import BeginRecordingAction
from apptools.undo.action.api import ClearRecordingAction, EndRecordingAction
from apptools.undo.action.api import CommandAction, RedoAction, UndoAction

# Block Canvas imports
from blockcanvas.app.ui.function_search_ui import function_search_view
from blockcanvas.app.project import Project
from blockcanvas.app.experiment import Experiment

# Local imports.
from views.traits_ui_view import TraitsUIView
from views.experiment_context_view import ExperimentContextView
from views.experiment_code_view import ExperimentCodeView
from views.function_search_view import FunctionSearchView
from application_editor_manager import ApplicationEditorManager
from application import Application

class ApplicationWindow(WorkbenchWindow):
    """ The ExampleUndoWindow class is a workbench window that contains example
    editors that demonstrate the use of the undo framework.
    """

    ###########################################################################
    # ApplicationWindow traits.
    ###########################################################################

    #### Private interface ####################################################

    # fixme: We need complete arguments as to why these need to be traits.
    #        I can see the benefit of reusing the same actions in different
    #        locations in the UI (menu, toolbar, etc.) and ensuring there
    #        names/implementations are uniform. But it is also verbose
    #        and results in a lot of boiler plate.  The alternative is just
    #        to create the actions on the fly when we need.


    ### Actions ###############################################################

    # The action that exits the application.
    _exit_action = Instance(Action)

    # Action for creating a new project, saving old one if desired.
    _new_project_action = Instance(Action)


    ### Menus #################################################################

    # The File menu.
    _file_menu = Instance(MenuManager)

    # The Edit menu.
    _edit_menu = Instance(MenuManager)

    # Macro management menu.
    _macro_menu = Instance(MenuManager)

    # The View menu for managing perspectives.
    _view_menu = Instance(MenuManager)


    ###########################################################################
    # WorkbenchWindow interface.
    ###########################################################################

    perspectives = [
        Perspective(
            name     = 'Edit',
            contents = [
                PerspectiveItem(id='Search', position='left'),
                PerspectiveItem(id='Function Documentation',
                                relative_to='Search', position='bottom'),
                PerspectiveItem(id='Experiement Code', position='bottom'),
                PerspectiveItem(id='Context', position='right')
            ]
        ),

        Perspective(
            name     = 'Debug',
            contents = [
                PerspectiveItem(id='Debug', position='left')
            ]
        )
    ]

    #### Trait initializers ###################################################


    def _editor_manager_default(self):
        """ Use our custom editor manager be default. """

        return ApplicationEditorManager(window=self)


    def _menu_bar_manager_default(self):
        """ Setup the menus for the application. """
        return MenuBarManager(self._file_menu, self._edit_menu,
                              self._macro_menu, self._view_menu,
                              window=self)

    def _tool_bar_manager_default(self):
        """ Trait initialiser. """

        return ToolBarManager(self._exit_action, show_tool_names=False)

    ##########################################################################
    # ApplicationWindow interface.
    ##########################################################################

    #### Trait initializers ##################################################

    def _views_default(self):
        """ Trait initializer. """

        # Using an initializer makes sure that every window instance gets its
        # own view instances (which is necessary since each view has a
        # reference to its toolkit-specific control etc.).

        # fixme: Ask Martin why he put this here instead of at the top.
        from pyface.workbench.debug.api import DebugView

        # fixme: This doesn't appear to be updating.
        debug_view = DebugView(window=self)

        # fixme: I am quite sure this is not the way these views should
        #        be set up, but it is the easiest spot for now.
        # Create a view of the search window.
        search_view = FunctionSearchView(name='Search',
                                         window=self)

        # Create a view of the html window.
        doc_view = TraitsUIView(name='Function Documentation',
                                obj=self.workbench.app.html_window,
                                window=self)

        # Create a view of the project context.
        context_view = ExperimentContextView(name='Context',
                                             obj=self.workbench.app.project.active_experiment,
                                             window=self)

        # Create a view of the project code.
        experiment_code_view = ExperimentCodeView(name='Experiment Code',
                                             obj=self.workbench.app.project.active_experiment,
                                             window=self)

        return [debug_view, search_view, doc_view, context_view,
                experiment_code_view]


    #### Menu initializers ###################################################

    def __file_menu_default(self):
        """ Initialize the File Menus. """

        new_group = Group(
                    # Create a new python script.
                    #NewScriptAction(),
                    # New Experiement. Ctrl-N should map here.
                    #NewExperimentAction(),
                    # Open an entirely new Project, closing the current one
                    # if necessary.
                    self._new_project_action

                )

        file_group = Group(new_group,
        #                   OpenAction()
        #                   CloseAction()
                     )

        exit_group = Group(self._exit_action)

        return MenuManager(new_group, exit_group, name="&File", id='FileMenu')

    def __edit_menu_default(self):
        """ Initialize the Edit Menus.
        """
        undo_manager = self.workbench.undo_manager

        # fixme: Add cut/copy/paste.
        # fixme: Add Ctrl-Z Ctrl-Y short cuts here.
        undo_group = Group(
                    UndoAction(undo_manager=undo_manager),
                    RedoAction(undo_manager=undo_manager)
                )

        return MenuManager(undo_group, name="&Edit", id='EditMenu')

    def __macro_menu_default(self):
        """ The Undo menu handles Undo/Redo and macro recording.

            fixme: Undo/Redo should go to the edit menu.
                   Macro recording should go somewhere else.
        """

        undo_manager = self.workbench.undo_manager

        script_group = Group(
                    BeginRecordingAction(undo_manager=undo_manager),
                    EndRecordingAction(undo_manager=undo_manager),
                    ClearRecordingAction(undo_manager=undo_manager)
                )

        return MenuManager(script_group, name="&Macro", id="MacroMenu")

    def __view_menu_default(self):
        """ The View menu allows you to change the visible perspectives.
        """
        return ViewMenuManager(name='&View', id='ViewMenu', window=self)


    ### Action Defaults ######################################################

    def __exit_action_default(self):
        """ Trait initialiser. """

        return Action(name="E&xit", on_perform=self.workbench.exit)


    def __new_project_action_default(self):
        """ Trait initialiser. """

        return Action(name="New Project", on_perform=self._new_project)

    def _new_project(self):
        """ Implementation for creating a new project.  This can contain
            UI code.
        """
        # fixme: Ask user it they want to save.  If so, do it.
        self.workbench.app.project.save()

        # Close any editors associated with the old project.
        # (Perhaps) all of them.
        # fixme, we just close the current experiment.
        old_editor = self.get_editor(self.workbench.app.project)
        old_editor.close()

        # Create a new project and set it as the application project.
        self.workbench.app.project = Project()
        self.workbench.app.project.add_experiment(Experiment())

        # Bring it up in the editor.
        self.edit(self.workbench.app.project)

    # fixme: This is temporary until we put the script into a view.
    #@on_trait_change('workbench.undo_manager.script_updated')
    #def _on_script_updated(self, undo_manager):
    #    if str(undo_manager) == "<undefined>":
    #        return
    #
    #    script = undo_manager.script
    #
    #    if script:
    #        print script,
    #    else:
    #        print "Script empty"

    def _active_editor_changed(self, old, new):
        """ Handle any UI related changes when a new editor becomes active.

            For now, we simply swap out the Undo Stacks.
        """

        # Tell the undo manager about the new command stack.
        if old is not None:
            old.command_stack.undo_manager.active_stack = None

        if new is not None:
            new.command_stack.undo_manager.active_stack = new.command_stack

        # Update any UI menus that need to be changed, etc.


#### EOF ######################################################################
