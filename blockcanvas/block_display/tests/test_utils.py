# Standard library imports
import unittest

# Enthought imports
from enthought.blocks.api import Block, unparse

# Local imports
from blockcanvas.block_display.utils import *


class BlockGraphTestCase(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_function_names(self):
        """ Does function_names find all the functions in an AST?
        """

        code = "x = func1(func2(1),2)\n" \
               "y = func3()\n"
        desired = [ "func1",  "func2", "func3" ]
        b = Block(code)
        actual = sorted(function_names(b))
        self.assertEqual(actual, desired)

    def test_block_name_replacer(self):
        """ Does BlockNameReplacer work?
        """
        code = "x = x(x, x)\nx\n"
        desired = "y = y(y, y)\ny\n"
        b = Block(code)
        rename_variable(b.ast, 'x', 'y')
        self.assertEqual(desired, unparse(b.ast))


if __name__ == '__main__':
    unittest.main()
