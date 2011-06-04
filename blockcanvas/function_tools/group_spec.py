"""
@author: 
Eraldo Pomponi
        
@copyright: 
The MIIC Development Team (eraldo.pomponi@uni-leipzig.de) 
    
@license: 
GNU Lesser General Public License, Version 3

(http://www.gnu.org/copyleft/lesser.html) 

Created on -- Jan 28, 2011 --
"""
# Sys lib
from compiler.ast import AssTuple, AssName, CallFunc, Name

# Enthought Traits imports
from traits.api import HasTraits, Instance, Property, \
                                 List, Str, Int

# Enthought BlockCanvas imports
from blockcanvas.function_tools.function_variables \
    import InputVariable, OutputVariable
from blockcanvas.function_tools.general_expression \
    import GeneralExpression


def find_next_binding(var, active_experiment):
    """Determines the next open binding for input and output variables based on the 
    current experiment's context and the binding of other statements.

    If no active experiment is give, simply the variable name is returned."""
    # Set the binding prefix we are looking for once
    binding_prefix = "{0}".format(var.name)

    if active_experiment != None:
        # Initialize binding prefix set with context
        bps = set([key for key in active_experiment.context.keys() if binding_prefix in key])

        # Add in bindings from statement prefixes.  
        # This ensures unique bindings even when the code + context has not been executed
        for stmt in active_experiment.exec_model.statements:
            # Add binding from other inputs
            for stmt_input in stmt.inputs:
                if binding_prefix in stmt_input.binding:
                    bps.add(stmt_input.binding)

            # Add binding from other outputs
            for stmt_output in stmt.outputs:
                if binding_prefix in stmt_output.binding:
                    bps.add(stmt_output.binding)

        num = len(bps) + 1
        while (binding_prefix + str(num)) in bps:
            num += 1
        next_binding = binding_prefix + str(num)
        return next_binding
    else:
        return binding_prefix


