# Standard library imports
import unittest

# Enthought library imports
from enthought.blocks.api import Block

# Local library imports
from enthought.block_canvas.function_tools.function_call import \
    FunctionCall
from enthought.block_canvas.function_tools.function_info import \
    find_functions

from enthought.block_canvas.function_tools.tests.typical_functions import simple, with_defaults, \
    with_defaults_none, with_varargs, with_kwargs, with_varargs_kwargs, \
    no_return, empty_return
    

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

            

    def test_simple(self):

        func_call = FunctionCall.from_function(simple)
                
        inputs = func_call.inputs

        # Check the names.
        desired = ['a','b']
        self.assertEqual([x.name for x in inputs], desired)

        # And the default values.
        desired = [None, None]
        self.assertEqual([x.default for x in inputs], desired)

        # And the values values.
        desired = ['a', 'b']
        self.assertEqual([x.binding for x in inputs], desired)

        # Now check the output names.
        outputs = [x.name for x in func_call.outputs]
        desired = ['x','y']
        self.assertEqual(outputs, desired)
        
        # Check the module.
        # fixme: Do we actually want to test this here?  I think only if
        #        we choose to move module up to the func_call level.
        desired = simple.__module__
        self.assertEqual(func_call.function.module, desired)

        
    def test_with_defaults(self):
        func = FunctionCall.from_function(with_defaults)

        inputs = func.inputs

        # Check the names.
        desired = ['a','b']
        self.assertEqual([x.name for x in inputs], desired)

        # And the default values.
        desired = [None, '3']
        self.assertEqual([x.default for x in inputs], desired)

        # Now check the output names.
        outputs = [x.name for x in func.outputs]
        desired = ['x','y']
        self.assertEqual(outputs, desired)

        # fixme: Need to test for this later once var_args
        #self.assertEqual(func.var_args,"")
        #self.assertEqual(func.kw_args,"")

    def test_with_defaults_none(self):

        func = FunctionCall.from_function(with_defaults_none)

        inputs = func.inputs

        # Check the names.
        desired = ['a','b']
        self.assertEqual([x.name for x in inputs], desired)

        # And the default values.
        desired = [None, 'None']
        self.assertEqual([x.default for x in inputs], desired)


