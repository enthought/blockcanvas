from enthought.traits.api import Interface, Enum


class ISelectable(Interface):
    """ Items on the canvas that are selectable.

        fixme: Currently, Selectable items must define a drag interface.  This
               doesn't seem right...
    """

    # Is this item currently selected?  coselected means the item is selected,
    # but it isn't the "primary" selected item.
    selection_state = Enum('unselected', 'selected', 'coselected')

#    # This would allow us to draw differently if we were singly selected of
#    # part of a multi-selection.  Revisit later.
#    primary_selection = Bool(False)

    #########################################################################
    # ISelectable interface
    #########################################################################

    #### Dragging methods ###################################################

    # These methods are to handle when an event is dragged across the canvas.

    def drag_start(self, event, item_fired=None):
        """ Prepare item for a potential drag event.
        """

    def dragging(self, event, item_fired=None):
        """ Handle a drag move event.
        """

    def drag_cancel(self, event, item_fired=None):
        """ Handle a drag being canceled. Often this is handled as if it ended
            normally.
        """

    def drag_end(self, event, item_fired=None):
        """ Handle the end of a dragging event.
        """
