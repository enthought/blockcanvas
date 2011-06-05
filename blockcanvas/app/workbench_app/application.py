""" Defines the Application object and runs it if executed as __main__.
"""

# Enthought library imports
from traits.api import (HasTraits, Instance, Str, on_trait_change)
from traitsui.api import HSplit, Item, VGroup, View, VSplit, \
                                    InstanceEditor
from apptools.appscripting.api import scriptable

# Block Canvas imports
from blockcanvas.block_display.block_editor import BlockEditor
from blockcanvas.context.ui.context_variable import ContextVariableList
from blockcanvas.context.ui.context_variable_ui import context_variables_view
from blockcanvas.function_tools.function_search import FunctionSearch
from blockcanvas.function_tools.function_library import FunctionLibrary
from blockcanvas.function_tools.html_info_ui import HtmlInfoUI
from blockcanvas.app import scripting
from blockcanvas.app.project import Project
from blockcanvas.app.experiment import Experiment

class Application(HasTraits):
    """ The Application object that ties together an execution model,
        the canvas, the function search window, and the shell.
    """

    ######################################################################
    # Application Traits
    ######################################################################

    # The currently loaded, active project
    project = Instance(Project)

    # The Function Library
    # fixme: This should probably not live here.
    function_library = Instance(FunctionLibrary, args=())

    # Window for displaying HTML help for functions.
    #
    # FIXME: This should not live here.
    # It would be better to re-factor this into an active_help_item
    # trait with an HTML Editor.
    html_window = Instance(HtmlInfoUI, args=())

    # Status bar text
    status = Str

    ######################################################################
    # object interface
    ######################################################################

    def __init__(self, code=None, data_context=None, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)

        # Set the global app object in the scripting module.
        scripting.app = self

        self.project = Project()

        if data_context is not None:
            self.project.add_context(data_context)

        if code is not None:
            exp = Experiment(code=code, shared_context=data_context)
        else:
            exp = Experiment(shared_context=data_context)
        self.project.add_experiment(exp)

        # XXX: the @on_trait_change decorator is not working for this!
        self.on_trait_change(self._context_items_modified,
                'project:active_experiment:context:items_modified')


    ######################################################################
    # Application interface
    ######################################################################

    ### load/save python scripts #########################################

    def load_script(self, filename):
        pass

    def save_script(self, filename=""):
        pass


    ### execution_model scripting api ####################################

    # fixme: Should this be a add_function, or is that to specific?
    # fixme: Make it scriptable...
    @scriptable
    def add_function_to_execution_model(self, function_call,
                                        x=None, y=None):
        """ Add a function/expression/etc to the active execution model.

            Include optional information about the location of the item
            on the canvas.
        """
        # fixme: Can the project ever be None?
        self.project.active_experiment.exec_model.add_function(function_call)
        return

    def remove_function_from_execution_model(self, function_call):
        """Remove a function from the execution model"""
        #FIXME: Should this take a UUID instead of a reference?
        self.project.active_experiment.exec_model.remove_function(function_call)
        return

    def update_function_variable_binding(self, function_call, variable, new_binding):
        """ Assign a variable a new binding"""
        #FIXME: Should this be pushed into the execution model?
        variable.binding = new_binding
        self.project.active_experiment.controller.update_nodes([],[],[function_call.uuid])
        return

    def update_node_with_edits(self, node, edited_node):
        """ Update a function/expression in the execution model with an edited
        copy.
        """
        node.copy_traits(edited_node)
        self.project.active_experiment.controller.update_nodes([], [], [node.uuid])

    def expand_all_boxes(self):
        """Expand all of the boxes on the canvas"""
        self.project.active_experiment.controller.expand_boxes()
        return

    def collapse_all_boxes(self):
        """Collapse all of the boxes on the canvas"""
        self.project.active_experiment.controller.collapse_boxes()
        return

    def scale_and_center(self):
        """Set the appropriate zoom level and position to see all of the
        blocks on the canvas"""
        self.project.active_experiment.controller.scale_and_center()

    def relayout_boxes(self):
        """Re-layout all of the boxes on the screen"""
        self.project.active_experiment.controller.position_nodes()

    def expand_box(self, box):
        """Expand a particular box on the canvas"""
        # FIXME: Should this operate on the UUID of the box, or
        # the underlying model object?
        box.expanded = True

    def collapse_box(self, box):
        # FIXME: Should this operate on the UUID of the box, or
        # the underlying model object?
        box.expanded = False

    # fixme: Make it scriptable...
    def select_function_on_canvas(self, item):
        """ Mark an item as selected on the canvas.

            Currently selected items are unselected.

        """
            #fixme: We really should have an execution_view_model that
            #       keeps track of selection, etc. so that views other
            #       than the canvas can react to and control changes in
            #       a more coherent way.
        controller = self.project.active_experiment.controller

        # Clear out current selection so that we don't end up trying
        # to add to a current selection... (fixme: is this necessary)
        controller.canvas.selection_manager.unselect_all()

        # Find the canvas box that cooresponds to the FunctionCall
        # object that we have and select it.
        # fixme: This should really be done on a ExecutionModelView
        #        object which is yet to be invented...
        canvas_box = controller._nodes[item]
        controller.canvas.selection_manager.select_item(canvas_box)


    # group/ungroup functions


    ### html window scripting api ############################################
    # fixme: When we get an active_help_item, these should disappear...

    def html_window_set_text(self, text):
        self.html_window.set_text(text)

    def html_window_set_html(self, text):
        self.html_window.set_html(text)

    def html_window_set_function_help(self, function_name, module_name):
        self.html_window.set_function_help(function_name, module_name)


    ### project scripting api ################################################

    def new_project(self):
        """ Set the active project on the application.
        """
            #fixme: This is no different than setting the actual trait.
            #       perhaps get rid of it.
        self.project = Project()


    ### Private interface ####################################################

    ### Trait handlers #######################################################

    def _context_items_modified(self, event):
        """ Trigger the update on the context UI.

        Since the events from the lower levels of the wrapped contexts get
        vetoed by their wrappers, and since we only want to look down at the
        lower level instead of looking at the functions, too, we do this instead
        of making the editor just listen to the changes.
        """
        self.context_viewer.update_variables()


if __name__ == '__main__':

    code =  "from blockcanvas.debug.my_operator import add, mul\n" \
       "def foo(x, y=3):\n" \
       "    z = x + y\n" \
       "    return z\n" \
       "def bar():\n" \
       "    pass\n" \
       "c = add(2, 3)\n" \
       "d = mul(2, 2)\n" \
       "e = mul(5, 3)\n" \
       "f = add(4, 2)\n" \
       "g = foo(2)\n"

    library = FunctionLibrary(modules=['os'])
    app = Application(code=code, function_library=library)
    app.configure_traits()
