# Enthought library imports
from enthought.traits.api import (HasTraits, Int, Bool, List)
from enthought.enable.traits.api import RGBAColor


class CanvasGridStyle(HasTraits):
    """ Grid line style settings.

        Note: I've made the default y_interval 1 pixel larger to deal with
              the aspect ration of the screen pixels.  This is almost surely
              screen dependent, and we should probably deal with this in a
              more intelligent way.
    """

    ##########################################################################
    # CanvasGridStyle traits
    ##########################################################################

    # Spacing between vertical grid lines.
    x_interval = Int(16)

    # Spacing between vertical grid lines.
    y_interval = Int(16)

    # Should gridlines be antialiased?
    antialias = Bool(False)

    # Pixels on,off dashing pattern for grid lines.
    line_dash = List([3,2])

    # Color for the grid lines. (default is a light blue)
    line_color = RGBAColor((.73, .83, .86))

    # Line width for the grid lines.
    line_width = Int(1)

    # Is the grid visible?
    visible = Bool(True)


