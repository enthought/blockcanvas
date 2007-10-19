""" Unit array tests.

"""
# Standard Library imports
import unittest

# Numeric library imports
from numpy import array, all, allclose, ndarray, sqrt #@UnresolvedImport

# Enthought library imports
from enthought.units.unit import InvalidConversion, dimensionless
from enthought.units.length import feet, meters
from enthought.units.time import second

# Numerical modeling library imports
from enthought.numerical_modeling.units.api import UnitArray, UnitScalar
from enthought.numerical_modeling.units.unit_manipulation import \
    convert_units, set_units, have_some_units, strip_units

class PassUnitsTestCase(unittest.TestCase):
    """ Some ufuncs keep units.
    """

    ############################################################################
    # ConvertUnitsTestCase interface.
    ############################################################################

    def test_add(self):
        a = UnitArray([1,2,3],units=meters/second)
        b = UnitArray([1,2,3],units=meters/second)
        result = a + b
        self.assertEqual(result.units, meters/second)

    def test_add_nopass(self):
        a = UnitArray([1,2,3],units=meters/second)
        b = UnitArray([1,2,3],units=feet)
        result = a + b
        assert result.units is None

    def test_subtract(self):
        a = UnitArray([1,2,3],units=meters/second)
        b = UnitArray([1,2,3],units=meters/second)
        result = a - b
        self.assertEqual(result.units, meters/second)

    def test_divide_pass(self):
        a = UnitArray([1,2,3],units=meters/second)
        result = a/3.0
        self.assertEqual(result.units, meters/second)

    def test_divide_no_pass(self):
        a = UnitArray([1,2,3],units=meters/second)
        result = 3.0/a
        assert result.units is None

    def test_multiply_pass(self):
        a = UnitArray([1,2,3],units=meters/second)
        result = a*3.0
        self.assertEqual(result.units, meters/second)
        result = 3.0*a
        self.assertEqual(result.units, meters/second)
        
    def test_sqrt_no_pass(self):
        a = UnitArray([1.0,2.0,3.0], units=meters/second)
        result = sqrt(a)
        assert result.units is None

    def test_sqrt_pass(self):
        a = UnitArray([1.0,2.0,3], units=dimensionless)
        result = sqrt(a)
        assert result.units == dimensionless

if __name__ == '__main__':
    unittest.main()
