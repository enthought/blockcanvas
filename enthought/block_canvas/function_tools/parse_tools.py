""" Tools for parsing/unparsing python code to discover information about it.
"""

# Standard library imports
import inspect
import compiler
from compiler.visitor import ASTVisitor
import sys
import warnings
from compiler.ast import Module, Function, Stmt

# Enthought library imports
from enthought.blocks.analysis import walk
from enthought.blocks.api import unparse

# Local imports
from decorator_tools import getsource
import _pkgutil
from function_variables import OutputVariable

# Flags for func_code.co_flags that indicate whether we have a
# variable number of arguments or keyword arguments for the function.
VAR_ARGS = 4
KW_ARGS = 8


##############################################################################
# Tools for finding function imports
##############################################################################

class LocalDefinitionsWalker:
    def __init__(self):
        self.local_funcs = {}

    def visitFunction(self, node):
        """ Add names of local function definitions to the info dict. """
        def_name = node.name
        self.local_funcs[def_name] = node

def find_local_defs(ast):
    """ Given Block's ast, return a dictionary of def names and
        the Function ast that represents them.  This will be used
        to create a LocalFunctionInfo.
    """
    res = walk(ast, LocalDefinitionsWalker()).local_funcs
    return res


##############################################################################
# Tools for finding function inputs
##############################################################################

def function_arguments_from_function(func):
    """ Given a function, return its args, keywords, and full argument list.

        Parameters
        ----------
        func
            a function object.

        Returns
        -------
        args
            List of (name, default) argument pairs.  `name` is always a string.
            `default` is None if it is not present.  Otherwise, it is a string
            version of the default.
        var_args
            Name of the \*args argument.  Empty if it missing.
        kw_args
            Name of the \*\*kw argument.  Empty if it missing.
    """

        #fixme: This is duplicated from:
        #    enthought\numerical_modeling\units\function_signature.py
        #fixme: Rework this methods so that it returns
        #    args, var_args, kw_args
        #    args should be a list of (name, default) strings.  If default
        #    is not set, it should be None.

    # Number of arguments to the function.
    arg_count = func.func_code.co_argcount

    # Names of the local variables in the function.
    var_names = list(func.func_code.co_varnames)

    # The variables that come from the function inputs are at the form of the
    # local variable list.
    args_ordered = var_names[:arg_count]

    # Tuple of default values.  They are the values supplied to keyword
    # arguments and match to the last arguments in the
    # args_ordered list. It is None, if there are no keyword arguments.
    defaults = func.func_defaults or []

    # map defaults to string values.
    defaults = [str(value) for value in defaults]

    no_defaults_count = len(args_ordered) - len(defaults)
    defaults = [None] * no_defaults_count + list(defaults)
    args = zip(args_ordered, defaults)

    # Handle variable length and arbitrary keyword arguments.
    var_args = ""
    kw_args = ""
    flags = func.func_code.co_flags
    var_kw_args = var_names[arg_count:]
    index = 0
    if flags & VAR_ARGS:
        var_args = var_kw_args[index]
        index += 1
    if flags & KW_ARGS:
        kw_args = var_kw_args[index]


    return args, var_args, kw_args



def function_inputs_from_call_ast(ast, info=None):
    """ Returns function names and input/output binding
        information from the CallFunc.
    """
    func = walk(ast, FunctionCallWalker())
    func_names = func.func_names
    func_args = func.func_args

    if len(func_names) == 1:
        return func_names, func_args
    else:
        return None

class FunctionCallWalker(ASTVisitor):
    """ Collects binding information from the CallFunc.
        This Walker is only useful if there is only one function
        being walked.
    """
    def __init__(self):
        self.func_names = []
        self.func_args = []

    def visitCallFunc(self, node):
        self.func_names.append(node.node.name)
        for arg in node.args:
            if hasattr(arg, 'name'):
                self.func_args.append(arg.name)
            elif hasattr(arg, 'value'):
                self.func_args.append(arg.value)
            else:
                msg = "Unknown argument, %s" % arg
                warnings.warn(msg)

