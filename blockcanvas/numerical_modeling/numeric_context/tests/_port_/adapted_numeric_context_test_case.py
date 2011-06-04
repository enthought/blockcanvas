# Standard imports
import unittest
from numpy import all, allclose, array, isnan, linspace, nan

# Enthought imports
from enthought.units import convert
from enthought.units.length import feet, fathom, meters, yard

# Geo imports
from geo.context.api import (NumericContext, ReductionContext, PassThruContext,
                             MaskFilter, OpenContext)
from geo.log import Log

class AdaptedDataContextTestCase(unittest.TestCase):

    ###########################################################################
    # TestCase interface
    ###########################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)

        # Put unit adapters on either side of a masking adapter to see if they
        # cooperate. Store meters in the raw context, push fathoms through the
        # mask, and expose feet to the outside world.
        self.units = units = { 'in':meters, 'mid':fathom, 'out':feet }

        # Set up data for the contexts
        depth = Log(linspace(0.0, 100.0, 11), units=units['in'])
        lith = array(['sand']*len(depth), dtype=object)

        # Create the contexts
        self.context = PassThruContext( ReductionContext( NumericContext() ) )
        self.raw_context = self.context.context_base

        # Add data (before creating the adapters)
        self.context.update(depth=depth, lith=lith)

        # (This simplifies creating UnitConversionAdapters)
        def always(value):
            class C(dict):
                def get(self, key, default=None):
                    return value
                def __repr__(self):
                    return '{*:%r}' % value
            return C()

        # Layer multiple adapters
        self.mask = (15.0 < depth) & (depth < 55.0)
        self.convert_out = lambda x: convert(x, units['in'], units['out'])
        self.convert_in = lambda x: convert(x, units['out'], units['in'])
        self.context.get_reduction_context(OpenContext).context_filter = \
            MaskFilter( mask = self.mask )

        # TODO Nest masking adapters (broken)
        # TODO Allow unit adapters on either side of masking adapters (broken)


    ###########################################################################
    # AdaptedDataContextTestCase interface
    ###########################################################################

    def test_getitem(self):
        """ Is getitem adapted correctly?
        """
        value = self.context['depth']
        #desired = self.convert_out(array((20., 30., 40., 50.)))
        desired = array((20., 30., 40., 50.))

        self.assertEqual(len(value), 4)
        self.assertTrue(allclose(value, desired))

    def test_setitem_existing_value(self):
        """ Is setitem adapted correctly for existing values?
        """
        #new_values = self.convert_out(array((30.0, 40.0, 50.0, 60.0)))
        new_values = array((30.0, 40.0, 50.0, 60.0))

        desired = self.raw_context['depth'].copy()
        #desired[self.mask] = self.convert_in(new_values)
        desired[self.mask] = new_values

        self.context['depth'] = Log(new_values, units=self.units['out'])
        value = self.raw_context['depth']

        self.assertEqual(len(value), len(desired))
        self.assertTrue(allclose(value, desired))

    def test_setitem_non_existing_value(self):
        """ Is setitem adapted correctly for non-existing values?
        """
        #new_values = self.convert_out(array((30.0, 40.0, 50.0, 60.0)))
        new_values = array((30.0, 40.0, 50.0, 60.0))
        dummy = 12345.67

        desired = self.raw_context['depth'].copy()
        #desired[self.mask] = self.convert_in(new_values)
        desired[self.mask] = new_values
        desired[~self.mask] = dummy

        self.context['foo'] = Log(new_values, units=self.units['out'])
        value = self.raw_context['foo']
        value[isnan(value)] = dummy

        self.assertEqual(len(value), len(desired))
        self.assertTrue(allclose(value, desired))

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
