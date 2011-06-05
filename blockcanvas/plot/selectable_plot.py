from numpy import array

# ETS imports
from traits.api import HasTraits, Instance, List, Str
from traitsui.api import Item, Group, View, SetEditor, InstanceEditor, VSplit
from codetools.contexts.i_context import IListenableContext

# Local imports
from context_plot import ContextPlotEditor


class ConfiguredContextPlot(HasTraits):
    context = Instance(IListenableContext, adapt='yes')
    plot_list = List(Str)

    def trait_view(self, name=None, view_element=None):
        return View(Item('context',
                     editor=ContextPlotEditor(plot_items=self.plot_list,
                                              view_shadows=True),
                     width=400,
                     height=100,
                     resizable=True,
                     show_label=False,)
                )

class SelectablePlot(HasTraits):
    plot = Instance(ConfiguredContextPlot)
    context = Instance(IListenableContext, adapt='yes')
    plot_list = List(Str)


    def __init__(self, **kwtraits):
        super(SelectablePlot, self).__init__(**kwtraits)
#        self.plot_list = []
        self._plot_list_changed([])
        return

    def trait_view(self, name=None, view_element=None):
        legal_values = [value for value in self.context.keys() if
                         hasattr(self.context[value], 'shape') and len(self.context[value].shape) == 1]
        return View(VSplit(Item('plot_list', editor=SetEditor(values=legal_values,
                                                       left_column_title='Variables',
                                                       right_column_title='Plots',
                                                       ),
                         show_label=False,
                         width=400,
                         height=100,
                         ),
                    Item('plot', editor=InstanceEditor(),
                         style='custom',
                         show_label=False),
                    ),
                    width=500,
                    height=500,
                    resizable=True
                )
    def _plot_list_changed(self, new):
        self.plot = ConfiguredContextPlot(context=self.context,
                                          plot_list=self.plot_list)
        return


if __name__ == '__main__':
    from codetools.contexts.geo_context import GeoContext
    context = GeoContext()
    context['a'] = array([5, 2, 1, 7, 10])
    context['b'] = array([9, 29, 1, 12, 6])
    print context['a'].shape
    print hasattr(context['a'], 'shape')
    plot = SelectablePlot(context=context, plot_list=[])
    plot.edit_traits(kind='modal')
