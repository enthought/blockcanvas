""" ParametricItem class defines an item for parametric-interactor.

    It is used for displaying the input values of a context.

"""

# Standard imports
import numpy

# ETS imports
from enthought.numerical_modeling.units.unit_scalar import UnitScalar
from enthought.traits.api import HasTraits, Str, Any, List
from enthought.traits.ui.api import View, Item, HGroup

# Local imports
from editors import int_eval_editor, float_eval_editor


#-------------------------------------------------------------------------------
#  ParametricItem class
#-------------------------------------------------------------------------------

class ParametricItem(HasTraits):
    """ Object used in the ParametricInteractor.

        It is used for displaying the input values and obtaining values for
        calculating shadow contexts.

    """

    # Name and current value in the context.
    name = Str
    input_value = Any

    # Parameters for evaluating values for calculating shadow contexts.
    high = Any
    low = Any
    step = Any

    # List of values for context[name] to be used for calculating shadow
    # contexts.
    output_list = List


    #---------------------------------------------------------------------------
    #  object interface
    #---------------------------------------------------------------------------

    ### private methods --------------------------------------------------------

    def _input_value_changed(self, trait, old, new):
        """ Change in input value should update the item
        """

        if isinstance(self.input_value, float) or isinstance(self.input_value,int):
            value = self.input_value
        elif isinstance(self.input_value, UnitScalar):
            value = self.input_value.tolist()
        else:
            value = None

        if value is not None:
            self.set(trait_change_notify = False,
                     high = self.input_value,
                     low = self.input_value,
                     step = 0)
            self._update_outputs()

        return


    def _high_changed(self, trait, old, new):
        self._set_value('high', old)
        self._update_outputs()


    def _low_changed(self, trait, old, new):
        self._set_value('low', old)
        self._update_outputs()


    def _step_changed(self, trait, old, new):
        self._set_value('step', old)
        self._update_outputs()


    ### public methods ---------------------------------------------------------

    def trait_view(self, name=None, view_element=None):
        """ Default view of the item
        """

        # Note: Use the title for the view only when running independent tests
        #        on ParametricItem.
#        title = 'Editing parameter: ' + self.name

        if isinstance(self.input_value, int):
            view = View(HGroup(Item('low', editor=int_eval_editor),
                               Item('high', editor=int_eval_editor),
                               Item('step', editor=int_eval_editor)))
        elif isinstance(self.input_value, float) or \
            isinstance(self.input_value, UnitScalar):
            view = View(HGroup(Item('low', editor=float_eval_editor),
                               Item('high', editor=float_eval_editor),
                               Item('step', editor=float_eval_editor)))
        else:
            view = View(Item('input_value', style = 'readonly'))

        return view


    #---------------------------------------------------------------------------
    #  ParametricItem interface
    #---------------------------------------------------------------------------

    ### private methods --------------------------------------------------------

    # FIXME: This method should go away once the text-editor is fixed to
    #        indicate erroneous data types.
    def _set_value(self, trait_name, old):
        """ Set the correct types for the traits specified in trait_name,
            if not revert to the old value.

            Parameters:
            -----------
            trait_name: Str
            old: Float or Int

        """

        value = getattr(self, trait_name)
        datatype, kw = type(self.input_value), {}

        try:
            kw[trait_name] = datatype(value)
        except ValueError:
            kw[trait_name] = old

        self.set(trait_change_notify = False, **kw)
        return


    # FIXME: Fix this whenever on_trait_change gets fixed.
#    @on_trait_change('low', 'high', 'step')
    def _update_outputs(self):
        """ Update outputs based on changes in low, high and step

            Different scenarios to be dealt with:
            1. low < high, step > 0: should return [low, low+step, ..., high]
            2. low < high, step < 0: should return [high, high+step, ..., low]
            3. low = high, step = Any: should return [low]
            4. low > high, step < 0: should return [low, low+step, ..., high]
            5. low > high, step > 0: should return [high, high+step, ..., low]
            6. low != high, step = 0: should return [input_value]

        """

        if self.step == 0:
            if self.high == self.low:
                self.output_list = [self.low]
            else:
                self.output_list = [self.input_value]

        else:
            low, high, step = self.low, self.high, self.step

            # Set the values for calculating range correctly.
            if (low < high and step < 0) or (low > high and step > 0):
                low, high = high, low

            if low != high:
                if isinstance(self.input_value, int):
                    self.output_list = range(low, high, step)
                else:
                    self.output_list = (numpy.arange(low, high, step)).tolist()

                # Add the extremum value if not included.
                if self.output_list[-1] != high:
                    self.output_list.append(high)
            else:
                self.output_list = [low]

        return


# FIXME: If one doesn't click enter after a change in step and exit immediately,
#        the change does not get recorded.

# Test
if __name__ == '__main__':
    p = ParametricItem(name = 'a', input_value = 100)
    ui = p.configure_traits()
    print 'Name:',p.name, 'Input:', p.input_value
    print 'Low:', p.low, 'High:', p.high, 'Step:', p.step
    print 'Output:', p.output_list


### EOF ------------------------------------------------------------------------
