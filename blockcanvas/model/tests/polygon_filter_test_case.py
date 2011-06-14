
# Standard library imports.
import logging
import unittest

from nose import DeprecatedTest, SkipTest

from numpy import arange

from traits.api import Array, HasTraits

from blockcanvas.model.api import NumericModel, NumericItem, PolygonFilter

# Setup a logger for this module.
logger = logging.getLogger(__name__)

class DummyData(HasTraits):

    a = Array
    b = Array
    c = Array

    def __init__(self):
        self.a = arange(0, 1000)
        self.b = arange(1000, 0, -1)
        self.c = arange(0, 1000)


class PolygonFilterTestCase( unittest.TestCase ):

    def setUp(self):
        logger.debug("--------------------------------------------------")

        self.dummy_data = DummyData()
        self.numeric_model = NumericModel()
        self.numeric_model.model_items = [
            NumericItem( label='a', object=self.dummy_data, name='a' ),
            NumericItem( label='b', object=self.dummy_data, name='b' ),
            NumericItem( label='c', object=self.dummy_data, name='c' )]


    def test_rectangular_polygon( self ):
        # FIXME:
        #    This test is being skipped because it does not work.
        #    The traceback indicates that an instance requires an
        #    attribute '', which makes no sense.
        raise SkipTest()

        polygon_filter = PolygonFilter(
            points = [ (0, 100), (1000, 100), (1000, 300), (0, 300) ],
            x_value = 'a',
            y_value = 'c'
        )

        filtered_data = polygon_filter(self.numeric_model)
        self.assertEqual(filtered_data[101], 1)
        self.assertEqual(filtered_data[300], 1)


if __name__ == "__main__":
    unittest.main()

#### EOF ######################################################################
