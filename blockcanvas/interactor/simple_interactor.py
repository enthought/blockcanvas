""" The most basic interactor possible
"""

# Standard library imports
import numpy

# ETS imports
from traits.api import (Any, Dict, HasTraits, Instance, List,
        on_trait_change)
from traitsui.api import View, Item, Group, TextEditor

# Block Canvas imports
from codetools.contexts.api import IListenableContext
from blockcanvas.block_display.execution_model import ExecutionModel

# Local imports
from editors import int_eval_editor, float_eval_editor, array_eval_editor


class SimpleInteractor(HasTraits):
    """ The most basic interactor possible.

        Provides a UI for modifying a block's input values.

        Note: This class does not force the block to execute when the context
        changes, that is someone elses responibility.
    """

    context = Instance(IListenableContext, adapt='yes')
    inputs = List()
    ranges = Dict()

    _input_prefix = "input_"

    def __init__(self, inputs=[], **kw):
        super(SimpleInteractor, self).__init__(**kw)
        self.inputs = list(inputs)
        self._setup_inputs()


    def trait_view(self, name=None, view_element=None):

        return View( Group(*self._view_items()),
                     id        = "interactor.SimpleInterator",
#                     title     = "Simple Interactor",
                     width     = 400,
                     height    = 200,
                     buttons   = ["OK"],
                     resizable = True )

    def _setup_inputs(self):
        for input in self.inputs:
            trait_name = self._input_prefix + input
            self.remove_trait(trait_name)
            self.add_trait(trait_name, Any)
            setattr(self, trait_name, self.context[input])


    def _view_items(self):
        items = []
        self._setup_inputs()

        for input in self.inputs:
            trait_name = self._input_prefix + input

            value = self.context[input]
            if isinstance(value, int):
                item = Item(name   = trait_name,
                            label  = input,
                            editor = int_eval_editor)
            elif isinstance(value, float):
                item = Item(name   = trait_name,
                            label  = input,
                            editor = float_eval_editor)
            elif isinstance(value, basestring):
                item = Item(name   = trait_name,
                            label  = input,
                            editor = TextEditor(auto_set=False, enter_set=True))
            elif isinstance(value, numpy.ndarray):
                item = Item(name   = trait_name,
                            label  = input,
                            editor = array_eval_editor)
            else:
                item = Item(name=trait_name)

            items.append(item)

        return items

    def _anytrait_changed(self, name, old, new):
        if name.startswith(self._input_prefix):
            name = name[len(self._input_prefix):]
            self.context[name] = new


if __name__ == "__main__":
    code = "from blockcanvas.debug.my_operator import add, mul\n" \
           "c = add(a,b)\n" \
           "d = mul(c, 2)\n" \
           "e = mul(c, 3)\n" \
           "f = add(d,e)"

    # Experiment setup.
    from codetools.contexts.api import DataContext
    from blockcanvas.app.experiment import Experiment
    context = DataContext(name='Data')
    context['a'] = 1
    context['b'] = 2

    exp = Experiment(code=code, shared_context=context)

    interactor = SimpleInteractor(inputs=exp.exec_model.block.inputs,
                                  context = exp.context)
    interactor.configure_traits()

    from pprint import pprint
    pprint(exp.context.items())
