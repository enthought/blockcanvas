# Standard library imports
import unittest

# Enthought library imports
from codetools.blocks.api import Block

# Local library imports
from blockcanvas.function_tools.function_call import \
    FunctionCall

from blockcanvas.function_tools.group_spec import \
    GroupSpec

from blockcanvas.function_tools.function_call_group import \
    FunctionCallGroup
    
from blockcanvas.function_tools.tests.typical_functions import simple, with_defaults, \
    with_defaults_none, with_varargs, with_kwargs, with_varargs_kwargs, \
    no_return, empty_return


class FunctionCallGroupTestCase(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        
        func_call1 = FunctionCall.from_function(simple)
        func_call2 = FunctionCall.from_function(with_defaults)
        
        self.statements = [func_call1,func_call2]
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # FunctionDefinitionTestCase interface
    ##########################################################################



    def test_simple(self):
        
        func_call_group = FunctionCallGroup(statements=self.statements)
        inputs = func_call_group.inputs
        
        # Check inputs.
        desired = ['a','b']
        self.assertEqual([x.name for x in inputs], desired)

        # Check binding.
        desired = ['a', 'b']
        self.assertEqual([x.binding for x in inputs], desired)

        # Check the output names.
        outputs = [x.name for x in func_call_group.outputs]
        desired = ['x','y','x','y']
        self.assertEqual(outputs, desired)
        
    ##########################################################################
    # Test call_signature
    ##########################################################################
    
    def test_for_single_celem(self):
        gfunc = GroupSpec(type='for1')
        func_call_group = FunctionCallGroup(gfunc=gfunc, statements=self.statements)
        
        desired_call_signature = """for celem in iterable:
    x, y = simple(a, b) 
    x, y = with_defaults(a, b=b)"""
        
        self.assertEqual(func_call_group.call_signature,desired_call_signature)
    
    def test_for_single_celem_enum_iterable(self):
        gfunc = GroupSpec(type='for1f')
        func_call_group = FunctionCallGroup(gfunc=gfunc, statements=self.statements)
        
        desired_call_signature = """for (i,celem) in enumerate(iterable):
    x, y = simple(a, b) 
    x, y = with_defaults(a, b=b)"""
        
        self.assertEqual(func_call_group.call_signature,desired_call_signature)
    
    def test_for_tuple_celem(self):
        gfunc = GroupSpec(type='for2')
        func_call_group = FunctionCallGroup(gfunc=gfunc, statements=self.statements)
        
        desired_call_signature = """for (tuple_x,tuple_y) in iterable:
    x, y = simple(a, b) 
    x, y = with_defaults(a, b=b)"""
    
        self.assertEqual(func_call_group.call_signature,desired_call_signature)

    def test_plain(self):
        gfunc = GroupSpec(type='plain')
        func_call_group = FunctionCallGroup(gfunc=gfunc, statements=self.statements)
        
        desired_call_signature = """
x, y = simple(a, b) 
x, y = with_defaults(a, b=b)"""
    
        self.assertEqual(func_call_group.call_signature,desired_call_signature)

    def test_nested_groups(self):
        
        statements = []
        gfunc = GroupSpec(type='for1')
        func_call_group = FunctionCallGroup(gfunc=gfunc, statements=self.statements)
        
        statements.extend(self.statements)
        statements.append(func_call_group)
        
        gfunc = GroupSpec(type='for2')
        func_call_group2 = FunctionCallGroup(gfunc=gfunc, statements=statements)
        
        desired_call_signature = """for (tuple_x,tuple_y) in iterable:
    x, y = simple(a, b) 
    x, y = with_defaults(a, b=b) 
    for celem in iterable:
        x, y = simple(a, b) 
        x, y = with_defaults(a, b=b)"""
        
        self.assertEqual(func_call_group2.call_signature,desired_call_signature)
        
    ##########################################################################
    # Test binding
    ##########################################################################

    def test_update_input_binding(self):
        gfunc = GroupSpec(type='for1')
        func_call_group = FunctionCallGroup(gfunc=gfunc, statements=self.statements)
        
        func_call_group.inputs[0].binding = 'k'

        func_call1 = self.statements[0]

        self.assertEqual(func_call1.inputs[0].binding,'k')
        
    def test_update_output_binding(self):
        gfunc = GroupSpec(type='for1')
        func_call_group = FunctionCallGroup(gfunc=gfunc, statements=self.statements)
        
        func_call_group.outputs[0].binding = 'k'

        func_call1 = self.statements[0]

        self.assertEqual(func_call1.outputs[0].binding,'k')
        
        
if __name__ == '__main__':
    unittest.main()
