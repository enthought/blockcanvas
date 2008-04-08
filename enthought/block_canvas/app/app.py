""" Defines the Application object and runs it if executed as __main__. """

# Standard library imports
import os
import re

# Enthought library imports
from enthought.pyface.message_dialog import MessageDialog
from enthought.traits.api import Instance, Str, HasTraits, on_trait_change
from enthought.appscripting.api import scriptable
from enthought.traits.ui.api import HSplit, Item, VGroup, View, VSplit, \
                                    InstanceEditor

# Block canvas imports
from enthought.block_canvas.block_display.block_editor import BlockEditor
from enthought.block_canvas.context.api import DataContext, MultiContext
from enthought.block_canvas.context.ui.context_variable import ContextVariableList
from enthought.block_canvas.execution.executing_context import ExecutingContext
from enthought.block_canvas.function_tools.function_search import FunctionSearch
from enthought.block_canvas.function_tools.function_library import FunctionLibrary
from enthought.block_canvas.ui.source_editor import MarkableSourceEditor
from enthought.block_canvas.function_tools.html_info_ui import HtmlInfoUI
from enthought.block_canvas.app.ui.function_search_ui import function_search_view
from enthought.block_canvas.app import scripting
from enthought.block_canvas.function_tools.i_minimal_function_info import \
    MinimalFunctionInfo
from enthought.block_canvas.function_tools.local_function_info import LocalFunctionInfo
from enthought.block_canvas.function_tools.python_function_info import PythonFunctionInfo
from enthought.block_canvas.function_tools.function_call import FunctionCall
from enthought.block_canvas.function_tools.general_expression import GeneralExpression

# Local, relative imports
from experiment import Experiment
from project import Project
from block_application_view_handler import (BlockApplicationMenuBar, 
                                            BlockApplicationViewHandler)


python_name = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')
import __builtin__
builtin_names = set(dir(__builtin__))

# A global object to represent a new function.  We're cheating
# here a bit and putting labels in the correct "columns" (name,
# module) to get the UI that we want.  The UI classes below have
# some code to special cases this class.
NEW_FUNCTION_ENTRY = MinimalFunctionInfo(name="Add New Function",
                                         module="Create a new function")

NEW_EXPR_ENTRY = MinimalFunctionInfo(name="Add New Expressions",
                                     module="Create a new expression block")


