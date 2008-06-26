""" Defines the Experiment class """

# Major library imports
import os
from os.path import join

# Enthought library imports
from enthought.traits.api import HasTraits, Instance, on_trait_change, Property, String

# Block canvas imports
from enthought.block_canvas.block_display.block_graph_controller import BlockGraphController
from enthought.block_canvas.block_display.execution_model import ExecutionModel
from enthought.block_canvas.canvas.block_canvas import BlockCanvas
from enthought.contexts.api import (DataContext,
    FunctionFilterContext, IListenableContext, MultiContext)
from enthought.block_canvas.execution.executing_context import ExecutingContext
from enthought.block_canvas.function_tools.local_function_info import LocalFunctionInfo
from enthought.block_canvas.function_tools.python_function_info import PythonFunctionInfo



class Experiment(HasTraits):
    """ 
    An Experiment represents a particular workflow and its associated data.
    It is associated with a particular context, but any data it produces
    is placed into a shadowing "local" context.
    
    It encapsulates an execution model, its associated canvas, and the
    local context.
    """
    
    # The name of the experiment.
    name = String()

    # The Execution Model object
    exec_model = Instance(ExecutionModel)

    # The Block Canvas
    canvas = Instance(BlockCanvas)
    
    # The controller between the canvas and execution model
    controller = Instance(BlockGraphController)
    
    # The execution context
    context = Instance(ExecutingContext)

    # A reference to a context that might be shared with other experiments.
    # This is usually a context from the project's list of contexts.  If None,
    # then all of the data in the experiment is kept "locally".
    #
    # Note: For most purposes, you should use the **context** attribute
    # and not this one, unless you really know what you are doing.
    shared_context = Property(Instance(IListenableContext))


    #---------------------------------------------------------------------
    # Private Traits
    #---------------------------------------------------------------------
    
    # A shadow trait for **shared_context** property
    _shared_context = Instance(IListenableContext, adapt='yes',
        rich_compare=False)

    # The context in which all of our execution model's generated values are
    # stored.  This context is exposed as part of self.context.  This remains
    # constant even as the _shared_context gets changed.
    _local_context = Instance(IListenableContext, rich_compare=False)

    # Class-level generator for the name of the local context; takes
    # **self** as an argument.
    _LOCAL_NAME_TEMPLATE = lambda x: "%s_local_%d" % (x.name, id(x))

    #---------------------------------------------------------------------
    # Public methods
    #---------------------------------------------------------------------

    def __init__(self, code=None, shared_context=None, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)

        if code is None:
            self.exec_model = ExecutionModel()
        else:
            self.exec_model = ExecutionModel.from_code(code)

        self.controller = BlockGraphController(execution_model = self.exec_model)
        self.canvas = BlockCanvas(graph_controller=self.controller)
        self.controller.canvas = self.canvas

        self._shared_context = shared_context
        self._local_context = DataContext(name = self._LOCAL_NAME_TEMPLATE())
        self._update_exec_context()

    def generate_unique_function_name(self):
        """ Returns a unique name for a new function based on the names of
        existing functions and imports in the code.
        """
        statements = self.exec_model.statements
        functions = set([s.label_name for s in statements 
                          if hasattr(s, 'function') and (
                              isinstance(s.function, PythonFunctionInfo) or 
                              isinstance(s.function, LocalFunctionInfo))])

        # Basic name generation method: template + counter
        base_name = "new_function"
        if base_name not in functions:
            return base_name
        i = 1
        while base_name + str(i) in functions:
            i += 1
        return base_name + str(i)

    #---------------------------------------------------------------------
    # Persistence
    #---------------------------------------------------------------------
    
    def load_from_config(self, config, dirname, project=None):
        """ Loads the experiment.  The existing state of the experiment is
        completely modified.  

        Parameters
        ----------
        config: a dict-like object
            The keys should correspond to the configspec for experiments as
            defined in project_config_spec.

        dirname: a string
            the absolute path to the subdirectory of the project that
            holds the experiment's saved data
        
        project: Project instance
            If provided, the project is used to hook up references to
            the shared context.
        """

        join = os.path.join
        self.name = config.get("name", "")

        if "code_file" in config:

            # Clear out the old references
            self.canvas = self.controller = self.exec_model = None

            self.exec_model = ExecutionModel.from_file(join(dirname, config["code_file"]))
            self.controller = BlockGraphController(execution_model = self.exec_model)
            self.canvas = BlockCanvas(graph_controller=self.controller)
            self.controller.canvas = self.canvas
        
        if "layout_file" in config:
            self.canvas.load_layout(join(dirname, config["layout_file"]))

        if "local_context" in config:
            self._local_context = DataContext.load(join(dirname, config["local_context"]))

        shared_context = None
        if project is not None:
            name = config.get("shared_context")
            if name != "":
                shared_context = project.find_context(name)
            
        self._shared_context = shared_context
        self._update_exec_context()


    def save(self, basename, dirname):
        """ Saves the experiment into a directory.
        
        Parameters
        ----------
        basename: string
            the name of the project directory
        dirname: string
            the name of the experiment's subdirectory
        
        Returns
        -------
        A dict representing the saved state for this object.  All path
        references in the dict will be relative to the given root directory.
        """

        # Make the directory using the absolute path.
        fullpath = join(basename, dirname)
        if not os.path.isdir(fullpath):
            os.mkdir(fullpath)
        
        config = {}
        config["name"] = self.name
        config["save_dir"] = dirname

        # Save out the canvas
        config["layout_file"] = "layout.dat"
        self.canvas.save_layout(join(fullpath, "layout.dat"))

        # Save the execution model's code
        config["code_file"] = "code.txt"
        f = file(join(fullpath, "code.txt"), "w")
        try:
            f.write(self.exec_model.code)
        finally:
            f.close()

        # Save the local context
        config["local_context"] = "local_context.pickle"
        self._local_context.save(join(fullpath, "local_context.pickle"))

        # Store the name of the shared context
        if self._shared_context is not None:
            config["shared_context"] = self._shared_context.name
        
        return config

    #---------------------------------------------------------------------
    # Trait Event Handlers
    #---------------------------------------------------------------------

    @on_trait_change('exec_model')
    def _exec_model_changed(self, name, old, new):
        """ Propagate the change to the objects under this one.
        """
        if self.controller is not None:
            self.controller.execution_model = new
        if self.context is not None:
            self.context.executable = new
    

    #---------------------------------------------------------------------
    # Property getters/setters
    #---------------------------------------------------------------------

    def _get_shared_context(self):
        return self._shared_context

    def _set_shared_context(self, newcontext):
        subcontexts = self.context.subcontext.subcontexts
        if self._shared_context is not None:
            assert(self._shared_context in subcontexts)
            if newcontext is None:
                subcontexts.remove(self._shared_context)
                self._shared_context = None
            else:
                # Swap out the new context for the old, in-place
                ndx = subcontexts.index(self._shared_context)
                subcontexts[ndx] = newcontext
                self._shared_context = newcontext
        elif newcontext is not None:
            self._shared_context = newcontext
            subcontexts.append(newcontext)
        return

        
    def _update_exec_context(self):
        mc = MultiContext(
            # Put the function filter in front so we don't dirty up the data
            # context with function objects.
            FunctionFilterContext(name='functions'),
            self._local_context,
            name='multi',
        )
        
        if self._shared_context is not None:
            mc.subcontexts.append(self._shared_context)

        self.context = ExecutingContext(
            executable=self.exec_model,
            subcontext=mc,
            name='exec',
        )


