# Standard library imports
import os
import sys
import unittest

# Enthought library imports
from enthought.block_canvas.function_tools.function_call_tools import localify_func_code


def local_path():
    return os.path.dirname(__file__)

class FunctionCallToolsTest(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        """ Ensure that the current directory is on the python path.

            We need this to import the test modules.
        """
        sys.path.append(local_path())
        unittest.TestCase.setUp(self)

    def tearDown(self):
        """ Remove the current directory from the python path.
        """
        del sys.path[-1]
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # FunctionCallToolsTest interface
    ##########################################################################

    def test_localify_func_code(self):
        old_code = """def foo(a, b, c):
    a = 1+1
    b = 2+2
    return a+b"""

        new_code = localify_func_code(old_code, 'foo', 'bar', 'enthought.foobar')
        desired_code = """def bar(a, b, c):
    from enthought.foobar import *
    a = 1+1
    b = 2+2
    return a+b
"""
        print repr(new_code)
        print repr(desired_code)
        self.assertEqual(new_code, desired_code)

if __name__ == '__main__':
    unittest.main()
