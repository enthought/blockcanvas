""" Unit testing for StochasticItem
"""

# Standard imports
import numpy, unittest

# Local imports
from blockcanvas.interactor.stochastic_item import StochasticItem
from traits.util.distribution.distribution import (Constant, Gaussian,
                                                      Uniform, Triangular)

class StochasticItemTestCase(unittest.TestCase):
    """ Unittesting for StochasticItem
    """

    def test_constant_distribution(self):
        """ Check if constant distribution works as desired.
        """

        value = StochasticItem(name = 'a', distribution = Constant())
        distribution = value.distribution

        # Check if the values of distribution are correct.
        self.assertTrue((distribution.values ==
                         distribution.value*numpy.ones(value.samples)).all())

        # Check if changing #samples works
        value.samples = 30
        self.assertTrue(len(distribution.values), 30)


    def test_gaussian_distribution(self):
        """ Check if gaussian distribution works
        """

        value = StochasticItem(name ='a', distribution = Gaussian())
        self.assertEqual(len(value.distribution.values),
                         value.samples)


    def test_triangular_distribution(self):
        """ Check if triangular distribution works
        """

        distribution = Triangular(low = 33.0, mode = 35.0, high = 39.0)
        value = StochasticItem(name = 'a', distribution = distribution)
        self.assertEqual(len(value.distribution.values),
                         value.samples)


    def test_uniform_distribution(self):
        """ Check if uniform distribution works
        """

        distribution = Uniform(low = 33.0, high = 35.0)
        value = StochasticItem(name = 'a', distribution = distribution)
        self.assertEqual(len(value.distribution.values),
                         value.samples)


### EOF -----------------------------------------------------------------------


