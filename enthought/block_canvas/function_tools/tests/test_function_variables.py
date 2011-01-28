# Standard library imports
import unittest

# Enthought library imports
from enthought.traits.api import TraitError

# local imports
from enthought.block_canvas.function_tools.function_variables import \
    Variable, InputVariable, OutputVariable


class VariableTestCase(unittest.TestCase):

    variable_class = Variable

    ##########################################################################
    # VariableTestCase interface
    ##########################################################################

    def test_default_binding(self):
        v = self.variable_class(name='a')
        self.assertEqual(v.name , 'a')
        self.assertEqual(v.binding , 'a')

    def test_set_binding(self):
        v = self.variable_class(name='a')
        self.assertEqual(v.name , 'a')
        self.assertEqual(v.binding , 'a')
        v.binding = '1'
        self.assertEqual(v.binding , '1')

class InputVariableTestCase(VariableTestCase):

    variable_class = InputVariable

    def test_no_default_value(self):
        v = self.variable_class(name='a')
        self.assertEqual(v.name , 'a')
        self.assertEqual(v.binding , 'a')

        self.assertFalse(v.keyword_argument)
        self.assertEqual(v.call_signature,"a")

    def test_default_value(self):
        v = self.variable_class(name='a', default='0')
        self.assertEqual(v.name , 'a')
        self.assertEqual(v.binding , '0')

        self.assertTrue(v.keyword_argument)
        self.assertEqual(v.call_signature,"")

    def test_bound_default_value(self):
        v = self.variable_class(name='a', default='0')
        v.binding = '1'
        self.assertEqual(v.binding , '1')
        self.assertEqual(v.call_signature,"a=1")

class OutputVariableTestCase(VariableTestCase):

    variable_class = OutputVariable

    def test_set_binding(self):
        v = self.variable_class(name='a', default='0')
        self.assertEqual(v.name , 'a')
        v.binding = "a1"
        self.assertEqual(v.binding , "a1")

    def test_set_number(self):
        v = self.variable_class(name='a', default='0')

        def set_number():
            v.binding = '1'
        self.assertRaises(TraitError, set_number)

    def test_bad_variable(self):
        v = self.variable_class(name='a', default='0')
        def set_bad_variable():
            v.binding = "1a"
        self.assertRaises(TraitError, set_bad_variable)


if __name__ == '__main__':
    unittest.main()
