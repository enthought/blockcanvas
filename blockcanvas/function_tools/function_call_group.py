"""
@author: 
Eraldo Pomponi
        
@copyright: 
The MIIC Development Team (eraldo.pomponi@uni-leipzig.de) 
    
@license: 
GNU Lesser General Public License, Version 3
(http://www.gnu.org/copyleft/lesser.html) 

Created on -- Jan 31, 2011 --
"""
# Major library imports
from copy import deepcopy
from uuid import UUID

import __builtin__
builtin_names = set(dir(__builtin__))

# Enthought Traits import
from traits.api import \
    Property, Instance, List, Str, Bool, Any, on_trait_change

# Enthought BlockCanvas import
from blockcanvas.app import scripting

from blockcanvas.function_tools.function_call import \
    FunctionCall
from blockcanvas.function_tools.callable_info import \
    CallableInfo
from blockcanvas.function_tools.function_search import \
    FunctionSearch
from blockcanvas.function_tools.function_library import \
    FunctionLibrary
from blockcanvas.class_tools.class_library import \
    ClassLibrary

# Local import
from function_call_group_ui import create_view
from group_spec import GroupSpec
from parse_code import retrieve_inputs_and_outputs
from utils import reindent

class FunctionCallGroup(FunctionCall):
    """ Groups together a series of FunctionCall Objects.
    
    Puts together a series of FunctioCall in a single group with its own 
    UUID and grouping function (i.e. an Instance of the object GroupSpec). 
    """
    
    # They must be sorted properly (i.e. sorted_statements attribute of an
    # execution model) 
    group_statements = List(Any)

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
    #
    # 'for1' = for loop : single current element : simple iterable 
    # 'for2' = for loop : tuple current element: simple iterable
    # 'for1f' = for loop : single current element : iterable as function output
    # 'for2f' = for loop : tuple current element: iterable as function output
    # 'plain' = no loop ... 
    
    
    # Instance of the grouping function
    gfunc = Instance(GroupSpec)
            
    # Read-only string of python code that calls the function.
    # It is replicated here because we want that it changes also when one of
    # the statements is changed not just the binding and the function code
    # as it is for the Parent class. 
    call_signature = Property()  
    
    code = Property(depends_on=['group_statements',
                                'group_statements_items', 
                                'group_statements.inputs.binding',
                                'group_statements.outputs.binding',
                                'function']) 
    _code = Str
         
    # List of UUID of the grouped functions 
    uuid_list = Property(depends_on=['group_statements',
                                     'group_statements_items'])
    _uuid_list = List(Instance(UUID))


    # FIXME: Needed just because of the type of view now implemented.
    # It will go away when this view will be replaced. 
    _prev_defer_execution = Bool  
    _prev_allow_execute = Bool
    
    ##########################################################################
    # Traits View and related handlers
    ##########################################################################
    
    def trait_view(self, view):
        """
        This implementation should go away immediately when groups are managed
        "graphically". A possible way to create a new "world" where the 
        execution is still serial is to create a new instance of LoopApp 
        that shares with the "main" one all the basic data 
        (contexts, class_library, func_library, func_search) but not the 
        same experiment. 
        """
        
        # To avoid circular imports
        from blockcanvas.app.app import Application
        
        code = None       
        app_exist = False
        
        if hasattr(scripting,'app'):                        
            
            app_exist = True
            
            # If the methods is called by another app that wants to add a group, 
            # retrieve it from the scripting module recursively.
            app = scripting.app
            
            # Save the current reference in the scripting module           
            if not hasattr(scripting,'app_tree'):
                scripting.app_tree = []
                
            scripting.app_tree.append(app)
                 
            class_library = app.class_library
            func_library = app.function_library 
            func_search = app.function_search  
        
        else:
            # It is more or less a test if the method works well so the module
            # is chosen by hand. 
            # It should never happen that this method is called outside an 
            # instance of the BlockCanvas app.     
            modules = ['os']        
            class_library = ClassLibrary(modules=modules)
            func_library = FunctionLibrary(modules=modules)
            func_search = FunctionSearch(all_functions=func_library.functions)
    
        # TODO: This new object overwrite the scripting.app reference so there 
        # should be a way to call a "fix_scripting_app" method when this view
        # is closed. FIXED: Now this step is done by update_from_UI 
        self.function_view_instance = Application(code=code,
                               class_library=class_library, 
                               function_library=func_library, 
                               function_search=func_search)
  
        if app_exist:            
            # Share the context with the Parent app if it exist
            self.function_view_instance.project.active_experiment.context.subcontext = \
            app.project.active_experiment.context.subcontext
            
            # During the editing of the group fired events due to change in the context
            # are deferred now and completely cleaned after the group creation to
            # avoid useless execution. 
            # Those parameters must be fixed after the group is Created/Updated. 
            # This step is done by "update_from_UI" method 
            self._prev_defer_execution = app.project.active_experiment.context.defer_execution
            app.project.active_experiment.context.defer_execution = True

            
            # To save some time is also nice to stop the execution in the calling app due to
            # events fired every time a statement is added to the execution model. 
            # It must be noticed that allow_execute must be saved instead of just put it to 
            # False, to properly manage nested groups/loops.
            self._prev_allow_execute = app.project.active_experiment.exec_model.allow_execute
            app.project.active_experiment.exec_model.allow_execute = False
            
        # No execution in the sub_app during the editing of the group
        self.function_view_instance.project.active_experiment.exec_model.allow_execute = False
                            
        # Add current element/s to the view
        if self.gfunc is not None:
            for curr_elem in self.gfunc.curr_elemts:
                self.function_view_instance.add_function_to_execution_model(curr_elem, x=None, y=None)
        
        # When reopening an existing group add its statements       
        for stmt in self.group_statements:
            self.function_view_instance.add_function_to_execution_model(stmt, x=None, y=None)

        return create_view(model=self.function_view_instance)


    ##########################################################################
    # FunctionCallGroup interface
    ##########################################################################
    
    ### Class methods -- constructors ########################################
    
    @classmethod
    def from_ids(cls, exec_mod, gfunc, ids):
        """Merge statements from an exec_model into a FunctionCallGroup Obj.
        
        It is necessary to pass a GroupSpec object (i.e. the grouping function)
        and the ids list (i.e. uuid) of the statements to merge. 
        If also just one of those ids are not valid it raises an 
        AssertionError.  
        """        
        # Needed to check selection result with assert
        loc_ids = deepcopy(ids)

        selec_stmt = [] 
        
        for statement in exec_mod.sorted_statements:
            if statement.uuid in loc_ids:
                selec_stmt.append(statement)   
                loc_ids.remove(statement.uuid)
        assert(loc_ids==[])
        
        func_name = exec_mod.generate_unique_function_name(base_name='group')        
        return cls(gfunc=gfunc, statements=selec_stmt, gname=func_name)
    
           
    def __init__(self, gfunc=None, statements=[], gname="", *args, **kwargs):   
        
        super(FunctionCallGroup,self).__init__(*args, **kwargs)     
        
        self.gfunc = gfunc
        
        # Remove the statements added by gfunc and only needed to access the 
        # current element through the canvas, then assign them 
        # to group_statements         
        self.clean_and_add_statements(statements)
        
        # Adaptation of the FaunctionCall object
        group_fun = CallableInfo() 
        
        # This name should be unique in the context. 
        if gname == "":
            group_fun.name = 'group'
        else:
            group_fun.name = gname
            
        group_fun.code = self.code
        
        self.function = group_fun

    def clean_and_add_statements(self, statements=[], ids=None):
        """ Clean and add statements to group_statements attribute.
        
        This method remove added statements for the exhibition in canvas
        of the "current_element" and then save those left in 
        group_statements attribute.
        As a side effect it also clean the list "ids" that contains the
        uuid of the statements added to this group. 
        """
        
    
        if ids is not None:
            for stmt in statements:
                assert(stmt.uuid in ids)
        
        if self.gfunc is None:
            self.group_statements = statements
            return ids
        
        to_remove = []
        for statement in statements:
            if statement in self.gfunc.curr_elemts:
                to_remove.append(statement)
                  
        for stmt in to_remove:
            statements.remove(stmt)
            if ids is not None:
                # Clean also ids list
                ids.remove(stmt.uuid)
        
        self.group_statements = statements
        # It could be useful for other applications
        return ids 
            

    def update_from_UI(self):
        """Update a FunctionCallGroup Object through the current View.
        
        It depends on the actual type of view that is not just a view but an
        entire app of the same type of that one that contains this object. 
        It is not an hack but must go away or be strongly modified if the 
        View will return just a view!!!    
        """
        if self.function_view_instance is None:
            return
        
        stmts = self.function_view_instance.project.active_experiment.exec_model.sorted_statements
        self.clean_and_add_statements(statements=stmts)
        
        # Restore the correct reference in the scripting module
        if hasattr(scripting,'app_tree') :
            scripting.app = scripting.app_tree.pop()
                
        # Clear the deferred names to skip execution & Restore defer_execution
        scripting.app.project.active_experiment.context._deferred_execution_names = []
        scripting.app.project.active_experiment.context.defer_execution = self._prev_defer_execution
        
        # Restore allow_execution in the calling app 
        scripting.app.project.active_experiment.exec_model.allow_execute = self._prev_allow_execute
           
      
    @on_trait_change('group_statements',
                     'group_statements_items', 
                     'group_statements.inputs.binding',
                     'group_statements.outputs.binding')  
    def _update_inputs_outputs(self):
        
        self.inputs = []
        self.outputs = []
        
        # TODO: This code is necessary if we want to reduce the variable 
        # accessible from outside the loop leaving only those one that 
        # have not been binded with any others. 

        basic_code = '\n'.join(statement.call_signature
             for statement in self.group_statements)
        
        # This function returns just the names of this variables instead of
        # InputVariable or OutputVariable. They are collected from the original
        # statements to retain the reference top those objects and guarantee 
        # their updates.  
        inputs_name, outputs_name = \
           retrieve_inputs_and_outputs(code = basic_code)

        # Outside of the function must be exposed proper reference to 
        # InputVariable and OutputVariable object present in the 
        # group_statements attribute according with the retrieved 
        # inputs_name and outputs_name 
        
        for stmt in self.group_statements:
            for input in stmt.inputs:
                # FIXME: I'm not sure if I must check just the binding value 
                # or both binding and name!!!!  
                if input.binding in inputs_name:
                    self.inputs.append(input)
                    inputs_name.remove(input.binding)
            for output in stmt.outputs:
                if output.binding in outputs_name:
                    self.outputs.append(output)
                    outputs_name.remove(output.binding)           
        assert(inputs_name==outputs_name==[])
        
        if self.gfunc is not None:
            self.inputs.extend(self.gfunc.inputs)
        
            
    ### Property get/set methods  ############################################
    
          
    def _get_call_signature(self):
        return self.code
    
    def _get_code(self):
         
        if self.group_statements == []:
            self._code = ""
        else:   
            if self.gfunc is not None:
                self._code = self.gfunc.call_signature
                indent_space = self.gfunc.indent_space
            else:
                indent_space = 0
                
            self._code += ' \n'.join(reindent(statement.call_signature,indent_space) \
                                     for statement in self.group_statements)    
        return self._code

    def _get_uuid_list(self):
                
        # Statements UUID concatenation 
        for statement in self.group_statements:
                self._uuid_list.append(statement.uuid)
        return self._uuid_list 
            
            
if __name__ == '__main__':

    from blockcanvas.function_tools.local_function_info import LocalFunctionInfo
    
    f1code = "def foo(x=3, y=4):\n" \
    "    z = x + y\n" \
    "    return z\n" 
   
    f2code = "def bar(k='ciao'):\n" \
    "    print 'K=%s' % k\n" 
    
    f1 = LocalFunctionInfo(code=f1code)
    f2 = LocalFunctionInfo(code=f2code)
    
    F1 = FunctionCall.from_callable_object(f1)
    F2 = FunctionCall.from_callable_object(f2)
    
    group_type = 'for1'
    lsp = GroupSpec(type=group_type)            
    node = FunctionCallGroup(lsp, statements=[F1,F2], gname='test_group');
    
    print "CODE:\n"
    print node.code
    print "\nUUID:%s\n" % node.uuid
    print "\nUUID_LIST:\n"
    for u in node.uuid_list:
        print 'uuid:%s\n' % u
    print "\nINPUTS:\n"
    for input in node.inputs:
        print 'name:%s binding:%s default:%s\n' % (input.name, input.binding, input.default)
    print "\nOUTPUTS:\n"
    for output in node.outputs:
        print 'name:%s binding:%s\n' % (output.name, output.binding)    
    
    













#EOF
