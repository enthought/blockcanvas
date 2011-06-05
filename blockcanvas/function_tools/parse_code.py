"""
@author: 
Eraldo Pomponi
        
@copyright: 
The MIIC Development Team (eraldo.pomponi@uni-leipzig.de) 
    
@license: 
GNU Lesser General Public License, Version 3
(http://www.gnu.org/copyleft/lesser.html) 

Created on -- Feb 15, 2011 --
"""
from compiler.ast import CallFunc

import __builtin__
builtin_names = set(dir(__builtin__))

from blockcanvas.function_tools.general_expression \
    import StatementWalker
    
# CodeTools imports
from codetools.blocks.api import parse
from codetools.blocks.analysis import walk


def retrieve_inputs_and_outputs(code="",reserved_inputs=[],reserved_outputs=[]):
    """ Parse code to retrieve inputs and outputs 
        taking into account who are reserved_inputs and 
        reserved_outputs.
        FIXME: fix the StatementWalker object to manage function_call 
               without returned value (no assignment).
    """
       
    ast = parse(code)
    walker = walk(ast, StatementWalker())
    imported_names = walker.imported_names
    outputs = []
    notinputs = set()
    for assigns, _ in walker.expressions:
        for name in assigns:
            if reserved_outputs is None or name not in reserved_outputs:
                outputs.append(name)
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
                # Icky. We don't know that the user gave code in the correct
                # order.
                inputs.append(name)
    
    return inputs,outputs

#EOF
