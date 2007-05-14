""" Test unit conversion functions used on input and output of functions.

    fixme: We need significant work on scalars.
"""

# Standard Library imports
import unittest

# Numeric library imports
from numpy import array, all, allclose, ndarray #@UnresolvedImport

# Enthought library imports
from enthought.units.unit import InvalidConversion
from enthought.units.length import feet, meters
from enthought.units.time import second

# Numerical modeling library imports
from enthought.numerical_modeling.units.api import UnitArray, UnitScalar
from enthought.numerical_modeling.units.unit_manipulation import \
    convert_units, set_units

class ConvertUnitsTestCase(unittest.TestCase):
    """ ConvertUnits should pretty much leave anything without units alone
        and pass them through silently.  UnitArrays do get converted,
        and so should scalars with units (although we haven't really dealt with
        those).
    """

    ############################################################################
    # TestCase interface.
    ############################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    ############################################################################
    # ConvertUnitsTestCase interface.
    ############################################################################

    def test_single_float(self):
        """ Does it pass a single value through correctly?
        """
        units = [None]
        result = convert_units(units, 1.0)
        self.assertEqual(1.0, result)

    def test_two_float(self):
        """ Does it pass a two values through correctly?
        """
        units = [None, None]
        result = convert_units(units, 1.0, 2.0)
        self.assertEqual([1.0, 2.0], result)

    def test_mismatch_raises_error(self):
        """ Is an exception raised if there aren't enough units specified?
        """
        self.assertRaises(ValueError, convert_units, ([None], 1.0, 2.0))

    def test_one_array(self):
        """ Does it pass a an array through correctly?
        """
        units = [None]
        a = array((1,2,3))
        result = convert_units(units, a)
        self.assertTrue(all(a==result))

    def test_two_arrays(self):
        """ Does it pass a two arrays through correctly?
        """
        units = [None, None]
        a = array((1,2,3))
        b = array((3,4,5))
        aa,bb = convert_units(units, a, b)
        self.assertTrue(all(a==aa))
        self.assertTrue(all(b==bb))

    def test_convert_array_with_units(self):
        """ Does it add units to an array correctly?

            fixme: This may be exactly what we don't want to happen!
        """
        units = [feet]
        a = array((1,2,3))
        aa = convert_units(units, a)
        self.assertTrue(all(a==aa))
        self.assertTrue(type(aa) is ndarray)

    def test_convert_unit_array(self):
        """ Does it convert an array correctly?
        """
        units = [feet]
        a = UnitArray((1,2,3),units=meters)
        aa = convert_units(units, a)
        self.assertTrue(allclose(a,aa.as_units(meters)))
        # fixme: This actually may be something we don't want.  For speed,
        #        if this were just a standard array, we would be better off.
        self.assertEqual(aa.units, feet)

    def test_convert_unit_scalar(self):
        """ Does it convert a scalar correctly?
        """
        units = [feet]
        a = UnitScalar(3.,units=meters)
        aa = convert_units(units, a)
        self.assertTrue(allclose(a,aa.as_units(meters)))
        self.assertEqual(aa.units, feet)

    def test_incompatible_array_units_raise_exception(self):
        """ Does a units mismatch raise an exception?

            fixme: Do we want this configurable?
        """
        units = [second]
        a = UnitArray((1,2,3),units=meters)
        self.assertRaises(InvalidConversion, convert_units, units, a)

    def test_incompatible_scalar_units_raise_exception(self):
        """ Does a units mismatch raise an exception?

            fixme: Do we want this configurable?
        """
        units = [second]
        a = UnitScalar(3.,units=meters)
        self.assertRaises(InvalidConversion, convert_units, units, a)

    def test_dont_convert_unit_array(self):
        """ Does it return the same object if units are the same?

            Note: This isn't required for accuracy, but it is a good
                  optimization.
        """
        units = [feet]
        a = UnitArray((1,2,3),units=feet)
        aa = convert_units(units, a)
        self.assertTrue(id(a),id(aa))

    def test_dont_convert_unit_scalar(self):
        """ Does it return the same object if units are the same?

            Note: This isn't required for accuracy, but it is a good
                  optimization.
        """
        units = [feet]
        a = UnitScalar(3.,units=feet)
        aa = convert_units(units, a)
        self.assertTrue(id(a),id(aa))

    def test_convert_different_args(self):
        """ Does it handle multiple different args correctly?
        """
        units = [feet, meters, None, feet]
        a = UnitArray((1,2,3),units=meters)
        b = array((2,3,4))
        c = 1
        d = UnitScalar(3.,units=meters)
        aa, bb, cc, dd = convert_units(units, a, b, c, d)
        self.assertTrue(allclose(a,aa.as_units(meters)))
        self.assertTrue(allclose(b,bb))
        self.assertEqual(c,cc)
        self.assertTrue(allclose(d,dd.as_units(meters)))

class SetUnitsTestCase(unittest.TestCase):


    ############################################################################
    # TestCase interface.
    ############################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    ############################################################################
    # SetUnitsTestCase interface.
    ############################################################################

    def test_single_float(self):
        """ Does it pass a single value through correctly?
        """
        units = [None]
        result = set_units(units, 1.0)
        self.assertEqual(1.0, result)

    def test_mismatch_raises_error(self):
        """ Is an exception raised if there aren't enough units specified?
        """
        self.assertRaises(ValueError, convert_units, [None], 1.0, 2.0)

    def test_one_array(self):
        """ Does it pass a an array through correctly?
        """
        units = [None]
        a = array((1,2,3))
        result = set_units(units, a)
        self.assertTrue(all(a==result))

    def test_set_scalar_with_units(self):
        """ Does it add units to a scalar correctly?
        """
        units = [feet]
        x = 3.0
        xx = set_units(units, x)
        self.assertEqual(x, xx)
        self.assertEqual(xx.units, feet)

    def test_set_array_with_units(self):
        """ Does it add units to an array correctly?

            fixme: This may be exactly what we don't want to happen!
        """
        units = [feet]
        a = array((1,2,3))
        aa = set_units(units, a)
        self.assertTrue(all(a==aa))
        self.assertEqual(aa.units, feet)

    def test_set_unit_overwrite_unit_scalar(self):
        """ Does it overwrite units on a UnitScalar correctly?
        """
        units = [feet]
        x = UnitScalar(3., units=meters)
        xx = set_units(units, x)
        self.assertEqual(x, xx)
        self.assertEqual(xx.units, feet)

    def test_set_unit_overwrite_unit_array(self):
        """ Does it overwrite units on a UnitArray correctly?
        """
        units = [feet]
        a = UnitArray((1,2,3),units=meters)
        aa = set_units(units, a)
        self.assertTrue(all(a==aa))
        self.assertEqual(aa.units, feet)
#
#    def test_raises_exception(self):
#        """ Does it return the same object if units are the same?
#
#            Note: This isn't required for accuracy, but it is a good
#                  optimization.
#        """
#        units = [feet]
#        a = UnitArray((1,2,3),units=feet)
#        aa = convert_units(units, a)
#        self.assertTrue(id(a),id(aa))
#
#    def test_convert_different_args(self):
#        """ Does it handle multiple different args correctly?
#        """
#        units = [feet, meters, None]
#        a = UnitArray((1,2,3),units=meters)
#        b = array((2,3,4))
#        c = 1
#        aa, bb, cc = convert_units(units, a, b, c)
#        self.assertTrue(allclose(a,aa.as_units(meters)))
#        self.assertTrue(allclose(b,bb))
#        self.assertEqual(c,cc)

if __name__ == '__main__':
    unittest.main()
