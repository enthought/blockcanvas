# Standard imports
import unittest
from numpy import array

# Local imports
from enthought.contexts.geo_context import GeoContext
from blockcanvas.plot.data_context_datasource import DataContextDataSource

class GeoContextDataSourceBasicTest(unittest.TestCase):

    def setUp(self):
        self.context = GeoContext()
        self.a = array([1, 2, 3])
        self.context['a'] = self.a
        self.b = array([4, 5, 6, 7])
        self.context['b'] = self.b
        self.datasource = DataContextDataSource(context=self.context,
                                                context_name='a')

    def test_get_data(self):
        self.assertTrue((self.datasource.get_data() == self.a).all())
        return

    def test_length(self):
        self.assertEqual(self.datasource.get_size(), len(self.a))
        return

    def test_event(self):
        self.did_fire = False
        def handle_fire():
            self.did_fire = True
            return

        self.datasource.on_trait_change(handle_fire, 'data_changed')
        self.context['a'] = array([7, 8, 9])
        self.assertTrue(self.did_fire)
        self.datasource.on_trait_change(handle_fire, 'data_changed', remove=True)
        return

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
