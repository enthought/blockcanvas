# Enthought library imports
from traits.api import Any, Enum, implements, HasTraits, Property

# Local library imports
from i_selectable import ISelectable


class SelectableComponentMixin(HasTraits):
    """ Mixin class that allows a generic component to be selected and moved
        on the canvas.
    """

    implements(ISelectable)

    #########################################################################
    # SelectableComponentMixin traits
    #########################################################################

    # Is the component selected?
    # 'coselected' means this item is selected, but isn't the "primary"
    # selected item.  For example, it might not have been selected first.
    selection_state = Enum('unselected', 'selected', 'coselected')

    # If my container has a selection manager, use it. Otherwise, None.
    selection_manager = Property

    # Stores the value that a user set for the selection manager
    _selection_manager = Any

    def _get_selection_manager(self):
        if self._selection_manager is not None:
            return self._selection_manager
        if self.container is not None:
            return getattr(self.container, "selection_manager", None)
        else:
            return None

    def _set_selection_manager(self, new):
        self._selection_manager = new

    def _selection_state_changed(self, old, new):
        """ Redraw if my selection state changes.
        """
        self.invalidate_draw()
        self.request_redraw()
