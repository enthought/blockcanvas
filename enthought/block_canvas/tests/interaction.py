""" Define some domain specific values to load into a Block Application.

    This example loads a set of library functions into the search
    tool, and a simple set of add/mul instructions into the block to start
    with.
"""

# Enable the trace() function that is handy as a replacement for print
try:
    from enthought.block_canvas.debug.injectrace import trace
except ImportError:
    pass
import os

# Enthought library imports
from enthought.numerical_modeling.workflow.block.api import Block

# Local imports
from enthought.block_canvas.app.block_application import BlockApplication
from enthought.block_canvas.block_display.block_unit import BlockUnit
from enthought.block_canvas.function_tools.handled_function_search import HandledFunctionSearch
from enthought.block_canvas.function_tools.function_library import Module

from enthought.block_canvas.context.data_context import DataContext


def main():

    # Search boxes for finding functions to place on module.
    function_search = HandledFunctionSearch()

    ### Setup execution block ###############################################
    # Context setup.
    context = DataContext(name='Data')
    context['a'] = 1.0
    context.defer_events = False

    ### Setup the main application object ###################################
    # Reload from a file
    # Note: test case for block persistence, set the file_path to '' if
    # persistence need not be tested
    file_path = ''

    if not os.path.isfile(file_path):
        code = "from numpy import arange\n" \
               "b=3\n" \
               "c=4\n" \
               "x = arange(0,10,.1)\n" \
               "y = a*x**2 + b*x + c\n"

        bu = BlockUnit(code=code,
                      data_context=context)
    else:
        bu = BlockUnit(data_context=context)
        bu.load_block_from_file(file_path)

    def loop_interactor(interactor):
        import time
        import numpy
        time.sleep(1)
        
        for i in range(1,100):
            interactor.interactor_shadow.input_a = numpy.sin(i/10)
            time.sleep(0.1)

        print "done"
        import sys
        sys.exit(0)


    from enthought.block_canvas.interactor.configurable_interactor import ConfigurableInteractor
    from enthought.block_canvas.interactor.shadow_interactor import ShadowInteractor
    from enthought.block_canvas.interactor.interactor_config import PlotConfig, InteractorConfig, VariableConfig
    from enthought.block_canvas.plot.configurable_context_plot import ConfigurableContextPlot
    from enthought.block_canvas.block_display.block_unit_variables import \
            BlockUnitVariableList
    from threading import Thread
    
    vars = BlockUnitVariableList(block = bu.codeblock.block, 
                                 context = bu._exec_context)
    config = InteractorConfig(vars = vars.variables, 
                              var_configs=[VariableConfig(name='a', type="Shadow")],
                              plot_configs=[PlotConfig(x='x', y='y')])
    interactor = ConfigurableInteractor(context = bu._exec_context, 
                                        block = bu.codeblock.block,
                                        interactor_config = config)
    
#    Thread(target=loop_interactor, args=(interactor,)).start()
    interactor.edit_traits(kind='livemodal')


if __name__ == "__main__":
    import cProfile
    import pstats

    main()

#    cProfile.run('main()', 'tmp.prof')
#    s = pstats.Stats('tmp.prof')
#    s.sort_stats('time')
#    s.print_stats(100, 'block')
#    s.print_stats(100, 'wx')

### EOF #####################################################################
