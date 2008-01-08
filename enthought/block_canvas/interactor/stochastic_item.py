""" StochasticItem class defines an item for stochastic interactor.

    It is used for displaying the input values of a context as well as the
    fields required by the chosen distribution.
    
"""

# ETS imports
from enthought.traits.api import HasTraits, Instance, Str, Property
from enthought.traits.ui.api import View, Item, HGroup
from enthought.util.distribution.distribution import \
     Constant, Distribution, Gaussian, Triangular, Uniform


#-------------------------------------------------------------------------------
#  StochasticItem class
#-------------------------------------------------------------------------------

class StochasticItem(HasTraits):
    """ Object for the StochasticInteractor.

        It is used for displaying the input values and obtaining values for
        various distributions.
        
    """

    # Name and current value in the context
    name = Str

    # Distribution details
    distribution = Instance(Distribution)
    samples = Property(depends_on = ['distribution'])
    

    #---------------------------------------------------------------------------
    #  object interface
    #---------------------------------------------------------------------------

    ### public methods ---------------------------------------------------------
    
    def trait_view(self, name=None, view_element=None):
        """ Default view
        """

        if isinstance(self.distribution, Constant):
            return View(HGroup(Item('object.distribution.value'),
                               Item('samples')),
                        buttons = ['OK'])
        elif isinstance(self.distribution, Gaussian):
            return View(HGroup(Item('object.distribution.mean'),
                               Item('object.distribution.std'),
                               Item('samples')),
                        buttons=['OK'])
        elif isinstance(self.distribution, Triangular):
            return View(HGroup(Item('object.distribution.mode'),
                               Item('object.distribution.low'),
                               Item('object.distribution.high'),
                               Item('samples')),
                        buttons=['OK'])
        else:
            return View(HGroup(Item('object.distribution.low'),
                               Item('object.distribution.high'),
                               Item('samples')),
                        buttons=['OK'])


    #---------------------------------------------------------------------------
    #  StochasticItem interface
    #---------------------------------------------------------------------------

    ### private methods --------------------------------------------------------

    def _get_samples(self):
        """ Property getter
        """

        return self.distribution.samples


    def _set_samples(self, value):
        """ Property setter
        """
        
        self.distribution.samples = int(value)
        return
    
        
# Test
if __name__ == '__main__':
    d = Constant(value=50.0)
    # d = Gaussian(mean=50.0, std=1.0)
    # d = Triangular(low=20., mode=40., high=50.)
    # d = Uniform(low=40., high=60.)
    s = StochasticItem(name='a', distribution=d)
    
    ui = s.edit_traits(kind='livemodal')
    if ui.result:
        print s.distribution.values
        
### EOF ------------------------------------------------------------------------
