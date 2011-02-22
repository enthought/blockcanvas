"""
@author: 
Eraldo Pomponi
        
@copyright: 
The MIIC Development Team (eraldo.pomponi@uni-leipzig.de) 
    
@license: 
GNU Lesser General Public License, Version 3
(http://www.gnu.org/copyleft/lesser.html) 

Created on -- Feb 7, 2011 --
"""

# Enthought TraitsUI imports
from enthought.traits.ui.api import (View, HSplit, VSplit, Item,
                                     InstanceEditor)

# Enthought BlockCanvas import
from enthought.block_canvas.block_display.block_editor import BlockEditor
from enthought.block_canvas.app.ui.function_search_ui import function_search_view
from enthought.block_canvas.app.block_application_view_handler import BlockApplicationViewHandler

def create_view(model=None):
    view = View( 
                HSplit(
                        VSplit(
                                Item('object.function_view_instance.function_search',
                                     editor = InstanceEditor(view=function_search_view),
                                     label      = 'Search',
                                     id         = 'search',
                                     style      = 'custom',
                                     dock       = 'horizontal',
                                     show_label = False),
                                Item('object.function_view_instance.html_window',
                                     style='custom',
                                     show_label=False,
                                     springy= True,
                                     resizable=True),
                                id='search_help_view'
                                ),      
                        Item( 'object.function_view_instance.project.active_experiment.canvas',
                                      label      = 'Canvas',
                                      id         = 'canvas',
                                      # FIXME:  need a new way to control the canvas
                                      # not using BlockEditor
                                      editor     = BlockEditor(),
                                      dock       = 'horizontal',
                                      show_label = False),
                        id='panel_split'),
              title     = 'Group Creation/Manipulation View',
              width     = 1024,
              height    = 768,
              id        = 'miic.core.group_creation',
              resizable = True,
              handler   = BlockApplicationViewHandler(model=model),
              buttons   = ['OK','Help']
            )
    return view

if __name__ == "__main__":
    pass

#    from python_function_info import PythonFunctionInfo
#    from function_call_group import FunctionCallGroup
#    from function_call import FunctionCall
#    from group_spec import GroupSpec
#    
#    func1 = PythonFunctionInfo(module='os',
#                          name='getenv')
#    func_call1 = FunctionCall.from_callable_object(func1)
#
#    func2 = PythonFunctionInfo(module='os',
#                          name='getenv')
#    func_call2 = FunctionCall.from_callable_object(func1)   
#    
#    gfunc = GroupSpec(type='plain')
#    
#    group_func_call = FunctionCallGroup(gfunc, statements=[func_call1,func_call2])
#    
#    group_func_call.configure_traits(view=create_view())
    
    