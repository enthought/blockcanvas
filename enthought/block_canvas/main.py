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
from enthought.blocks.api import Block
from enthought.etsconfig.api import ETSConfig
from enthought.logger.api import add_log_queue_handler, create_log_file_handler

# Local imports
from enthought.block_canvas.app.block_application import BlockApplication
from enthought.contexts.data_context import DataContext

def initialize_logger():
    import logging
    import sys
    logfiledir = os.path.join(ETSConfig.application_data, 'block_canvas')
    if not os.path.exists(logfiledir):
        os.mkdir(logfiledir)
    logfile = os.path.join(logfiledir, 'ets.log')
    root = logging.getLogger()
    root.addHandler(create_log_file_handler(logfile))
    add_log_queue_handler(root)

    root.info("     ************************************************")
    root.info("     **     Enthought BlockCanvas app")
    root.info("     **       file: %s" % os.path.abspath(__file__))
    root.info("     **       args: %s" % sys.argv[1:])
    root.info("     ************************************************")


def load_vars(filename):
    g = globals()
    execfile(filename, g)
    code = g['code']
    context = g['context']

    return code, context

def hardcode_vars():

    ### Setup execution block ###############################################
    # Context setup.
    context = DataContext(name='Data')
    context['a'] = 0.5
    context['b'] = 3.0
    context['c'] = 4.0
    """
    context.defer_events = True
    x = arange(0,10,.01)
    context['a'] = 1.0
    context['b'] = array([1, 2, 3])
    context['c'] = array([4, 5, 6])
    context.defer_events = False
    """
    context.defer_events = False

    code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
           "from numpy import arange\n" \
           "x = arange(0,10,.1)\n" \
           "c1 = mul(a,a)\n" \
           "x1 = mul(x,x)\n" \
           "t1 = mul(c1,x1)\n" \
           "t2 = mul(b, x)\n" \
           "t3 = add(t1,t2)\n" \
           "y = add(t3,c)\n"

    return code, context

def main(code, context):
    initialize_logger()
    d = BlockApplication(code=code, context=context)

    ### Start the GUI  ######################################################
    d.configure_traits()

    # Persist the block
    # Note: set the file_path earlier in the code.
#    d.block_unit.save_block_to_file(file_path)

if __name__ == "__main__":
    import sys, os.path
    # fixme: This code only works on platforms for which a wx.GCDC context is
    # defined...
    #from enthought.traits.ui.dock_window_theme \
    #    import dock_window_theme, button_dock_window_theme
    #    
    #dock_window_theme( button_dock_window_theme )
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        code, context = load_vars(sys.argv[1])
    else:
        code, context = hardcode_vars()

    main(code, context)
    
### EOF #####################################################################
