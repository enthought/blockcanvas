# Enthought library imports
from enthought.enable.api import TextFieldStyle
from enthought.traits.api import Float, HasTraits, Instance, Tuple

# Local imports
from canvas_box_style import CanvasBoxStyle


class StyleManager(HasTraits):
    """ A style manager for Enable components to query for style information.
        fixme: Style information is hardcoded!
    """

    # Enable box styles
    box_normal_style = Instance(CanvasBoxStyle, ())
    box_selected_style = Instance(CanvasBoxStyle)
    box_dimmed_style = Instance(CanvasBoxStyle)
    box_flagged_style = Instance(CanvasBoxStyle)

    # Enable line style information
    line_bg_color = Tuple((.9, .9, .9, 1.0))
    line_edge_color = Tuple((.6, .6, .6, 1.0))

    # Text field style information
    text_field_style = Instance(TextFieldStyle, ())

    # Bullet style information
    # FIXME: not used currently because when we instantiate the bullets, the
    # IOField does not know about its container (nor its
    # containers style_manager).
    bullet_input_color = Tuple((0.7, 0.7, 0.7, 0.8))
    bullet_output_color = Tuple((0.3, 0.3, 0.3, 0.8))
    bullet_hover_border_color = Tuple((0.9, 0.9, 0.9, 0.8))
    bullet_drag_color = Tuple((0.8, 0.8, 0.8, 0.4))

    # Port style information
    port_radius = Float(5.0)
    port_border_color = Tuple((0.5, 0.5, 0.5, 1.0))
    port_in_color = Tuple((0.5, 0.5, 0.5, 1.0))
    port_out_color = Tuple((0.5, 0.5, 0.5, 1.0))


    #########################################################################
    # StyleManager inferface
    #########################################################################

    ##### Trait default initializers ########################################

    def _box_selected_style_default(self):
        return CanvasBoxStyle(sash_fill_color=(.9, .65, .1, 1.0),
                              sash_border_color=(.56, .4, .06, 1.0),
                              window_border_color=(.56, .4, .06, 1.0))

    def _box_dimmed_style_default(self):
        return CanvasBoxStyle(sash_fill_color=(.75, .75, .75, 1.0))

    def _box_flagged_style_default(self):
        return CanvasBoxStyle(sash_fill_color=(.65, 0, 0, 1.0))
