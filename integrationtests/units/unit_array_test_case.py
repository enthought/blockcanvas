# Standard library imports
from cPickle import dumps, loads
import timeit
import unittest

# Numeric library imports
import numpy
from numpy import all

# Enthought Library imports
import enthought.units as units
from enthought.testing.api import skip
from enthought.units.length import meters, feet
from enthought.units.time import seconds
from enthought.units.unit import dimensionless

# Numerical modeling library imports
from enthought.numerical_modeling.units.api import UnitArray

class UnitArrayTestCase(unittest.TestCase):

    ############################################################################
    # unittest.TestCase interface
    ############################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)


    ############################################################################
    # Test construction from arrays
    ############################################################################

    def test_create_1d_from_list(self):
        """ Create an array from a 1D list.
        """
        a = UnitArray([1,2,3])
        assert(a[0] == 1)

    def test_create_2d_from_list(self):
        """ Create an array from a 2D list.
        """
        a = UnitArray([[1,2,3],
                 [4,5,6]])
        assert(a[1,2] == 6)


    ############################################################################
    # Test mathematical operations
    ############################################################################

    def test_sin(self):
        """ Unary operation on a UnitArray should return a UnitArray.
        """
        a = UnitArray([1,2,3])
        res = numpy.sin(a) #@UndefinedVariable
        assert (type(res) is UnitArray)

    def test_add(self):
        """ Binary operation of array + UnitArray should return a UnitArray.
        """
        ary = numpy.array((1,2,3))
        unit_ary = UnitArray(ary)
        res = unit_ary + ary
        assert type(res) is UnitArray

    def test_array_equality(self):
        """ Rich comparison of array == UnitArray should compare the data
        """
        ary = numpy.array((1,2,3))
        unit_ary = UnitArray(ary)
        res = unit_ary + ary
        assert numpy.all(res == (ary+ary))


    ############################################################################
    # Tests for units
    ############################################################################

    def test_units_default(self):
        """ Are their units on this UnitArray.
        """
        ary = numpy.array((1,2,3))
        unit_ary = UnitArray(ary)
        self.assertEqual(unit_ary.units, None)

    def test_units_init(self):
        """ Are their units on this UnitArray.
        """
        ary = numpy.array((1,2,3))
        unit_ary = UnitArray(ary, units=dimensionless)
        self.assertEqual(unit_ary.units, dimensionless)

    def test_as_units(self):
        """ Conversion from one unit system to another.
        """
        ary = numpy.array((1,2,3))
        unit_ary = UnitArray(ary, units=meters)
        new_unit_ary = unit_ary.as_units(feet)

        # Test the values are correct
        desired_array = units.convert(ary, meters, feet)
        self.assert_(numpy.all(desired_array==new_unit_ary))

        # Also, make sure the units are correctly assigned.
        self.assertEqual(new_unit_ary.units, feet)

        # fixme: We should also test that any other items in the unit_ary are
        #        copied.


    ############################################################################
    # Test cloning type behavior.
    ############################################################################

    def test_slice_keeps_attributes(self):
        """ Does a sliced version of a UnitArray keeps its attributes?
        """
        ary = numpy.array((1,2,3))
        unit_ary = UnitArray(ary, units=meters)
        new_unit_ary = unit_ary[:2]

        # Also, make sure the units and family_name are correctly assigned.
        self.assertEqual(new_unit_ary.units, meters)

    def test_add_keeps_attributes(self):
        """ In "new=UnitArray+ary", new should have attributes of UnitArray.
        """
        ary = numpy.array((1,2,3))
        unit_ary = UnitArray(ary, units=meters)
        new_unit_ary = ary + unit_ary

        # Also, make sure the units and family_name are correctly assigned.
        self.assertEqual(new_unit_ary.units, meters)

    def test_concatenate(self):
        unit_ary_1 = UnitArray(numpy.array((1,2,3)), units=meters)
        unit_ary_2 = UnitArray(numpy.array((4,5,6)), units=meters)

        new_unit_ary = UnitArray.concatenate([unit_ary_1, unit_ary_2])
        expected = UnitArray((1,2,3,4,5,6), units=meters)
        self.assertTrue(numpy.all(new_unit_ary == expected))

    def test_concatenate_keeps_attribute(self):
        """ concatenating does not call __new__ on the result
            so the attribute must be set correctly in __array_finalize__
        """
        unit_ary_1 = UnitArray(numpy.array((1,2,3)), units=meters)
        unit_ary_2 = UnitArray(numpy.array((1,2,3)), units=meters)

        new_unit_ary = UnitArray.concatenate([unit_ary_1, unit_ary_2])

        self.assertEqual(new_unit_ary.units, meters)

    def test_concatenate_keeps_attribute_using_mixed_units(self):
        """ concatenating does not call __new__ on the result
            so the attribute must be set correctly in __array_finalize__.
            This test creates another unit array with different units
            before the concatenate to make sure the finalize method does not
            assign the wrong units
        """
        unit_ary_1 = UnitArray(numpy.array((1,2,3)), units=meters)
        unit_ary_2 = UnitArray(numpy.array((1,2,3)), units=meters)

        unit_ary_3 = UnitArray(numpy.array((1,2,3)), units=feet)
        new_unit_ary = UnitArray.concatenate([unit_ary_1, unit_ary_2])

        self.assertEqual(new_unit_ary.units, meters)

    ############################################################################
    # Test mathematical operations
    ############################################################################

    def test_index_name(self):
        """ Can set and retreive the index_name?
        """
        ary = numpy.array((1,2,3))
        unit_ary = UnitArray(ary)
        unit_ary.index_name = "depth"
        self.assertEqual(unit_ary.index_name, "depth")


    ############################################################################
    # Test Construction Speed
    ############################################################################

    @skip
    def test_construction_is_not_slow(self):
        """ Ensure instantiating a UnitArray is <1.1 slower than for arrays.

            Note that we are using a very small array to test this case so that
            we are seeing the "worst case" overhead.
        """

        ### Parameters #########################################################

        # Slowdown we will allow compared to standard python evaluation
        allowed_slowdown = 1.1

        # Number of timer iterations.
        N = 30000

        ### Array creation #####################################################
        setup = "from numpy import array\n"
        expr = 'array((1,2,3))'
        std = timeit.Timer(expr, setup)
        std_res = std.timeit(N)

        ### UnitArray creation #################################################
        setup = "from enthought.numerical_modeling.units.api import UnitArray\n"
        expr = 'UnitArray((1,2,3))'
        unit_ary = timeit.Timer(expr, setup)
        unit_ary_res = unit_ary.timeit(N)

        slowdown = unit_ary_res/std_res
        assert slowdown < allowed_slowdown, 'actual slowdown: %f' % slowdown

    @skip
    def test_finalize_is_not_slow(self):
        """ Finalizing (cloning) a UnitArray is less than 1.1 slower than arrays

            __array_finalize__ is called every time a math operation, slice,
            etc. are called on a unit_array.  We do not want this to have much
            overhead compared to stanard array operations.

            Here, we compare the speed of adding 1 to an array and to a
            UnitArray.

            Note that we are using a very small array to test this case so that
            we are seeing the "worst case" overhead.
        """

        ### Parameters #########################################################

        # Slowdown we will allow compared to standard python evaluation
        allowed_slowdown = 1.1

        # Number of timer iterations.
        N = 30000

        ### Array ##############################################################
        setup = "from numpy import array\n" \
                "val = array((1,2,3))\n"
        expr = 'val+1'
        std = timeit.Timer(expr, setup)
        std_res = std.timeit(N)

        ### UnitArray ##########################################################
        setup = (
            "from enthought.numerical_modeling.units.api import UnitArray\n"
            "val = UnitArray((1,2,3))\n"
        )
        expr = 'val+1'
        unit_ary = timeit.Timer(expr, setup)
        unit_ary_res = unit_ary.timeit(N)

        slowdown = unit_ary_res/std_res
        assert slowdown < allowed_slowdown, 'actual slowdown: %f' % slowdown

class UnitArrayPickleTestCase(unittest.TestCase):

    def test_pickle(self):
        'Pickling'
        for a in (

            UnitArray(0),
            UnitArray([0,1]),
            UnitArray([0,1], units=feet/seconds),
            UnitArray([[0.5,1.0], [10.,20.]], units=meters),

            ):
            state = dumps(a)
            b = loads(state)
            self.assertTrue(all(b == a))
            self.assertTrue(hasattr(b, 'units'))
            self.assertEqual(b.units,a.units)

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
