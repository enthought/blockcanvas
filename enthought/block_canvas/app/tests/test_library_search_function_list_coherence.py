# Note: I put this in the same directory so that I didn't have to mess around with the path.

# General library imports
from nose.tools import assert_equal

# ETS Imports
from enthought.traits.api import push_exception_handler, pop_exception_handler
from enthought.block_canvas.function_tools.function_library import FunctionLibrary
from enthought.block_canvas.function_tools.i_minimal_function_info import MinimalFunctionInfo
from enthought.block_canvas.app.app import Application


# Module-level setup and teardown.
def setup():
    # If a trait exception occurs, fail the test.
    push_exception_handler( handler = lambda o,t,ov,nv: None,
                            reraise_exceptions = True,
                            main = True,
                          )

def teardown():
    pop_exception_handler()

##############################################################################
# FunctionSearch should update when FunctionLibrary.functions changes.
#
# Test that trait change listeners are hooked up correctly.
##############################################################################

def test_initializing_with_library_initializes_function_searh():
        
    library = FunctionLibrary(modules=['os'])

    b = Application(function_library=library)
    # FIXME:
    #   The assertion below is failing because in
    #   enthought/block_canvas/app/app.py line 541
    #   post_init is set to True, which means that function_library
    #   is not updated upon initialization.  The post_init change
    #   was made in a number of locations in this file at changeset 19002.
    #assert_equal(b.function_search.all_functions, library.functions)

def test_changing_library_initializes_function_searh():
        
    library = FunctionLibrary(modules=['os'])

    b = Application()
    b.function_library = library
    assert_equal(b.function_search.all_functions, library.functions) 


def test_changing_library_functions_initializes_function_searh():
        
    library = FunctionLibrary(modules=['os'])

    b = Application()
    b.function_library = library
    assert_equal(b.function_search.all_functions, library.functions) 
    
    # This forces the library to recalculate its functions.
    library.modules = ['os', 'telnetlib']
    assert_equal(b.function_search.all_functions, library.functions) 

def test_appending_library_functions_initializes_function_searh():
        
    library = FunctionLibrary(modules=['os'])

    b = Application()
    b.function_library = library
    assert_equal(b.function_search.all_functions, library.functions) 
    
    # This is sorta cheating, but add an item to the function list
    # and ensure that we are updating.
    library.functions.append(MinimalFunctionInfo())
    assert_equal(b.function_search.all_functions, library.functions) 
