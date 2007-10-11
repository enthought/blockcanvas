""" Test function signature extraction.
"""

# Standard Library imports
import unittest

# Numerical modeling library imports
from enthought.numerical_modeling.units.function_signature import def_signature


# Some functions to test on.
def just_args(x, y):
    pass

def just_kwds(y=1, x=2):
    pass

def args_and_kwds(x, z=1, y=2):
    pass


class FunctionSignatureTestCase(unittest.TestCase):

    def test_just_args(self):
        self.assertEquals(def_signature(just_args), "def just_args(x, y):")

    def test_just_kwds(self):
        self.assertEquals(def_signature(just_kwds), "def just_kwds(y=1, x=2):")

    def test_args_and_kwds(self):
        self.assertEquals(def_signature(args_and_kwds), "def args_and_kwds(x, z=1, y=2):")


if __name__ == '__main__':
    unittest.main()
