from enthought.traits.api import Instance, Str
from enthought.chaco2.array_data_source import ArrayDataSource
from enthought.chaco2.abstract_data_source import AbstractDataSource
from enthought.block_canvas.context.i_context import IListenableContext
from enthought.traits.api import on_trait_change

class DataContextDataSource(ArrayDataSource):
    context = Instance(IListenableContext, adapt='yes')
    context_name = Str
    sort_order = 'none'
    
    def __init__(self, **kwtraits):
        AbstractDataSource.__init__(self, **kwtraits)
        return
    
    def get_data(self):
        """Get the data from the DataContext"""
        return self.context[self.context_name]

    def get_size(self):
        """Get the length of the data in the context"""
        return len(self.get_data())
    
    # This should be more sophisticated to see which item changes
    @on_trait_change('context:items_modified')
    def _update_context(self):
        self.data_changed = True

    
    def set_data(self, new_data, sort_order=None):
        self.context[self.context_name] = new_data
        self._data = new_data
        if sort_order is not None:
            self.sort_order = sort_order
        self._compute_bounds()
        self.data_changed = True
        return
