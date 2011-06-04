# fixme: Need test for regex_from_str

import os
import sys
import unittest

# local imports
from blockcanvas.function_tools.function_search import \
    FunctionSearch
from blockcanvas.function_tools.function_library import \
    FunctionLibrary

class FunctionSearchTestCase(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        # Add this directory to sys.path.
        self.dir = os.path.abspath(os.path.dirname(__file__))
        sys.path.append(self.dir)
        library = FunctionLibrary(modules=['os', 'sample_package'])
        self.fs = FunctionSearch(all_functions=library.functions)
        unittest.TestCase.setUp(self)

    def tearDown(self):
        if self.dir in sys.path:
            sys.path.remove(self.dir)
        del self.dir
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # FunctionSearchTestCase interface
    ##########################################################################

    def test_exact(self):
        """ Filtering for exact name works?
        """

        self.fs.search_term = 'getenv'
        actual = [function.name for function in self.fs.search_results]
        desired = ['getenv']
        self.assertEqual(sorted(actual), sorted(desired))

    def test_two_modules(self):
        """ Do we get filtered results from two different modules?
        """

        # Put the local dir in the sys.path so sample_package can be imported
        import sys
        sys.path.append(os.path.dirname(__file__))

        self.fs.search_term = 'exec'
        desired = ['execl', 'execle', 'execlp', 'execlpe', 'execvp', 'execvpe']
        actual = [function.name for function in self.fs.search_results]
        self.assertEqual(sorted(actual), sorted(desired))

    def test_module_filters(self):
        """ Do function package filters work?
        """
        self.fs.module_filters = "*sample_pack*"
        self.fs.search_term = 'sp_func'
        actual = [function.name for function in self.fs.search_results]
        desired=[]
        self.assertEqual(sorted(actual), sorted(desired))

    def test_name_filters(self):
        """ Do function name filters work?
        """
        self.fs.name_filters = "*sp*"
        self.fs.search_term = 'sp_func'
        actual = [function.name for function in self.fs.search_results]
        desired=[]
        self.assertEqual(sorted(actual), sorted(desired))

    def test_matching(self):
        """ Test that wildcards and case insensitivity are working properly
        """

        # Wildcards at beginning
        self.fs.search_term = '*cl'
        desired = ['execl', 'execle', 'execlp', 'execlpe']
        actual = [function.name for function in self.fs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

        # Wildcards in middle
        self.fs.search_term = 'e*cl'
        desired = ['execl', 'execle', 'execlp', 'execlpe']
        actual = [function.name for function in self.fs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

        # Explicit wildcard at end
        self.fs.search_term = 'execl*'
        desired = ['execl', 'execle', 'execlp', 'execlpe']
        actual = [function.name for function in self.fs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

        # Case insensitivity
        self.fs.search_term = 'EXECL*'
        desired = ['execl', 'execle', 'execlp', 'execlpe']
        actual = [function.name for function in self.fs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

    def test_search_location(self):
        """ Does searching in the python path of functions work?
        """

        self.fs.search_name = False
        self.fs.search_module = True

        self.fs.search_term = "sample_package.bar"
        desired = ["bar_func1", "bar_func2"]
        actual = [function.name for function in self.fs.search_results]
        self.assertEqual(sorted(desired), sorted(actual))

    def test_update_all_functions_forces_new_search(self):
        library = FunctionLibrary()
        fs = FunctionSearch(all_functions=library.functions)
        self.assertEqual(len(fs.search_results), 0)

        library.modules=['os', 'sample_package']
        # Ensure we found some functions.  This isn't a test of
        # FunctionSearch, but we want it to be true to ensure our
        # test is valid.
        self.assertNotEqual(len(library.functions), 0)

        # Now ensure the search results are updated and have something
        # in them.
        fs.all_functions = library.functions
        self.assertNotEqual(len(fs.search_results), 0)


if __name__ == '__main__':
    unittest.main()
