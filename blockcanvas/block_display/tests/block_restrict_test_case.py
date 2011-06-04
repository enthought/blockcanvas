import unittest

# ETS imports
from enthought.blocks.api import Block

# application imports
from enthought.contexts.api import DataContext

class BlockRestrictestCase(unittest.TestCase):
    """ Block restriction is tested in the numerical_modeling code, these
        tests are meant to test the interaction with other components
    """

    def test_simple_output_reduction(self):
        code = 'from enthought.block_canvas.debug.my_operator import add, mul\n' \
                'c = add(a,b)\n' \
                'd = mul(a,16)\n'

        block = Block(code)

        context = DataContext()
        context['a'] = 1
        context['b'] = 2

        sub_block = block.restrict(outputs=('d'))
        self.assertEqual(sub_block.inputs, set(['a']))

        sub_block.execute(context)
        self.assertTrue(context.has_key('d'))
        self.assertEqual(context['d'], 16)

    def test_dependent_output_reduction(self):
        code = 'from enthought.block_canvas.debug.my_operator import add, mul\n' \
                'c = add(a,b)\n' \
                'd = mul(c,16)\n'

        block = Block(code)

        context = DataContext()
        context['a'] = 1
        context['b'] = 2

        sub_block = block.restrict(outputs=('d'))
        self.assertEqual(sub_block.inputs, set(['a', 'b']))

        sub_block.execute(context)
        self.assertTrue(context.has_key('c'))
        self.assertEqual(context['c'], 3)
        self.assertTrue(context.has_key('d'))
        self.assertEqual(context['d'], 48)

    def test_unbound_inputs(self):
        code = 'from enthought.block_canvas.debug.my_operator import add, mul\n' \
               "c = add(a,b)\n" \
               "d = mul(c,a)\n" \
               "z = add(b, 2)"

        block = Block(code)

        context = DataContext()
        context['a'] = 2
        context['b'] = 1

        sub_block = block.restrict(inputs=('a'))
        self.assertEqual(sub_block.inputs, set(['a', 'b']))
        self.assertEqual(sub_block.outputs, set(['c', 'd', 'add', 'mul']))

        sub_block.execute(context)
        self.assertTrue(context.has_key('c'))
        self.assertEqual(context['c'], 3)
        self.assertTrue(context.has_key('d'))
        self.assertEqual(context['d'], 6)


    def test_bound_inputs(self):
        code = "c = a * b\n" \
               "x = 3 + c\n"

        block = Block(code)

        context = DataContext()
        context['a'] = 1
        context['b'] = 2

        sub_block = block.restrict(inputs=('c'))
        self.assertEqual(sub_block.inputs, set(['c']))

if __name__ == '__main__':
    unittest.main()
