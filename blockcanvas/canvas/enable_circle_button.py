""" Circular kiva-drawn button with text inside of it.

    NOTE: THIS IS NOT CURRENTLY USED IN ANY OF THE CODE!
"""

# Enthought library imports
from traits.api import Str
from kiva.traits.api import KivaFont
from enable.api import Component
from enable.traits.api import RGBAColor


class EnableCircleButton(Component):
    """ Implements generic behavior for a selectable/movable box on an enable
        canvas.
    """

    #########################################################################
    # Component Traits
    #########################################################################

    bgcolor = "transparent"
    border_visible = False


    #########################################################################
    # EnableBox Traits
    #########################################################################

    # Text label for box.
    # fixme: May eventually need to be a text object.
    label = Str

    # Font for text in Box.
    # fixme: refactor to text object for the box.
    font = KivaFont("modern 16")

    # Color for Box label.
    text_color = RGBAColor('black')

    ### Private traits ######################################################

    # Fill color to draw box as when moving.
    # fixme: doesn't seem like it should be here.
    #_over_color = RGBAColor((0.0, 0.8, 0.8, 1.0))


    #########################################################################
    # Component Interface
    #########################################################################


    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        gc.save_state()
        gc.set_fill_color(self.color)
        dx, dy = self.bounds
        x, y = self.position
        radius = min(dx/2.0, dy/2.0)
        gc.arc(x+dx/2.0, y+dy/2.0, radius, 0.0, 2*3.14159)
        gc.fill_path()
        gc.restore_state()

        self._draw_label(gc, view_bounds, mode)


    #########################################################################
    # EnableCircle Interface
    #########################################################################

    def _draw_label(self, gc, view_bounds=None, mode="default"):
        """ Draw label centered in the circle.
        """

        dx, dy = self.bounds
        x, y = self.position

        gc.save_state()

        # calculate text offset to center it in the box.
        # fixme: We have to set the font before a call, otherwise we get a
        #        traceback.  There should be a default font.
        gc.set_font(self.font)

        # center the text within the box.
        tx, ty, width, height = gc.get_text_extent(self.label)
        text_offset = (x + (dx-width)/2.0 + tx, y + (dy-height)/2.0 + ty)

        # Now draw the text.
        gc.set_fill_color(self.text_color_)
        gc.show_text(self.label, text_offset)

        gc.restore_state()

        return
