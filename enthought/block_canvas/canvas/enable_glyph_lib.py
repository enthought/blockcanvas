#!/usr/bin/env python

###################################################################
#
# Copyright Enthought, Inc. 2007
#
# Author: Travis N. Vaught
#
# Revision: 11/21/2007
#
# Glyph library providing various glyph images that are drawn into a graphics
# context (gc).  The gc and the glyph location and dimensions are provided as
# arguments to each function
#
####################################################################
from __future__ import with_statement

# Standard lib imports
from math import acos


def default_glyph(gc, x, y, height, width):
    """ The default 'drawn' image for buttons provided by the 
        glyph library when no other button is found or specified
    """

    with gc:
        # Draw a filled circle as the default image

        gc.set_fill_color((0.2, 0.2, 0.8, 0.8))
        gc.set_stroke_color((0.0, 0.0, 0.0, 0.8))
        gc.begin_path()
        gc.arc(x + width*0.5, y + width*0.5, width*0.5, 0, 2*3.14159)
        gc.draw_path()

    return

def gray_close_button(gc, x, y, height, width):

    with gc:        
        # Draw a filled circle 
        # Transparent for now
        gc.set_fill_color((0.5, 0.5, 0.5, 0.0))
        gc.set_stroke_color((0.5, 0.5, 0.5, 0.0))
        gc.begin_path()
        gc.arc(x + width*0.5, y + width*0.5, width*0.5, 0, 2*3.14159)
        gc.draw_path()


        # Draw 'x'
        radius = width * 0.2
        gc.set_fill_color((1.0, 1.0, 1.0, 1.0))
        gc.set_stroke_color((1.0, 1.0, 1.0, 1.0))
        gc.set_line_width(width*0.1666666)

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y1)
        gc.line_to(x2, y2)
        gc.move_to(x1, y2)
        gc.line_to(x2, y1)
        gc.draw_path()

    return

def gray_close_button_over(gc, x, y, height, width):

    with gc:        
        # Draw a filled circle 
        gc.set_fill_color((1.0, 1.0, 1.0, 0.4))
        gc.set_stroke_color((1.0, 1.0, 1.0, 0.4))
        gc.begin_path()
        gc.arc(x + width*0.5, y + width*0.5, width*0.5, 0, 2*3.14159)
        gc.draw_path()

        # Draw 'x'
        radius = width * 0.2
        gc.set_fill_color((0.0, 0.0, 0.0, 1.0))
        gc.set_stroke_color((0.0, 0.0, 0.0, 1.0))
        gc.set_line_width(width*0.1666666)

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y1)
        gc.line_to(x2, y2)
        gc.move_to(x1, y2)
        gc.line_to(x2, y1)
        gc.draw_path()
        
    return

def gray_close_button_down(gc, x, y, height, width):

    with gc:        
        # Draw a filled circle 
        gc.set_fill_color((0.4, 0.4, 0.4, 0.8))
        gc.set_stroke_color((0.1, 0.1, 0.1, 0.8))
        gc.begin_path()
        gc.arc(x + width*0.5, y + width*0.5, width*0.5, 0, 2*3.14159)
        gc.draw_path()


        # Draw 'x'
        radius = width * 0.2
        gc.set_fill_color((1.0, 1.0, 1.0, 1.0))
        gc.set_stroke_color((1.0, 1.0, 1.0, 1.0))
        gc.set_line_width(width*0.1666666)

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y1)
        gc.line_to(x2, y2)
        gc.move_to(x1, y2)
        gc.line_to(x2, y1)
        gc.draw_path()
       
    return

def gray_chevron_right_button(gc, x, y, height, width):

    with gc:        
        # Draw a filled circle 
        # Transparent for now
        gc.set_fill_color((0.5, 0.5, 0.5, 0.0))
        gc.set_stroke_color((0.5, 0.5, 0.5, 0.0))
        gc.begin_path()
        gc.arc(x + width*0.5, y + width*0.5, width*0.5, 0, 2*3.14159)
        gc.draw_path()

        # Draw chevron pointing down
        radius = width * 0.2
        gc.set_fill_color((1.0, 1.0, 1.0, 1.0))
        gc.set_stroke_color((1.0, 1.0, 1.0, 1.0))
        #gc.set_line_width(width*0.1666666)

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y1)
        gc.line_to(x2, (y1 + y2) * 0.5)
        gc.line_to(x1, y2)
        gc.line_to(x1, y1)
        gc.draw_path()

    return

