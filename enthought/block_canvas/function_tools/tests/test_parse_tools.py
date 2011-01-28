# Standard library imports
import unittest
import compiler

# local imports
from enthought.block_canvas.function_tools.parse_tools import \
    function_returns_from_function, function_arguments_from_function, \
    function_arguments_from_ast

from parse_tools_test_functions import *

##############################################################################
# function_returns_from_function tests
##############################################################################

class FunctionReturnsFromFunctionTestCase(unittest.TestCase):
    """ This test case also is a reasonable test for
        function_returns_from_ast and function_returns_from_code because
        it is a wrapper around these.
    """

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_return_constant(self):
        actual = function_returns_from_function(return_constant)
        self.assertEqual(actual, ['result'])

    def test_return_none(self):
        actual = function_returns_from_function(return_none)
        self.assertEqual(actual, [])

    def test_empty_return(self):
        actual = function_returns_from_function(empty_return)
        self.assertEqual(actual, [])

    def test_return_vp(self):
        actual = function_returns_from_function(return_vp)
        self.assertEqual(actual, ['vp'])

    def test_return_vp_vs(self):
        actual = function_returns_from_function(return_vp_vs)
        self.assertEqual(actual, ['vp', 'vs'])

    def test_return_vp_vs2(self):
        actual = function_returns_from_function(return_vp_vs2)
        self.assertEqual(actual, ['vp', 'vs'])

    def test_local(self):
        """ We fail on locals, but we shouldn't cause tracebacks.
        """

        def return_local(val):
            return val

        actual = function_returns_from_function(return_local)
        actual = None
        self.assertEqual(actual, None)


    def test_builtin(self):
        """ Ensure we don't completely fail when inpsecting a builtin.
        """
        actual = function_returns_from_function(dir)
        actual = None
        self.assertEqual(actual, None)

    def test_extension_function(self):
        """ Ensure we don't completely fail when inpsecting an extension.
        """
        import select
        actual = function_returns_from_function(select.select)
        actual = None
        self.assertEqual(actual, None)



##############################################################################
# function_arguments_from_function tests
##############################################################################

class FunctionArgumentsFromFunctionTestCase(unittest.TestCase):
    """ This test case also is a reasonable test for
        function_returns_from_ast and function_returns_from_code because
        it is a wrapper around these.
    """

    def test_just_args(self):

        def func(x, y):
            pass

        args, var_args, kw_args = function_arguments_from_function(func)
        self.assertEqual(args, [('x',None),('y',None)])
        self.assertEqual(var_args, "")
        self.assertEqual(kw_args, "")

    def test_just_kwds(self):

        def func(x=1, y=2):
            pass

        args, var_args, kw_args = function_arguments_from_function(func)
        self.assertEqual(args, [('x','1'),('y','2')])
        self.assertEqual(var_args, "")
        self.assertEqual(kw_args, "")

    def test_args_and_kwds(self):

        def func(x, z=1, y=2):
            pass

        args, var_args, kw_args = function_arguments_from_function(func)
        self.assertEqual(args, [('x',None),('z','1'), ('y','2')])
        self.assertEqual(var_args, "")
        self.assertEqual(kw_args, "")


    def test_args_and_kwds_and_varargs(self):

        def func(x, z=1, y=2, *args):
            pass

        args, var_args, kw_args = function_arguments_from_function(func)
        self.assertEqual(args, [('x',None),('z','1'), ('y','2')])
        self.assertEqual(var_args, "args")
        self.assertEqual(kw_args, "")

    def test_args_and_kwds_and_varargs_and_kwargs(self):

        def func(x, z=1, y=2, *args, **kw):
            pass

        args, var_args, kw_args = function_arguments_from_function(func)
        self.assertEqual(args, [('x',None),('z','1'), ('y','2')])
        self.assertEqual(var_args, "args")
        self.assertEqual(kw_args, "kw")

##############################################################################
# function_arguments_from_ast tests
##############################################################################

class FunctionArgumentsFromAstTestCase(unittest.TestCase):
    """ This test case also is a reasonable test for
        function_returns_from_ast and function_returns_from_code because
        it is a wrapper around these.
    """

    def _args_from_code(self, code):
        mod = compiler.parse(code)
        # Pull the function out the Module->Stmt nodes of the tree.
        func = mod.node.nodes[0]
        return function_arguments_from_ast(func)

    def test_just_args(self):

        code = "def func(x, y):\n" \
               "    pass"

        args, var_args, kw_args = self._args_from_code(code)
        self.assertEqual(args, [('x',None),('y',None)])
        self.assertEqual(var_args, "")
        self.assertEqual(kw_args, "")

    def test_just_kwds(self):

        code = "def func(x=1, y=2):\n" \
               "    pass"

        args, var_args, kw_args = self._args_from_code(code)
        self.assertEqual(args, [('x','1'),('y','2')])
        self.assertEqual(var_args, "")
        self.assertEqual(kw_args, "")

    def test_args_and_kwds(self):

        code = "def func(x, z=1, y=2):\n" \
               "    pass"

        args, var_args, kw_args = self._args_from_code(code)
        self.assertEqual(args, [('x',None),('z','1'), ('y','2')])
        self.assertEqual(var_args, "")
        self.assertEqual(kw_args, "")


    def test_args_and_kwds_and_varargs(self):

        code = "def func(x, z=1, y=2, *args):\n" \
               "    pass"

        args, var_args, kw_args = self._args_from_code(code)
        self.assertEqual(args, [('x',None),('z','1'), ('y','2')])
        self.assertEqual(var_args, "args")
        self.assertEqual(kw_args, "")

    def test_args_and_kwds_and_varargs_and_kwargs(self):

        code = "def func(x, z=1, y=2, *args, **kw):\n" \
               "    pass"

        args, var_args, kw_args = self._args_from_code(code)
        self.assertEqual(args, [('x',None),('z','1'), ('y','2')])
        self.assertEqual(var_args, "args")
        self.assertEqual(kw_args, "kw")

if __name__ == '__main__':
    unittest.main()
