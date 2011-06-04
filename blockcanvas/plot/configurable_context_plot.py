# ETS imports
from traits.api import HasTraits, Instance, List, Str
from traitsui.api import View, Item

# Application imports
from enthought.contexts.i_context import IListenableContext
#from enthought.block_canvas.interactor.interactor_config import PlotConfig

# Local imports
from context_plot import ContextPlotEditor

class ConfigurableContextPlot(HasTraits):
    context = Instance(IListenableContext, adapt='yes')
    plot_configs = List()   #(PlotConfig)

    def trait_view(self, name=None, view_element=None):
        return View(Item('context',
                     editor=ContextPlotEditor(plot_configs=self.plot_configs,
                                              view_shadows=True,
                                              orientation='h'),
                     width=400,
                     height=100,
                     resizable=True,
                     show_label=False,)
                )
