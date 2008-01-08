""" Class that represents a pure python function.

    fixme: We do not want to import the function if we can avoid it, because
           we use this for tool-tips, etc. in the FunctionSearch, and we don't
           need to load a module just to find a functions doc string.
"""
# Standard Library imports
import _pkgutil
import parse_tools
import compiler
import inspect
import _ast
        
# Enthought library imports
from enthought.traits.api import Str, List

from enthought.block_canvas.function_tools.parse_tools import \
    function_arguments_from_ast, function_returns_from_ast


# Local imports
from callable_info import CallableInfo, InputArgument, OutputArgument


class PythonFunctionInfo(CallableInfo):
    """ Python function object in an importable module
    """
           
    # We redefine these properties to be cached properties based on the name
    # of the module.  If the code changes on disk, we can't catch this currently.
    #code = Property(Str, depends_on=['module', 'name'])


    inputs = List(InputArgument)

    outputs = List(OutputArgument)

    # If the function failed to load on its last try, an error message
    # describing the problem
    # fixme: I think this might need to go in the callable object interface.
    load_error = Str
    

    ##########################################################################
    # Function interface.
    ##########################################################################
    
    ### object interface ####################################################
    
    def __init__(self, module="", name="", **traits):
        """ 
        """
        self.set(module=module,name=name)
        super(PythonFunctionInfo, self).__init__(**traits)
        self._update_from_source()


    ### Class methods -- constructors ########################################
    
    @classmethod
    def from_function(cls, python_func, **traits):
        """ Create an ExtensionFunctionInfo from the Python object itself.
        """
        # Trust the function attributes if they exist. While the flexibility of
        # being able to override them might be nice, it interferes with our
        # ability to accurately locate the function definition, in the case of
        # __module__.
        if hasattr(python_func, '__name__'):
            traits['name'] = python_func.__name__
        if hasattr(python_func, '__doc__') and python_func.__doc__ is not None:
            traits['doc_string'] = python_func.__doc__
        if hasattr(python_func, '__module__'):
            traits['module'] = python_func.__module__

        new_item = cls(**traits)
        return new_item
        

    ### Private interface ####################################################
        
    def _update_from_source(self):
        """ Update the _ast trait based from the source code read from the
            specified module for the given name.
        """

        ast, module_source = self._ast_mod_source_from_module_and_name(self.module, self.name)
        
        if ast:
            # On success, update all our traits and reset the error message.
            self._update_doc_string(ast)
            self._update_inputs(ast)
            self._update_outputs(ast)
            self._update_code(module_source)
            self.load_error = ""
        else:
            # On failure, set everything to empty.
            self.doc_string = ""
            self.code = ""  
            self.inputs = []
            self.outputs = []

    def _ast_mod_source_from_module_and_name(self, module, name):
        """ Retreive the AST and module source for a function given its module
            and name.
        
            If it fails to find the module or find the function within
            the module, set the load_error appropriately and return None.
            Otherwise, return the FuncDef ast for the function.
            Additionally, return the module source for use with other parsers.            
        """
        # Find the source code for the specified module.
        try:
            loader = _pkgutil.get_loader(module)
        except:
            # A variety of exceptions can be thrown from getting the loader,
            # mostly dealing with a failure to parse an __init__.py file
            self.load_error = "failed to find module '%s'" % self.module
            return None, None
        
        if loader is None:
            self.load_error = "failed to find module '%s'" % self.module 
            return None, None
            
        # fixme: Can this fail if the above succeeded?
        module_source = loader.get_source()
            
                
        # Convert it to an ast, and find all function asts defined in it.
        try:
            module_ast = compiler.parse(module_source)
        except:
            # This catches parse errors in the python source
            self.load_error = "failed to parse module '%s'" % self.module
            return None, None
        
        # fixme: find_local_defs is a bit primitive.  If we have problems,
        #        with finding the wrong function, this is the place to look.
        funcs = parse_tools.find_local_defs(module_ast)
        ast = funcs.get(name, None)

        if ast is None:
            # fixme much better error handling here.
            self.load_error = "failed to find '%s' in module '%s'" % \
                (self.name, self.module)
    
        return ast, module_source
        
            
    def _update_doc_string(self, ast):
        """ Retreive the doc string from the ast.  Return an empty string if 
            it is None.
        """
        if ast.doc is None:
            self.doc_string = ""
        else:    
            self.doc_string = ast.doc
        return

    def _update_inputs(self, ast):            
        """ Set the input signature as found from the underlying function
            object.
        """    
        args = function_arguments_from_ast(ast)
        inputs = [InputArgument(name=arg[0], default=arg[1]) for arg in args[0]]
        self.inputs = inputs
        return

    def _update_outputs(self, ast):            
        """ Set the output signature as found from the underlying function
            object.
        """    
        returns = function_returns_from_ast(ast)
        self.outputs = [OutputArgument(name=name) for name in returns]
        return

    def _update_code(self, module_source):            
        """ Regenerate the code for the function.
        """    
        # This isn't quite right as it will omit comments above the function.
        #  Need to scan upwards from the function.

        ast = compile(module_source, '', 'exec', _ast.PyCF_ONLY_AST)        
        lineno = -1
        for node in ast.body:
            if isinstance(node, _ast.FunctionDef) and node.name == self.name:
                lineno = node.lineno
    
        if lineno >= 0:
            codelines = module_source.split('\n')
            codelines = [codeline + '\n' for codeline in codelines]
            self.code = ''.join(inspect.getblock(codelines[lineno-1:]))
        else:
            self.code = ''
        return
    
            
