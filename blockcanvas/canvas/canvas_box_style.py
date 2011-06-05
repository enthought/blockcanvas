from traits.api import HasTraits, Int
from enable.kiva.trait_defs.kiva_font_trait import KivaFont
from enable.trait_defs.rgba_color_trait import RGBAColor



class CanvasBoxStyle(HasTraits):
    """ This class holds style settings for rendering an EnableBox on the canvas.

        I don't think this is the way styles should be implemented really.
        It seems that there should be some attempt to match string names that
        are looked up. instead of this hard coded naming approach.  This isn't
        my area, but something like CSS seems like it would be better.  I'll
        leave this to some other style guru.

        So, this class exists to make it easy to play with different rendering
        styles of function boxes and switch the entire set out on the fly.
    """

    # Radius for rounded corners.
    corner_radius = Int(7)

    # Height of window sash.
    sash_height = Int(20)

    # Fill color for window sash.
    sash_fill_color = RGBAColor((.5,.5,.5))
    sash_border_color = RGBAColor((.6,.6,.6))
    sash_border_width = Int(1)

    window_fill_color = RGBAColor((.9,.9,.9))
    window_border_color = RGBAColor((.6,.6,.6))
    window_border_width = Int(1)


    # Offset from left corner in sash
    title_x_offset = Int

    # Offset from bottom of sash
    title_y_offset = Int(4)

    # Color for Box label.
    title_color = RGBAColor('white', style='simple')

    # fixme: Should KivaFont be like colors with a shadow attribute?
    title_font = KivaFont("Arial 15")

    # Maximum number of characters to display for title.
    title_maximum_length = Int(20)

    # Color for the body text (main text of the box)
    body_color = RGBAColor('black', style='simple')

    # Font for body text
    body_font = KivaFont("Arial 12")
