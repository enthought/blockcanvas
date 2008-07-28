""" Simple line that has its end points connected to "connection points" on
    other items on the canvas.  Whenever those items move, this line will
    update its position and redraw accordingly.
"""

# Enthought library imports
from enthought.traits.api import Enum, Float, Instance, on_trait_change
from enthought.enable.api import Component, ColorTrait

# Local imports
from canvas_box import CanvasBox
from simple_math import distance_to_line, point_in_box


class EnableLine(Component):
    """ This class handles drawing the connection lines between CanvasBoxes.

        The lines position and bounds are calculated as the bounding box of the
        actual line.  Its hit test (is_in) method is overidden to hittest on
        the line instead of its bounding box.
    """

    #########################################################################
    # EnableLine traits
    #########################################################################

    # CanvasBox who's output is the start of the line
    start_node = Instance(CanvasBox)

    # CanvasBox who's input is the end of the line
    end_node = Instance(CanvasBox)
    
    # Whether to draw as a straight line or a bezier curve
    curve_type = Enum('line', 'curve')

    #########################################################################
    # Component traits
    #########################################################################

    bgcolor = "transparent"
    
    #########################################################################
    # CoordinateBox interface
    #########################################################################

    def is_in(self, x, y):
        """ Hit test the line.  This method test whether we
            are within some distance (tolerance) of the line
            segment.
        """
        # fixme: This is likely to get slow for large numbers
        #        of lines.
        pt1 = self.start_node.bottom_center
        pt2 = self.end_node.top_center
        mouse = [x,y]

        # How close to the line do we have to be?
        tolerance = 3

        # If the length of the enable_line is 0, returning False
        xdiff, ydiff = pt1[0]-pt2[0], pt1[1]-pt2[1]

        if xdiff <= 0 or ydiff <= 0:
            result = False
        elif (distance_to_line(pt1, pt2, mouse) < tolerance and
            point_in_box(pt1, pt2, mouse, tolerance)):
            result = True
        else:
            result = False

        return result


    #########################################################################
    # Component interface
    #########################################################################

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
        """ Draw a line from the start function's output position to the
            end function's input position.
            fixme: Bezier curves only work if the blocks are laid out vertically
            fixme: Color and width should be part of a style, as they should
                   also be in the function box
        """
        
        if self.curve_type == "curve":
            self._draw_bezier(gc)
        else:
            self._draw_line(gc)
        return
    
    def _draw_ports(self, gc):
        gc.save_state()
        start = self.start_node.bottom_center
        end = self.end_node.top_center
        
        gc.set_stroke_color(self.container.style_manager.port_border_color)
        
        # Draw Port Out
        gc.set_fill_color(self.container.style_manager.port_out_color)
        gc.begin_path()
        gc.arc(start[0], start[1], self.container.style_manager.port_radius,
                3.14159, 2 * 3.14159)
        gc.close_path() 
        gc.draw_path()
        
        # Draw Port In
        gc.set_fill_color(self.container.style_manager.port_in_color)
        gc.begin_path()
        # seems to be off by one, so subtract one
        gc.arc(end[0], end[1]-1, self.container.style_manager.port_radius,
                0,  3.14159)
        gc.close_path()
        gc.draw_path()
        
        gc.restore_state()

    def _draw_line(self, gc):
        gc.save_state()
        start = self.start_node.bottom_center
        end = self.end_node.top_center
        gc.set_fill_color(self.container.style_manager.line_edge_color)
        gc.set_line_width(2.0)
        gc.begin_path()
        gc.move_to(start[0], start[1])
        gc.line_to(end[0], end[1])
        gc.stroke_path()
        
        gc.restore_state()
        
        self._draw_ports(gc)

    def _draw_bezier(self, gc):
        gc.save_state()

        start = self.start_node.bottom_center
        end = self.end_node.top_center
        # control points for bezier curves...
        y_diff = abs(start[1] - end[1])
        control1 = [ start[0], start[1]-y_diff ]
        control2 = [ end[0], end[1]+y_diff ]
        width = 2.5

        # Draw the bezier curve which is background of the line
        gc.set_stroke_color(self.container.style_manager.line_bg_color)
        gc.set_line_width(width*2)
        gc.begin_path()
        gc.move_to(start[0], start[1])
        gc.curve_to(control1[0], control1[1],
                    control2[0], control2[1],
                    end[0], end[1])
        gc.stroke_path()

        # Draw the two bezier curves which make up line's edges
        gc.set_stroke_color(self.container.style_manager.line_edge_color)
        gc.set_line_width(1)
        gc.begin_path()
        if start[0] <= end[0]:
            gc.move_to(start[0]-width, start[1])
            gc.curve_to(control1[0]-width, control1[1]-width,
                        control2[0]-width, control2[1]-width,
                        end[0]-width, end[1])
            gc.move_to(start[0]+width, start[1])
            gc.curve_to(control1[0]+width, control1[1]+width,
                        control2[0]+width, control2[1]+width,
                        end[0]+width, end[1])
        else:
            gc.move_to(start[0]-width, start[1])
            gc.curve_to(control1[0]-width, control1[1]+width,
                        control2[0]-width, control2[1]+width,
                        end[0]-width, end[1])
            gc.move_to(start[0]+width, start[1])
            gc.curve_to(control1[0]+width, control1[1]-width,
                        control2[0]+width, control2[1]-width,
                        end[0]+width, end[1])
        gc.stroke_path()
        gc.restore_state()

        self._draw_ports(gc)

    #########################################################################
    # EnableLine interface
    #########################################################################

    ### Trait change listeners ##############################################

    @on_trait_change('start_node, start_node:bottom_center, end_node, \
                      end_node:top_center, container')
    def _update(self):
        if None in (self.start_node, self.end_node):
            return
        p1 = self.start_node.bottom_center
        p2 = self.end_node.top_center
        x = min(p1[0], p2[0])
        x2 = max(p1[0], p2[0])
        y = min(p1[1], p2[1])
        y2 = max(p1[1], p2[1])
        self.position = [x,y]
        # Don't let bounds be set to 0, otherwise, horizontal and vertical
        # lines will not render because enable skips rendering items with
        # bounds=[0,0]
        self.bounds = [max(x2-x,1), max(y2-y,1)]
    
        # avoid firing too many request_redraws on the block_canvas; if our
        # position changes, it's usually in response to a block moving, which
        # will cause the canvas to update properly
        #self.request_redraw()
