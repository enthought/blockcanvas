import unittest

from blockcanvas.interactor.simple_interactor import SimpleInteractor
from enthought.contexts.api import DataContext
from enthought.blocks.api import Block

class SimpleInteractorTestCase(unittest.TestCase):

    def setUp(self):
        # Context setup.
        self.context = DataContext(name='Data')
        self.context['a'] = 1
        self.context['b'] = 2
        self.inputs = ['a', 'b']

    def test_specific_inputs(self):
        """ Test the interactor does add attributes for the inputs
        """
        self.context = DataContext(name='Data')
        self.context['a'] = 1
        self.context['b'] = 2
        self.context['c'] = 3
        self.context['d'] = 4
        self.context['e'] = 5

        interactor = SimpleInteractor(['a', 'd', 'e'], context=self.context)

        self.assertTrue(hasattr(interactor, interactor._input_prefix + "a"))
        self.assertTrue(hasattr(interactor, interactor._input_prefix + "d"))
        self.assertTrue(hasattr(interactor, interactor._input_prefix + "e"))
        self.assertFalse(hasattr(interactor, interactor._input_prefix + "c"))
        self.assertFalse(hasattr(interactor, interactor._input_prefix + "b"))

    def test_input_change(self):
        """ Test that a change made to the interactor appears in the
            context as well
        """
        interactor = SimpleInteractor(self.inputs, context=self.context)
        interactor.input_a = 4

        self.assertEqual(interactor.input_a, 4)
        self.assertEqual(self.context['a'], 4)

