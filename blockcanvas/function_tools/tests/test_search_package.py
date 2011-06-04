# Standard library imports
import unittest
import os
import imp
import sys

# Local imports
from blockcanvas.function_tools.search_package import (is_package, is_module,
                                           find_package_sub_modules,
                                           find_functions_import_recurse,
                                           python_path_from_file_path,
                                           find_functions)

class IsPackageTestCase(unittest.TestCase):

    ##########################################################################
    # IsPackageTestCase interface
    ##########################################################################

    def test_is_package_for_module(self):
        self.assertFalse(is_package('os'))

    def test_is_package_for_package(self):
        sys.path.append(os.path.dirname(__file__))
        self.assertTrue(is_package('sample_package'))
        del sys.path[-1]

    def test_is_module_for_module(self):
        self.assertTrue(is_module('os'))

    def test_is_module_for_package(self):
        sys.path.append(os.path.dirname(__file__))
        self.assertFalse(is_module('sample_package'))
        del sys.path[-1]

class PackagePathsTestCase(unittest.TestCase):

    ##########################################################################
    # PackagePathsTestCase interface
    ##########################################################################

    def test_find_package_sub_modules_nonrecursive(self):
        abs_paths = find_package_sub_modules('sample_package', recurse=False)
        actual = [os.path.split(abs_path)[1] for abs_path in abs_paths]
        desired = ['__init__.py', 'sp_func.py', 'error_package.py' ]
        self.assertEqual(sorted(actual), sorted(desired))


    def test_find_package_sub_modules_recursive(self):
        abs_paths = find_package_sub_modules('sample_package', recurse=True)
        actual = [os.path.split(abs_path)[1] for abs_path in abs_paths]
        desired = ['__init__.py', '__init__.py', 'bar_func.py', 'sp_func.py',
                   'error_package.py']
        self.assertEqual(sorted(actual), sorted(desired))


class FindFunctionsTestCase(unittest.TestCase):

    ##########################################################################
    # FindFunctionsTestCase interface
    ##########################################################################

    def test_find_functions_ast(self):
        functions = find_functions('sample_package', import_method=False)
        # Test finding all functions
        actual = [ name for module, name in functions]
        desired = ['badfunction', 'sp_func1', 'bar_func1', 'bar_func2', 'ex_sp_func']
        self.assertEqual(sorted(actual), sorted(desired))


    def test_find_functions_import(self):
        functions = find_functions('sample_package', import_method=True)
        # Test finding all functions
        actual = [ name for module, name in functions]
        desired = ['badfunction', 'sp_func1', 'bar_func1', 'bar_func2', 'ex_sp_func']
        self.assertEqual(sorted(actual), sorted(desired))

class FindFunctionsImportRecurseTestCase(unittest.TestCase):

    def test_finds_builtins(self):
        functions = find_functions_import_recurse('_socket')
        function_names = [name for module, name in functions]
        self.assertTrue('getservbyname' in function_names)

class PythonPathFromFilePathTestCase(unittest.TestCase):

    def test_package_name_in_path(self):
        package = 'xml'
        file_path = os.path.join('blah','xml','binky','mod.py')
        package_path = os.path.join('blah', 'xml')
        python_path = python_path_from_file_path(package, file_path, package_path=package_path)
        self.assertEqual(python_path,'xml.binky.mod')


    def test_package_name_repeated_in_path(self):
        package = 'xml'
        file_path = os.path.join('foo','bar','xml','blah',
                                 'xml', 'binky','mod.py')
        package_path = os.path.join('foo', 'bar', 'xml', 'blah', 'xml')
        python_path = python_path_from_file_path(package, file_path, package_path=package_path)
        self.assertEqual(python_path, 'xml.binky.mod')

    def test_python_path_from_file_path(self):
        path = imp.find_module('sample_package')[1] + "/sp_func.py"
        actual = python_path_from_file_path('sample_package', path)
        desired = 'sample_package.sp_func'
        self.assertEqual(actual, desired)

if __name__ == '__main__':
    unittest.main()
