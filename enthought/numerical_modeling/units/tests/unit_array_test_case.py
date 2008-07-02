""" Unit array tests.

"""
# Standard Library imports
import unittest
import operator

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

    def test_add_compatible(self):
        a = UnitArray([1,2,3],units=meters)
        b = UnitArray([1,2,3],units=feet)
        result = a + b
        mplusf = (meters+feet).value
        assert result[0] == mplusf
        self.assertEqual(result.units, meters)

    def test_add_nopass(self):
        a = UnitArray([1,2,3],units=meters/second)
        b = UnitArray([1,2,3],units=feet)
        self.assertRaises(InvalidConversion, operator.add, a, b)

    def test_subtract(self):
        a = UnitArray([1,2,3],units=meters/second)
        b = UnitArray([1,2,3],units=meters/second)
        result = a - b
        self.assertEqual(result.units, meters/second)

    def test_subtract_compatible(self):
        a = UnitArray([1,2,3],units=meters)
        b = UnitArray([1,2,3],units=feet)
        result = a - b
        mminusf = (meters-feet).value
        assert result[0] == mminusf
        self.assertEqual(result.units, meters)

    def test_subtract_dimensionless(self):
        a = UnitArray([1,2,3], units=dimensionless)
        b = 1
        result = a - b
        self.assertEqual(result.units, dimensionless)
        result = b - a
        self.assertEqual(result.units, dimensionless)
        c = array([3,2,1])
        result = a - c
        self.assertEqual(result.units, dimensionless)
        result = c - a
        self.assertEqual(result.units, dimensionless)

    def test_divide_pass(self):
        a = UnitArray([1,2,3],units=meters/second)
        result = a/3.0
        self.assertEqual(result.units, meters/second)
        result = 3.0/a
        self.assertEqual(result.units, second/meters)
        b = UnitArray([3,2,1], units=second)
        result = a/b
        self.assertEqual(result.units, meters/second**2)

    def test_multiply_pass(self):
        a = UnitArray([1,2,3],units=meters/second)
        result = a*3.0
        self.assertEqual(result.units, meters/second)
        result = 3.0*a
        assert (array(result) == array([3.0,6.0,9.0])).all()
        self.assertEqual(result.units, meters/second)
        result = 10*a
        self.assertEqual(result.units, meters/second)
        result = a*10
        assert (array(result) == array([10,20,30])).all()
        self.assertEqual(result.units, meters/second)
        result = UnitScalar(3.0, units=second)*a
        assert (array(result) == array([3.0,6.0,9.0])).all()
        self.assertEqual(result.units, meters)
        

    def test_multiply_units(self):
        a = UnitArray([1,2,3],units=meters)
        b = UnitArray([1,2,3],units=second)
        result = a*b
        self.assertEqual(result.units, meters*second)

    def test_pow_pass(self):
        a = UnitArray([1,2,3],units=meters)
        b = 0.5
        result = a**b
        self.assertEqual(result.units, meters**0.5)
        c = array(0.5)
        result = a**c
        self.assertEqual(result.units, meters**0.5)
        d = UnitArray(0.5, units=dimensionless)
        result = a**d
        self.assertEqual(result.units, meters**0.5)
        
    def test_sqrt_no_pass(self):
        a = UnitArray([1.0,2.0,3.0], units=meters/second)
        result = sqrt(a)
        assert result.units is None

    def test_sqrt_pass(self):
        a = UnitArray([1.0,2.0,3], units=dimensionless)
        result = sqrt(a)
        assert result.units == dimensionless

    def test_le(self):
        a = UnitArray([1.0,2.0,3], units=dimensionless)
        b = UnitArray([3.0,1.0,1], units=2.0*dimensionless)
        result = a <= b
        assert result[0] == True
        assert result[1] == True
        assert result[2] == False
        c = 2.0
        result = b <= c
        assert result[0] == False
        assert result[1] == True
        assert result[2] == True
        d = array([1.0, 2.0, 3.0])
        assert result[0] == False
        assert result[1] == True
        assert result[2] == True

    def test_lt(self):
        a = UnitArray([1.0,4.0,3], units=dimensionless)
        b = UnitArray([3.0,2.0,1], units=2.0*dimensionless)
        result = a < b
        assert result[0] == True
        assert result[1] == False
        assert result[2] == False
        c = 4.0
        result = b < c
        assert result[0] == False
        assert result[1] == False
        assert result[2] == True
        d = array([1.0, 4.0, 3.0])
        result = b < d
        assert result[0] == False
        assert result[1] == False
        assert result[2] == True

    def test_ge(self):
        a = UnitArray([1.0,4.0,3], units=dimensionless)
        b = UnitArray([3.0,2.0,1], units=2.0*dimensionless)
        result = a >= b
        assert result[0] == False
        assert result[1] == True
        assert result[2] == True
        c = 4.0
        result = b >= c
        assert result[0] == True
        assert result[1] == True
        assert result[2] == False
        d = array([1.0, 4.0, 3.0])
        result = b >= d
        assert result[0] == True
        assert result[1] == True
        assert result[2] == False

    def test_gt(self):
        a = UnitArray([1.0,4.0,3], units=dimensionless)
        b = UnitArray([3.0,2.0,1], units=2.0*dimensionless)
        result = a > b
        assert result[0] == False
        assert result[1] == False
        assert result[2] == True
        c = 4.0
        result = b > c
        assert result[0] == True
        assert result[1] == False
        assert result[2] == False
        d = array([1.0, 4.0, 3.0])
        result = b > d
        assert result[0] == True
        assert result[1] == False
        assert result[2] == False

    def test_eq(self):
        a = UnitArray([1.0,4.0,3], units=dimensionless)
        b = UnitArray([3.0,2.0,1], units=2.0*dimensionless)
        result = a == b
        assert result[0] == False
        assert result[1] == True
        assert result[2] == False
        c = 4.0
        result = b == c
        assert result[0] == False
        assert result[1] == True
        assert result[2] == False
        d = array([1.0, 4.0, 3.0])
        result = b == d
        assert result[0] == False
        assert result[1] == True
        assert result[2] == False

    def test_ne(self):
        a = UnitArray([1.0,4.0,3], units=dimensionless)
        b = UnitArray([3.0,2.0,1], units=2.0*dimensionless)
        result = a != b
        assert result[0] == True
        assert result[1] == False
        assert result[2] == True
        c = 4.0
        result = b != c
        assert result[0] == True
        assert result[1] == False
        assert result[2] == True
        d = array([1.0, 4.0, 3.0])
        result = b != d
        assert result[0] == True
        assert result[1] == False
        assert result[2] == True

if __name__ == '__main__':
    unittest.main()
