""" Basic movable and labeled Loop for a Canvas.
"""
# Enthought library imports
from enable.api import Container
from enable.font_metrics_provider import font_metrics_provider
from traits.api import Any, Bool, Float, Instance, List, on_trait_change, Property, Str

# Local library imports
from canvas_box import CanvasBox
from enable_box_tools import BoxResizeTool, BoxMoveTool, BoxSelectionTool
from enable_button_group import EnableButtonGroup, EnableTopRightButtonGroup
from enable_glyph_button import EnableGlyphButton
from io_field import IOField
from selectable_component_mixin import SelectableComponentMixin
from helper import get_scale

class CanvasLoop(CanvasBox):
    """ Implements behavior for a selectable, movable box on
        a canvas.
    """

    # Displayed label
    label = Property
    _label = Str("Loop")


