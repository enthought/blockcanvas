""" Tests for PythonFunction.
"""
import unittest
import os

# Enthought library imports
from enthought.block_canvas.function_tools.search_package import get_module_path

# local imports
from enthought.block_canvas.function_tools.python_function_info import \
    PythonFunctionInfo
    
from typical_functions import empty, simple, \
    with_defaults, with_defaults_none
                                     


class PythonFunctionInfoTestCase(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # PythonFunctionInfoTestCase interface
    ##########################################################################

    def _check_input(self, actual, desired):
        """Check a list of InputArguments against a tuple of
        (name, default) pairs and assert if not equal"""
        for input_index, desired_input in enumerate(desired):
            self.assertEqual(actual[input_index].name, desired_input[0])
            self.assertEqual(actual[input_index].default, desired_input[1])
        return

    def _check_output(self, actual, desired):
        """Check a list of OutputArguments against a list of desired names.
        assert if not equal."""
        for output_index, desired_output in enumerate(desired):
            self.assertEqual(actual[output_index].name, desired_output)
        return

    def test_empty(self):
        """ Can we handle a function without any inputs/outputs?
        """
        func = PythonFunctionInfo.from_function(empty)
        self.assertEqual(func.doc_string, "")


    def test_simple(self):
        func = PythonFunctionInfo.from_function(simple)

        # Check the inputs.
        inputs = func.inputs
        desired = (('a', None), ('b', None))
        self._check_input(inputs, desired)

        # Now check the output names.
        outputs = func.outputs
        desired = ('x','y')
        self._check_output(outputs, desired)
        
    def test_with_defaults(self):
        func = PythonFunctionInfo.from_function(with_defaults)

        # Check the inputs.
        inputs = func.inputs
        desired = (('a', None), ('b', '3'))
        self._check_input(inputs, desired)

        # Now check the output names.
        outputs = func.outputs
        desired = ('x','y')
        self._check_output(outputs, desired)

    def test_with_defaults_none(self):
        func = PythonFunctionInfo.from_function(with_defaults_none)

        # Check the inputs.
        inputs = func.inputs
        desired = (('a', None), ('b', 'None'))
        self._check_input(inputs, desired)

        # Now check the output names.
        outputs = func.outputs
        desired = ('x','y')
        self._check_output(outputs, desired)

    def test_change_library_name(self):
        func = PythonFunctionInfo.from_function(simple)

        self.assertEqual(func.name, 'simple')
        self.assertEqual(func.library_name, 'simple')
        
        func.library_name = 'foo'
        self.assertEqual(func.name, 'simple')
        self.assertEqual(func.library_name, 'foo')
        
    def test_code(self):
        func = PythonFunctionInfo.from_function(simple)
        correct_code = """def simple(a,b):
    x,y=a,b
    return x,y
"""
        self.assertEqual(func.code, correct_code)
   
    def test_parse_error(self):
        # Because having a function checked in with a parse error creates problems
        # with the egg builder, we take an existing file and modify it.
        old_module = 'enthought.block_canvas.function_tools.tests.sample_package.error_package'
        old_filename = get_module_path(old_module)
        new_filename = old_filename[:-3] + '2.py'
        new_module = old_module+'2'
        lines = open(old_filename).readlines()
        # Strip off the colon on the end of the second line to create a syntax error
        lines[1] = lines[1][:-1]
        open(new_filename, 'w').writelines(lines)
        
        func = PythonFunctionInfo(module=new_module, name='badfunction')
        self.assertEqual(func.load_error, "failed to parse module '%s'" % new_module)
        os.unlink(new_filename)
        
# Missing Tests
# 1. All the classmethod constructors.
# 2. Changing package, name, etc. does it update loader.
# 3. varargs/kwargs when implemented
# 4. Functions with errors in them -- no return vale in particular

if __name__ == '__main__':
    unittest.main()
