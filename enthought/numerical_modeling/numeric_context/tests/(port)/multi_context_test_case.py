# Standard library imports
import unittest
import timeit

# Enthought library imports
from enthought.traits.api import Any

# Geo library imports
from abstract_context_test_case import AbstractContextTestCase
from geo.context.api import MultiContext, DataContext

class MultiContextTestCase(AbstractContextTestCase):

    ############################################################################
    # AbstractContextTestCase interface
    ############################################################################

    def context_factory(self, *args, **kw):
        """ Return the type of context we are testing.
        """
        return MultiContext(DataContext(*args, **kw))

    def matched_input_output_pair(self):
        """ Return values for testing dictionary get/set, etc.
        """
        return 1.2, 1.2

    ############################################################################
    # MultiContextTestCase interface
    ############################################################################

    def test_set_rebind_between_contexts(self):
        """ Can we rebind variables between contained contexts?
        """

        class C(DataContext):
            f = Any
            def __init__(self, f):
                super(C, self).__init__(f=f)
            def allows(self, value, name):
                return self.f(value, name)

        # `allows' predicates
        all = lambda v,n: True
        none = lambda v,n: False
        positive = lambda v,n: v > 0
        negative = lambda v,n: v < 0

        # Make a multi-context where the top context only accepts positive
        # numbers and the next one accepts anything. For robustness, add some
        # noise below.
        multi = MultiContext(C(positive), C(all),
                             C(all), C(none), C(negative)) # Noise
        [upper, lower] = multi.contexts[0:2]

        for a,b in [(3,8), (3,-8), (-3,8), (-3,-8)]:

            # Bind and rebind 'x'
            multi['x'] = a
            multi['x'] = b

            # 'x' should have the latter binding
            self.assertEqual(multi['x'], b)

            # 'x' shouldn't have multiple bindings
            self.assertEqual(1, sum([ int('x' in c) for c in multi.contexts ]))

            # 'x' should live in the upper context if it's positive, else in
            # the lower one
            if multi['x'] > 0:
                self.assertTrue('x' in upper)
            else:
                self.assertTrue('x' in lower)

    def test_eval_is_not_slow(self):
        """ eval() with DataContext is the speed of a dict. (slowdown < 1.2)

            x is currently set at 1.3 (see allowable_slowdown below)

            This is test using a vp array with 20 values in it to try and get
            a reasonable use case.
        """

        ### Parameters #########################################################

        # Slowdown we will allow compared to standard python evaluation
        allowed_slowdown = 1.2

        # Number of timer iterations.
        N = 10000

        ### Standard execution #################################################
        setup = "from numpy import arange\n" \
                "vp=arange(20.)\n"
        expr = 'vp+vp+vp+vp+vp+vp'
        std = timeit.Timer(expr, setup)
        std_res = std.timeit(N)

        ### Eval execution #####################################################
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

        ### DataContext execution ##############################################
        this_setup = "from geo.context.api import MultiContext\n" \
                     "context=MultiContext()\n" \
                     "context['vp'] = vp\n"
        context_setup = setup + this_setup + compiled_setup
        context_expr = "eval(compiled_expr, globals(), context)"
        context_timer = timeit.Timer(context_expr, context_setup)
        context_res = eval_timer.timeit(N)

        slowdown = context_res/std_res
        msg = 'actual slowdown: %f' % slowdown
        assert slowdown < allowed_slowdown, msg

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
