""" Methods using function calls.
"""

# Standard imports
import os
import re

# Enthought library imports
from enthought.etsconfig.api import ETSConfig
from enthought.pyface.api import confirm, error, YES

# Local imports
#from function_definition import FunctionDefinition
from utils import get_code_from_file, USER_MODULE_NAME

def localify_func_code(code, old_func_name, new_func_name, module_name):
    """To make a PythonFunctionInfo into a LocalFunctionInfo, we
    need to potentially change the name of the function, and add
    a line of imports into the function.  Pass in the code,
    the old name, the name to rename to, and the module name
    of the original function"""
    # FIXME: It would be better to do this with the _ast module
    renamed_code = re.sub(r'(.*def )' + old_func_name + r'(.*\()',
                          r'\1' + new_func_name + r'\2',
                          code)
    import_str = 'from %s import *\n' % module_name
    lines = renamed_code.split('\n')
    newcode = ''
    inserted = False
    for lineno, line in enumerate(lines):
        if lineno != len(lines)-1:
            newcode += line + '\n'
        else:
            newcode += line
        if line.count('def')>0 and not inserted:
            indent = re.match(r'([ \t]*).*', lines[lineno+1]).group(1)
            newcode += indent + import_str
            inserted = True
    return newcode

    

def edit_function_call(func_def):
    
    if func_def.code is None:
        msg = "Perhaps your python path is not set correctly or\n" \
              "there is an error in the file (or one it imports).\n"
        error(None, msg, "Error loading function")
        
        return None

    # If it is a user-defined function, one would want to edit it
    # else it can remain un-editable.
    path_dir = os.path.dirname(func_def.filename)
    usr_path = os.path.join(ETSConfig.user_data, USER_MODULE_NAME)

    if path_dir == usr_path:
        # This is a user function
        
        is_ok = edit_user_function(func_def)

        if is_ok:
            if func_def.dirty:
                func_def.write(overwrite = True)
                
            return func_def            
    else:
        is_ok = edit_sys_function(func_def)
            
        if is_ok:
            if func_def.dirty:
                func_def.write(overwrite = False)
            return func_def
        
def edit_user_function(func_def):
    ui = func_def.edit_traits( view = edittable_function_call_view,
                                kind='livemodal')
    
    if not ui.result:
        # The user cancelled the edit
        func_def.reload()
        return None

    return ui.result

def edit_sys_function(func_def):
    func_def.make_user_function()
    
    ui = func_def.edit_traits(view=edittable_function_call_view,
                               kind='livemodal')
    if not ui.result:
        # The user cancelled the edit
        func_def.reload()
        return None
        
    return ui.result

def activate_function_call(func_def):
    """ Given a function and its path (optionally), open a function-call.

        If the function is a user-defined/edited/saved function then make it
        editable. If the user edits the code of the user-function, overwrite the
        function and prompt the user to add the function. If the user does not
        edit the code of the function, just add it as other functions would be
        added.

        Parameters:
        -----------
        func_def: FunctionDefinition
            Contains the function, and its python path.

        Returns:
        --------
        edited_function: function_object
            The function that is edited.
        activated_function: function_object
            The function that must be activated.
        python_string: List[Str]
            includes import and function call to be added to a script.

    """
    
    if func_def.code is None:
        msg = "Perhaps your python path is not set correctly or\n" \
              "there is an error in the file (or one it imports).\n"
        error(None, msg, "Error loading function")
        
        return None

    # If it is a user-defined function, one would want to edit it
    # else it can remain un-editable.
    path_dir = os.path.dirname(func_def.filename)
    usr_path = os.path.join(ETSConfig.user_data, USER_MODULE_NAME)

    if path_dir == usr_path:
        # This is a user function
        
        # We no longer edit the function before dropping it on the canvas 
        #is_ok = edit_user_function(func_def)
        
        # Note: If the user edits the code, one should save the
        #        code and ask the user if (s)he wants to continue
        #        adding the function to the block.
        #        If the user does not edit the code, it should be
        #        the same as it is for a regular function, that is,
        #        the user automatically adds the code to the block.
        if func_def.dirty:
            func_def.write(overwrite = True)

            # Ask for confirmation if the user has to add it to
            # block now or quit without adding.
            msg= 'The user function \'%s' % func_def.name+ \
                 '\' has been edited and overwritten at \n' + \
                 '%s \n\n'% func_def.filename + \
                 'Do you wish to add the function to the block?'

            if confirm(None, msg) == YES:
                return func_def
            else:
                return None
            
        else:
            return func_def

    else:
        # This is a sys function which we are trying to override as a new user func
        # We no longer edit the function before dropping it on the canvas
        #is_ok = edit_sys_function(func_def)

        if func_def.dirty:
            func_def.write(overwrite = False)

            # Ask for confirmation if the user has to add it to
            # block now or quit without adding.
            msg= 'The user function \'%s' % func_def.name+ \
                 '\' has been written at \n' + \
                 '%s \n\n'% func_def.filename + \
                 'Do you wish to add the function to the block?'

            if confirm(None, msg) == YES:
                return func_def
            else:
                return None
            
        else:
            return func_def
        
    return None


### EOF ------------------------------------------------------------------------
