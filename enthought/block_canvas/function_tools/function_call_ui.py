from enthought.traits.ui.api import (View, Group, HGroup, VGroup, VSplit, Item,
                                     Label, TableEditor, CodeEditor, InstanceEditor, spring, Tabbed)
from enthought.traits.ui import menu
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.api import WindowColor
from enthought.traits.ui.editors import ButtonEditor


def create_view(readonly = False, show_units = False):
    if show_units:
        # fixme: Should combine the units with the name to reduce size?
        #        Are people going to change units here or on a global settings level?
        #        I think the latter.
        columns = [ObjectColumn(name='name', label='Name', editable=False, width=0.3),
                   ObjectColumn(name='units', label='Units', editable=False, width=0.3),
                   ObjectColumn(name='binding', label='Binding', editable=True, width=0.4),
                  ]
    else:
        columns = [ObjectColumn(name='name', label='Name', editable=False, width=0.4),
                   ObjectColumn(name='binding', label='Binding', editable=True, width=0.6),
                  ]
        
    if readonly:
        code_editor_style = 'readonly'
    else:
        code_editor_style = 'simple'
        
    
    view = View(
               VSplit(                      
                      VGroup(Item('object.function.name'),
                             Item('object.function.module'),
                                    

                             HGroup(
                                    VGroup(Label("Inputs"),
                                           Item('inputs',
                                         # minimum settings to get rid of
                                         # toolbar at top of table.
                                         editor=TableEditor(columns=columns,
                                                            editable=True,
                                                            configurable=False,
                                                            sortable=False,
                                                            sort_model = True,
                                                            selection_bg_color = 'white',
                                                            selection_color = 'black',
                                                            label_bg_color = WindowColor,
                                                            cell_bg_color = 'white',
                                         ),
                                         show_label=False,
                                         ),
                                    ),
                                    VGroup(Label("Outputs"),
                                           Item('outputs',
                                             # minimum settings to get rid of
                                             # toolbar at top of table.
                                             editor=TableEditor(columns=columns,
                                                            editable=True,
                                                            configurable=False,
                                                            sortable=False,
                                                            sort_model = True,
                                                            selection_bg_color = 'white',
                                                            selection_color = 'black',
                                                            label_bg_color = WindowColor,
                                                            cell_bg_color = 'white',
                                         ),
                                         show_label=False,
                                        ),
                                        ),
                                    ),
                            ),
                      Group(
                            Item('object.function.code',
                                 editor=CodeEditor(),
                                 style=code_editor_style,
                                 show_label=False),

                            Item('convert_to_local',
                                 editor=ButtonEditor(),
                                 enabled_when='function.__class__.__name__.count("PythonFunctionInfo")>0',
                                 show_label=False,
                                ),
                    ),
                  ),
                  width=720, # about 80 columns wide on code view.
                  height=700,
                  resizable=True,
                  buttons=menu.OKCancelButtons,
                  close_result=False,
         )
    
    return view

def create_alternate_view():
    columns = [ObjectColumn(name='name', label='Name', editable=False, width=0.4),
               ObjectColumn(name='binding', label='Binding', editable=True, width=0.6),
               ]

    view = View(
        Tabbed(                      
            # Allow for a user specified view of the inputs
            Item('function_view_instance', 
                editor=InstanceEditor(view='traits_view'), 
                label = "Properties",
                show_label=False, 
                style='custom', 
                resizable=True,
                ),

            VGroup(
                Item('object.function.name'),
                Item('object.function.module'),

                HGroup(
                    VGroup(
                        Label("Inputs"),
                        Item('inputs',
                            # minimum settings to get rid of
                            # toolbar at top of table.
                            editor=TableEditor(
                                columns=columns,
                                editable=True,
                                configurable=False,
                                sortable=False,
                                sort_model = True,
                                selection_bg_color = 'white',
                                selection_color = 'black',
                                label_bg_color = WindowColor,
                                cell_bg_color = 'white',
                                ),
                            show_label=False,
                            resizable=True,
                            ),
                        ),

                    VGroup(
                        Label("Outputs"),
                        Item('outputs',
                            # minimum settings to get rid of
                            # toolbar at top of table.
                            editor=TableEditor(
                                columns=columns,
                                editable=True,
                                configurable=False,
                                sortable=False,
                                sort_model = True,
                                selection_bg_color = 'white',
                                selection_color = 'black',
                                label_bg_color = WindowColor,
                                cell_bg_color = 'white',
                                ),
                            show_label=False,
                            resizable=True,
                            ),
                        ),
                    ),
                label="Context Info",
                ),
            ),
                  
#            width=720, # about 80 columns wide on code view.
#            height=700,
            resizable=True,
            buttons=menu.OKCancelButtons,
            close_result=False,
         )
    
    return view
    

if __name__ == "__main__":
    from python_function_info import PythonFunctionInfo
    from function_call import FunctionCall
    func = PythonFunctionInfo(module='cp.rockphysics.converge.fluids.brine_properties',
                          name='brine_properties')
    func_call = FunctionCall.from_callable_object(func)
    func_call.configure_traits(view=create_view())
