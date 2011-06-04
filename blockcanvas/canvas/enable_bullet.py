# Enthought library imports
from enthought.enable.api import ColorTrait, Component, Pointer
from enthought.enable.tools.api import DragTool
from enthought.traits.api import Bool, Enum, Instance, Int, Property, Str, Tuple

# Local imports
import enable_glyph_lib

class Bullet(Component):

    color = ColorTrait("gray")

    drag_color = ColorTrait((0.6, 0.6, 0.6, 0.5))
    border_color = ColorTrait((0.4, 0.4, 0.4, 1.0))
    bgcolor = "clear"

    bullet_state = Enum("up", "down", "dragging", "over", "dropping")

    normal_pointer = Pointer("arrow")

    moving_pointer = Pointer("hand")

    # This is currently determines the size of the widget, since we're just
    # drawing a triangle for now
    bounds=[9,12]

    def perform(self, event):
        """
        Called when the button is depressed.  'event' is the Enable mouse event
        that triggered this call.
        """
        pass

    def _draw_mainlayer(self, gc, view_bounds, mode="default"):
        if self.event_state == "selected":
            enable_glyph_lib.io_bullet_over(gc, self.x, self.y, self.width, self.height)
        elif self.bullet_state == "up":
            enable_glyph_lib.io_bullet_up(gc, self.x, self.y, self.width, self.height)
        elif self.bullet_state == "dragging":
            enable_glyph_lib.io_bullet_drag(gc, self.x, self.y, self.width, self.height)
        elif self.bullet_state == "over":
            enable_glyph_lib.io_bullet_over(gc, self.x, self.y, self.width, self.height)
        elif self.bullet_state == "dropping":
            enable_glyph_lib.io_bullet_drop_target(gc, self.x, self.y, self.width, self.height)
        else:
            enable_glyph_lib.io_bullet_down(gc, self.x, self.y, self.width, self.height)

        return

    def normal_left_down(self, event):
        self.bullet_state = "down"
        self.pointer = self.moving_pointer
        self.request_redraw()
        event.handled = True

    def normal_mouse_enter(self, event):
        self.bullet_state = "over"
        self.pointer = self.moving_pointer
        self.request_redraw()
        event.handled = True

    def normal_mouse_leave(self, event):
        self.bullet_state = "up"
        self.pointer = self.normal_pointer
        self.request_redraw()
        event.handled = True

    def normal_left_up(self, event):
        self.bullet_state = "up"
        self.pointer = self.normal_pointer
        self.request_redraw()
        self.perform(event)
        event.handled = True


