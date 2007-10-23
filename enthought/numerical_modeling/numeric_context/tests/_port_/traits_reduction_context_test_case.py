# Standard Library Imports
import unittest
import timeit

# Geo Library imports
from geo.context.api import NumericContext, ReductionContext, TraitsContext
from abstract_context_test_case import AbstractContextTestCase

class TraitsReductionContextTestCase(AbstractContextTestCase):

    ############################################################################
    # AbstactContextTestCase interface
    ############################################################################

    def context_factory(self, *args, **kw):
        """ Return the type of context we are testing.
        """
        return TraitsContext( ReductionContext( NumericContext(*args, **kw) ) )

    def matched_input_output_pair(self):
        """ Return values for testing dictionary get/set, etc.
        """
        return 1.2, 1.2

    ############################################################################
    # TraitsReductionContextTestCase interface
    ############################################################################

    # TODO Re-enable when we start watching efficiency
    def HIDE_test_eval_is_not_slow(self):
        """ eval() with DataContext is the speed of a dict. (slowdown < 2.0)

            This is test using a vp array with 20 values in it to try and get
            a reasonable use case.
        """

        ### Parameters ########################################################

        # Slowdown we will allow compared to standard python evaluation
        allowed_slowdown = 2.0

        # Number of timer iterations.
        N = 10000

        ### Standard execution ################################################
        setup = "from numpy import arange\n" \
                "vp=arange(20.)\n"
        expr = 'vp+vp+vp+vp+vp+vp'
        std = timeit.Timer(expr, setup)
        std_res = std.timeit(N)

        ### Eval execution ####################################################
        # Note: This is not used, but it is here for reference
        #
        # eval is actually slower (by an order or so of magnitude for single
        # numbers) than a simple expression.  But for our array, it should be
        # about the same speed.
        compiled_setup = "compiled_expr = compile('%s','expr','eval')\n" % expr
        eval_setup = setup + compiled_setup
        eval_expr = "eval(compiled_expr)"
        eval_timer = timeit.Timer(eval_expr, eval_setup)
        eval_res = eval_timer.timeit(N)

        ### NumericContext execution #############################################
        this_setup = "from geo.context.api import NumericContext, ReductionContext, TraitsContext\n" \
                     "context=TraitsContext(ReductionContext(NumericContext()))\n" \
                     "context['vp'] = vp\n"
        context_setup = setup + this_setup + compiled_setup
        context_expr = "eval(compiled_expr, globals(), context)"
        context_timer = timeit.Timer(context_expr, context_setup)
        context_res = context_timer.timeit(N)

        slowdown = context_res/std_res
        msg = 'actual slowdown: %f' % slowdown
        assert slowdown < allowed_slowdown, msg

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
