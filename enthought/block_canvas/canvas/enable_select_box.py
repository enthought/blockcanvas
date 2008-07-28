# Enthought library imports
from enthought.traits.api import Tuple
from enthought.enable.api import ColorTrait, Component, LineStyle

class EnableSelectBox(Component):
    """ Implements generic behavior for a selection box
    """

    # Color for the box's edge
    stroke_color = ColorTrait((0, 0, 0, 1))

    # Color to fill the box with
    fill_color = ColorTrait((0, 0, 0, .1))

    # Style for the box's edge
    style = LineStyle("solid")

    # Private traits
    _original_position = Tuple

    #---------------------------------------------------------------------------
    # EnableSelectBox interface
    #---------------------------------------------------------------------------

    def set_drag_start(self, x, y):
        """ Sets the fixed coordinate which is the start of the selection.
            Effectively resets the selection box.
        """

        self.position = [x, y]
        self._original_position = (x, y)
        self.bounds = [0, 0]

    def set_drag_dimensions(self, x2, y2):
        """ Set the coordinate which is under the mouse, assuming the mouse is
            being used for selection.
        """
        if x2 < self._original_position[0]:
            self.x = x2
            self.width = self._original_position[0] - x2
        else:
            self.x = self._original_position[0]
            self.width = x2 - self.x
        if y2 < self._original_position[1]:
            self.y = y2
            self.height = self._original_position[1] - y2
        else:
            self.y = self._original_position[1]
            self.height = y2 - self.y

    def is_component_in(self, c):
        """ Returns true if any part of the component is considered "inside"
        the select box.
        """

        return ( self.is_in(c.x, c.y) or self.is_in(c.x2, c.y2) or
                 self.is_in(c.x, c.y2) or self.is_in(c.x2, c.y) )

    def is_completely_in(self, c):
        """ Only returns true if all of the component is entirely inside 
        the select box.
        """

        return ( self.is_in(c.x, c.y) and self.is_in(c.x2, c.y2) and
                 self.is_in(c.x, c.y2) and self.is_in(c.x2, c.y) )

    #---------------------------------------------------------------------------
    # Component interface
    #---------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        gc.save_state()
        gc.set_antialias(1)
        gc.set_stroke_color(self.stroke_color_)
        gc.set_fill_color(self.fill_color_)
        gc.begin_path()
        gc.rect(self.x, self.y, self.width, self.height)
        gc.draw_path()
        gc.restore_state()

    def _draw_background(self, gc, view_bounds=None, mode="default"):
        pass
