""" Simple user interface for viewing/editing code in a LocalPythonFunction.

    The UI has read-only tables for the input/outputs of the function.  Below
    that has a code window that allows users to edit the function.  When the 
    function is edited, the inputs/outputs should update appropriately.  If
    there is a syntax error (load_error) in the text, the error is reported
    in a text box at the bottom of the UI.
    
    Since we don't really do this in the application (we edit the FunctionCall),
    the UI has been made private.  It is useful for testing that a LocalPythonFunction 
    is updating correctly based on changes to its code.
"""

from enthought.traits.ui.api import (View, Group, HGroup, VGroup, VSplit, Item,
                                     Label, TableEditor, CodeEditor)
from enthought.traits.ui import menu
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.api import WindowColor


input_columns = [ObjectColumn(name='name', label='Name', editable=False, width=0.4),
                 ObjectColumn(name='default', label='Default', editable=False, width=0.6),
                ]

output_columns = [ObjectColumn(name='name', label='Name', editable=False, width=0.4),
                  ObjectColumn(name='name', label='Name', editable=False, width=0.6),
                  ]
        
view = View(
       VSplit(
              HGroup(
                     VGroup(Label("Inputs"),
                            Item('inputs',
                                 # minimum settings to get rid of
                                 # toolbar at top of table.
                                 editor=TableEditor(columns=input_columns,
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
                                 editor=TableEditor(columns=output_columns,
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
              Group(
                    Item('code',
                         editor=CodeEditor(),
                         show_label=False),
                 Item('load_error',
                      show_label=False),

              ),
          ),
          width=720, # about 80 columns wide on code view.
          height=700,
          resizable=True,
          buttons=menu.OKCancelButtons,
          close_result=False,
)

if __name__ == "__main__":
    from enthought.block_canvas.function_tools.local_python_function import \
        LocalPythonFunction
        
    code = "def new_function():\n" \
           "    pass"
    func = LocalPythonFunction(code=code)           
    func.configure_traits(view=view)
