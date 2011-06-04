import sys, unittest
from numpy import all, arange, array, ndarray

from traits.testing.api import doctest_for_module

from enthought.blocks.api import Block
from enthought.numerical_modeling.numeric_context.context_factory import default_context

class ExecutionTestCase(unittest.TestCase):

    ### Support ###############################################################

    def _base(self, code, expected):
        context = default_context()
        Block(code).execute(context)
        for k in expected:
            self.assert_(k in context)
            if isinstance(expected[k], ndarray) or \
               isinstance(context[k], ndarray):
                self.assert_(all(expected[k] == context[k]),
                             'expected = %s, dict(context) = %s' % \
                                 (expected, dict(context)))
            else:
                self.assertEqual(expected[k], context[k])

    ### Tests #################################################################

    def test_basic(self):
        'Basic'
        self._base('''
from numpy import array
x = array((1,2,3))
''', {'x' : array((1,2,3))})

    def test_assign_3(self):
        "Assign '3'"
        self._base('''
x = 3
''', {'x' : 3})

    def test_assign_none(self):
        "Assign 'None'"
        self._base('''
x = None
''', {'x' : None})

    def test_reassign(self):
        'Re-assignment'

        self._base('''
from numpy import array
x = 1
x = 0
''', {'x' : 0})

        self._base('''
from numpy import array
x = 0
x = array((1,2,3))
''', {'x' : array((1,2,3))})

        self._base('''
from numpy import array
x = array((1,2,3))
x = 0
''', {'x' : 0})

        self._base('''
from numpy import array
x = array((2,3,4))
x = array((1,2,3))
''', {'x' : array((1,2,3))})

    def test_masking_not_nested(self):
        'Masking (not nested)'

        self._base('''
from numpy import array
x = array((0,0,3))
push_mask(x == 0)
x = array((1,2))
pop_mask()
''', {'x' : array((1,2,3))})

        self._base('''
from numpy import array
x = array((1,2,3))
push_mask(x == 2)
x = 0
pop_mask()
''', {'x' : array((1,0,3))})

        self._base('''
from numpy import array
x = array((1,2,3))
push_mask(x == 2)
x = 0
pop_mask()
push_mask(x > 2)
x = 5
pop_mask()
''', {'x' : array((1,0,5))})

        # In a mask, expand unknown scalars into arrays with default fill
        self._base('''
from numpy import arange
samples = arange(5)
push_mask(samples < 2)
x = 3
y = 'a'
pop_mask()
push_mask((2 <= samples) & (samples < 4))
x = 5
pop_mask()
''', { 'x' : array((3,3,5,5,0)),
       'y' : array(('a', 'a', '', '', ''), dtype=object) })

    def foo_masking_nested(self):
        'Masking (nested)'

        self._base('''
from numpy import arange, empty_like
x = arange(10)
y = empty_like(x) * 0
push_mask(x < 5)
y = x
push_mask(y % 2 == 0)
y = y*y
pop_mask()
pop_mask()
''', { 'x' : arange(10), 'y' : array((0,1,4,3,16,0,0,0,0,0)) })

        self._base('''
from numpy import arange
x = arange(5)
push_mask(x < 4)
push_mask(x < 3)
push_mask(x < 2)
push_mask(x < 1)
x = 5
pop_mask()
pop_mask()
pop_mask()
pop_mask()
''', {'x' : array((5,1,2,3,4))})

        self._base('''
from numpy import arange
x = arange(5)
push_mask(x < 4)
push_mask(x < 3)
push_mask(x < 2)
push_mask(x < 1)
y = 5
pop_mask()
pop_mask()
pop_mask()
pop_mask()
''', { 'x' : arange(5), 'y' : array((5,0,0,0,0)) })

if __name__ == '__main__':
    unittest.main(argv=sys.argv)
