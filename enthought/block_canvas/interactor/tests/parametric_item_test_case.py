""" Unit testing for ParametricItem.
"""

# Standard imports
import unittest

# Local imports
from enthought.block_canvas.interactor.parametric_item import ParametricItem


class ParametricItemTestCase(unittest.TestCase):
    """ Unittesting for ParametricItem
    """

    def setUp(self):
        self.value = ParametricItem(name = 'a', input_value = 100)


    def test_inputs(self):
        """ Is the default setting done correctly ?
        """

        self.assertEqual(self.value.name, 'a')
        self.assertEqual(self.value.input_value, 100)
        self.assertEqual(self.value.low, 100)
        self.assertEqual(self.value.high, 100)
        self.assertEqual(self.value.step, 0)


    def test_attribute_changes(self):
        """ Does the output list change desirably to the changes in attributes?
        """

        self.value.low = 0
        self.assertEqual(self.value.output_list, [100])

        self.value.step = 10
        desired_output = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        self.assertEqual(self.value.output_list, desired_output)

        self.value.low = 150
        desired_output = [100, 110, 120, 130, 140, 150]
        self.assertEqual(self.value.output_list, desired_output)

        self.value.step = -10
        desired_output = [150, 140, 130, 120, 110, 100]
        self.assertEqual(self.value.output_list, desired_output)

        self.value.input_value = -100
        self.value.low = -150
        self.value.step = 10

        desired_output = [-150, -140, -130, -120, -110, -100]
        self.assertEqual(self.value.output_list, desired_output)

        self.value.high = -200
        desired_output = [-200, -190, -180, -170, -160, -150]
        self.assertEqual(self.value.output_list, desired_output)


### EOF ------------------------------------------------------------------------