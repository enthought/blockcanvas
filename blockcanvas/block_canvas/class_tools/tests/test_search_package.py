# Standard library imports
import unittest
import os
import imp
import sys

# Local imports
from enthought.block_canvas.class_tools.search_package import (
                                           find_classes,
                                           find_classes_import_recurse,
                                           )

class FindClassesTestCase(unittest.TestCase):

    ##########################################################################
    # FindclassesTestCase interface
    ##########################################################################

    def test_find_classes_ast(self):
        classes = find_classes('sample_package', import_method=False)
        # Test finding all classes
        actual = [ name for module, name in classes]
        desired = ['BadClass', 'GetTheOldStyleClass', 'BarClass1', 'BarClass2', 'GetTheNewStyleClass']
        self.assertEqual(sorted(actual), sorted(desired))


    def test_find_classes_import(self):
        classes = find_classes('sample_package', import_method=True)
        # Test finding all classes
        actual = [ name for module, name in classes]
        desired = ['BadClass', 'GetTheOldStyleClass', 'BarClass1', 'BarClass2', 'GetTheNewStyleClass']
        self.assertEqual(sorted(actual), sorted(desired))

class FindClassesImportRecurseTestCase(unittest.TestCase):

    def test_finds_builtins(self):
        classes = find_classes_import_recurse('_socket')
        class_names = [name for module, name in classes]
        self.assertTrue('socket' in class_names)

if __name__ == '__main__':
    unittest.main()
