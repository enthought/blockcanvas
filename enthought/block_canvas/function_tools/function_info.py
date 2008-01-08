""" Tools for finding imported and locally defined functions. """

# Standard Library Imports
import warnings

# Enthought Library imports
from enthought.numerical_modeling.workflow.block.analysis import walk
from enthought.numerical_modeling.workflow.block.api import unparse

# Local imports
import _pkgutil
from local_function_info import LocalFunctionInfo
from callable_info import python_function_info_from_function


class FunctionInfoWalker(object):
    def __init__(self):
        self.function_callables = {}

    def visitFrom(self, node):
        """ Add name -> function object information to info dict. """
        nodelist = node.asList()
        import_base = nodelist[0]
        import_names = nodelist[1]
        for name in import_names:
            func_name = name[0]
            func = self.get_function_object(import_base, func_name) 

            if callable(func):
                info = python_function_info_from_function(func,
                    module=import_base, name=func_name)
                # Map the 'as' name to the function object if it has been
                # renamed.
                as_name = name[1]
                if as_name:
                    func_name = as_name
                self.function_callables[func_name] = info
        
    def get_function_object(self, python_path, name):
        """ Get the python function for a given function """
        fullname = '.'.join((python_path, name))
        try:
            loader = _pkgutil.get_loader(fullname.rsplit('.', 1)[0])
            module  = loader.load_module(python_path)
            function = getattr(module, name)
            return function
        except Exception, e:
            msg = ("Failed to find function %s [%s: %s]" % 
                (name, e.__class__.__name__, e))
            warnings.warn(msg)
            return None

    def visitFunction(self, node):
        """ Add local function definitions to the info dict"""
        def_name = node.name
        self.function_callables[def_name] = LocalFunctionInfo.from_function_ast(node)

def find_functions(ast):
    """ Given Block's ast, return a dictionary of imports and local
        functions.  Dictionary is of function name -> Callable.
    """
    res = walk(ast, FunctionInfoWalker())
    return res.function_callables

