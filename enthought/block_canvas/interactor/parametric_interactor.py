""" Class for parametric interactor

    1. It should display all keys of the context with a Low-High-Step to be
        filled up.
    2. Changes in these boxes should create appropriate shadows in the
        parametric context.

"""

# Standard imports
import logging

# ETS imports
from enthought.traits.api import Instance, Any, Button
from enthought.traits.ui.api import (Item, InstanceEditor, View, HGroup, Group,
                                     spring)

# Application imports
from enthought.contexts.i_context import IListenableContext

# Local imports
from parametric_item import ParametricItem
from simple_interactor import SimpleInteractor
from utils import add_list_to_listed_list

# Logger
logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
#  ParametricInteractor class
#-------------------------------------------------------------------------------

class ParametricInteractor(SimpleInteractor):

    update_contexts_button = Button('Create shadow contexts')
    context = Instance(IListenableContext, adapt='yes')

    #---------------------------------------------------------------------------
    #  object interface
    #---------------------------------------------------------------------------

    def trait_view(self, name=None, view_element=None):
        """ Default view; overloading SimpleInteractor method.
        """

        return View( Group(*self._view_items() +
                           [HGroup(spring,
                                   Item('update_contexts_button',
                                        show_label=False),
                                    )],
                           **{'show_border': True}
                           ),
                     id        = "interactor.ParametricInterator",
                     width     = 400,
                     height    = 200,
                     buttons   = ["OK"],
                     resizable = True
                )


    #---------------------------------------------------------------------------
    #  SimpleInteractor interface
    #---------------------------------------------------------------------------

    ### private methods --------------------------------------------------------

    def _setup_inputs(self):
        """ Overloading the method in SimpleInteractor to store ParametricItems
            for each block input.

        """

        for input in self.inputs:
            trait_name = self._input_prefix + input
            self.remove_trait(trait_name)
            self.add_trait(trait_name, Any)

            value = ParametricItem(input_value=self.context[input], name=input)
            if self.ranges.has_key(input):
                value.high = self.ranges[input][1]
                value.low = self.ranges[input][0]
                if len(self.ranges[input]) == 3:
                    value.step = self.ranges[input][2]
            setattr(self, trait_name, value)
        return


    def _view_items(self):
        """ Overloading the method in SimpleInteractor for return view
        """

        items = []
        self._setup_inputs()

        for input in self.inputs:
            trait_name = self._input_prefix + input
            items.append(Item(trait_name, style='custom',label=input,
                              editor=InstanceEditor()))

        return items


    def _anytrait_changed(self, name, old, new):
        """ Overloading the method in SimpleInteractor
        """
        pass


    #---------------------------------------------------------------------------
    #  ParametricInteractor Interface
    #---------------------------------------------------------------------------

    ### private methods --------------------------------------------------------

    def _update_contexts_button_changed(self):
        """ Batch updating of contexts.
        """
        # XXX: this needs to be converted to a non-shadow based execution (or
        # shadows need to be reinstated).
        raise NotImplementedError

        # Create all combinations possible for the context
        list_of_lists = []
        for i in range(len(self.inputs)):
            trait = getattr(self, self._input_prefix+ self.inputs[i])
            list_of_lists = add_list_to_listed_list(trait.output_list,
                                                    list_of_lists)

        # Make a shadow context for each of the combinations
        for list in list_of_lists:
            dict = {}
            count = 0
            for i in range(len(self.inputs)):
                trait = getattr(self, self._input_prefix+self.inputs[i])
                if len(trait.output_list):
                    dict[self.inputs[i]] = list[count]
                    count = count+1

            if len(dict):
                self.context.create_shadow(dict)

                # Trigger event to draw plot
                key = dict.keys()[0]
                self.context.shadows[-1][key] = dict[key]

        # Log a message on the number of shadows created.
        logger.debug('ParametricInteractor: Created %d shadows' %
                     len(list_of_lists))
        return


    ### public methods ---------------------------------------------------------

    def extract_range_dict(self):
        """ Return a dictionary with ranges of inputs

            Returns:
            --------
            range_dict: Dict
                e.g. : {'a': (<a_low>, <a_high>)}

        """

        range_dict = {}
        list_inputs = [name for name in self.editable_traits()
                       if self._input_prefix in name]

        # Ranges should include values for low, high and step.
        for name in list_inputs:
            parametric_item = getattr(self, name)
            input_name = name[name.find('_')+1:]
            range_dict[input_name] = (parametric_item.low,
                                      parametric_item.high,
                                      parametric_item.step)


        return range_dict


# Test
if __name__ == '__main__':
    from enthought.blocks.api import Block
    from enthought.contexts.api import DataContext, MultiContext
#    from context.api import GeoContext
#    from enthought.numerical_modeling.units.api import UnitArray
#    from enthought.units.length import meter

    code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
           "c = add(a,b)\n" \
           "d = mul(c, 2)\n" \
           "e = mul(c, 3)\n" \
           "f = add(d,e)"

    block=Block(code)

#    context = ParametricContext(GeoContext(), {})
#    context['a'] = UnitArray((1,2,3), units=meter)
#    context['b'] = UnitArray((2,3,4), units=meter)
#
#    interactor = ParametricInteractor(context=context, block = block)
#    interactor.configure_traits()

    # Context setup.
    context = MultiContext(DataContext(name='Data'),{})
    context['a'] = 1
    context['b'] = 2

    interactor = ParametricInteractor(context=context, block = block)
    interactor.configure_traits()

    for shadow in context.shadows:
        block.execute(shadow)
        print shadow['f'], 'Check with:', 5*(shadow['a']+shadow['b'])

### EOF ------------------------------------------------------------------------
