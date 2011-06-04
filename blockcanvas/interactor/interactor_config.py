# Standard imports
from numpy import ndarray

# ETS imports
from traits.api import HasTraits, List, Str, Int, Enum
from traitsui.api import View, Item, Label, TableEditor, EnumEditor
from traitsui.table_column import ObjectColumn
from traitsui.menu import OKCancelButtons
from traitsui.api import WindowColor

# Application imports
from blockcanvas.ui.table_menu_handler import new_delete_menu, TableMenuHandler


class InteractorConfigHandler(TableMenuHandler):
    """ Handler for the InteractorConfig's default view.
    """

    def get_focused_editor(self, selection):
        """ Due to the lameness of Traits' action/menu system, we have to
            determine which editor the user is using based on the selection.
        """

        if isinstance(selection[0], VariableConfig): return 0
        else: return 1


class VariableConfig(HasTraits):
    """ Represents the configuration details for variable in interactor.
    """

    name = Str
    type = Enum('Shadow', 'Parametric', 'Stochastic: Constant',
                'Stochastic: Gaussian', 'Stochastic: Triangular',
                'Stochastic: Uniform')


class PlotConfig(HasTraits):
    """ Represents the configuration details for a plot of a block's/context's
        output variables
    """

    number = Int(1)
    x = Str
    y = Str
    color = Str
    type = Enum('Line', 'Scatter')


class InteractorConfig(HasTraits):
    """ Configuration object for interactors. Provides a view that allows for
        the selection of inputs for interactors, as well as plot setup.
    """

    vars = List

    var_configs = List(VariableConfig)
    plot_configs = List(PlotConfig)


    def trait_view(self, name=None, view_element=None):

        var_editor_vals = sorted([v.name for v in self.vars])
        var_editor_vals.insert(0, '')
        var_col = [ ObjectColumn(name='name', label='Variable', editable=True,
                                 editor=EnumEditor(values=var_editor_vals),
                                 width=.5),
                    ObjectColumn(name='type', label='Interactor Type',
                                 width=.5, editable=True) ]

        plot_editor_vals = sorted([ value.name for value in self.vars if
                                       isinstance(value.value, ndarray) and
                                       (len(value.value.shape) == 1 or len(value.value.shape) == 2)])

        plot_editor = EnumEditor(values=plot_editor_vals)
        plot_col = [ ObjectColumn(name='number', label='Number', editable=True,
                                  width=.1),
                     ObjectColumn(name='x', label='X Axis', editable=True,
                                  editor=plot_editor, width=.25),
                     ObjectColumn(name='y', label='Y Axis', editable=True,
                                  editor=plot_editor, width=.25),
                     # FIXME: This needs to be re-enabled and tested
                     #ObjectColumn(name='color', label='Color', editable=True,
                     #             editor=plot_editor, width=.25),
                     ObjectColumn(name='type', label='Type', editable=True,
                                  width=.15) ]

        return View(Label('Set up interactors:'),
                    Item('var_configs',
                         editor=TableEditor(columns=var_col,
                                            editable=True,
                                            deletable=False,
                                            configurable=False,
                                            sortable=False,
                                            sort_model = True,
                                            auto_add=True,
                                            menu=new_delete_menu,
                                            row_factory=VariableConfig,
                                            selection_bg_color = None,
                                            label_bg_color = WindowColor,
                                            cell_bg_color = 0xFFFFFF,
                                            ),
                         show_label=False,
                        ),
                     Label('Set up plots:'),
                     Item('plot_configs',
                          editor=TableEditor(columns=plot_col,
                                             editable=True,
                                             deletable=False,
                                             configurable=False,
                                             sortable=False,
                                             auto_add=True,
                                             menu=new_delete_menu,
                                             row_factory=PlotConfig,
                                             selection_bg_color = None,
                                             label_bg_color = WindowColor,
                                             cell_bg_color = 0xFFFFFF,
),
                          show_label=False,
                         ),
                     id="interactor.InteractorConfig",
                     title="Configure Interactor",
                     buttons=OKCancelButtons,
                     handler=InteractorConfigHandler(),
                     close_result=False,
                     resizable=True,
                    )



if __name__ == "__main__":
    import numpy as np
    from enthought.contexts.api import DataContext
    from blockcanvas.block_display.block_unit_variables import BlockUnitVariableList
    from enthought.contexts.api import DataContext
    from blockcanvas.app.experiment import Experiment

    code = "from blockcanvas.debug.my_operator import add, mul\n" \
           "c = add(a,b)\n" \
           "d = mul(c, 2)\n" \
           "e = mul(c, 3)\n" \
           "f = add(d,e)"

    context = DataContext(name='Data')
    context['a'] = np.linspace(0, 10.0, 20)
    context['b'] = np.linspace(-12, 12, 20)

    exp = Experiment(code=code, shared_context=context)
    # FIXME: Shouldn't have to manually call this now
    exp.context.execute_for_names(["a","b"])

    vars = BlockUnitVariableList(block=exp.exec_model.block, context=exp.context)
    interactor = InteractorConfig(vars=vars.variables)
    interactor.configure_traits()

    for varconf in interactor.var_configs:
        print 'name: '+ varconf.name + ', type: ' + varconf.type
    for plotconf in interactor.plot_configs:
        print str(plotconf.number) + ': ' + plotconf.x + ', ' + plotconf.y + \
              ', ' + plotconf.color
