# Standard library imports
import sys
import unittest

# Enthought library imports
from traits.testing.api import doctest_for_module

# Local imports
from enthought.block_canvas.canvas import simple_math

class SimpleMathTestCase(doctest_for_module(simple_math)):
    pass


if __name__ == '__main__':
    unittest.main(argv=sys.argv)
