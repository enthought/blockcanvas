""" Manage a list of selection items in an Enable container.  It includes
    logic for determining whether a new selected item should be added to
    or removed from the selection list based on a) whether it is in the list
    and b) whether Ctrl/Shift keys are down.
"""

# Enthought library imports
from enthought.traits.api import HasTraits, List, Bool

# Local imports
from i_selectable import ISelectable


class SelectionManager(HasTraits):
    """ Manages a list of selected items.  Items in this list should
        have a selection_state trait (Is this ISelectable??).

        One item (the first right now) has its selection_state set to
        'selected'.  All others have their state set to 'coselected'.

        fixme: Currently, the first item selected is always the "primary"
               selection and all other items are the "coselected" items.

        fixme: The logic for this still needs work to make it clean.
    """

    #########################################################################
    # SelectionManager traits
    #########################################################################

    # List of the selected items.
    selection = List(ISelectable)

    # If True, calling select_item adds to rather than replaces the selection list
    add_subtract_mode = Bool(False)

    # Flag variable to prevent an exponential number of calls to drag_prepare()
    # TODO: refactor the way EnableBox handles selections so that this loop-
    #       breaking is not necessary
    _handling_drag_prepare = Bool(False)
    _handling_drag_move = Bool(False)
    _handling_drag_done = Bool(False)

    #########################################################################
    # SelectionManager interface
    #########################################################################

    def select_item(self, item, allow_remove=True):
        """ Request that items be added/removed to the selection list.

            If the item is not in the selection list, it either becomes the
            selected item or is added to the selection list.  If the item
            is already in the selection list, it is (usually) removed from the
            list.

            item -- An object implements ISelectable
            allow_remove -- Is the manager allowed to remove the item from the
                            selection? 
        """

        if item in self.selection:
            if allow_remove==True:
                if self.add_subtract_mode:
                    # Toggle ourselves out of the selection.
                    self.selection.remove(item)
                else:
                    # clear the entire selection.
                    self.unselect_all()
        else:
            if self.add_subtract_mode:
                # In add_mode, we append this item to the current selection.
                self.selection.append(item)
            else:
                # Otherwise, clear the current selection, and make this the
                # only selected item.
                self.selection = [item]
            
            if item.graph_node:
                node = item.graph_node
                if hasattr(node, 'function'):
                    from enthought.block_canvas.app.scripting import app
                    app.html_window_set_function_help(node.function.name, node.function.module)

    def select_items(self, items, allow_remove=True):
        """ Requests that the list of items be added to the selection list.
        """
        old_mode = self.add_subtract_mode
        self.add_subtract_mode = True

        for item in items:
            self.select_item(item, allow_remove)

        self.add_subtract_mode = old_mode

    def unselect_all(self):
        """ Remove all items from selection.
        """
        self.selection = []

    def move_selection(self, dx, dy, source=None):
        """ Moves all the components in the selection by dx and dy.  If
        source is not None, then it is skipped and not moved.
        """
        for item in self.selection:
            if item == source:
                continue
            pos = item.position
            item.position = [pos[0]+dx, pos[1]+dy]


    #### Private methods ####################################################

    def _mark_unselected(self, unselected):
        for item in unselected:
            item.selection_state = 'unselected'

    def _mark_selected(self, selected, coselected=[]):
        for item in selected:
            item.selection_state = 'selected'
        for item in coselected:
            item.selection_state = 'coselected'

    #### Trait listeners ####################################################

    def _selection_changed(self, old, new):
        """ When the entire lists changes, we need to update all the
            items selection_state trait.

            The first item has its selection_state set to 'selected'.
            All others have their selection_state set to 'coselected'.
        """
        self._mark_unselected(old)

        # split of first item as 'selected', and all others as 'coselected'
        self._mark_selected(new[:1], new[1:])

    def _selection_items_changed(self, event):
        """ Individual items in the selection list changed.
        """
        # This always does extra work, but it is also always right...
        if event.removed:
            self._mark_unselected(event.removed)

        # Split of first item as 'selected', and all others as 'coselected'
        # Loop through the entire list instead of event.add to make sure we get
        # the first item in the list 'selected' and all others 'unselected'
        # fixme: If this proves to be slow at some point, we can work harder
        #        to update a minimal set.
        self._mark_selected(self.selection[:1], self.selection[1:])


