""" Unit testing for parametric interactor.
"""

# Standard imports
import unittest

# Major library imports.
import nose

raise nose.SkipTest("ParametricInteractor not implemented")

# ETS imports
from enthought.numerical_modeling.workflow.block.api import Block

# Local imports
from enthought.block_canvas.context.api import DataContext, MultiContext
from enthought.block_canvas.interactor.parametric_interactor import ParametricInteractor


class ParametricInteractorTestCase(unittest.TestCase):
    """ Unit testing for ParametricInteractor
    """

    def setUp(self):
        code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
               "c = add(a,b)\n" \
               "d = mul(c, 2)\n" \
               "e = mul(c, 3)\n" \
               "f = add(d,e)"

        self.block=Block(code)

        # Context setup.
        self.context = MultiContext(DataContext(name='Data'),{})
        self.context['a'] = 1
        self.context['b'] = 2


    def test_attributes(self):
        """ Test if creation of attributes is working correctly
        """
        interactor = ParametricInteractor(context=self.context,block=self.block)

        self.assertTrue(hasattr(interactor, interactor._input_prefix + "a"))
        self.assertTrue(hasattr(interactor, interactor._input_prefix + "b"))

        # Check if the parameter items were written correctly
        attribute_a = getattr(interactor, interactor._input_prefix+'a')
        attribute_b = getattr(interactor, interactor._input_prefix+'b')

        self.assertEqual(attribute_a.step, 0)
        self.assertEqual(attribute_a.low, 1)
        self.assertEqual(attribute_a.high, 1)

        self.assertEqual(attribute_b.step, 0)
        self.assertEqual(attribute_b.low, 2)
        self.assertEqual(attribute_b.high, 2)

        # Check if the inputs in the interactor are right
        self.assertEqual(interactor.inputs, list(self.block.inputs))


    def test_create_shadows(self):
        """ Test if creating shadows is working correctly
        """
        interactor = ParametricInteractor(context=self.context,block=self.block)

        # Change the parameters for the attributes
        attribute_a = getattr(interactor, interactor._input_prefix+'a')
        attribute_b = getattr(interactor, interactor._input_prefix+'b')

        attribute_a.high = 4
        attribute_a.step = 1

        attribute_b.high = 3
        attribute_b.step = 1

        # Create the shadows.
        interactor._update_contexts_button_changed()

        # Check if the shadows were created correctly.
        self.assertEqual(len(self.context.shadows),
                len(attribute_a.output_list)*len(attribute_b.output_list))

        # Check if the shadow context gives desired result.
        self.block.execute(self.context.shadows[-1])
        self.assertEqual(self.context.shadows[-1]['f'],
               5*(self.context.shadows[-1]['a']+self.context.shadows[-1]['b']))


### EOF ------------------------------------------------------------------------