class GroupSpec(HasTraits):
    """ Specific information for each Group type.
    
    This object describe each method to group statements together 
    (TODO: at this moment just the for and while loops are supported) and how
    to manage it in the ExecutionModel object produced by the canvas also in 
    terms of free inputs that each group "adds" and that cannot be recognized 
    by the StatementWalker parser. It also define which is/are the variable/s 
    that should be accessible in the creation of the group body as 
    "current element". 
    """

    # The type of grouping function. It is needed to manage different 
    # call_signature creation. There are two main branches right now: 
    #
    #  - Proper group (e.g. for, while)
    #  - Plain group 
    #
    # The first branch is obvious. The second represent groups created 
    # to collect together possibly many statements that realize a 
    # well defined part of the work flow. For example "pre_processing" 
    # or "hw_interface" etc. It is necessary to obtain a clean view even
    # when the number of blocks becomes consistent. 
    # Those block are just created in the view but they are not persistent. 
    # To make them useful also for a successive reopening of the same project, 
    # they must be (previously) separately saved as function. 
    #
    # 'for1' = for loop : single current element : simple iterable 
    # 'for2' = for loop : tuple current element: simple iterable
    # 'for1f' = for loop : single current element : iterable as function output
    # 'while' = .....
    # 'plain' = no loop ... 
      
    # TODO: implement 'for1f' 'for2f' 'while' 'plain'
    type = Str 
    _type = ['for1','for1f','for2','while','plain','custom']
    
    # The Indent amount necessary to correctly represent group body. Default to 4 spaces 
    indent_space = Int
    
    inputs = List(InputVariable)
    
    # It is a list of instance because we could have multiple current elements,
    # for example when we are dealing with tuple ("for (i,elem) in iterable:") 
    curr_elemts = List(Instance(GeneralExpression))
    
    # Property that depends on the input attribute and the 
    # curr_element signature.
    # It is useful when current element is a tuple.
    call_signature = Property(depends_on=['input','curr_elem'])
    _call_signature = Str()
    
    # Template for the call_signature creation
    call_sig_template = Str()
    
    # Fake free input variables introduced by adding the loop to a 
    # block of statements (i.e. the ast parser must not take into account those 
    # variables because they are added just for creating a loop and must not be
    # changed in the canvas)   
    reserved_inputs = Property(depends_on=['inputs'])
    _reserved_inputs = List(Str, None)
    
    # The same as for the input
    reserved_outputs = Property(depends_on=['curr_elemts'])
    _reserved_outputs = List(Str, None)


    @classmethod
    def from_ast(cls,ast_type,ast,active_experiment=None):
                
        if ast_type == 'for':
            indent_space = 4
            assign_node,list = ast
            # Single current_elem
            if isinstance(assign_node, AssName):
                outputs = [assign_node.name]
            # Tuple current_elem
            elif isinstance(assign_node, AssTuple):
                outputs = []
                for node in assign_node.nodes:
                    outputs.append(node.name)
                    
            # TODO: It manage just for loop with an iterable that can be 
            # a Name:'iterable' or a CallFunc 'enumerate(iterable)'. All other 
            # possibilities are not supported yet.
            
            # Iterable obtained after applying a function 
            if isinstance(list, CallFunc):
                func_name = list.node.name
                inputs = [arg.name for arg in list.args]
                call_signature_temp = 'for %%s in %s%%s:\n' % func_name
            # Simple itarable Name
            elif isinstance(list, Name):
                inputs = [list.name]
                call_signature_temp = 'for %s in %s:\n' 
                
            return cls(type='custom',\
                       inputs=inputs,\
                       outputs=outputs,\
                       call_signature_temp=call_signature_temp,\
                       indent_space=indent_space,\
                       active_experiment=active_experiment)
        
        # TODO: While loop implementation
        elif ast_type == 'while':
            pass

            
    def __init__(self,type=None,inputs=[],outputs=[],call_signature_temp="",indent_space=4, active_experiment=None):
        """  
        There are two ways to create this object:
            - passing the type that must be between the tabulated one
            - custom
            
        In the latter case all the parameters must be passed to create a group specification object.
        """

        if self.type is not None:
            assert(type in self._type)
            self.type = type
                
            # Tabulated loop versions
            if self.type == 'for1':    
                self.for__single_celem(active_experiment)
            elif self.type == 'for2':
                self.for__tuple_celem(active_experiment)
            elif self.type == 'plain':
                self.indent_space = 0
            elif self.type == 'custom':
                for input_name in inputs:
                    self.add_input(input_name, active_experiment)
                for output_name in outputs:
                    self.add_celem(output_name, active_experiment)
                self.call_sig_template = call_signature_temp
                # Explicitly assign the indent amount
                self.indent_space = indent_space
                 
    
    def add_input(self,var_name,active_experiment):
        """ Add a new input to the gfunc specification. 
        
        The new input is named as the first available name in the context 
        with var_name root. 
        """
        i_var = InputVariable()
        i_var.name = var_name
        i_var.name = find_next_binding(i_var,active_experiment)
        self.inputs.append(i_var)

    def add_celem(self,var_name,active_experiment):
        """ Add a new output to the gfunc specification. 
        
        The new celem is named as the first available name in the context 
        with var_name root. 
        Each celem is an instance of GeneralExpression to create it in a 
        way that can be added "as is" to the execution model. 
        """
        o_var = OutputVariable()
        o_var.name = var_name
        o_var.name = find_next_binding(o_var,active_experiment) 
        
        c_el = GeneralExpression(code=o_var.name)
        c_el.outputs = [o_var]
        self.curr_elemts.append(c_el)
        
 
    def for__single_celem(self,active_experiment):
        """ For loop with one current element and a simple iterable.
        
        Loop signature is:
        
        for celem in iterable:
        ....body
        
        """
        self.call_sig_template = "for %s in %s:\n"
        
        # Explicitly assign the indent amount 
        self.indent_space = 4;
        
        # It is an input variable for the resulting block of code
        self.add_input('iterable', active_experiment)

        # It is an output variable from the canvas point of view. 
        # It is displayed by the canvas as a Block with just an 
        # output. 
        self.add_celem('celem', active_experiment)
    
    def for__tuple_celem(self,active_experiment):
        """ For loop with tuple current element and a simple iterable.
        
        Loop signature is:
        
        for (tuple_x,tuple_y) in iterable:
        ....body
        
        """
        self.call_sig_template = "for %s in %s:\n"
        
        # Explicitly assign the indent amount
        self.indent_space = 4;
        
        # It is an input variable for the resulting block of code
        self.add_input('iterable', active_experiment)
        
        # It is an output variable from the canvas point of view. 
        # It is displayed by the canvas as a Block with just an 
        # output. 
        self.add_celem('tuple_x', active_experiment)
        self.add_celem('tuple_y', active_experiment)
       
           
    ####### Private methods ###################################################
    
    def _get_call_signature(self):
        
        # If it is a "degenerated" group, the call_signature is just a new line 
        if self.type == 'plain':
            return '\n'
        
        # Current_elem call_signature creation 
        if len(self.curr_elemts) > 1 :
            list_of_signature = [curr_elem.call_signature for curr_elem in self.curr_elemts]
            celem_call_signature = '(' + ','.join(list_of_signature) + ')'
        else:
            celem_call_signature = self.curr_elemts[0].call_signature
        
        # Iterable call_signature creation
        if len(self.inputs) > 1 :
            iterable_signature = '('+','.join(in_var.binding for in_var in self.inputs)+')'
        else:
            iterable_signature = self.inputs[0].binding
        
        # Combine the above signatures using the template stored in call_sig_template 
        self._call_signature = self.call_sig_template % (celem_call_signature, iterable_signature)
        
        return self._call_signature
    
    def _get_reserved_outputs(self):
        return None
    
    def _get_reserved_inputs(self):
        #list_of_signature = [curr_elem.call_signature for curr_elem in self.curr_elemts]
        return ['%s' % curr_elem.call_signature for curr_elem in self.curr_elemts]

        
if __name__ == '__main__':

    """
    Test code
    """
    loop_type = 'for1'
    a = GroupSpec(type=loop_type)
    print a.call_signature,  a.reserved_inputs, a.reserved_outputs
    
    