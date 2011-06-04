# Standard library imports
import unittest
import compiler

# Enthought library imports
from enthought.block_canvas.function_tools.local_function_info import \
    LocalFunctionInfo
from enthought.block_canvas.function_tools.parse_tools import find_local_defs


class LocalFunctionInfoTestCase(unittest.TestCase):


    ##########################################################################
    # LocalFunctionInfoTestCase interface
    ##########################################################################

    def test_update_changes_settings(self):
        """ When the code changes, do the inputs, outputs, name, etc update?
        """

        # Initialize function with code.
        code = "def foo():\n" \
               "    pass"

        ast_code = compiler.parse(code)
        local_funcs = find_local_defs(ast_code)
        func = LocalFunctionInfo.from_function_ast(local_funcs['foo'])

        self.assertEqual(func.name, "foo")
        inputs = [(x.name, x.default) for x in func.inputs]
        self.assertEqual(inputs, [])
        outputs = [x.name for x in func.outputs]
        self.assertEqual(outputs, [])
        self.assertEqual(func.doc_string, "")
        self.assertTrue(func.is_valid)
        self.assertFalse(func.load_error)

        # Now update the function with new code.
        func.code = "def bar(x):\n" \
                    "    'doc string'\n" \
                    "    return y"

        self.assertEqual(func.name, "bar")
        inputs = [(x.name, x.default) for x in func.inputs]
        self.assertEqual(inputs, [('x',None)])
        outputs = [x.name for x in func.outputs]
        self.assertEqual(outputs, ['y'])
        self.assertEqual(func.doc_string, 'doc string')
        self.assertTrue(func.is_valid)
        self.assertFalse(func.load_error)

    def test_bad_code(self):
        """ Do we handle bad code safely?
        """
        code = "blah("

        func = LocalFunctionInfo(code=code)
        self.assertEqual(func.inputs, [])
        self.assertEqual(func.outputs, [])
        self.assertFalse(func.is_valid)
        self.assertTrue(func.load_error)

        # And if we update, do all the values change as desired.
        func.code = "def bar(x):\n" \
                    "    return y"

        self.assertEqual(func.name, "bar")
        inputs = [(x.name, x.default) for x in func.inputs]
        self.assertEqual(inputs, [('x',None)])
        outputs = [x.name for x in func.outputs]
        self.assertEqual(outputs, ['y'])
        self.assertTrue(func.is_valid)
        self.assertFalse(func.load_error)

    def test_empty(self):
        """ Do we handle bad code safely?
        """
        code = ""

        func = LocalFunctionInfo(code=code)
        self.assertEqual(func.inputs, [])
        self.assertEqual(func.outputs, [])
        self.assertFalse(func.is_valid)
        self.assertFalse(func.load_error)

        # And if we update, do all the values change as desired.
        func.code = "def bar(x):\n" \
                    "    return y"

        self.assertEqual(func.name, "bar")
        inputs = [(x.name, x.default) for x in func.inputs]
        self.assertEqual(inputs, [('x',None)])
        outputs = [x.name for x in func.outputs]
        self.assertEqual(outputs, ['y'])
        self.assertTrue(func.is_valid)
        self.assertFalse(func.load_error)

if __name__ == '__main__':
    unittest.main()
