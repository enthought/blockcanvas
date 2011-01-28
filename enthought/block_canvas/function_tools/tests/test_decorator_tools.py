# Standard library imports
import unittest
import inspect

# local imports
from enthought.block_canvas.function_tools.decorator_tools import getsource
from decorator_tools_test_functions import add, non_decorated_add


class DecoratorToolsTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_getsource(self):
        source1 = inspect.getsource(non_decorated_add)
        source2 = getsource(add)

        # Check if the source code except for the heading is the same
        s1 = source1.split('\n')
        s2 = source2.split('\n')

        s1.pop(0)
        s2.pop(0)

        self.assertEqual(s1, s2)


### EOF ------------------------------------------------------------------------