def _get_keyword_defaults(default_nodes, func_name):
    """ Translate the default nodes of an ast into default arguments.
    """
    # Unwrap the default values.
    # fixme: We could stand better warning messages here.
    defaults=[]
    for node in default_nodes:
        # fixme
        if isinstance(node, compiler.ast.Const):
            default = str(node.value)
        elif isinstance(node, compiler.ast.Name):
            if node.name in ["None", "True", "False"]:
                default = node.name
            else:
                msg = "Got variable name for keyword value in " \
                      "function: %s.  Using its name: %s" % \
                      (func_name, node.name)
                warnings.warn(msg)
                default = node.name
        else:
            # Try unparsing and evaluating it.  This will work if
            # the value is something like "-1.0".  If we fail for
            # any reason, issue a warning and use undefined as the
            # value.
            try:
                default = unparse(node)
            except:
                msg = "Got '%s' node for keyword value in function." \
                      "  Using None as a stopgap." % node
                warnings.warn(msg)
                default = None

        defaults.append(default)

    return defaults

def _get_varargs_kwargs(varargs, kwargs, argnames):
    """ Determine the variable names for the varargs and kwargs variables.


        These will be empty if the function doesn't have either of
        these values (varargs==kwargs==False).  Otherwise, this
        method will determine which names to read out of the argnames
        list to determine these values.

        Parameters:
        -----------
        varargs: Bool
            Does this function have a *args value in the signature?

        kwargs: Str
            The name of the arbitrary keywords argument in its
            signature?

        argnames: List(Str)
            The names of all the function arguments as read from
            the AST.

        Returns:
        --------
        func_varargs: Str
            Name of the varargs variable

        func_kwargs: Str
            Name of keyword args variable

    """

    if varargs and not kwargs:
        func_varargs = argnames[-1]
        func_kwargs = ""
    elif not varargs and kwargs:
        func_varargs = ""
        func_kwargs = argnames[-1]
    elif varargs and kwargs:
        func_varargs = argnames[-2]
        func_kwargs = argnames[-1]
    else:
        func_varargs = ""
        func_kwargs = ""
    return func_varargs, func_kwargs


def function_arguments_from_ast(ast):
    """ Convert the inputs found in the AST into InputVariable objects.

        This handles finding the keyword arguments and trying to convert
        them from their AST representation into something that is useful
        as a default argument.  We also track whether the input arguments
        include a varargs (``*args``) and kwargs (``**kw``) style argument.  If
        they do, we assign the names to the varargs and kwargs traits on
        the class.
    """
    # First, find out if the function has any *args or **kw type arguments.
    # If so, update the names of these varargs and kwargs traits.
    varargs = ast.varargs == True
    kwargs = ast.kwargs == True
    var_args, kw_args = _get_varargs_kwargs(varargs, kwargs, ast.argnames)

    # There is little used syntax in python where arguments can be specified
    # in a tuple for grouping.  We flatten these out.
    flattened_argnames = []
    for argname in ast.argnames:
        if type(argname) == type(()):
            flattened_argnames.extend(argname)
        else:
            flattened_argnames.append(argname)


    # Now trim off the varargs and kwargs names from the argument list
    # if they exist.
    argname_count = len(flattened_argnames) - varargs - kwargs
    argnames = flattened_argnames[:argname_count]


    # Create the array of arg,defaults pairs.  Use undefined, if no default
    # is given.
    defaults = _get_keyword_defaults(ast.defaults, ast.name)
    no_defaults_count = len(argnames) - len(defaults)
    defaults = [None] * no_defaults_count + defaults
    args = zip(argnames, defaults)

    return args, var_args, kw_args

def outputs_from_function_ast(func_ast):
    """ Find the outputs by parsing the return statement in the ast and
        getting the names of the returned arguments.

    """
    # Limit the ast to the one for this function node.
    ast = find_function_node(func_ast, True)
    results = compiler.walk(ast, ReturnVariablesFinder()).return_vals

    if results:
        output_names = results[0]
        # Create an output variable for each of the return values.
        outputs = [OutputVariable(name=arg) for arg in output_names]
    else:
        # This function doesn't have any outputs.
        outputs = []
    return outputs

def find_function_node(func_ast, check_name):
    """finds the funtion node, optionally matching the name

       fixme: Why would you ever not want to check that the name matches?
              This seems dangerous.
    """

    ast = func_ast

    if isinstance(ast, Module):
        ast = ast.node

    if isinstance(ast, Function):
        return ast

    if isinstance(ast, Stmt):
        for node in ast.nodes:
            if isinstance(node, Function):
                if not check_name:
                    return node
                #FIXME what the heck is self?
                if node.name == self.name:
                    return node

    raise ValueError("Code does not contain a function declaration")


