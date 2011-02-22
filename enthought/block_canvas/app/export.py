"""
@author: 
Eraldo Pomponi
        
@copyright: 
The MIIC Development Team (eraldo.pomponi@uni-leipzig.de) 
    
@license: 
GNU Lesser General Public License, Version 3
(http://www.gnu.org/copyleft/lesser.html) 

@summary: 
This modules contains functions to export the execution model in a file in a way
that can be used outside the canvas and that permit to included it (appended) to 
an exist module (maybe for reusing it through the canvas). 

Created on -- Jan 20, 2011 --
"""

# Major library imports
import logging
from compiler.ast import CallFunc

import __builtin__
builtin_names = set(dir(__builtin__))

 
# Enthought CodeTools
from enthought.blocks.analysis import walk
from enthought.blocks.api import parse

# Enthought BlockCanvas
from enthought.block_canvas.function_tools.function_variables \
    import InputVariable, OutputVariable
    
from enthought.block_canvas.function_tools.general_expression \
    import StatementWalker, GeneralExpression
   
from enthought.block_canvas.function_tools.function_call_group import FunctionCallGroup
from enthought.block_canvas.function_tools.utils import reindent, is_str

logger = logging.getLogger(__name__)

# Helping functions ##########################################################              
                



# Exposed functions ##########################################################
   
def export_as_function(filename, func_name, \
                       imports_and_locals, sorted_statements, context, \
                       reserved_inputs=None, reserved_outputs=None, mode="w"):
    """
    Export an execution model plus a context as a Function.
    
    This function create the code to be saved on a file to export an execution 
    model (import, locals and sorted statements) plus the associated context. 
    The latter have been obtained in the form of direct binding between 
    variables and their value if it is present in the context.  
    Only the "free" variables are left as arguments of the obtained function.
    """
        
    basic_code = imports_and_locals + '\n'.join(statement.call_signature
                         for statement in sorted_statements)

    inputs,outputs = _retrieve_inputs_and_outputs(basic_code, \
                                                  reserved_inputs, \
                                                  reserved_outputs)
            
    base_name = _create_base_name(func_name,inputs,context)
    imp_and_loc = _create_code_from_imports_and_locals(imports_and_locals, \
                                                       indents_amount=4)
    body = _create_code_from_statements(sorted_statements,inputs, \
                                        context, indents_amount=4)
    return_code = _create_return_code(outputs)
   
    code = base_name + \
          imp_and_loc + \
          "\n\n"+ \
          body + \
          "\n" + \
          return_code + \
          "\n#EOF\n"

    f = file(filename, mode)
    try:
        f.write(code)
    finally:
        f.close()
        
        
def export_as_script(filename, imports_and_locals, \
                     sorted_statements, context, \
                     reserved_inputs=None, reserved_outputs=None, mode="w"):
    """
    Export an execution model plus a context as a Python script.
    
    This function create the code to be saved on a file to export an execution 
    model (import, locals and sorted statements) plus the associated context. 
    The latter have been obtained in the form of direct binding between 
    variables and their value if it is present in the context.  
    """
    
    basic_code = imports_and_locals + '\n'.join(statement.call_signature
                         for statement in sorted_statements)
      
    inputs,_ = _retrieve_inputs_and_outputs(basic_code, \
                                            reserved_inputs,reserved_outputs)
            
    imp_and_loc = _create_code_from_imports_and_locals(imports_and_locals, \
                                                       indents_amount=0)  
    body = _create_code_from_statements(sorted_statements,inputs, \
                                        context, indents_amount=0)
   
    code = imp_and_loc + \
          "\n\n"+ \
          body + \
          "\n#EOF\n"

    f = file(filename, mode)
    try:
        f.write(code)
    finally:
        f.close()

# Reserved functions #########################################################

def _create_base_name(func_name, inputs, context):

    base_name_template = "def %(name)s(" 
    base_name = base_name_template % {'name':func_name} 
    
    free_input_vars = ', '.join(var.name for var in inputs \
                                if var.name not in context) 
            
    if free_input_vars != "":
        return "%(base_name)s %(inputs)s): \n" % \
               {'base_name':base_name,'inputs':free_input_vars}
    else:
        return "%(base_name)s): \n" % \
               {'base_name':base_name}
    
    
def _create_code_from_imports_and_locals(imports_and_locals, \
                                         indents_amount=4):
        
    return ' \n'.join(reindent(import_statement,indents_amount) \
                      for import_statement in \
                      imports_and_locals.splitlines() \
                      if import_statement != '')
        
        