#    def test_with_varargs(self):
#
#        func = FunctionCall.from_function(with_varargs)
#
#        inputs = func.inputs
#
#        # Check the names.
#        desired = ['a','b']
#        self.assertEqual([x.name for x in inputs], desired)
#
#        # And the default values.
#        desired = [None, '3']
#        self.assertEqual([x.default for x in inputs], desired)
#
#        # Now check the output names.
#        outputs = [x.name for x in func.outputs]
#        desired = ['x','y','z']
#        self.assertEqual(outputs, desired)
#
#        self.assertEqual(func.var_args,"args")
#        self.assertEqual(func.kw_args,"")
#
#    def test_with_kwargs(self):
#
#        func = FunctionCall.from_function(with_kwargs)
#
#        inputs = func.inputs
#
#        # Check the names.
#        desired = ['a','b']
#        self.assertEqual([x.name for x in inputs], desired)
#
#        # And the default values.
#        desired = [None, '3']
#        self.assertEqual([x.default for x in inputs], desired)
#
#        # Now check the output names.
#        outputs = [x.name for x in func.outputs]
#        desired = ['x','y','z']
#        self.assertEqual(outputs, desired)
#
#        self.assertEqual(func.var_args,"")
#        self.assertEqual(func.kw_args,"kw")
#
#
#    def test_with_varargs_kwargs(self):
#
#        func = FunctionCall.from_function(with_varargs_kwargs)            
#
#        inputs = func.inputs
#
#        # Check the names.
#        desired = ['a','b']
#        self.assertEqual([x.name for x in inputs], desired)
#
#        # And the default values.
#        desired = [None, '3']
#        self.assertEqual([x.default for x in inputs], desired)
#
#        # Now check the output names.
#        outputs = [x.name for x in func.outputs]
#        desired = ['x','y','z','zz']
#        self.assertEqual(outputs, desired)
#
#        self.assertEqual(func.var_args,"args")
#        self.assertEqual(func.kw_args,"kw")
        
    def test_no_return(self):

        func = FunctionCall.from_function(no_return)            


        # Now check the output names.
        outputs = [x.name for x in func.outputs]
        desired = []
        self.assertEqual(outputs, desired)

    
    def test_label_name(self):

        func = FunctionCall.from_function(simple)            
        self.assertEqual(func.label_name,"simple")
        
        func.function.name = "no_return"
        self.assertEqual(func.label_name, "no_return")

        func.function.library_name = "foo"
        self.assertEqual(func.label_name,"foo")

    
    
    ### Call Signature tests #################################################

    def test_simple_call_signature(self):

        func = FunctionCall.from_function(simple)
                
        desired = 'x, y = simple(a, b)'
        self.assertEqual(func.call_signature, desired)


    def test_no_return_call_signature(self):
           
        func = FunctionCall.from_function(no_return)
                
        desired = 'no_return(a, b)'
        self.assertEqual(func.call_signature, desired)

    def test_empty_return_call_signature(self):

        func = FunctionCall.from_function(empty_return)
                
        desired = 'empty_return(a, b)'
        self.assertEqual(func.call_signature, desired)        
        
    def test_unbound_default_call_signature(self):


        func = FunctionCall.from_function(with_defaults)
                
        desired = 'x, y = with_defaults(a)'
        self.assertEqual(func.call_signature, desired)

    def test_name_change_updates_call_signature(self):

        func = FunctionCall.from_function(simple)
                
        desired = 'x, y = simple(a, b)'
        self.assertEqual(func.call_signature, desired)
        
        func.label_name = 'baz'
        desired = 'x, y = baz(a, b)'
        self.assertEqual(func.call_signature, desired)
        
        # fixme: HAVE NOT TESTED WHAT THIS DOES TO IMPORT STATEMENT,
        #        ETC.

    #
    # Test pre-processing step
    #
    def test_import_preprocessing(self):
        code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
           "c = add(a,b)\n" \
           "d = mul(c, 2)\n" \
           "e = mul(c, 3)\n" \
           "f = add(d,e)"

        foo_block = Block(code)
        info = find_functions(foo_block.ast)        

        desired = 'enthought.block_canvas.debug.my_operator'
        assert 'add' in info
        assert info['add']
        add_func = info['add']
        self.assertEqual(add_func.module, desired)

        assert 'mul' in info
        assert info['mul']
        mul_func = info['mul']
        self.assertEqual(mul_func.module, desired)

    def test_import_rename_preprocessing(self):
        code = "from enthought.block_canvas.debug.my_operator import add as add1\n" \
               "a = add1(1,2)\n" \
               "b = add1(a,3)"

        foo_block = Block(code)
        info = find_functions(foo_block.ast)
            
        assert 'add1' in info
        assert not( 'add' in info )
        assert info['add1']

        desired = 'enthought.block_canvas.debug.my_operator'
        add1_func = info['add1']
        self.assertEqual(add1_func.module, desired)

    def test_local_function_preprocessing(self):
        code = "def foo(a,b):\n" \
               "\tx,y=a,b\n" \
               "\treturn x,y\n" \
               "i,j = foo(1,2)\n" 
        foo_block = Block(code)
        info = find_functions(foo_block.ast)

        assert 'foo' in info
        assert info['foo']
    
    # 
    # Test from_ast()
    # 
    def test_import(self):
        code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
           "c = add(a,b)\n" \
           "d = mul(c, 2)\n" \
           "e = mul(c, 3)\n" \
           "f = add(d,e)"

        foo_block = Block(code)
        info = find_functions(foo_block.ast)
        foo_call = FunctionCall.from_ast(foo_block.sub_blocks[1].ast, info)
        
        desired = 'result = add(a, b)'
        self.assertEqual(foo_call.call_signature, desired)


    def test_import_and_rename(self):
        code = "from enthought.block_canvas.debug.my_operator import add as add1\n" \
               "a = add1(1,2)\n" \
               "b = add1(a,3)"
        foo_block = Block(code)
        info = find_functions(foo_block.ast)
        foo_call = FunctionCall.from_ast(foo_block.sub_blocks[1].ast, info)

        desired = 'result = add(1, 2)'
        self.assertEqual(foo_call.call_signature, desired)

    def test_local_def(self):
        code = "def foo(a):\n" \
               "    b = a\n" \
               "    return b\n" \
               "y = foo(2)\n" 
        foo_block = Block(code)
        info = find_functions(foo_block.ast)
        foo_call = FunctionCall.from_ast(foo_block.sub_blocks[-1].ast, info)

        desired = 'b = foo(2)'
        self.assertEqual(foo_call.call_signature, desired) 

# This test is more for the AST version of things...
#    def test_with_arg_defaults(self):
#        """ THIS TEST WILL FAIL! (IT SHOULDN'T).
#        
#            We don't handle default arguments that are not const as keyword
#            arguments right now.
#        """
#        global_value=4
#        def with_arg_defaults(a,b=3,c=global_value):
#            x,y,z=a,b,c
#            return x,y,z
#
#        func = FunctionCall.from_function(with_arg_defaults)
#
#        inputs = func.inputs
#
#        # Check the names.
#        desired = ['a','b','c']
#        self.assertEqual([x.name for x in inputs], desired)
#
#        # And the default values.
#        # This is the actual desired, but for now, we'll take our "punted" value.
#        #desired = [None, 3, 4]
#        desired = [None, 3, 'global_value']
#        self.assertEqual([x.default for x in inputs], desired)
#
#        # Now check the output names.
#        outputs = [x.name for x in func.outputs]
#        desired = ['x','y','z']
#        self.assertEqual(outputs, desired)


                         
# Missing Tests
# 1. construction from call ast.
# 2. label changes change function name.
# 3. Test that we can handle a large number of functions
#    without problems (try some standard python modules).
# 4. Handling generic callable objects in a sane way.

if __name__ == '__main__':
    unittest.main()