##############################################################################
# Tools for finding function return values.
##############################################################################

def function_returns_from_code(code):
    """ Find the function returns from its source

        Parameters:
        -----------
        code: Str
            source code of the function

    """

    # try/except to protect against parse errors.
    try:
        ast = compiler.parse(code)
    except SyntaxError:
        ast = None

    if ast is not None:
        result = function_returns_from_ast(ast)
    else:
        result = None

    return result


def function_returns_from_ast(ast):
    """ Find the function returns from a function's ast.

        Parameters:
        -----------
        code: Str
            source code of the function

    """

    result = None

    if ast is not None:
        return_vals = walk(ast, ReturnVariablesFinder()).return_vals
        if len(return_vals) != 0:
            # The last set of return vals is likely to be the most used.
            result = return_vals[-1]
        else:
            result = []
    return result

def function_returns_from_function(func):
    """ Find the return values names from a function by looking at its source.

        This isn't always possible, but this function gets the source code,
        looks for return statements for variable names.  If all values in
        the return statement are variable names, it returns these names.  If
        it is more complex, or it is unable to find the source code, it returns
        None.

        Example:

        >>> from ftplib import parse227
        >>> function_returns_from_function(parse227)
        ['host', 'port']

    """
    result = None

    # Get the source for the function.  Ensure that func is actually a function.
    # fixme: Inspect may not be a very reliable source for getting the code.
    #        check into how often this fails.
    try:
        try:
            source = inspect.getsource(func)
        except IOError:
            source = getsource(func)
    except TypeError:
        source = None

    if source is not None:
        # Remove tabs to make local functions global
        lines = source.expandtabs().splitlines()
        stripped = lines[0].lstrip()
        indent = sys.maxint
        if stripped:
            indent = min(indent, len(lines[0])-len(stripped))

        for i in range(len(lines)):
            stripped = lines[i].lstrip()
            current_indent = max(0,len(lines[i])-len(stripped)-indent)
            lines[i] = ' '*current_indent+stripped

        source = '\n'.join(lines)

        # Obtain the function returns from the source
        result = function_returns_from_code(source)

    return result


class ReturnVariablesFinder:
    """ AST Visitor Class for finding the return_vals from a function.

        return_vals is a list of lists.  Each list is the set of variable
        names from a return statement in the function.  For example:

            >>> code = '''
            ... def foo(x):
            ...     if x:
            ...         return vp, vs
            ...     else:
            ...         return vp
            ... '''
            >>> import compiler
            >>> ast = compiler.parse(code)
            >>> walk(ast, ReturnVariablesFinder()).return_vals
            [['vp', 'vs'], ['vp']]

        This will only return the values from functions that have simple
        return statements.  For example

            >>> code = '''
            ... def foo(x):
            ...     return bar(x)
            ... '''
            >>> import compiler
            >>> ast = compiler.parse(code)
            >>> walk(ast, ReturnVariablesFinder()).return_vals
            [['result']]

        fixme: Handle empty list return statement in some way.
    """

    def __init__(self):
        self.return_vals = list()

    def visitReturn(self, node):
        """ Inspect the return node's contents to see if it is filled with
            simple name variables that we can infer are the names of the
            return variables.
        """
        from compiler.ast import Tuple, Name, Const

        # If the contents of the return statement is a name variable, then
        # it is the only return value for this statement.
        if isinstance(node.value, Name):
            self.return_vals.append([node.value.name])

        # If it is a tuple, and all the tuple contents are Name variables,
        # then we'll return the list.
        elif isinstance(node.value, Tuple):
            children = node.value.nodes
            names = [child.name for child in children
                         if isinstance(child,Name)]
            # Ensure all variables were simple name variables.
            if len(names) == len(children):
                self.return_vals.append(names)

        # its a const or the result of an operation in which case we cannot
        # guess at a good name
        elif isinstance(node.value, Const) and (node.value.value is None):
            # This is the case for an empty return statement, we return
            # an empty list.
            # fixme: It will also cause a 'return None' line to report
            #        that it doesn't return anything.  I think this is
            #        fine, but I'm not positive.
            self.return_vals.append([])
        else:
            # We default to treating the return value as a single value
            # called "result"
            self.return_vals.append(['result'])

        return



if __name__ == "__main__":
    import doctest
    doctest.testmod()
