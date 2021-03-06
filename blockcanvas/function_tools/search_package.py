""" This module contains utility functions for finding the functions contained
    within package or module and its sub-packages or modules.

        # Search a module for all its functions.
        >>> from search_package2 import find_functions
        >>> find_functions('atexit')
        [('atexit', '_run_exitfuncs'), ('atexit', 'register')]

        # Search a package and all its sub-packages for functions.
        >>> funcs = find_functions('xml')
        >>> for func in funcs[:3]: print func
        ('xml.dom.domreg', 'registerDOMImplementation')
        ('xml.dom.domreg', '_good_enough')
        ('xml.dom.domreg', 'getDOMImplementation')


"""

# Standard libary imports
import os
import inspect
from glob import glob
import _ast
import logging


import _pkgutil # local copy of Python 2.5 pkgutil.py

# Globals
logger = logging.getLogger(__name__)


##############################################################################
# Main function - this is probably the one you are interested in
##############################################################################

def find_functions(package, import_method=False):
    """ Recursively find all the functions in a package or module.

        By default, find_functions searches for functions by "scanning"
        the code for function definitions.  It does this by using Python's
        AST.  This prevents python from loading all of the modules into
        memory, but it also can miss some functions.  Setting
        import_method=True will actually import the modules in its search
        and may find functions that are not found using the other method.

        Parameters
        ----------
        package: str
            A string such as 'foo.bar' that specifies the package to
            search.  The package must be on the python path.
        import_method: bool
            Default is False.   When True, modules are imported when
            searching for functions.

        Returns
        -------
        functions: list of tuples
            A list of tuples with (module, name). module is a string for
            specifying the python module and the function name.  For example
            function 'foo.bar' would be returned as ('foo','bar')
    """

    if import_method:
        functions = find_functions_import(package)
    else:
        functions = find_functions_ast(package)

    return functions

##############################################################################
# Search helper functions/classes
##############################################################################

def find_functions_ast(package):
    """ Find functions by traversing an abstract syntax tree generated by the
        compiler module.
        fixme: expand docstring, possibly provide response about non-existant
        modules/packages
    """
    functions = []
    # It is a package (ie a directory)
    if is_package(package):
        package_path = get_module_path(package)
        file_paths = find_package_sub_modules(package)
        for file_path in file_paths:
            try:
                file = open(file_path)
                # Adding a new line to the source, so that compile wouldn't
                # throw a SyntaxError on EOF comment
                source = file.read().replace('\r\n','\n')+'\n'
                ast = compile(source, file_path,'exec', _ast.PyCF_ONLY_AST)
                file.close()
                python_path = python_path_from_file_path(package, file_path, package_path=package_path)
                functions.extend(visit_ast_node(ast, file_path, python_path))
            except SyntaxError:
                msg = 'SyntaxError in parsing file %s'% file_path
                logger.error(msg)

    # It is a module (ie a .py file)
    elif is_module(package):
        file_path = get_module_path(package)
        file = open(file_path)

        # Adding a new line to the source, so that compile wouldn't
        # throw a SyntaxError on EOF comment
        source = file.read().replace('\r\n','\n')+'\n'

        ast = compile(source, file_path, 'exec', _ast.PyCF_ONLY_AST)
        file.close()
        functions.extend(visit_ast_node(ast, file_path, package))

    return functions


def visit_ast_node(node, path, python_path):
    """ Given a and _ast node produced by 'compile' with the _ast.PyCF_ONLY_AST
        flag, returns a list of CallableObjects s from that node's toplevel
        functions.
    """
    functions = []

    for child in node.body:
        if isinstance(child, _ast.FunctionDef):
            mod_and_name = (python_path, child.name)
            functions.append(mod_and_name)

    return functions


def find_functions_import(package):
    """ Find functions using an import statement. Sloppier and consumes more
        memory than find_functions_ast, but also get submodules of the modules,
        which the ast method cannot do. For example, giving it 'os', it would
        also find functions from os.path. It also follows import statements in
        the files, which may or may not be desirable.
    """
    functions = []
    if is_package(package):
        package_path = get_module_path(package)
        file_paths = find_package_sub_modules(package)

        for file_path in file_paths:
            python_path = python_path_from_file_path(package, file_path, package_path=package_path)
            results = find_functions_import_recurse(python_path)
            functions.extend(results)
    else:
        functions = find_functions_import_recurse(package)

    return functions

