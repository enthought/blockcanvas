from enthought.traits.api import Event, Str, Enum, Property
from enthought.enable.api import Component

from string_image import StringImage


class EnableImageButton(Component):
    """ Clickable image for an Enable Canvas.

        fixme: We don't handle a different image for clicked and we don't
               offset the image or anything like that.  We need to do this.
               Does it require a timer?
        fixme: We may want an image alpha set up for this.
    """

    # Image used to draw button normally
    normal_image = StringImage

    # Image used to draw button when mouse is over it.
    over_image =  StringImage

    # Which image is currently used for the button?
    active_image = Property

    # Text that shows up as a tool tip for the button.
    # fixme: Not implemented.
    tooltip = Str

    # Event fired when button is clicked.
    clicked = Event

    # Should we draw the button normally in its "mouse over" state?
    mouse_over_state = Enum('normal', 'over')

    # We don't want to have a background painted for us.
    bgcolor = "none"

    # bounds of button are calculated based on the active_image size.
    bounds = Property


    #########################################################################
    # object interface
    #########################################################################

    def __init__(self, *args, **kw):
        super(EnableImageButton, self).__init__(*args, **kw)

        # fixme: This is to force initialization of image shadow traits.
        #        This is only necessary because of a bug in traits.  Hopefully
        #        it will go away soon.
        if self.normal_image == "":
            self.normal_image = " "
        if self.over_image == "":
            self.over_image = " "


    #########################################################################
    # Interactor (event handling) interface
    #########################################################################

    ### mouse state transition methods ######################################

    def normal_pre_mouse_enter(self, event):
        event.handled = True
        # Don't mouse_over state if it wasn't orginally clicked here.
        if event.left_down != True:
            self.mouse_over_state = "over"
        self.invalidate_draw()

    def normal_pre_mouse_leave(self, event):
        event.handled = True
        self.mouse_over_state = "normal"
        self.invalidate_draw()

    def normal_left_down(self, event):
        event.handled = True
        self.event_state = "down"
        self.invalidate_draw()

    def down_left_up(self, event):
        event.handled = True
        if self.mouse_over_state == "over":
            self.clicked = event
        self.event_state = "normal"
        self.invalidate_draw()


    #########################################################################
    # Component private interface
    #########################################################################

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draw the currently active image onto the canvas.
        """
        image = self.active_image
        rect = (self.x, self.y, image.width(), image.height())
        gc.draw_image(image, rect)

    ### trait properties get/set ############################################

    def _get_bounds(self):
        """ Return the bounds of the button based on the active image size.
        """
        img = self.active_image
        return [img.width(), img.height()]

    #########################################################################
    # EnableImageButton private interface
    #########################################################################

    ### trait handlers #######################################################

    def _get_active_image(self):
        """ Pick the image that is currently active for the button.
        """
        if (self.mouse_over_state == 'over' and
            self.over_image not in ["", " "]): # fixme: default values.
            image = self.over_image_
        else:
            image = self.normal_image_

        return image

    def _mouse_over_state_changed(self):
        """ If the mouse over state changes, we need to redraw with the
            appropriate image.
        """
        self.request_redraw()


"""
Test cases needed.
    *. Only Normal Image.
    *. No Normal Image (draw x?)
    *. Bad name for Normal Image
    *. Normal and Over Image.
    *.
    *. Tests for mouse event chain.
    *. click event.
        *. Only get click event if we went down and came up over the button.
    *. Draw state transition diagram.
"""

if __name__ == "__main__":
    button = EnableImageButton()
    print button.normal_image
    print button.normal_image_
    print button.active_image
    print button.bounds
