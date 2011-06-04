""" Unit testing for stochastic interactor.
"""

# Standard imports
import numpy, unittest

# Major library imports.
import nose

# ETS imports
from enthought.numerical_modeling.workflow.api import Block

# Local imports
from enthought.contexts.api import DataContext, MultiContext
from blockcanvas.interactor.stochastic_interactor import \
     StochasticInteractor


class StochasticInteractorTestCase(unittest.TestCase):
    """ Unit testing for StochasticInteractor
    """

    def setUp(self):
        code = "from blockcanvas.debug.my_operator import add\n"\
               "c = add(a,b)"
        self.block = Block(code)

        # Context setup
        self.context = MultiContext(DataContext(name='Data'), {})
        self.context['a'] = 1
        self.context['b'] = 2


    def test_attributes(self):
        """ Test if creation of attributes is working correctly.
        """

        interactor = StochasticInteractor(context = self.context,
                                          block = self.block,
                                          distribution = 'constant',
                                          inputs = ['b'])

        self.assertTrue(hasattr(interactor, interactor._input_prefix + 'b'))

        # Check if the attribute is correct
        attribute_b = getattr(interactor, interactor._input_prefix + 'b')
        distribution_b = attribute_b.distribution
        self.assertEqual(distribution_b.value, self.context['b'])
        desired = self.context['b']*numpy.ones(attribute_b.samples)
        self.assertTrue((desired == distribution_b.values).all())


    def test_create_shadows(self):
        """ Test if shadows are working correctly.
        """

        raise nose.SkipTest("shadows not implemented")

        interactor = StochasticInteractor(context = self.context,
                                          block = self.block,
                                          distribution = 'uniform',
                                          inputs = ['b'])

        # Change attributes
        attribute_b = getattr(interactor, interactor._input_prefix+'b')
        distribution_b = attribute_b.distribution

        distribution_b.low = 20.0
        distribution_b.high = 30.0

        # Create shadows
        interactor._execute_button_changed()

        # Check if the shadows were created correctly.
        self.assertEqual(len(distribution_b.values), len(self.context.shadows))

        # Check if the shadow context gives desired effects.
        self.block.execute(self.context.shadows[-1])
        self.assertEqual(self.context.shadows[-1]['c'],
                         self.context['a']+self.context.shadows[-1]['b'])


### EOF -----------------------------------------------------------------------
