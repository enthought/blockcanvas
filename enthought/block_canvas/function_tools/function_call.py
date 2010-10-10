""" Class that holds information about how a function is to be called and
    provides methods for creating python code strings that will call the
    method with appropriate arguments.

    It is useful for displaying UIs for functions on the workflow canvas.

    Note: It may also be more fundemental -- for example part of a Block node
          to make it easier to edit inputs/outputs on nodes and also to
          coordinate text and graphic views of a workflow.  This isn't
          clear yet.

    fixme: Output variable bindings can *only* be a valid python variable.
           We need a trait to represent this restriction.
"""
# Standard library imports
import warnings

# enthought library imports
from uuid import UUID, uuid4
from enthought.traits.api import (Any, Delegate, Event, HasTraits, Instance, 
        List, on_trait_change, Property, Str)
from enthought.traits.ui.api import (View, Item, HGroup, CodeEditor, 
        ButtonEditor, VGroup, spring)

# Local imports
from callable_info import CallableInfo
from function_call_tools import localify_func_code
from function_call_ui import create_view, create_alternate_view
from function_variables import InputVariable, OutputVariable
from local_function_info import LocalFunctionInfo
from parse_tools import function_inputs_from_call_ast
from python_function_info import PythonFunctionInfo

class FunctionCall(HasTraits):
    """ Class that holds information about how a function is to be called.
    """

    # Name displayed for the function in a UI as well as in the call signature.
    # If it is not specified, then we use the function's library name.
    # This should be a delegate, but traits delegates check the type from the
    # delegatee, so the delegatee can't be None if the trait is assigned to.
    label_name = Property #Delegate('function', 'library_name', modify=False)
    _label_name = Any(None)

    # List of the function's input variable names, bindings, and default values.
    inputs = List(InputVariable)

    # List of the function's output variables names and bindings
    outputs = List(OutputVariable)

    # The "function" class the associated with this call.
    # fixme: I think this should really be an interface...
    function = Instance(CallableInfo)

    # The code for this function including its signature line.
    code = Delegate('function', 'code', modify=True)

    # Read-only string of python code that calls the function.
    call_signature = Property(depends_on=['outputs.binding','function'])

    # Specify an alternate view
    inputs_view_class = Any()

    # A unique identifier
    uuid = Instance(UUID)
    _uuid_default = lambda self: uuid4()

    # Convert a PythonFunctionInfo object to a LocalFunctionInfo object
    convert_to_local = Event

    ##########################################################################
    # Traits View and related handlers
    ##########################################################################
    def trait_view(self, view):
        if self.inputs_view_class == None:
            return create_view()
        else:
            return create_alternate_view()
    
    def _convert_to_local_fired(self, event):
        new_name = 'local_' + self.function.library_name
        new_code = localify_func_code(self.function.code,
                                      self.function.library_name,
                                      new_name,
                                      self.function.module)
        new_func = LocalFunctionInfo(name=new_name,
                                     code=new_code,
                                     )
        self.function = new_func
        return



    ##########################################################################
    # FunctionCall interface
    ##########################################################################

    ### Class methods -- constructors ########################################
    
    # fixme: This is the signature we want.    
    #def from_ast(cls, ast, function_info=None):
    @classmethod
    def from_ast(cls, ast, function_callables=None):
        """ Create a FunctionCall object from a python abstract syntax tree
            object.  
            
            The AST is expected to be for expressions from code of this type:
            
                a, b = foo(c,d)
            
            This has the assignment variables as well as the call of the 
            function.                    
        """

        # Initialize result
        result = None

        # What function has been called in this ast?
        res = function_inputs_from_call_ast(ast)

        if res:
            name, args = res
            func_name = name[0]
            
            if func_name in function_callables:
                result = FunctionCall.from_callable_object(function_callables[func_name])

            else:
                # fixme: If we fail to find the location information,
                #        we should still make a FunctionCall object.
                #        We can just set the CallableInfo it points
                #        at to be None.  The bindings, etc. are still
                #        valid.
                result = cls(label_name=func_name)

            # Returns have be gotten from the block code
            if len(args) == len(result.inputs):
                for arg, input in zip(args, result.inputs):
                    input.binding = str(arg)

        else:
            # FIXME: What should we return if this ast doesn't contain
            # a valid FuncCall or more than one FuncCall?
            msg = "%s does not contain a valid function call." % ast
            warnings.warn(msg)
        return result

    @classmethod
    def from_callable_object(cls, function, inputs_view_class=None):
        """ Create a FunctionCall object given a CallableInfo.  

            The bindings for inputs and outputs will default to Undefined.
            The location for the function will default to the file information
            for the function.           
            
            Note that this currently only works for PythonFunctionInfo and 
            LocalPythonFunctionInfo objects.
        """

        inputs = [InputVariable(name=input.name, default=input.default)
                      for input in function.inputs]

        # fixme: Outputs should just be a list of strings...
        outputs = [OutputVariable(name=output.name) for output in function.outputs]
        result = cls(inputs=inputs, outputs=outputs, function=function, inputs_view_class=inputs_view_class)

        return result

    @classmethod
    def from_function(cls, function, inputs_view_class=None):
        """ Create a FunctionCall object given a CallableInfo.  

            The bindings for inputs and outputs will default to Undefined.
            The location for the function will default to the file information
            for the function.           
            
            Note that this currently only works for PythonFunctionInfo and 
            LocalPythonFunctionInfo objects.
        """
    
        callable_object = PythonFunctionInfo.from_function(function)
        return cls.from_callable_object(callable_object, inputs_view_class)

    @classmethod
    def create_empty_function(cls, code=None):
        """
        """
        raise NotImplementedError


    ### Property get/set methods  ############################################

    def _get_label_name(self):
        if self._label_name is None:
            return self.function.library_name
        else:
            return self._label_name

    def _set_label_name(self, name):
        self._label_name = name
        return 
        
    def _get_call_signature(self):
        """ Return a python code that will call this function with the
            appropriate bindings.
            
            Returns:
            --------
            code: Str
                Code representing the function call and assignment
        """

        # Join all non-empty call signatures together as a comma separated
        # string.
        in_args = ', '.join([input.call_signature for input in self.inputs
                             if input.call_signature])

        if len(self.outputs) > 0:
            out_args = ', '.join(output.binding for output in self.outputs)
            call_signature = "%s = %s(%s)" % (out_args, self.label_name, in_args)
        else:
            call_signature = "%s(%s)" % (self.label_name, in_args)
            
        return call_signature


    ### static trait listeners  ##############################################

    # FIXME: These static listeners should be changed to use the decorator
    # syntax, but when coded that way, they don't work for some reason.
    # This has been entered as ticket #1352.
    def _inputs_changed_for_function(self):
        self.update_from_function()
    def _inputs_items_changed_for_function(self):
        self.update_from_function()

    def _outputs_changed_for_function(self):
        self.update_from_function()
    def _outputs_items_changed_for_function(self):
        self.update_from_function()

    def _code_changed_for_function(self):
        self.update_from_function()

    def update_from_function(self):
        """ Updates input and output variable bindings appropriately when
        the FunctionInfo's code changes.
        
        This is not the same as just calling from_callable_object and then
        cloning the traits, because the existing bindings have to be taken
        into account.
        """
        function = self.function
        
        input_bindings = dict((obj.name,obj._binding) for obj in self.inputs)
        inputs = []
        for input in function.inputs:
            var = InputVariable(name=input.name, default=input.default)
            if input.name in input_bindings and input_bindings[input.name] is not None:
                var.binding = input_bindings[input.name]
            inputs.append(var)
        self.inputs = inputs

        output_bindings = dict((obj.name,obj._binding) for obj in self.outputs)
        outputs = []
        for output in function.outputs:
            var = OutputVariable(name=output.name)
            if output.name in output_bindings and output_bindings[output.name] is not None:
                var.binding = output_bindings[output.name]
            outputs.append(var)
        self.outputs = outputs


def foo(a,b=3):
    x, y = a,b
    return x,y

if __name__ == '__main__':

    from function_info import find_functions
    from enthought.blocks.api import Block
    code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
           "c = add(a,b)\n" \
           "d = mul(c, 2)\n" \
           "e = mul(c, 3)\n" \
           "f = add(d,e)"

    foo_block = Block(code)
    info = find_functions(foo_block.ast)
    print "Info", info
    foo_call = FunctionCall.from_ast(foo_block.sub_blocks[1].ast, info)

    code = "def foo(a):\n" \
           "\tb = a\n" \
           "\treturn b\n" \
           "y = foo(2)\n" 
    foo_block = Block(code)
    info = find_functions(foo_block.ast)
    print "Info", info
    foo_call = FunctionCall.from_ast(foo_block.sub_blocks[-1].ast, info)
    print 'Name:', foo_call.name
    print 'Inputs:', foo_call.inputs
    print 'Outputs:', foo_call.outputs