def find_functions_import_recurse(module_name):
    """ Search a module and all the modules within it for functions.

        The function imports the module and searches its __dict__ for
        functions.  It also search any module found within the module
        for functions.
    """
    functions = []
    try:
        exec "import " + module_name in globals()
        exec "mod_dict = " + module_name+".__dict__"
    except:
        # Skip the rest of processing.
        mod_dict = {}

    for name, item in mod_dict.items():

        if (inspect.isfunction(item) or
            inspect.isbuiltin(item)):
            mod_and_name = (module_name, item.__name__)
            functions.append(mod_and_name)
        elif (inspect.ismodule(item) and
              item is not 'UserDict'):
            results = find_functions_import_recurse(module_name+'.'+name)
            functions.extend(results)

    return functions

##########################################################################
# Utility functions
##########################################################################

def python_path_from_file_path(package, file_path, package_path=None):
    """ Given a package/module name and the absolute path to a python file,
        return a path in the form that python can understand (ie one that
        could be specified in an import statement)  package_path can be
        optionally specified to give the file path to the package.  This
        is automatically determined if not specified, but as determining this
        is an expensive operation, it is best to calculate this outside
        the function if one will be looking up many functions in the same
        module.
    """


    file_path = normalize_path_separator(file_path)
    if package_path == None:
        try:
            package_path = get_module_path(package)
        except:
            # FIXME: We're failing to get the loader, probably because
            # of a bad import or syntax error in __init__.py.
            # Use the old algorithm for now but this should be marked
            # to the user in the future.
            try:
                start = file_path.rindex(package+os.path.sep)
            except ValueError:
                start = file_path.rindex(package)

            stop = file_path.rindex('.')
            python_path = file_path[start:stop]
            python_path = python_path.replace(os.path.sep, '.')
            return python_path

    package_path = normalize_path_separator(package_path)

    try:
        if file_path.find(package_path) != 0:
            return ''
        file_suffix = file_path[len(package_path):]
        package_suffix = file_suffix.replace(os.path.sep, '.')
        if package_suffix[-3:] == '.py':
            package_suffix = package_suffix[:-3]
        return package + package_suffix
    except:
        return ''

def normalize_path_separator(file_path):
    """ Ensure the file path uses the platform's directory separator.
    """
    return os.path.join(*os.path.split(file_path))

def get_module_path(module_name):
    """ Given a module, get an absolute path to it.

        pkgutil, instead of imp, is used for 2 reasons:

          * pkgutil works with dotted names
          * pkgutil works with eggs

        There are a couple of downsides, the methods we use are not
        documented and the method was added in python 2.5. For convenience,
        _pkgutil is used instread, which is copied from Python 2.5 to support
        Python 2.4.

    """

    imp_loader = _pkgutil.get_loader(module_name)
    if imp_loader is None:
        logger.error("Search Path not found for module: %s", module_name)
        return ''
    return imp_loader.filename

def is_package(module_name):
    """ Return whether the given module name is a package.

        This function will search the standard python path for the module.
        If it is defined as an __init__.py, we return True.  Otherwise False.
    """

    path = get_module_path(module_name)
    if os.path.isdir(path):
        result = True
    else:
        result = False

    return result

def is_module(module_name):
    """ Return whether the given module name is a module.
    """

    path = get_module_path(module_name)
    if os.path.isfile(path):
        result = True
    else:
        result = False

    return result

def find_package_sub_modules(package, recurse=True):
    """ Return a list of python modules (.py files) in a package.
    """

    path = get_module_path(package)
    return find_path_sub_modules(path, recurse)

def find_path_sub_modules(path, recurse=True):
    """ Return a list of python modules (.py files) in a directory.
        If an __init__.py file is not present, do not look in the directory.
    """

    sub_modules = []
    check_init_path = os.path.join(path, "__init__.py")
    if os.path.isdir(path) and os.path.isfile(check_init_path):
        # First, handle adding all python files as sub modules to the list.
        python_file_pattern = os.path.join(path,'*.py')
        python_files = glob(python_file_pattern)
        sub_modules.extend(python_files)

        # Now search any subdirectory for packages.
        if recurse:
            files = [os.path.join(path, file) for file in os.listdir(path)]
            dirs = [d for d in files if os.path.isdir(d)]

            for dir in dirs:
                python_files = find_path_sub_modules(dir)
                sub_modules.extend(python_files)

    return sub_modules


if __name__ == "__main__":
    import doctest
    doctest.testmod()
