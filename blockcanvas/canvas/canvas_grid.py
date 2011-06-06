""" Component for drawing grid lines within a canvas.

    fixme:  This probably is pretty much identical to Chaco's grid.  Change to
            using it, or refactor it into Enable.
"""

# Numeric library imports
from numpy import arange, empty

# Enthought library imports
from traits.api import Array, Instance, Bool, Any, on_trait_change
from enable.api import AbstractOverlay
from kiva.image import GraphicsContext

# Local imports
from canvas_grid_style import CanvasGridStyle

import time

class CanvasGrid(AbstractOverlay):
    """ Manage and draw the grid lines on a canvas.
    """

    ##########################################################################
    # CanvasGrid interface
    ##########################################################################

    # Provides style settings for configuring grid.
    style = Instance(CanvasGridStyle, ())

    # Should we backbuffer the grid to speed up drawing?
    # Faster if this is on, less memory if it is off.
    backbuffer = Bool(False)

    ### private traits #######################################################

    # List of start points for vertical grid lines.
    _vertical_start = Array

    # List of end points for vertical grid lines.
    _vertical_end = Array

    # List of start points for horizontal grid lines.
    _horizontal_start = Array

    # List of end points for horizontal grid lines.
    _horizontal_end = Array

    # Backbuffer used for storing the image.
    _backbuffer = Any

    ##########################################################################
    # Component interface
    ##########################################################################

    ### private interface  ###################################################

    def overlay(self, component, gc, view_bounds=None, mode="default"):
        if self.style.visible is True:
            self._draw_grid_lines(gc, view_bounds, mode)
        return


    ##########################################################################
    # CanvasGrid interface
    ##########################################################################

    ### private interface  ###################################################

    def _draw_grid_lines(self, gc, view_bounds=None, mode="default"):
        """ Draw gridlines on the canvas.

            fixme: We need to add drawing modes to the canvas, and this one
                   should draw in "background" mode or something to ensure
                   that it is always behind everything else.
        """

        nv = len(self._vertical_start)
        nh = len(self._horizontal_start)
        if (nv > 0) or (nh > 0):
            gc.save_state()

            # Style setup.
            gc.set_line_dash(self.style.line_dash)
            gc.set_stroke_color(self.style.line_color)
            gc.set_line_width(self.style.line_width)
            gc.set_antialias(self.style.antialias)

            # Draw lines.
            if nv > 0:
                gc.line_set(self._vertical_start,self._vertical_end)
            if nh > 0:
                gc.line_set(self._horizontal_start,self._horizontal_end)
            gc.stroke_path()

            gc.restore_state()


    ### trait handlers #######################################################

    @on_trait_change('component.view_bounds,component.bounds,component.bounds_items')
    def _update_grid_line_points(self):
        """ Create grid lines based on its parent containers bounds.
        """

        x_interval = self.style.x_interval
        y_interval = self.style.y_interval

        # Check to see if we need to take into account the viewport being
        # zoomed out.  If so, we look for integer multiples of the zoom
        # level and scale the x_interval and y_interval accordingly.
        if len(self.component.viewports) > 0:
            vp = self.component.viewports[0]
            if vp.enable_zoom and vp.zoom < 1.0:
                factor = int(1 / vp.zoom)
                x_interval *= factor
                y_interval *= factor

        x, y, x2, y2 = self.component.view_bounds
        w = x2 - x + 1
        h = y2 - y + 1

        # Compute the remainder of the current x,y of the view_bounds
        # modulo x_interval and y_interval, so we know at what offset to
        # start drawing the grid lines.
        x = (int(x) / x_interval) * x_interval
        x2 = x + w
        y = (int(y) / y_interval) * y_interval
        y2 = y + h

        x_points = arange(x, x2+x_interval/2., x_interval,
                          dtype=float)
        self._vertical_start = empty((len(x_points),2), dtype=float)
        self._vertical_start[:,0] = x_points
        self._vertical_start[:,1] = y

        self._vertical_end = empty((len(x_points),2), dtype=float)
        self._vertical_end[:,0] = x_points
        self._vertical_end[:,1] = y2


        y_points = arange(y, y2+y_interval/2., y_interval,
                          dtype=float)
        self._horizontal_start = empty((len(y_points),2), dtype=float)
        self._horizontal_start[:,0] = x
        self._horizontal_start[:,1] = y_points

        self._horizontal_end = empty((len(y_points),2), dtype=float)
        self._horizontal_end[:,0] = x2
        self._horizontal_end[:,1] = y_points

        self.request_redraw()
