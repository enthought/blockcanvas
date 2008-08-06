# Standard library imports
import unittest, platform

# Local imports
from enthought.block_canvas.function_tools.rest_html import convert_string, get_html_from_function_info 

from enthought.block_canvas.function_tools.python_function_info import PythonFunctionInfo

class RestHTMLTestCase(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # RestHTMLTestCase interface
    ##########################################################################

    def test_indentation_fix(self):
        # If it does not work, both these functions will throw errors when
        # docutils tries to parse them
        convert_string(proper_func1.__doc__)
        convert_string(proper_func2.__doc__)
        convert_string(bad_func1.__doc__)

    def test_convert_function_proper_docstring(self):
        html1 = get_html_from_function_info(PythonFunctionInfo.from_function(proper_func1))
        html2 = get_html_from_function_info(PythonFunctionInfo.from_function(proper_func2))
        # If [unit] is in the html, it has properly identified by
        # convert_function
        self.assertNotEqual(html1.find('[km/s]'), -1)
        self.assertNotEqual(html2.find('[g/cc]'), -1)

    def test_convert_function_bad_docstring(self):
        html = get_html_from_function_info(PythonFunctionInfo.from_function(bad_func1))
        self.assertEqual(html.find('Parameters'), -1)

    def test_platform_specific(self):
        html = get_html_from_function_info(PythonFunctionInfo.from_function(proper_func1))
        p = platform.system()
        if p == 'Windows':
            self.assertNotEqual(html.find('<style'), -1)
        else:
            self.assertEqual(html.find('<style'), -1)

def bad_func1():
    ''' I'm a bad function.
    My docstring is wrong.
    '''

    pass

def proper_func1():
    ''' Estimates Rhob from Vp using Gardner, Gardner, Gregory.

    Parameters
    ----------
    vp : sequence : units=km/s
      P-velocity in km/s
    cons : scalar
      Multiplicative constant, default is .32
    expn : scalar
      Exponential constant, default is .23

    Returns
    -------
    rhob : sequence
      Bulk density in g/cc

    Description
    -----------
    Estimates bulk density from vp using Gardner, Gardner, Gregory equation:
      
               Rhob = cons * (Vp**expn)  in g/cc

    where the default value of 'cons' is .32 and the default value of 'expn' is
    .23 for Vp in ft/sec.
    '''
    pass

def proper_func2():
    """
    Fixes the density log

    Parameters
    ----------
    density_log : array : units=g/cc
       The Density
    index : array : units=ft
       The index for the density
    water_depth : scalar : units=ft
       How much water are we in?
    kb : scalar : units=ft
       The Kelly Bushing
    td : scalar : units=ft
       Total Depth
    density_fill_value : scalar : units=g/cc
       Value for missing densities
    
    Returns
    -------
    density_log : array : units=g/cc
       The new density log
    index : array : units=ft
       The new index
    """
    pass