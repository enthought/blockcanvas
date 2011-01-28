from enthought.traits.ui.api import (View, Group, HGroup, VGroup, VSplit, Item,
                                     Label, TableEditor, CodeEditor)
from enthought.traits.ui import menu
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.api import WindowColor


def create_view(model_view, readonly = False, show_units = True):
    if show_units:
        columns = [ObjectColumn(name='name', label='Name', editable=False, width=0.3),
                   ObjectColumn(name='units', label='Units', editable=False, width=0.3),
                   ObjectColumn(name='binding', label='Value', editable=True, width=0.4),
                  ]
    else:
        columns = [ObjectColumn(name='name', label='Name', editable=False, width=0.4),
                   ObjectColumn(name='binding', label='Value', editable=True, width=0.6),
                  ]

    if readonly:
        code_editor_style = 'readonly'
    else:
        code_editor_style = 'simple'


    view = View(
               VSplit(
                      HGroup(
                             VGroup(Label("Inputs"),
                                    Item('object.model.inputs',
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
                                    Item('object.model.outputs',
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
                      Group(
                            Item('object.model.code',
                                 editor=CodeEditor(),
                                 style=code_editor_style,
                                 show_label=False),

                      ),
                  ),
                  model_view=model_view,
                  width=720, # about 80 columns wide on code view.
                  height=700,
                  resizable=True,
                  buttons=menu.OKCancelButtons,
                  close_result=False,
         )

    return view

