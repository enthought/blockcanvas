""" Adapt a data context and as a PlotData object so that it behaves as a
    source for chaco plots.
"""
from numpy import arange

# Enthought library imports
from chaco.abstract_plot_data import AbstractPlotData
from enthought.contexts.data_context import DataContext
from traits.api import on_trait_change, Instance
from enthought.contexts.i_context import IListenableContext
from blockcanvas.plot.data_context_datasource import DataContextDataSource


class PlotDataContextAdapter(AbstractPlotData):
    """ Makes a DataContext behave like a Chaco AbstractPlotData class.

        This makes it easy to use a context as a source for chaco plots.
    """

    ##########################################################################
    # PlotDataContextAdapter traits
    ##########################################################################

    # The underlying context that holds the values.
    context = Instance(IListenableContext, adapt='yes')


    ##########################################################################
    # AbstractPlotData traits
    ##########################################################################

    # fixme: For now, this is a read-only class.
    # Can consumers write data back through this interface using set_data()?
    writable = False

    # Can consumers set selections?
    selectable = False


    ##########################################################################
    # AbstractPlotData interface
    ##########################################################################

    def list_data(self):
        """ Returns a list of valid names to use for get_data().  These are
            generally strings but can also be integers or any other hashable type.
        """
        key_list = []
        key_list.extend(self.context.keys())
        if hasattr(self.context, 'shadows'):
            for shadow_num, shadow in enumerate(self.context.shadows):
                key_list.extend(['shadow_' + str(shadow_num) + '_' + name \
                                 for name in shadow.keys()])
        return self.context.keys()


    def get_data(self, name):
        """ Returns the data or datasource associated with name.  If there is
            no data or datasource associated with the name, returns None.

            fixme: Do we need to do anything here to ensure that the data
            returned is an array?
        """
        # Find the appropriate shadow context if it's a shadow lookup
        if hasattr(self.context, 'shadows') and name[:7] == 'shadow_':
            split_name = name.split('_')
            context = self.context.shadows[int(split_name[1])]
            name = '_'.join(split_name[2:])
        else:
            context = self.context

        base_lookup = context.get(name, None)
        # If lookup fails, see if it's an index lookup
        if base_lookup == None:
            if name[-6:] == '_index':
                base_lookup = context.get(name[:-6], None)
                if hasattr(base_lookup, 'shape') and len(base_lookup.shape) == 1:
                    return arange(len(base_lookup))

        return base_lookup


    def set_data(self, name, new_data, generate_name=False):
        """ If writable is True, then this sets the data associated with the
        given name to the new value.  If writable if False, then this should
        do nothing.  If generate_name is True, then the datasource should
        create a new name to bind to the data, and return it.

        If the name does not exist, then attaches a new data entry to this
        PlotData.

        Returns the new data's name.
        """
        raise NotImplementedError


    def set_selection(self, name, selection):
        """ Sets the selection on the specified data.  This informs the class
        that Chaco has selected a portion of the data.  'Selection' is a binary
        array of the same length as the data named 'name'.
        """
        raise NotImplementedError


    ##########################################################################
    # PlotDataContextAdapter interface
    ##########################################################################

    def get_datasource(self, name):
        """Gets a chaco DataSource for the named object."""
        return DataContextDataSource(context=self.context, context_name=name)

    @on_trait_change('context:items_modified')
    def _fire_data_changed(self, obj, name, old, value):
        """ Translate 'items_modified' event to a chaco 'data_changed' event.
        """
        event = {}
        event['added'] = value.added
        event['removed'] = value.removed
        event['changed'] = value.modified
        self.data_changed = event

if __name__ == '__main__':
    from numpy import array
    data = DataContext()
    data['vp'] = array((1,2,3,4))
    data['vs'] = array((1,2,3,4))/2.
    plot_data = PlotDataContextAdapter(context=data)
    print plot_data.get_data('vp')
