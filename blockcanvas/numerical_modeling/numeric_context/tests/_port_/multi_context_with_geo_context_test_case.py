# Standard Library Imports
import unittest
import timeit

from numpy import array

# Geo Library imports
from multi_context_test_case import MultiContextTestCase
from geo.context.api import MultiContext, GeoContext

class MultiContextWithGeoContextTestCase(MultiContextTestCase):
    """ Test a MultiContext with a GeoContext at the top.

        The GeoContext only accepts ndarray and Log objects which results in
        new behavior over a standard GeoContext that needs to be tested.
    """

    ############################################################################
    # AbstactContextTestCase interface
    ############################################################################

    def context_factory(self):
        """ Return the type of context we are testing.
        """
        return MultiContext(GeoContext(), {})

    def matched_input_output_pair(self):
        """ Return values for testing dictionary get/set, etc.
        """
        return array((1,2,3)), array((1,2,3))

    ############################################################################
    # MultiContext interface
    ############################################################################

    def test_overwrite_data(self):
        """ Does write to primary delete variables with the same name in data?
        """
        context = self.context_factory()
        [upper, lower] = context.contexts

        # Write data that will go into the geo context.
        context['a'] = array((1,2,3))
        self.assertTrue((context['a'] == array((1,2,3))).all())
        self.assertTrue('a' in upper)
        self.assertTrue('a' not in lower)

        # Now, overwrite it with data that goes into the normal context below.
        context['a'] = 1
        self.assertTrue(context['a'] == 1)
        self.assertTrue('a' not in upper)
        self.assertTrue('a' in lower)

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
