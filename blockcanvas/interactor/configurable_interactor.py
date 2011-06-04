""" Class that contains an interactor and a configure button to trigger the
    configuration of the interactor
"""

# Standard imports
import os, logging

# ETS imports
from traits.api import Any, Instance, Str, Dict
from traitsui.api import View, Group, Item, Handler, InstanceEditor
from traitsui.menu import OKButton, Action

# Application imports
from enthought.block_canvas.plot.configurable_context_plot \
        import ConfigurableContextPlot

# Local imports
from simple_interactor import SimpleInteractor
from parametric_interactor import ParametricInteractor
from shadow_interactor import ShadowInteractor
from stochastic_interactor import StochasticInteractor
from interactor_config import InteractorConfig
from utils import load_range_files

# Global logger
logger = logging.getLogger(__name__)

# List of interactors:
INTERACTOR_LIST = ['parametric', 'shadow', 'stochastic_constant',
                   'stochastic_gaussian', 'stochastic_triangular',
                   'stochastic_uniform']

#-------------------------------------------------------------------------------
#  ConfigurableInteractorHandler class
#-------------------------------------------------------------------------------

class ConfigurableInteractorHandler(Handler):
    """ Handler for a ConfigurableInteractor.
    """

    def configure(self, info):
        """ Refresh the interactor when the configure button is pressed.
        """

        ui = info.object.interactor_config.edit_traits(kind = 'livemodal')
        if ui.result:
            info.object.reset_inputs()

        return


    def closed(self, info, is_ok):
        """ Persist range information.
        """

        if is_ok:
            info.object.save_ranges_to_files(info.object.file_path_dict)

        return


    def save_shadows(self, info):
        """ Save shadows out to the context's saved-contexts.
        """

        context = info.object.context
        # Clear self references before pickling
        if context.has_key('context'):
            context_val = context.pop('context')
        else:
            context_val = None

        for shadow in context.shadows:
            context.save_any_context(shadow, shadow.name)

        # Reset self references if there were any
        if not context_val is None:
            context['context'] = context_val

        return


#-------------------------------------------------------------------------------
#  ConfigurableInteractor class
#-------------------------------------------------------------------------------

