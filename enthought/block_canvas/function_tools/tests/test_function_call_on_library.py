""" This tests that FunctionCall can generate a FunctionCall object for
    all the functions found in the standard libary.
"""

# Standard library imports
from glob import glob
import os
import unittest
import xml

# Local library imports
from enthought.block_canvas.function_tools.function_call import \
    FunctionCall


class FunctionCallTestCase(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # FunctionDefinitionTestCase interface
    ##########################################################################


    def test_xml_library(self):

        # Find the library directory for python.
        lib_dir = os.path.dirname(xml.__file__)
        self._test_py_modules_in_directory(lib_dir)

    def _test_py_modules_in_directory(self, lib_dir):

        py_files = glob(os.path.join(lib_dir,'*.py'))
        module_names = []
        for path in py_files:
            base_name = os.path.basename(path)
            module_name, ext = os.path.splitext(base_name)
            module_names.append(module_name)

        for module_name in module_names:
            # fixme: do this with pkgutil?
            try:
                # Skip modules that don't import.  Since not all modules
                # in the standard library will import on all platforms.
                exec "import %s" % module_name
                module = eval(module_name)
            except ImportError:
                module = None

            if module:
                functions = _get_functions(module)

                for function in functions:
                    func = FunctionCall.from_function(function)
                    signature = func.call_signature
                    # Uncomment this to see a printout of all the signatures.
                    #print signature

#############################################################################
# Utility Functions
#############################################################################

def _get_functions(module):
    " Retreive all the functions from a module "
    import types
    functions = [function for function in module.__dict__.values() if
                     isinstance(function, types.FunctionType)]
    return functions


if __name__ == '__main__':
    unittest.main()
