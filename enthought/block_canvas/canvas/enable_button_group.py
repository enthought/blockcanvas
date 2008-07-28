""" Class to handle the layout of a group of components horizontally.

    This is probably an equivalent for a "Toolbar", or such a thing could
    sub-class from this.
"""

# Enthought library imports
from enthought.traits.api import List, Int, Delegate, on_trait_change
from enthought.enable.abstract_layout_controller import \
    AbstractLayoutController
from enthought.enable.container import Container


class HorizontalLayoutController(AbstractLayoutController):
    """ Lay out container items horizontally with spacing between them.
    """

    ##########################################################################
    # HorizontalLayoutController traits
    ##########################################################################

    # Horizontal spacing to put between each item
    spacing = Int(1)


    ##########################################################################
    # AbstractLayoutController interface
    ##########################################################################

    def layout(self, container):
        """ Layout objects horizontally with some spacing in between them.
        """
        x_position = 0
        for component in container.components:
            component.x = x_position
            x_position = component.x2 + self.spacing + 1
            component.y = 0


class EnableButtonGroup(Container):
    """ Group of buttons laid out horizontally.

        fixme: Actually, this handles any arbitrary set of components.  It
               doesn't just work for buttons.  Perhaps we should rename and
               refactor into Enable?
    """

    ##########################################################################
    # Component traits
    ##########################################################################

    bgcolor = "transparent"


    ##########################################################################
    # Container traits
    ##########################################################################

    layout_controller = HorizontalLayoutController()


    ##########################################################################
    # EnableButtonGroup interface
    ##########################################################################

    ### trait listeners ######################################################

    @on_trait_change('_components', '_components_items')
    def _call_layout(self):
        """ Call the layout algorithm whenever the components list changes.

            fixme: I would think the container interface would do this
                   automatically...?  After all, the layout_controller is
                   part of its interface.
        """
        self.layout_controller.layout(self)


class EnableTopRightButtonGroup(EnableButtonGroup):
    """ Button Group that anchors itself to the top right corner of its
        enclosing container.

        fixme: Really should factor this into a more general "anchorable"
               component idea.
    """

    ##########################################################################
    # EnableTopRightButtonGroup traits
    ##########################################################################

    # Offset from the upper right hand corner of its container.
    offset = List([5, 4])


    ##########################################################################
    # EnableTopRightButtonGroup interface
    ##########################################################################

    ### trait listeners ######################################################

    @on_trait_change('container', 'container.bounds')
    def _update_position(self):
        """ Whenever the container or its bounds change, re-position buttons.
        """
        if self.container is not None:
            new_bounds = self.container.bounds
            x_extents, y_extents = new_bounds[0], new_bounds[1]

            x_new = x_extents - self.offset[0] - self.width
            y_new = y_extents - self.offset[1] - self.height

            self.position = [x_new, y_new]
            self.request_redraw()

#EOF
