from traits.api import Event, Str, Enum, Property
from enable.api import Component

from string_image import StringImage
import enable_glyph_lib

class EnableGlyphButton(Component):
    """ Clickable glyph button for an Enable Canvas.
    """

        #fixme: We don't handle a different image for clicked and we don't
        #       offset the image or anything like that.  We need to do this.
        #       Does it require a timer?
        #fixme: We may want an image alpha set up for this.

    # Active glyph to render
    active_glyph = Property

    normal_glyph = Str("default_glyph")

    over_glyph = Str("default_glyph")

    down_glyph = Str("default_glyph")

    # Text that shows up as a tool tip for the button.
    # fixme: Not implemented.
    tooltip = Str

    # Event fired when button is clicked.
    clicked = Event

    # Should we draw the button normally in its "mouse over" state?
    mouse_over_state = Enum('normal', 'over')

    # We don't want to have a background painted for us.
    bgcolor = "none"

    # bounds of button are calculated based on the active_glyph size.
    bounds = Property


    #########################################################################
    # object interface
    #########################################################################

    def __init__(self, *args, **kw):
        super(EnableGlyphButton, self).__init__(*args, **kw)

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
        # Call to the glyph lib to render active_glyph
        # FIXME: is there a better way to call a function within a module
        # with a string?
        enable_glyph_lib.__dict__[self.active_glyph](gc, self.x, self.y,
                self.width, self.height)

    ### trait properties get/set ############################################

    def _get_bounds(self):
        """ Return the bounds of the button based on the active image size.
        """

        return [12, 12]

    #########################################################################
    # EnableImageButton private interface
    #########################################################################

    ### trait handlers #######################################################

    def _get_active_glyph(self):
        """ Pick the glyph that is currently active for the button.
        """
        if (self.mouse_over_state == 'over' and
            self.over_glyph not in ["", " "]): # fixme: default values.
            glyph = self.over_glyph
        elif (self.mouse_over_state == 'down' and
            self.down_glyph not in ["", " "]):
            glyph = self.down_glyph
        else:
            glyph = self.normal_glyph

        return glyph

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
