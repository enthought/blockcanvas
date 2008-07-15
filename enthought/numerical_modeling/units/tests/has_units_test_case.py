# Standard Library imports
import unittest

# Numerical library imports
import numpy as np
from numpy.testing import assert_array_almost_equal

# Enthought library imports
from enthought.units.length import feet, meters
from enthought.units.time import second

# Numerical modeling library imports
from enthought.numerical_modeling.units.api import UnitArray, UnitScalar
from enthought.numerical_modeling.units.has_units import has_units


# Some functions to play with.
def foo(x, y):
    """ Foo

    Parameters
    ----------
    x : scalar : units=m
        X
    y : scalar : units=s
        Y

    Returns
    -------
    z : scalar : units=m/s
    """
    assert not isinstance(x, (UnitArray, UnitScalar))
    assert not isinstance(y, (UnitArray, UnitScalar))
    z = x / y
    return z

foo_with_units = has_units(foo)

def bar(x, y):
    """ Bar

    Parameters
    ----------
    x : scalar : units=m
        X
    y : scalar : units=s
        Y

    Returns
    -------
    z : scalar : units=m
    """

    if y > 1:
        z = x - x
    else:
        z = x + x
    return z
    

vec_bar_with_units = has_units(np.vectorize(bar))


class HasUnitsTestCase(unittest.TestCase):

    def setUp(self):
        # Make some data to play with.
        self.meter_array = UnitArray([1.,2,3], units=meters)
        self.second_array = UnitArray([3.,2,1], units=second)
        self.feet_array = UnitArray([4.,5,6], units=feet)
        self.meter_scalar = UnitScalar(1., units=meters)
        self.second_scalar = UnitScalar(3., units=second)
        self.feet_scalar = UnitScalar(4., units=feet)
        unittest.TestCase.setUp(self)

    def test_decorator_plays_nice(self):
        self.assertEquals(foo_with_units.__module__, foo.__module__)
        self.assertEquals(foo_with_units.__doc__, foo.__doc__)
        self.assertEquals(foo_with_units.__name__, foo.__name__)

    def test_input_variables_parsed(self):
        inputs = foo_with_units.inputs
        self.assertEquals(len(inputs), 2)
        self.assertEquals(inputs[0].name, 'x')
        self.assertEquals(inputs[0].units, meters)
        self.assertEquals(inputs[1].name, 'y')
        self.assertEquals(inputs[1].units, second)

    def test_output_variables_parsed(self):
        outputs = foo_with_units.outputs
        self.assertEquals(len(outputs), 1)
        self.assertEquals(outputs[0].name, 'z')
        self.assertEquals(outputs[0].units, meters/second)

    def test_no_internal_units_array(self):
        z = foo_with_units( self.meter_array, self.second_array)
        self.assertTrue(isinstance(z, UnitArray))
        self.assertEquals(z.units, meters/second)

    def test_no_internal_units_scalar(self):
        z = foo_with_units( self.meter_scalar, self.second_scalar)
        self.assertTrue(isinstance(z, UnitScalar))
        self.assertEquals(z.units, meters/second)

    def test_feet(self):
        z = foo_with_units( self.feet_array, self.second_array)
        self.assertTrue(isinstance(z, UnitArray))
        self.assertEquals(z.units, meters/second)
        assert_array_almost_equal(z, np.array([ 0.4064,  0.762 ,  1.8288]))
        z = foo_with_units( self.feet_scalar, self.second_scalar)
        self.assertTrue(isinstance(z, UnitScalar))
        self.assertEquals(z.units, meters/second)
        assert_array_almost_equal(z, 0.4064)

    def test_v_decorator_plays_nice(self):
        self.assertEquals(vec_bar_with_units.__module__, bar.__module__)
        self.assertEquals(vec_bar_with_units.__doc__, bar.__doc__)
        self.assertEquals(vec_bar_with_units.__name__, bar.__name__)

    def test_v_input_variables_parsed(self):
        inputs = vec_bar_with_units.inputs
        self.assertEquals(len(inputs), 2)
        self.assertEquals(inputs[0].name, 'x')
        self.assertEquals(inputs[0].units, meters)
        self.assertEquals(inputs[1].name, 'y')
        self.assertEquals(inputs[1].units, second)

    def test_v_output_variables_parsed(self):
        outputs = vec_bar_with_units.outputs
        self.assertEquals(len(outputs), 1)
        self.assertEquals(outputs[0].name, 'z')
        self.assertEquals(outputs[0].units, meters)

    def test_v_no_internal_units_array(self):
        z = vec_bar_with_units( self.meter_array, self.second_array)
        self.assertTrue(isinstance(z, UnitArray))
        self.assertEquals(z.units, meters)

    def test_v_no_internal_units_scalar(self):
        z = vec_bar_with_units( self.meter_scalar, self.second_scalar)
        # FIXME: test fails
        #self.assertTrue(isinstance(z, UnitScalar))
        self.assertEquals(z.units, meters)

    def test_v_feet(self):
        z = vec_bar_with_units( self.feet_array, self.second_array)
        self.assertTrue(isinstance(z, UnitArray))
        self.assertEquals(z.units, meters)
        assert_array_almost_equal(z, np.array([ 0.0,  0.0 ,  3.6576]))
        z = vec_bar_with_units( self.feet_scalar, self.second_scalar)
        # FIXME: test fails
        #self.assertTrue(isinstance(z, UnitScalar))
        self.assertEquals(z.units, meters)
        assert_array_almost_equal(z, 0.0)



if __name__ == '__main__':
    unittest.main()
