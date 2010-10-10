# fixme: Need test for regex_from_str

import os
import sys
import unittest

# local imports
from enthought.block_canvas.class_tools.class_search import ClassSearch
from enthought.block_canvas.class_tools.class_library import ClassLibrary

class ClassSearchTestCase(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        # Add this directory to sys.path.
        self.dir = os.path.abspath(os.path.dirname(__file__))
        sys.path.append(self.dir)
        library = ClassLibrary(modules=['datetime', 'sample_package'])
        self.cs = ClassSearch(all_classes=library.classes)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        if self.dir in sys.path:
            sys.path.remove(self.dir)
        del self.dir
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # ClassSearchTestCase interface
    ##########################################################################

    def test_exact(self):
        """ Filtering for exact name works?
        """

        self.cs.search_term = 'tzinfo'
        actual = [a_class.name for a_class in self.cs.search_results]
        desired = ['tzinfo']
        self.assertEqual(sorted(actual), sorted(desired))

    def test_two_modules(self):
        """ Do we get filtered results from two different modules?
        """

        # Put the local dir in the sys.path so sample_package can be imported
        import sys
        sys.path.append(os.path.dirname(__file__))

        self.cs.search_term = 'delta'
        desired = ['timedelta']
        actual = [a_class.name for a_class in self.cs.search_results]
        self.assertEqual(sorted(actual), sorted(desired))

    def test_module_filters(self):
        """ Do class package filters work?
        """
        self.cs.module_filters = "*sample_pack*"
        self.cs.search_term = 'BadClass'
        actual = [a_class.name for a_class in self.cs.search_results]
        desired=[]
        self.assertEqual(sorted(actual), sorted(desired))

    def test_name_filters(self):
        """ Do class name filters work?
        """
        self.cs.name_filters = "*New*"
        self.cs.search_term = 'GetTheNewStyleClass'
        actual = [a_class.name for a_class in self.cs.search_results]
        desired=[]
        self.assertEqual(sorted(actual), sorted(desired))

    def test_matching(self):
        """ Test that wildcards and case insensitivity are working properly
        """

        # Wildcards at beginning
        self.cs.search_term = '*fo'
        desired = ['tzinfo']
        actual = [a_class.name for a_class in self.cs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

        # Wildcards in middle
        self.cs.search_term = 'd*e'
        desired = ['GetTheOldStyleClass', 'date', 'datetime', 'time', 'timedelta', 'tzinfo']
        actual = [a_class.name for a_class in self.cs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

        # Explicit wildcard at end
        self.cs.search_term = 'dat*'
        desired = ['date', 'datetime', 'time', 'timedelta', 'tzinfo']
        actual = [a_class.name for a_class in self.cs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

        # Case insensitivity
        self.cs.search_term = 'DAT*'
        desired = ['date', 'datetime', 'time', 'timedelta', 'tzinfo']
        actual = [a_class.name for a_class in self.cs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

    def test_search_location(self):
        """ Does searching in the python path of classes work?
        """
        
        self.cs.search_name = False
        self.cs.search_module = True
        
        self.cs.search_term = "sample_package.bar"
        desired = ["BarClass1", "BarClass2"]
        actual = [a_class.name for a_class in self.cs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))
        
    def test_update_all_classes_forces_new_search(self):
        library = ClassLibrary()
        cs = ClassSearch(all_classes=library.classes)
        self.assertEqual(len(cs.search_results), 0)
        
        library.modules=['datetime', 'sample_package']
        # Ensure we found some classes.  This isn't a test of
        # ClassSearch, but we want it to be true to ensure our
        # test is valid.
        self.assertNotEqual(len(library.classes), 0)
        
        # Now ensure the search results are updated and have something
        # in them.
        cs.all_classes = library.classes
        self.assertNotEqual(len(cs.search_results), 0)
        
        
if __name__ == '__main__':
    unittest.main()
