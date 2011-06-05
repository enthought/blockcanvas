""" Class for stochastic interactor
"""

# Standard imports
import logging

# Enthought library imports
from traits.api import Button, Enum, Any
from traitsui.api import (Item, View, HGroup, spring, InstanceEditor,
                                     Group)
from traits.util.distribution.distribution import \
     Distribution, Constant, Gaussian, Triangular, Uniform

# Local imports
from editors import int_eval_editor, float_eval_editor
from simple_interactor import SimpleInteractor
from stochastic_item import StochasticItem

# Logger
logger = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
#  StochasticInteractor class
#-------------------------------------------------------------------------------

class StochasticInteractor(SimpleInteractor):

    execute_button = Button('Execute')
    distribution = Enum('constant', 'gaussian', 'triangular', 'uniform')

    #---------------------------------------------------------------------------
    # object interface
    #---------------------------------------------------------------------------

    def trait_view(self, name=None, view_element=None):
        """ Default view; overloading definition in parent class
        """

        return View( Group(*self._view_items() +
                           [HGroup(spring,
                                   Item('execute_button',
                                        show_label=False),
                                   )],
                           **{'show_border' : True}
                           ),
                     id  = 'interactor.StochasticInteractor',
                     width = 800,
                     height = 200,
                     buttons = ['OK'],
                     resizable = True,
                 )

    #---------------------------------------------------------------------------
    #  SimpleInteractor interface
    #---------------------------------------------------------------------------

    ### private methods --------------------------------------------------------

    def _setup_inputs(self):
        """
        """

        for input in self.inputs:
            value = self.context[input]
            if isinstance(value, int) or isinstance(value, float):
                trait_name = self._input_prefix + input
                self.remove_trait(trait_name)
                self.add_trait(trait_name, Any)

                # Check if the distribution parameters have been loaded from
                # a file; else assign them default values.
                if self.distribution == 'constant':
                    if self.ranges.has_key(input):
                        distribution = Constant(value = self.ranges[input][0])
                    else:
                        distribution = Constant(value = value)

                elif self.distribution == 'gaussian':
                    if self.ranges.has_key(input):
                        distribution = Gaussian(mean = self.ranges[input][0],
                                                std = self.ranges[input][1])
                    else:
                        distribution = Gaussian(mean = value, std = 2.0)

                elif self.distribution == 'triangular':
                    if self.ranges.has_key(input):
                        distribution = Triangular(mode = self.ranges[input][0],
                                                  low = self.ranges[input][1],
                                                  high = self.ranges[input][2])
                    else:
                        distribution = Triangular(mode = value,
                                                  low = value-2,
                                                  high = value+2)
                else:
                    if self.ranges.has_key(input):
                        distribution = Uniform(low = self.ranges[input][0],
                                               high = self.ranges[input][1])
                    else:
                        distribution = Uniform(low = value, high = value+2)

                # Add a stochastic item as an attribute.
                s_item = StochasticItem(name = trait_name,
                                        distribution = distribution)
                setattr(self, trait_name, s_item)

        return


    def _view_items(self):
        """ Overloading defintion in simple-interactor, for building a view
            given inputs.
        """

        items = []

        self._setup_inputs()
        for input in self.inputs:
            trait_name = self._input_prefix + input
            if hasattr(self, trait_name):
                items.append(Item(trait_name, style='custom', label=input,
                                  editor=InstanceEditor()))

        return items


    def _anytrait_changed(self, name, old, new):
        """ Overloading the defintion in SimpleInteractor
        """
        pass


    #---------------------------------------------------------------------------
    #  StochasticInteractor Interface
    #---------------------------------------------------------------------------

    ### private methods --------------------------------------------------------

    def _execute_button_changed(self):
        """ Execute stochastic process.
        """

        # XXX: this needs to be converted to a non-shadow based execution (or
        # shadows need to be reinstated).
        raise NotImplementedError

        # Obtain a list of tuple of shadows; and the input causing its creation
        shadow_list = []

        # Obtain seeds for running the stochastic process in a distributing
        # computing environment in future.
        seeds = {}
        results = { '_seeds': seeds }

        # Create shadow contexts
        for input in self.inputs:
            trait_name = self._input_prefix + input
            if hasattr(self, trait_name):
                distribution = getattr(self, trait_name).distribution
                values = distribution.values
                seeds[trait_name] = distribution.set_state(None)
                for val in values:
                    shadow = self.context.create_shadow(input, val)
                    shadow_list.append((input, shadow))

        # Restrict the block to the variable, and use the shadow context
        for shadow in shadow_list:
            self.block.restrict(inputs = [shadow[0]])
            self.block.execute(shadow[1])

        return

    ### public methods --------------------------------------------------------

    def extract_range_dict(self):
        """ Return a dictionary with ranges of inputs

            Returns:
            --------
            range_dict: Dict
               e.g. {'a': (<a_low>, <a_high>)}

        """

        range_dict = {}
        list_inputs = [name for name in self.editable_traits()
                       if self._input_prefix in name]
        attr_dict = { 'constant': ['value'],
                      'gaussian': ['mean', 'std'],
                      'triangular': ['mode', 'low', 'high'],
                      'uniform': ['low', 'high']
            }

        # Ranges should include parameters of the distribution.
        for name in list_inputs:
            stochastic_item = getattr(self, name)
            input_name = name[name.find('_')+1:]
            dist_val = stochastic_item.distribution
            value_list = []
            for attr_name in attr_dict[self.distribution]:
                value_list.append(getattr(dist_val, attr_name))
            range_dict[input_name] = tuple(value_list)

        return range_dict


# Test
if __name__ == '__main__':
    from blockcanvas.numerical_modeling.workflow.api import Block
    from codetools.contexts.api import DataContext, MultiContext

    code = "from blockcanvas.debug.my_operator import add, mul\n"\
           "c = add(a,b)\n"\
           "d = mul(c,2)\n"\
           "e = mul(z,3)\n"\
           "f = add(d,e)"
    block = Block(code)
    context = MultiContext(DataContext(name='Data'), {})
    context['a'] = 35
    context['b'] = 33
    context['z'] = 30

    interactor = StochasticInteractor(context=context, block=block,
                                      inputs=['b','z'], distribution='gaussian')
    interactor.edit_traits(kind='livemodal')

### EOF ------------------------------------------------------------------------
