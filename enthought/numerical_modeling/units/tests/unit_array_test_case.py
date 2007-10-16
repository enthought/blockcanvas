""" Unit array tests.

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
    convert_units, set_units, have_some_units, strip_units

class PassUnitsTestCase(unittest.TestCase):
    """ Some ufuncs keep units.
    """

    ############################################################################
    # ConvertUnitsTestCase interface.
    ############################################################################

    def test_add(self):
        """ Does it pass a single value through correctly?
        """
        a = UnitArray([1,2,3],units='m/s')
        b = UnitArray([1,2,3],units='m/s')
        result = a + b
        self.assertEqual(result.units, 'm/s')


    def test_subtract(self):
        """ Does it pass a single value through correctly?
        """
        a = UnitArray([1,2,3],units='m/s')
        b = UnitArray([1,2,3],units='m/s')
        result = a - b
        self.assertEqual(result.units, 'm/s')


if __name__ == '__main__':
    unittest.main()