class ConfigurableInteractor(SimpleInteractor):
    """ Class that contains an interactor and also facilitates its configuration
    """

    # The configuration information for this interactor
    interactor_config = Instance(InteractorConfig)

    # The interactors and plot to displayed
    plot = Instance(ConfigurableContextPlot)

    # Dict of files to save preferences, like ranges for interactors.
    file_path_dict = Dict

    # Protected traits for refreshing UI
    _view_proxy = Any

    # Interactor prefix
    _interactor_prefix = Str('interactor_')

    #---------------------------------------------------------------------------
    #  Object interface
    #---------------------------------------------------------------------------

    def __init__(self, **traits):
        super(ConfigurableInteractor, self).__init__(**traits)
        self._view_proxy = self
        self._setup_inputs()


    #---------------------------------------------------------------------------
    #  HasTraits interface
    #---------------------------------------------------------------------------

    def trait_view(self, name = None, view_elements = None):
        if name == 'actual_view':
            return View( Group( *self._view_items() ) )
        else:
            return View(Item(name='_view_proxy', show_label = False,
                             editor=InstanceEditor(view='actual_view'),
                             style = 'custom'),
                        Item(name='plot', show_label = False, style = 'custom'),
                        title = 'Interactor',
                        resizable = True,
                        id = 'interactor.ConfigurableInteractor',
                        buttons = [#Action(name='Save shadows',
                                   #       action='save_shadows'),
                                   Action(name="Configure", action="configure"),
                                   OKButton ],
                        handler = ConfigurableInteractorHandler()
                    )


    #---------------------------------------------------------------------------
    #  ConfigurableInteractor interface
    #---------------------------------------------------------------------------

    def _view_items(self):
        items = []
        for var in INTERACTOR_LIST:
            trait_name = self._interactor_prefix + var
            if hasattr(self, trait_name):
                items.append(Item(name = trait_name, show_label = False,
                                  editor=InstanceEditor(), style = 'custom'))

        return items


    def _setup_inputs(self):
        """ Overriding base class method
        """

        assert(self.interactor_config is not None)

        # Set the plot
        self.plot = ConfigurableContextPlot(context=self.context,
                            plot_configs=self.interactor_config.plot_configs)

        # Set the interactors
        parametric_vars, shadow_vars = [], []
        stochastic_constant_vars, stochastic_gaussian_vars = [], []
        stochastic_triangular_vars, stochastic_uniform_vars = [], []

        mapping = {'parametric': parametric_vars,
                   'shadow': shadow_vars,
                   'stochastic_constant': stochastic_constant_vars,
                   'stochastic_gaussian': stochastic_gaussian_vars,
                   'stochastic_triangular': stochastic_triangular_vars,
                   'stochastic_uniform': stochastic_uniform_vars}

        for var in self.interactor_config.var_configs:
            if var.name is not None and var.name != '':
                mapping_type = var.type.replace(': ', '_').lower()
                mapping[mapping_type].append(var.name)

        for key in mapping.keys():
            if len(mapping[key]) > 0:
                trait_name = self._interactor_prefix + key

                if key == 'parametric':
                    value = ParametricInteractor(mapping[key],
                                                 block = self.block,
                                                 context = self.context)
                elif key == 'shadow':
                    value = ShadowInteractor(mapping[key],
                                             block = self.block,
                                             context = self.context)
                else:
                    distr_type = key[key.find('_')+1:]
                    value = StochasticInteractor(mapping[key],
                                                 block = self.block,
                                                 context = self.context,
                                                 distribution = distr_type)
                setattr(self, trait_name, value)

        self.apply_ranges()
        return


    def _destroy_items(self):
        """ When refreshing the interactors, delete the previous ones.
        """

        for var in INTERACTOR_LIST:
            trait_name = self._interactor_prefix + var
            if hasattr(self, trait_name):
                value = getattr(self, trait_name)
                self.remove_trait(trait_name)
                del value

        return


    #---------------------------------------------------------------------------
    # Trait listeners
    #---------------------------------------------------------------------------

    def _context_changed(self):
        # Warning, this should never listen for an event on the context
        # which is fired because the shadow changed, which will cause an
        # infinite recursion
        if self.traits_inited():
            self._destroy_items()
            self._setup_inputs()

        return


    def _block_changed(self):
        if self.traits_inited():
            self._destroy_items()
            self._setup_inputs()

        return


    ### public methods ---------------------------------------------------------

    def apply_ranges(self):
        """ Apply previously loaded ranges.
        """

        for key in INTERACTOR_LIST:
            trait_name = self._interactor_prefix + key

            if hasattr(self, trait_name) and self.ranges.has_key(key):
                interactor = getattr(self, trait_name)
                interactor.ranges = self.ranges[key]

        return


    def load_ranges_from_files(self, project_file_dict, global_dict = None):
        """ Load ranges for variables from file

            Parameters:
            -----------
            project_file_dict : Dict
                File containing project preferences for the various interactors.
                The keys should be 'shadow', 'parametric', 'stochastic_*'; where
                * = 'constant', 'gaussian', 'triangular', 'uniform'.

            global_dict : Dict
                File containing the users' global preferences for the various
                interactors. The keys should be 'shadow', 'parametric',
                'stochastic_*'; where * = 'constant', 'gaussian', 'triangular',
                'uniform'.

        """

        for key in INTERACTOR_LIST:
            file_dict = {}

            if project_file_dict.has_key(key):
                filename = project_file_dict[key]
                if filename is not None and os.path.exists(filename):
                    file_dict['project'] = filename

            if global_dict is not None and global_dict.has_key(key):
                filename = global_dict[key]
                if filename is not None and os.path.exists(filename):
                    file_dict['global'] = filename

            ranges = load_range_files(file_dict)

            if len(ranges):
                current_ranges = ranges['units']
                for k,v in ranges['user'].items():
                    current_ranges[k] = v
                self.ranges[key] = current_ranges

        self.apply_ranges()

        return


    def reset_inputs(self):
        """ Resetting inputs on re-configure
        """

        self._destroy_items()
        #self.context.shadows = []
        self._setup_inputs()
        self._view_proxy = None
        self._view_proxy = self

        return


    def save_ranges_to_files(self, file_dict):
        """ Save ranges for variables to file

            Parameters:
            -----------
            file_dict : Dict
                Dictionary of file_paths.

        """

        for key in INTERACTOR_LIST:
            trait_name = self._interactor_prefix + key
            if hasattr(self, trait_name) and file_dict.has_key(key):
                interactor = getattr(self, trait_name)
                range_dict = interactor.extract_range_dict()

                if len(range_dict):
                    file_object = open(file_dict[key], 'w')

                    for k,v in range_dict.items():
                        v = [str(val) for val in v]
                        str_val = k+'\t'+'\t'.join(v)+'\n'
                        file_object.write(str_val)

                    logger.debug('ConfigurableInteractor: Saving ranges of %s '
                                 'interactor to file %s' %
                                 (key, file_dict[key]))
                    file_object.close()

        return

def new_main():
    from numpy import linspace
    from enthought.contexts.api import DataContext
    from enthought.block_canvas.block_display.block_unit_variables import BlockUnitVariableList
    from enthought.contexts.api import DataContext
    from enthought.block_canvas.app.experiment import Experiment

    code = "y = a*x*x + b*x + c"
    context = DataContext(name='Data')

    exp = Experiment(code=code, shared_context=context)
    context.update(dict(a=1.0, b=1.0, c=0.0))
    context['x'] = linspace(-5., 5., 60)

    # FIXME: Shouldn't have to manually call this now
    exp.context.execute_for_names(["a", "b", "c"])

    block = exp.exec_model.block

    # Use the experiment's local context as the shadow context
    exp.context.shadows = [exp._local_context]

    vars = BlockUnitVariableList(block=block, context=exp.context)
    config_interactor = InteractorConfig(vars=vars.variables)

    interactor = ConfigurableInteractor(context=exp.context, block=block,
                                        interactor_config = config_interactor)
    interactor.configure_traits()

# Test code
if __name__ == '__main__':
    new_main()