class Application(HasTraits):
    """
    The Application object that ties together an
    execution model, the canvas, the function search window,
    and the shell.
    """
    
    ######################################################################
    # Application Traits
    ######################################################################

    # The currently loaded, active project
    project = Instance(Project)
    
    # The view model for the current project's context.
    context_viewer = Instance(ContextVariableList)

    # The Function Search
    # fixme: This should probably not live here.
    function_search = Instance(FunctionSearch, args=())

    # The Function Library
    # fixme: This should probably not live here.
    function_library = Instance(FunctionLibrary, args=())    

    # The data directory.
    data_directory = Str()

    # The directory for other files.
    file_directory = Str()
   
    # Window for displaying HTML help for functions.
    # fixme: It would be better to re-factor this into an active_help_item
    #        trait with an HTML Editor...
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

        if data_context is None:
            data_context = DataContext(name='data')
        self.project.add_context(data_context)

        if code is not None:
            exp = Experiment(code=code, shared_context=data_context)
        else:
            exp = Experiment(shared_context=data_context)
        self.project.active_experiment = exp

        self.context_viewer = ContextVariableList(context=exp.context)

        # XXX: the @on_trait_change decorator is not working for this!
        self.on_trait_change(self._context_items_modified,
            'project:active_experiment.context:items_modified')


    ######################################################################
    # HasTraits interface
    ######################################################################

    def trait_view(self, name=None, view_elements=None):
        return View(
          VGroup( 
            HSplit(
                  VSplit(
                    Item('function_search',
                         editor = InstanceEditor(view=function_search_view),
                         label      = 'Search',
                         id         = 'search',
                         style      = 'custom',
                         dock       = 'horizontal',
                         show_label = False,                      
                    ),
                    Item('html_window',
                         style='custom',
                         show_label=False,
                         springy= True,
                         resizable=True,
                    ),
                    id='search_help_view'
                  ),      
                VSplit(
                    Item( 'object.project.active_experiment.canvas',
                          label      = 'Canvas',
                          id         = 'canvas',
                          # FIXME:  need a new way to control the canvas
                          # not using BlockEditor
                          editor     = BlockEditor(),
                          dock       = 'horizontal',
                          show_label = False
                    ),
                    Item( 'object.project.active_experiment.exec_model.code',
                          label      = 'Code',
                          id         = 'code',
                          editor     = MarkableSourceEditor( dim_lines = 'dim_lines',
                                                dim_color = 'dim_color',
                                                squiggle_lines = 'squiggle_lines',
                                                             ),
                          dock       = 'horizontal',
                          show_label = False
                    ),
                ),
                Item( 'context_viewer',
                      label = 'Context',
                      id = 'context_table',
                      editor = InstanceEditor(),
                      style = 'custom',
                      dock = 'horizontal',
                      show_label = False,
                ),
                id='panel_split',
            ),
            Item( 'status',
                  style      = 'readonly',
                  show_label = False,
                  resizable  = False 
            ),
          ),
          title     = 'Block Canvas',
          menubar   = BlockApplicationMenuBar,
          width     = 800,
          height    = 600,
          id        = 'enthought.block_canvas.app.application',
          resizable = True,
          handler   = BlockApplicationViewHandler(model=self),
        )
        
        
    ######################################################################
    # Application interface
    ######################################################################
    
    ### load/save python scripts #########################################    

    def load_script(self, filename):
        pass

    def save_script(self, filename=""):
        pass

    def run_custom_ui(self, filename, live=True):
        """ Load a module to visually interact with the context.

        Parameters
        ----------
        filename : str
            The filename of the module with the view. It should expose
            a function called "viewable(context)" which takes an
            ExecutingContext and returns a HasTraits instance which can be
            edited with .edit_traits().
        live : bool, optional
            If True, then the interaction happens directly with the context
            itself. If False, a "copy-on-write" shadow context is put in front
            of the context.
        """
        globals = {}
        try:
            execfile(filename, globals)
        except Exception, e:
            msg = ("Cannot execute the file %s\n%s: %s" % (filename,
                e.__class__.__name__, e))
            dlg = MessageDialog(message=msg, severity='error')
            dlg.open()
            return

        if 'viewable' not in globals:
            msg = ("Cannot find the 'viewable' function in the module %s" 
                % filename)
            dlg = MessageDialog(message=msg, severity='error')
            dlg.open()
            return

        viewable = globals['viewable']
        if live:
            context = self.project.active_experiment.context
        else:
            # Create a copy-on-write context.
            exp_context = self.project.active_experiment.context
            context = ExecutingContext(executable=exp_context.executable,
                subcontext=MultiContext({}, exp_context.subcontext))
            # XXX: put this in a view model with a button to shove the data back
            # into the main context.
        tui = viewable(context)
        tui.edit_traits(kind='live')

    ### project-related scripting api ####################################

    def get_active_project(self):
        return self.project

    ### persistence #################################################

    def load_context(self, context, mode='add'):
        """ Load a new context.

        Parameters
        ----------
        context : IContext
        mode : str, optional
            If 'add', add all of the data to the current context. If 'new',
            simply add to the list of contexts. If 'substitute', replace the
            current context.
        """
        if mode == 'add':
            old_context = self.context_viewer.context
            exp_context = self.project.active_experiment.shared_context
            exp_context.update(context)
        elif mode == 'new':
            self.project.add_context(context)
        elif mode == 'substitute':
            # Find the current context in the project and replace it with the
            # newly loaded one
            cur_context = self.project.active_experiment.shared_context
            ndx = self.project.contexts.index(cur_context)
            self.project.contexts[ndx] = context
            self.project.active_experiment.shared_context = context
        else:
            raise ValueError(
                "mode must be 'add, 'new', or 'substitute'; got %r" % mode)

    def load_project(self, dirname):
        """ Load a new project into the application.  If there is an existing
        project, it will be lost.  It is the caller's responsibility to save
        out the existing project.
        """
        new_proj = Project.from_dir(dirname)
        if new_proj is None:
            raise IOError('Unable to load project from directory "%s"' % dirname)
        self.project = new_proj

    def save_project(self, dirname):
        """ Saves the current project to the given directory. """
        if self.project is not None:
            raise IOError('Application has no current project.')
        self.project.save(dirname)

    ### execution_model scripting api ####################################
    
    def add_function_object_to_model(self, item, x=None, y=None):
        """ Add the double clicked or dropped FunctionCall object to 
            the code/canvas.
        
            The added function is also marked as selected.
            
            If "New Function" is clicked, we hand back a FunctionCall based
            on a LocalFunctionInfo.  Otherwise, we hand back a FunctionCall
            based on a PythonFunctionInfo.
            
            # fixme: We need to add LocalFunctionInfo objects to the
            #        FunctionLibrary somehow.
        """
        if item == NEW_EXPR_ENTRY:
            node = GeneralExpression()

        elif item == NEW_FUNCTION_ENTRY:
            exp = self.project.active_experiment
            func_name = exp.generate_unique_function_name()

            # This should create a LocalFunctionInfo...
            # fixme: Generate a unique name that isn't on the canvas.
            code_template = "def %(name)s(a, b):\n" \
                            "    return x, y\n"
            code = code_template % {'name':func_name}                   
            # fixme: Short term for testing.  Remove imports in future and 
            #        replace with FunctionCall UI.
            function = LocalFunctionInfo(code=code)
            node = FunctionCall.from_callable_object(function)

        else:
            function = PythonFunctionInfo(name=item.name,
                                          module=item.module)
            node = FunctionCall.from_callable_object(function)
        
        # Bring up the dialog box to edit it
        node.edit_traits(kind="modal")

        self.add_function_to_execution_model(node, x, y)    
        self.select_function_on_canvas(node)
        

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
        assert function_call in self.project.active_experiment.exec_model.statements
        variable.binding = new_binding
        self.project.active_experiment.controller.update_nodes([],[],[function_call.uuid])
        return
    
    def update_node_with_edits(self, node, edited_node):
        """ Update a function/expression in the execution model with an edited
        copy.
        """
        node.copy_traits(edited_node)
        self.update_node_ui(node)

    def update_node_ui(self, node):
        """ Update the UI for the given node.
        """
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
            
            fixme: We really should have an execution_view_model that
                   keeps track of selection, etc. so that views other
                   than the canvas can react to and control changes in
                   a more coherent way.
        """
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

    @on_trait_change('context_viewer:execute_for_names')
    def execute_for_names(self, names=None):
        """ When the user clicks the "Execute" menu item on the context UI,
        actually execute the code.
        """
        # XXX: undo/redo
        exp = self.project.active_experiment
        # When this gets run, we may not have an active experiment.
        if exp is None:
            return
        if names is None or len(names) == 0:
            # Don't actually pass this in. Use None instead. Counter-intuitive
            # in code, but from the UI, it makes sense.
            names = None
        exp.context.execute_for_names(names)

    #@on_trait_change('project:active_experiment:exec_model:statements:inputs.binding')
    #def execute_for_input_binding(self, object, name, old, new):
    #    """ When bindings change, execute the code for the new binding. 
    #    """
    #    if name == 'binding':
    #        self.execute_for_names([new])
    #    elif name == 'inputs':
    #        names = [n.binding for n in new]
    #        self.execute_for_names(names)

    #@on_trait_change('project:active_experiment:exec_model:statements:outputs.binding')
    #def execute_for_output_binding(self, object, name, old, new):
    #    """ When bindings change, execute the code for the new binding. 
    #    """
    #    # We need to actually search for the node to get it to re-execute.
    #    # XXX: not enough time. Just re-executing the whole thing for now.
    #    # This means that every time we add a new function, the whole thing gets
    #    # executed since this fires the first time a function gets added.
    #     self.execute_for_names()

    def execute_for_binding(self, variable, old, new):
        """ This is a HACK.
            FIXME:  Just executing the code when a variable binding changes.
            This will update the context.
            The @on_trait_change() decorator isn't working on the two
            functions above this one after you double click to edit a
            canvas box.
        """
        self.execute_for_names()

    @on_trait_change('project.active_experiment.exec_model.statements',
                     'project.active_experiment.exec_model.statements_items')
    def execute_for_statements(self, object, name, old, new):
        """ When the list of statements changes, re-execute all of the code.
        """
        self.execute_for_names()

    @on_trait_change('context_viewer:delete_names')
    def delete_names(self, object, name, old, new):
        """ When the user clicks the "Delete" menu item on the context UI,
        actually perform the deletion.
        """
        # XXX: undo/redo
        exec_context = self.project.active_experiment.context
        exec_context.defer_events = True
        for name in new:
            del exec_context[name]
        exec_context.defer_events = False

    def assign_binding(self, graph_node, variable, name):
        """ Assign the binding of a variable for a graph node to a particular
        name.
        """
        # XXX: undo/redo
        variable.binding = name
        self.project.active_experiment.controller.update_nodes([], [], [graph_node])

    # expand/contract all
    # group/ungroup functions
    # remove function   
    

    ### html window scripting api ########################################
    # fixme: When we get an active_help_item, these should disappear...
    
    def html_window_set_text(self, text):
        self.html_window.set_text(text)

    def html_window_set_html(self, text):
        self.html_window.set_html(text)
        
    def html_window_set_function_help(self, function_name, module_name):
        self.html_window.set_function_help(function_name, module_name)

            
    ### Private interface ################################################
    
    ### Trait handlers ###################################################    

    # fixme: This should go away as the API becomes well defined.
    @on_trait_change('function_search', 'function_library.functions+')
    def _update_search_functions_from_library(self):
        """ Ensure that the functions searched in function search object
            are always in sync with the functions available in the function
            library.
        """    
        self.function_search.all_functions = self.function_library.functions

    def _context_items_modified(self, event):
        """ Trigger the update on the context UI.

        Since the events from the lower levels of the wrapped contexts get
        vetoed by their wrappers, and since we only want to look down at the
        lower level instead of looking at the functions, too, we do this instead
        of making the editor just listen to the changes.
        """
        self.context_viewer.update_variables()

    @on_trait_change('project.active_experiment')
    def experiment_changed(self, object, name, old, new):
        if self.context_viewer is None:
            return
        if self.project and self.project.active_experiment:
            self.context_viewer.context = self.project.active_experiment.context
        else:
            self.context_viewer.context = None
        self.context_viewer.update_variables()

    def _data_directory_default(self):
        cwd = os.getcwd()
        # XXX: this is good for the demo with rockphysics_main.py but may not be
        # good in general.
        d = os.path.join(cwd, 'data')
        if not os.path.exists(d) or not os.path.isdir(d):
            d = cwd
        return d

    def _file_directory_default(self):
        cwd = os.getcwd()
        return cwd


    
if __name__ == '__main__':

    code =  "from enthought.block_canvas.debug.my_operator import add, mul\n" \
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
    
    # Enable logging
    import logging 
    logging.getLogger().addHandler(logging.StreamHandler())
    logging.getLogger().setLevel(logging.DEBUG)  

    library = FunctionLibrary(modules=['os'])
    app = Application(code=code, data_context=DataContext(name='data'),
        function_library=library)
    app.configure_traits()