def _create_code_from_statements(sorted_statements, inputs, context, \
                                 indents_amount=8, reserved_inputs=[]):
                        
    stat_list = []
    for stmt in sorted_statements:
        if isinstance(stmt,GeneralExpression):
            stat_list.append(reindent(stmt.call_signature,indents_amount))
        elif isinstance(stmt,FunctionCallGroup):
            stat_list.append(reindent(stmt.gfunc.call_signature,indents_amount))
            if stmt.gfunc.type=='plain':
                add_space = 0
            else:
                add_space = 4
            reserved_inputs = stmt.gfunc.reserved_inputs
            stat_list.append(reindent(_create_code_from_statements(stmt.group_statements,
                                             inputs,
                                             context,
                                             indents_amount=indents_amount+add_space,
                                             reserved_inputs = reserved_inputs),
                                      indents_amount))
        else:
            stat_list.append(reindent(_statement_static_signature(stmt,
                                                                  inputs,
                                                                  context,
                                                                  reserved_inputs=reserved_inputs),
                                      indents_amount))
                  
    return ' \n'.join(stat_list)
    
    
def _retrieve_inputs_and_outputs(code = "", reserved_inputs=None, \
                                 reserved_outputs=None):
    """ Parse code to retrieve inputs and outputs 
        taking into account who are the reserved_inputs and 
        reserved_outputs. 
        This function returns list of InputVariable, OutputVariable.
    """
      
    if code =="":
        return
    
    ast = parse(code)
    walker = walk(ast, StatementWalker())
    imported_names = walker.imported_names
    outputs = []
    notinputs = set()
    
    for assigns, _ in walker.expressions:
        for name in assigns:
            if reserved_outputs is None or name not in reserved_outputs:
                outputs.append(OutputVariable(name=name, binding=name))
            notinputs.add(name)

    notinputs.update(imported_names)

    # Add function definition to the list of notinputs
    function_calls = [expr for assigns, expr in walker.expressions \
                           if isinstance(expr, CallFunc) ]
    
    [notinputs.add(call.node.name) for call in function_calls]   
    
    # Add the builtins, too.
    notinputs.update(builtin_names)
    inputs = []
    for name in walker.names:
        if name not in notinputs:
            if reserved_inputs is None or name not in reserved_inputs:
                inputs.append(InputVariable(name=name, binding=name))
    
    return inputs,outputs


def _create_return_code(outputs):
    
    return_template = "    return %(output)s\n"
    output_vars = ', '.join(var.name for var in outputs)
    return return_template % {'output': output_vars}


def _statement_static_signature(statement, inputs, context, reserved_inputs=[]):
    
    # Join all non-empty call signatures together as a comma separated
    # string replacing static binding (with values in the context)  
    # with context['binding'] itself
    
    in_args_list = [];
    for input in statement.inputs:
        if input.call_signature:
            in_args_list.append("%s" % _static_input_signature(input,inputs,context,reserved_inputs=reserved_inputs))
    
    in_args = ', '.join(in_args_list)

    if len(statement.outputs) > 0:
        out_args = ', '.join(output.binding for output in statement.outputs)
        call_signature = "%s = %s(%s)" % (out_args, statement.label_name, in_args)
    else:
        call_signature = "%s(%s)" % (statement.label_name, in_args)
        
    return call_signature


def _static_input_signature(input, inputs, context, reserved_inputs = []):
                
    # input_names = [input_var.name for input_var in inputs]

    if input.binding in context and input.binding not in reserved_inputs: # and input.binding in input_names:
        value = context[input.binding]
        
        if not input.keyword_argument:
            if is_str(value):
                signature = "'%s'" %(value)
            else:
                signature = "%s" %(value)  
        else:    
            if input._binding is None:
                signature = ""
            else:
                if is_str(value):
                    signature = "%s='%s'" %(input.name, value)
                else:
                    signature = "%s=%s" %(input.name, value)                 
    else:
        value = input.binding
        
        if not input.keyword_argument:
            signature = value
        else:    
            if input._binding is None:
                signature = ""
            else:
                signature = "%s=%s" %(input.name, value)
    
    return signature
    

if __name__ == '__main__':

    """
    Test code
    """
    from enthought.contexts.api import DataContext 
    from execution_model import ExecutionModelExtended as ExecutionModel

           
    code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
       "def bar(xx,yy):\n" \
       "    k = xx * yy\n" \
       "    return k\n\n" \
       "a = add(c,2)\n" \
       "b = mul(3,2)\n" \
       "y = bar(a,b)\n"
       
    exec_model = ExecutionModel.from_code(code)
    
    imports_and_locals = exec_model.imports_and_locals
    sorted_statements = exec_model.sorted_statements
    context = DataContext(name = 'test')
    context['a'] = 5
    context['b'] = 6
    context['y'] = 30
    
    filename = 'test_f.py'
    func_name = 'test_f'
       
    export_as_function(filename, func_name, \
                       imports_and_locals, sorted_statements, context)
    
    filename = 'test_s.py'
    
    export_as_script(filename, \
                     imports_and_locals, sorted_statements, context)
    




#EOF
