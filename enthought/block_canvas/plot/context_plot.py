from numpy import array, ndarray, min, max
from colorsys import hsv_to_rgb

# Enthought library imports
from enthought.chaco.api import PlotComponent, VPlotContainer, HPlotContainer, hsv
from enthought.chaco.plot import Plot
from enthought.chaco.tools.pan_tool import PanTool
from enthought.chaco.plot_containers import OverlayPlotContainer
from enthought.enable.api import Window
from enthought.traits.api import HasTraits, Instance, Bool, List
from enthought.traits.trait_types import Enum
from enthought.traits.ui.api import BasicEditorFactory, Editor, Item, View

# Application imports
from enthought.contexts.i_context import IListenableContext
from enthought.block_canvas.interactor.interactor_config import PlotConfig


# Local Imports
from plot_data_context_adapter import PlotDataContextAdapter
from enthought.chaco.data_range_1d import DataRange1D
from enthought.chaco.default_colormaps import gray


def color_generator():
    h = 0.3
    s = 1.0
    v = 1.0
    while 1:
        yield hsv_to_rgb(h, s, v)
        h = (h + (11.0/37.0)) % 1.0


class _ContextPlotEditor(Editor):
    scrollable = True
    plot = Instance(PlotComponent)
    view_shadows = Bool(True)
    plot_items = List()
    show_all = Bool(False)
    plot_configs = List()  #(PlotConfig)
    orientation = Enum('v', 'h')

    def init(self, parent):
        self.create_plot()
        self._window = Window(parent,
                              component=self.plot,
                              bgcolor=(236/255.0, 233/255.0, 216/255.0))
        self.control = self._window.control
        self.value.on_trait_change(self._context_items_changed, 'items_modified')
        return


    def _shadow_changed(self, event):
        self._context_items_changed(event)
    def _context_items_changed(self, event):
        if len(event.added)>0 or len(event.removed)>0:
            self.update_editor()

    def update_editor(self):
        self.create_plot()
        self._window.component = self.plot
        self.plot.request_redraw()
        return

    def create_plot(self):
        if hasattr(self.value, 'shadows'):
            color_gen = color_generator()
            shadowcolors = {}
            for shadow in self.value.shadows:
                shadowcolors[shadow] = color_gen.next()

        container_class = {'h' : HPlotContainer, 'v' : VPlotContainer}[self.orientation]
        container = container_class(spacing=15, padding=15, bgcolor = 'transparent')
        container.fill_padding = True
        container.bgcolor=(236/255.0, 233/255.0, 216/255.0)

        if self.show_all:
            self.plot_items = self.value.keys()

        if len(self.plot_items)>0:
            plot_configs = []
            for (plot_num, var_name) in enumerate(self.plot_items):
                if not (isinstance(self.value[var_name], ndarray) and \
                        len(self.value[var_name].shape) == 1):
                    continue
                plot_configs.append(PlotConfig(x=var_name + '_index',
                                               y=var_name,
                                               type='Line',
                                               number=plot_num))
            self.plot_configs = plot_configs


        if len(self.plot_configs)>0:
            number_to_plots = {}
            for plot_config in self.plot_configs:
                plotlist = number_to_plots.get(plot_config.number, [])
                plotlist.append(plot_config)
                number_to_plots[plot_config.number] = plotlist

            keys = number_to_plots.keys()
            keys.sort()
            container_list = [number_to_plots[number] for number in keys]

            for plot_group in container_list:
                context_adapter = PlotDataContextAdapter(context=self.value)
                plot = Plot(context_adapter)
                plot.padding = 15
                plot.padding_left=35
                plot.padding_bottom = 30
                plot.spacing=15
                plot.border_visible = True
                for plot_item in plot_group:
                    if len(self.value[plot_item.y].shape) == 2:
                        color_range = DataRange1D(low=min(self.value[plot_item.y]),
                                                  high=max(self.value[plot_item.y]))
                        plot.img_plot(plot_item.y, colormap=gray(color_range),
                                      name=plot_item.y)

                    else:
                        plot_type = {'Line':'line', 'Scatter':'scatter'}[plot_item.type]
                        plot.plot((plot_item.x, plot_item.y),
                                  name=plot_item.x + " , " + plot_item.y,
                                  color=(.7, .7, .7),
                                  type=plot_type,)
                        if plot.index_axis.title != '':
                            plot.index_axis.title = plot.index_axis.title + ', ' + plot_item.x
                        else:
                            plot.index_axis.title = plot_item.x

                        if plot.value_axis.title != '':
                            plot.value_axis.title = plot.value_axis.title + ', ' + plot_item.y
                        else:
                            plot.value_axis.title = plot_item.y


                        if self.view_shadows and hasattr(self.value, 'shadows'):
                            self.generate_shadow_plots(plot, shadowcolors, plot_item, plot_type)



                plot.tools.append(PanTool(plot))
                container.add(plot)

        self.plot = container

    def generate_shadow_plots(self, plot, shadowcolors, plot_item, plot_type):
        shadow_num = 0
        shadow = None

        for shadow_num, shadow in enumerate(self.value.shadows):
            show_shadow = False
            x_value = plot_item.x
            y_value = plot_item.y
            color_value = plot_item.color
            if plot_item.x in shadow.keys():
                show_shadow = True
                x_value = 'shadow_' + str(shadow_num) + '_' + plot_item.x

            if plot_item.y in shadow.keys():
                show_shadow = True
                y_value = 'shadow_' + str(shadow_num) + '_' + plot_item.y

            if plot_item.color is not None and plot_item.color in shadow.keys():
                color_value = 'shadow_' + str(shadow_num) + '_' + plot_item.y

            if show_shadow:
                if color_value is not None and color_value != '':
                    plot.plot((x_value, y_value, color_value),
                              type='cmap_scatter',
                              name='shadow: ' + x_value + ' ' + y_value,
                              bgcolor='transparent',
                              color_mapper=hsv)
                else:
                    plot.plot((x_value, y_value),
                              type=plot_type, name='shadow: ' + x_value + ' ' + y_value,
                              color=shadowcolors[shadow], bgcolor='transparent', )
        return


class ContextPlotEditor(BasicEditorFactory):

    plot_items = List()
    view_shadows = Bool(True)
    show_all = Bool(False)
    plot_configs = List()  #(PlotConfig)
    klass = _ContextPlotEditor
    orientation = Enum('v', 'h')

    def simple_editor ( self, ui, object, name, description, parent ):
        return self.klass( parent,
                           factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = name,
                           description = description,
                           plot_items  = self.plot_items,
                           view_shadows = self.view_shadows,
                           plot_configs = self.plot_configs,
                           orientation = self.orientation,
                           show_all = self.show_all,
                           )




class ContextPlot(HasTraits):
    context = Instance(IListenableContext, adapt='yes')
    traits_view = View(
                       Item('context', show_label = False,
                            editor=ContextPlotEditor(show_all=True)),
                       width=500, height=500)





if __name__ == '__main__':
    from enthought.contexts.geo_context import GeoContext

    context = GeoContext()
    context['a'] = array([5, 2, 1, 7, 10])
    context['b'] = array([9, 29, 1, 12, 6])

    plot = ContextPlot(context=context)
    plot.edit_traits(kind='modal')
