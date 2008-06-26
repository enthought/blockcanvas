# Standard library imports
from cPickle import dump, load
from math import log10, ceil
import numpy

# ETS imports
from enthought.traits.api import Any, Enum, Float, HasTraits, Int, Str, Trait
from enthought.traits.ui.api import (View, Item, Group, HGroup, TextEditor,
    RangeEditor, InstanceEditor, ViewHandler)
from enthought.numerical_modeling.units.unit_scalar import UnitScalar

# Local imports
from editors import array_eval_editor
from simple_interactor import SimpleInteractor


class ShadowInteractor(SimpleInteractor):
    """ Simple interactor for a single shadow
    """

    def _view_items(self):
        items = []
        self._setup_inputs()

        for input in self.inputs:
            trait_name = self._input_prefix + input

            value = self.context[input]
            if isinstance(value, UnitScalar):
                value = value.tolist()

            if isinstance(value, int):
                if self.ranges.has_key(input):
                    low_range, high_range = self.ranges[input]
                else:
                    low_range, high_range = int(value-10), int(value+10)
                for name, value in ((trait_name+'__low', low_range),
                                    (trait_name+'__high', high_range)):
                    self.add_trait(name, Int)
                    setattr(self, name, value)
                item = HGroup(Item(name   = trait_name,
                                   label  = input,
                                   editor = RangeEditor(low_name=trait_name+'__low',
                                                        high_name=trait_name+'__high',
                                                        format='%d',
                                                        is_float=False,
                                                       ),
                                   springy = True,
                                   ),
                              Item(trait_name + '__low', label='Low', width=-30),
                              Item(trait_name + '__high', label='High', width=-30),
                             )

            elif isinstance(value, float):
                if self.ranges.has_key(input):
                    low_range, high_range = self.ranges[input]
                else:
                    low_range, high_range = self._get_default_ranges(value)
                for name, value in ((trait_name + '__low', low_range),
                                    (trait_name + '__high', high_range)):
                    self.add_trait(name, Float)
                    setattr(self, name, value)
                item = HGroup(Item(name   = trait_name,
                                   label  = input,
                                   editor = RangeEditor(low_name=trait_name+'__low',
                                                        high_name=trait_name+'__high',
                                                       ),
                                   springy = True,
                                   ),
                              Item(trait_name + '__low', label='Low', width=-30),
                              Item(trait_name + '__high', label='High', width=-30),
                             )

            elif isinstance(value, basestring):
                item = Item(name   = trait_name,
                            label  = input,
                            editor = TextEditor(auto_set=False, enter_set=True),
                            _type = 'String',
                )
            elif isinstance(value, numpy.ndarray):
                item = Item(name   = trait_name,
                            label  = input,
                            editor = array_eval_editor,
                            _type = 'Array',
                )
            else:
                item = Item(name=trait_name)

            items.append(item)
        return items

    def _get_default_ranges(self, value):
        if abs(value) > 10.0:
            oom = log10(abs(value))
            low_range = value - 10**(oom+1)
            high_range = value + 10**(oom+1)
        else:
            low_range, high_range = -10.0, 10.0
        return low_range, high_range

    def extract_range_dict(self):
        """ Return a dictionary with ranges of inputs

            Returns:
            --------
            range_dict: Dict
                e.g. : {'a': (<a_low>, <a_high>)}
        """

        range_dict = {}
        list_range = [name for name in self.editable_traits()
                     if '__high' in name or '__low' in name]
        list_inputs = [name for name in self.editable_traits()
                       if self._input_prefix in name and not name in
                       list_range]

        # Ranges should include values for low and high.
        for name in list_inputs:
            if name+'__high' in list_range and \
                name+'__low' in list_range:
                input_name = name[name.find('_')+1:]
                range_dict[input_name] = (getattr(self, name+'__low'),
                                          getattr(self, name+'__high'))

        return range_dict


def round_two_places(value):
    scale = pow(10, ceil(log10(value)))
    return scale*(round(value/scale, 2))

def new_main():
    from enthought.contexts.api import DataContext
    from enthought.block_canvas.app.experiment import Experiment
    
    code2 = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
           "c = mul(a,b)\n" \
           "d = mul(c, 2)\n" \
           "e = mul(c, 3)\n" \
           "f = add(d,e)"
    context = DataContext(name='data')
    context.update(dict(a=2, b=3))
    exp = Experiment(code=code2, shared_context=context)

    interactor = ShadowInteractor(inputs=exp.exec_model.block.inputs, context=exp.context)
    interactor.configure_traits()
    from pprint import pprint

    print "***** Experiment executing context *****"
    pprint(exp.context.items())

    print "\n***** Shared context *****"
    pprint(context.items())


if __name__ == "__main__":
    import logging
    logging.basicConfig()
    new_main()
