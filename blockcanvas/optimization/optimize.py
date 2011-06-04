from numpy import zeros, arange

# Enthought library imports
from traits.api import HasTraits, Instance, Str, Int, Float, List
from traitsui.api import View, Item, TableEditor
from enthought.blocks.api import Block
from enthought.contexts.parametric_context import ShadowContext
from enthought.contexts.parametric_context import ParametricContext

from enthought.contexts.data_context import DataContext
from enthought.block_canvas.cobyla2c.cobyla import minimize
from enthought.greenlet import greenlet
from enthought.block_canvas.plot.configurable_context_plot import ConfigurableContextPlot
from enthought.block_canvas.interactor.interactor_config import PlotConfig
from enthought.block_canvas.plot.context_plot import ContextPlotEditor
from traitsui.table_column import ObjectColumn

# FIXME this has many limitations -- mostly realted to dealing with only
# one variable at a time

class InputOptimizationVariable(HasTraits):
    name = Str
    min = Float
    max = Float

    traits_view = View(Item('name'),
                       Item('min'),
                       Item('max')
                       )

#class ConstraintOptimizationVariable():


class Optimizer(HasTraits):

    context = Instance(ParametricContext)
    block = Instance(Block)
    objective_var = Str
#    constraint_vars = List(ConstraintOptimizationVariable)
    constraint_var = Str
    input_vars = List(InputOptimizationVariable)
    _working_context = Instance(DataContext)

    inputs_table_editor = TableEditor(columns=[ObjectColumn(name='name'),
                                               ObjectColumn(name='min'),
                                               ObjectColumn(name='max')],
                                      editable=True,
                                      deletable=True,
                                      row_factory=InputOptimizationVariable,
                                      )
    traits_view = View(Item('objective_var'),
                       Item('constraint_var',),
                       Item('input_vars', editor=inputs_table_editor),
                       buttons=['OK', 'Cancel'],
                       close_result=False,
                       width=500,
                       height=500,
                       resizable=True
                       )
    def optimize(self):
        input_var_names = [var_obj.name for var_obj in self.input_vars]

        # FIXME: Do we want to create shadows with multiple names?
        self._working_context = self.context.create_shadow(input_var_names[0])
        for var_name in input_var_names:
            self._working_context[var_name] = self.context[var_name][:]
        sub_block = self.block.restrict(inputs=input_var_names,
                                        outputs=[self.objective_var, self.constraint_var])
        input_len = len(self._working_context[input_var_names[0]])
        cobyla_instances = [COBYLAInstance(index=i, optimizer=self) for \
                            i in range(input_len)]
        greenlet_list = [greenlet(cobyla_instance.minimize_at_index) for \
                         cobyla_instance in cobyla_instances]
        self.cobyla_status_arr = zeros(input_len, dtype=bool)
        active_greenlets = input_len
        while active_greenlets > 0:
            active_greenlets = 0
            for greenlet_inst in greenlet_list:
                if not greenlet_inst.dead:
                    active_greenlets += 1
                    greenlet_inst.switch()
            sub_block.execute(self._working_context)

        self.context['plot_index'] = arange(input_len)
        input_plots = [PlotConfig(number=plot_num, x = 'plot_index', y=var_name, type='Line') for \
                       plot_num, var_name in enumerate(input_var_names)]


        plot_configs = input_plots + [
                        PlotConfig(number=len(input_var_names), x='plot_index', y=self.objective_var, type='Line'),
                        PlotConfig(number=len(input_var_names) + 1, x='plot_index', y=self.constraint_var, type='Line'),]

        result_view = View(Item('context',
                                editor=ContextPlotEditor(#view_shadows=True,
                                                         plot_configs=plot_configs,
                                                         ),
                                show_label=False),
                            width=500,
                            height=500,
                            resizable=True)
        self.edit_traits(view=result_view, kind='modal')

        return



class COBYLAInstance(HasTraits):
    # The index in the array to be optimized that this instance refers to
    index = Int()
    # A back reference to the overall optimizer
    optimizer = Instance(Optimizer)

    def minimize_at_index(self):
        context = self.optimizer._working_context
        input_vars = [var_obj.name for var_obj in self.optimizer.input_vars]
        input_upper_bounds = [var_obj.max for var_obj in self.optimizer.input_vars]
        input_lower_bounds = [var_obj.min for var_obj in self.optimizer.input_vars]

        result = minimize(self.objective_func,
                          [context[input_var][self.index] for input_var in input_vars],
                          low = input_lower_bounds,
                          up = input_upper_bounds,
                          )
        for var_index, var_name in enumerate(input_vars):
            context[var_name][self.index] = result[2][var_index]



    def objective_func(self, x):
        optimizer = self.optimizer
        context = optimizer._working_context
        index = self.index
        for var_index in range(len(optimizer.input_vars)):
            context[optimizer.input_vars[var_index].name][index] = x[var_index]
        greenlet.getcurrent().parent.switch()
        return (context[optimizer.objective_var][index],
                [context[optimizer.constraint_var][index]])