def gray_chevron_right_button_over(gc, x, y, height, width):

    with gc:        
        # Draw a filled circle 
        gc.set_fill_color((1.0, 1.0, 1.0, 0.4))
        gc.set_stroke_color((1.0, 1.0, 1.0, 0.4))
        gc.begin_path()
        gc.arc(x + width*0.5, y + width*0.5, width*0.5, 0, 2*3.14159)
        gc.draw_path()


        # Draw chevron pointing right
        radius = width * 0.2
        gc.set_fill_color((0.0, 0.0, 0.0, 1.0))
        gc.set_stroke_color((0.0, 0.0, 0.0, 1.0))

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y1)
        gc.line_to(x2, (y1 + y2) * 0.5)
        gc.line_to(x1, y2)
        gc.line_to(x1, y1)
        gc.draw_path()
        
    return

def gray_chevron_down_button(gc, x, y, height, width):

    with gc:        
        # Draw a filled circle 
        # this is transparent for now
        gc.set_fill_color((0.5, 0.5, 0.5, 0.0))
        gc.set_stroke_color((0.5, 0.5, 0.5, 0.0))
        gc.begin_path()
        gc.arc(x + width*0.5, y + width*0.5, width*0.5, 0, 2*3.14159)
        gc.draw_path()


        # Draw chevron pointing right
        radius = width * 0.2
        gc.set_fill_color((1.0, 1.0, 1.0, 1.0))
        gc.set_stroke_color((1.0, 1.0, 1.0, 1.0))

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y2)
        gc.line_to((x1 + x2) * 0.5 , y1)
        gc.line_to(x2, y2)
        gc.line_to(x1, y2)
        gc.draw_path()
        
    return

def gray_chevron_down_button_over(gc, x, y, height, width):

    with gc:        
        # Draw a filled circle 
        gc.set_fill_color((1.0, 1.0, 1.0, 0.4))
        gc.set_stroke_color((1.0, 1.0, 1.0, 0.4))
        gc.begin_path()
        gc.arc(x + width*0.5, y + width*0.5, width*0.5, 0, 2*3.14159)
        gc.draw_path()


        # Draw chevron pointing right
        radius = width * 0.2
        gc.set_fill_color((0.0, 0.0, 0.0, 1.0))
        gc.set_stroke_color((0.0, 0.0, 0.0, 1.0))

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y2)
        gc.line_to((x1 + x2) * 0.5 , y1)
        gc.line_to(x2, y2)
        gc.line_to(x1, y2)
        gc.draw_path()
        
    return

def close_button(gc, x, y, height, width):
        
    with gc:
        # Draw button background
        radius = width/4.0
        gc.set_fill_color((1.0, 0.0, 0.0, 1.0))
        gc.set_stroke_color((0.5, 0.0, 0.0, 1.0))

        gc.begin_path()
        gc.move_to(x + radius, y)
        gc.arc_to(x + width, y, 
                x + width, y + radius, radius)
        gc.arc_to(x + width, y + height,
                x + width - radius, y + height,
                radius)
        gc.arc_to(x, y + height,
                x, y, radius)
        gc.arc_to(x, y,
                x + width + radius, y, 
                radius)
        gc.draw_path()

        # Draw 'x'
        radius = 2.5
        gc.set_fill_color((1.0, 1.0, 1.0, 1.0))
        gc.set_stroke_color((1.0, 1.0, 1.0, 1.0))
        gc.set_line_width(2.0)

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y1)
        gc.line_to(x2, y2)
        gc.move_to(x1, y2)
        gc.line_to(x2, y1)
        gc.draw_path()

    return

def close_button_over(gc, x, y, height, width):

    with gc:
        # Draw button background
        radius = width/4.0
        gc.set_fill_color((1.0, 0.3, 0.3, 1.0))
        gc.set_stroke_color((0.5, 0.2, 0.2, 1.0))

        gc.begin_path()
        gc.move_to(x + radius, y)
        gc.arc_to(x + width, y, 
                x + width, y + radius, radius)
        gc.arc_to(x + width, y + height,
                x + width - radius, y + height,
                radius)
        gc.arc_to(x, y + height,
                x, y, radius)
        gc.arc_to(x, y,
                x + width + radius, y, 
                radius)
        gc.draw_path()

        # Draw 'x'
        radius = 2.5
        gc.set_fill_color((1.0, 1.0, 1.0, 1.0))
        gc.set_stroke_color((1.0, 1.0, 1.0, 1.0))
        gc.set_line_width(2.0)

        gc.begin_path()
        x1 = x + radius + width * 0.05
        x2 = x + width * 0.95 - radius
        y1 = y + radius + width * 0.05
        y2 = y + width * 0.95 - radius

        gc.move_to(x1, y1)
        gc.line_to(x2, y2)
        gc.move_to(x1, y2)
        gc.line_to(x2, y1)
        gc.draw_path()

    return

def io_bullet_up(gc, x, y, height, width):
    _io_bullet_draw(gc, x, y, height, width,
                          fill_color=(0.5, 0.5, 0.5, 1.0),
                          border_color=(0.4, 0.4, 0.4, 1.0))

def io_bullet_over(gc, x, y, height, width):
    _io_bullet_draw(gc, x, y, height, width,
                          fill_color=(0.5, 0.5, 0.5, 0.8),
                          border_color=(0.4, 0.4, 0.4, 1.0),
                          highlight_color=(0.6, 0.8, 0.9, 0.7))

def io_bullet_drag(gc, x, y, height, width):
    _io_bullet_draw(gc, x, y, height, width,
                          fill_color=(0.5, 0.5, 0.5, 0.3),
                          border_color=(0.4, 0.4, 0.4, 0.5))
    
def io_bullet_down(gc, x, y, height, width):
    _io_bullet_draw(gc, x, y, height, width,
                          fill_color=(0.3, 0.3, 0.3, 1.0),
                          border_color=(0.4, 0.4, 0.4, 1.0))
    
def io_bullet_drop_target(gc, x, y, height, width):
    _io_bullet_draw(gc, x, y, height, width,
                          fill_color=(0.3, 0.3, 0.3, 1.0),
                          border_color=(0.4, 0.4, 0.4, 1.0),
                          highlight_color=(0.9, 0.8, 0.6, 0.7))
    
def _io_bullet_draw(gc, x, y, height, width, fill_color, 
                    border_color, highlight_color=(0.0, 0.0, 0.0, 0.0)):
    
    with gc:
        # Draw bounding circle for selection and offset
        radius = width * 0.5
        
        gc.set_fill_color(highlight_color)
        if highlight_color[3]>0.0:
            gc.set_stroke_color((0.1, 0.1, 0.1, 0.5))
        else:
            gc.set_stroke_color((0.0, 0.0, 0.0, 0.0))
        
        gc.begin_path()
        gc.arc(x + width * 0.5,
            y + height * 0.5,
            radius,
            0, 2 * 3.14159)
        gc.draw_path()

        # Draw connector glyph

        #draw_triangle_glyph(gc, x, y, height, width, 
        #                    fill_color, border_color, highlight_color)

        draw_circle_glyph(gc, x, y, height, width, 
                            fill_color, border_color, highlight_color)

        #draw_square_glyph(gc, x, y, height, width, 
        #                    fill_color, border_color, highlight_color)
        
    return

def draw_triangle_glyph(gc, x, y, height, width, fill_color,
                    border_color, highlight_color=(0.0, 0.0, 0.0, 0.0)):
    # Draw triangle glyph
    gc.set_fill_color(fill_color)
    gc.set_stroke_color(border_color)

    gc.begin_path()
    x1 = x + width * 0.2
    x2 = x + width * 0.8
    y1 = y + height * 0.2
    y2 = y + height * 0.8

    gc.move_to(x1, y1)
    gc.line_to(x2, (y1 + y2) * 0.5)
    gc.line_to(x1, y2)
    gc.line_to(x1, y1)
    gc.draw_path()

    return 

def draw_circle_glyph(gc, x, y, height, width, fill_color,
                    border_color, highlight_color=(0.0, 0.0, 0.0, 0.0)):
    # Draw circle glyph
    gc.set_fill_color(fill_color)
    gc.set_stroke_color(border_color)

    radius = width * 0.4

    gc.begin_path()
    gc.arc(x + width * 0.5,
           y + height * 0.5,
           radius,
           0, 2 * 3.14159)
    gc.draw_path()

    return 

def draw_square_glyph(gc, x, y, height, width, fill_color,
                    border_color, highlight_color=(0.0, 0.0, 0.0, 0.0)):
    # Draw square glyph
    gc.set_fill_color(fill_color)
    gc.set_stroke_color(border_color)

    gc.begin_path()
    x1 = x + width * 0.2
    x2 = x + width * 0.8
    y1 = y + height * 0.2
    y2 = y + height * 0.8

    gc.move_to(x1, y1)
    gc.line_to(x2, y1)
    gc.line_to(x2, y2)
    gc.line_to(x1, y2)
    gc.draw_path()

    return 

def _io_pie_draw(gc, x, y, height, width, fill_color, border_color):
    
    with gc:
        # Draw vanguard glyph
        gc.set_fill_color(fill_color)
        gc.set_stroke_color(border_color)
        
        gc.begin_path()
        gc.move_to(x + width/3, y)
        gc.line_to(x + width, y + height/2 - 2)
        gc.arc_to(x + width, y + height/2, 
                x + width, y + height/2 + 2, 3.0)
        gc.line_to(x + width/3, y + height)
        gc.arc_to(x, y + height/2, x + width/3,
                y,
                width * 0.5)
        
        gc.close_path()
        gc.draw_path()

    return



# EOF #######################################################
