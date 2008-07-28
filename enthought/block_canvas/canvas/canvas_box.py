""" Basic movable and labeled box for a Canvas.
"""
# Enthought library imports
from enthought.enable.api import Container
from enthought.kiva import font_metrics_provider
from enthought.traits.api import Any, Bool, Float, Instance, List, on_trait_change, Property, Str

# Local library imports
from canvas_box_style import CanvasBoxStyle
from enable_box_tools import BoxResizeTool, BoxMoveTool, BoxSelectionTool
from enable_button_group import EnableButtonGroup, EnableTopRightButtonGroup
from enable_glyph_button import EnableGlyphButton
from io_field import IOField
from selectable_component_mixin import SelectableComponentMixin
from helper import get_scale

class CanvasBox(Container, SelectableComponentMixin):
    """ Implements behavior for a selectable, movable box on
        a canvas.
    """

    #---------------------------------------------------------------------
    # Component Traits
    #---------------------------------------------------------------------

    # We will handle our own drawing, with rounded corners, no need for
    # default borders or background colors.
    border_visible = False
    bgcolor = "transparent"

    # Due to rounded corners, we'll have to set our own size
    auto_size = False

    # Set unifired draw to True
    unified_draw = Bool(True)

    #---------------------------------------------------------------------
    # CanvasBox Traits
    #---------------------------------------------------------------------

    # Function Call object that this box represents.
    # This corresponds to a statement in the execution model's self.statements
    graph_node = Any()  # Should be a FunctionCall or a GeneralExpression or
                        # something else which satisfies that general interface.

    # TextField cells for the inputs and outputs
    input_fields = List(Any)
    output_fields = List(Any)

    # Height and padding for each TextField cell being laid out
    # Width is determined later by measuring the extents of the text.
    cell_height = Float(12.0)
    cell_padding = Float(1.0)

    # Location of certain useful points in the box
    # fixme: These would be more generic if they were "named" connection points,
    #        and a Box had a list (or dict) of connection points that indicated
    #        locations on the box.  There would be a default set ("upper-left",
    #        "center", etc.), but users could add new ones.
    top_center = Property(depends_on=['position', 'bounds'])
    bottom_center = Property(depends_on=['position', 'bounds'])

    # Displayed label
    label = Property
    _label = Str()

    # Are we displaying the expanded view or the default view?
    # Only relevant if the sashing is being drawn.
    expanded = Bool(True)

    # Have we been set to dimmed?
    dimmed = Bool(False)

    # Have we been set as flagged?
    flagged = Bool(False)

    # The width and height of the body, used to calculate box bounds
    body_bounds = Property

    # The width and height of the sash, used to calculate box bounds
    sash_bounds = Property

    # The width and height of the box
    # width = max(sash width, body width)
    # height = sash_height + body height
    box_bounds = Property

    # Size of the border drawn around group boxes
    border = Float(4.0)

    # The move_tool is being exposed as public because in order to make the 
    # selection_manager work correctly, it must pass the drag events to 
    # all the items in the selection_manager's selection.
    move_tool = Instance(BoxMoveTool)

    #--- Protected traits ------------------------------------------------

    # Group of buttons in right of the sash
    _window_buttons = Instance(EnableButtonGroup)

    # Provides style settings for how the box renders.
    # fixme: We shouldn't have to instantiate one of these, but in order to
    #        add window buttons we need style information
    _style = Instance(CanvasBoxStyle, ())

    # Used by tools to prevent a left up event from clearing the selection
    # after a drag.  This shouldn't be necessary.
    _lock_selection = Bool(False)

    # An object to use to measure text extents
    _font_metrics_provider = Any

    #---------------------------------------------------------------------
    # object interface
    #---------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        """ Override __init__ so that we can initialize bounds.
        """

        self._font_metrics_provider = font_metrics_provider()
        super(CanvasBox, self).__init__(*args, **kwargs)

        self.tools.append(BoxSelectionTool(self))
        self.move_tool = BoxMoveTool(self)
        self.tools.append(self.move_tool)

    #---------------------------------------------------------------------
    # Component interface
    #---------------------------------------------------------------------

    def _draw_container_background(self, gc, view_bounds=None, mode='default'):
        self._draw_box(gc, view_bounds, mode)

    #---------------------------------------------------------------------
    # Interactor interface
    #---------------------------------------------------------------------

    def normal_left_dclick(self, event):
        """ Double click opens the edit dialog for the function.
            FIXME:  Double Click should trigger editing of self.graph_node
        """
        # Explicitly edit a copy of the graph_node and make the replacement
        # ourselves using the scripting layer.
        from enthought.block_canvas.app.scripting import app
        graph_node = self.graph_node.clone_traits()

        # Check the result of editing the traits.  Don't trigger
        # and update if the user hits Cancel button.
        res = graph_node.edit_traits(kind='modal')
        if res.result:
            app.update_node_with_edits(self.graph_node, graph_node)

        event.handled=True


    def normal_left_down(self, event):
        """  If this event occurs in the body of the canvas box, try to clear the
             selection.  Otherwise, let this even pass to tools.
        """
        if self.container and self.event_in_body(event.x, event.y):
            self.container.wiring_tool.clear_selection()
            event.handled = True

    def normal_left_up(self, event):
        """ If this event occurs in the body of the canvas, then set
            event.handled = True so that tools will not get the event.
        """
        if self.container and self.event_in_body(event.x, event.y):
            event.handled = True

    def event_in_body(self, x, y):
        """ Did this event occur in the body area of this box? """
        upper_x = self.x + self.body_bounds[0]
        upper_y = self.y + self.body_bounds[1]
        if ((x > self.x and x < upper_x) and
            (y > self.y and y < upper_y)):
            return True
        return False    

    #---------------------------------------------------------------------
    # CanvasBox interface
    #---------------------------------------------------------------------

    def expand_clicked(self):
        """ Called when the expand button is clicked.
        """
        from enthought.block_canvas.app.scripting import app
        if self.expanded:
            app.collapse_box(self)
        else:
            app.expand_box(self)
        return

    def close_clicked(self):
        """ When close button is clicked, inform our controller to delete
            selected components.
        """
        if self.container:
            if self.selection_state in ['selected','coselected']:
                selection = self.container.selection_manager.selection
            else:
                selection = [self]
            from enthought.block_canvas.app.scripting import app
            for item in selection:
                app.remove_function_from_execution_model(item.graph_node)
        return

    def create_io_fields(self):
        """ Create the input and output cells only when the graph_node is changed.
            These cells will be positioned later before the draw.
        """

        # Clear out any possibly old input/output fields
        self._remove_io_fields()
        self.input_fields = []
        self.output_fields = []

        graph_node = self.graph_node
        inputs = graph_node.inputs
        input_fields = []
        for input in inputs:
            tfield = IOField( graph_node = graph_node, variable = input,
                              height=self.cell_height, type="input", box=self)
            input_fields.append(tfield)
        self.input_fields = input_fields

        outputs = graph_node.outputs
        output_fields = []
        for output in outputs:
            tfield = IOField( graph_node = graph_node, variable = output,
                              height=self.cell_height, type="output", box=self)
            output_fields.append(tfield)
        self.output_fields = output_fields

    def _add_io_fields(self):
        if self.input_fields:
            self.add(*self.input_fields)
        if self.output_fields:
            self.add(*self.output_fields)
        self.position_cells()

    def _remove_io_fields(self):
        if self.input_fields:
            for input in self.input_fields:
                try: self.remove(input)
                except: pass
        if self.output_fields:
            for output in self.output_fields:
                try: self.remove(output)
                except: pass

    def position_cells(self):
        # Align the input and output columns at the same height.
        max_height = max(len(self.input_fields), len(self.output_fields)) * self.cell_height
        if self.input_fields:
            max_input_width = max([field.width for field in self.input_fields])
        else:
            max_input_width = 0
        if self.output_fields:
            max_output_width = max([field.width for field in self.output_fields])
        else:
            max_output_width = 0
        len_input = len(self.input_fields)
        len_output = len(self.output_fields)
        if len_input > len_output:
            output_diff = len_input - len_output
            input_diff = 0
        else:
            output_diff = 0
            input_diff = len_output - len_input

        x = self._style.corner_radius
        y_space = self.cell_height + self.cell_padding
        y = input_diff * y_space + self._style.corner_radius
        # Traverse in reverse order since we're positioning
        # cells from bottom to top
        for i in range(len(self.input_fields)-1, -1, -1):
            cell = self.input_fields[i]
            cell.position = [x,y]
            y = y + y_space

        y = output_diff * y_space + self._style.corner_radius
        x2 = self._style.corner_radius + max_input_width + self.cell_padding + max_output_width
        # Traverse in reverse order since we're positioning
        # cells from bottom to top
        for i in range(len(self.output_fields)-1, -1, -1):
            cell = self.output_fields[i]
            cell.y = y
            cell.x2 = x2
            y = y + y_space
            
    #--- Trait default initializers --------------------------------------

    def __window_buttons_default(self):
        """ Set up the help/expand/close button group in top right corner.
        """

        # Create a button group to hold the window buttons.
        # spacing is the distance between neighboring buttons.
        # offset is the distance from the top-right of this window
        # fixme: y offset should be calculated to be even with the bottom of
        #        the text.
        offset = [self._style.corner_radius,6]
        window_buttons = EnableTopRightButtonGroup(spacing=5, offset=offset,
                                                   auto_size=True)

        # Expand button
        expand_button = EnableGlyphButton(normal_glyph="gray_chevron_down_button",
                over_glyph="gray_chevron_down_button_over")
        expand_button.on_trait_change(self.expand_clicked, 'clicked')
        window_buttons.add(expand_button)

        # Close button.
        close_button = EnableGlyphButton(normal_glyph="gray_close_button",
                over_glyph="gray_close_button_over",
                down_glyph="gray_close_button_down")
        
        close_button.on_trait_change(self.close_clicked, 'clicked')
        window_buttons.add(close_button)

        return window_buttons
    
    #--- Trait listeners -------------------------------------------------

    def _style_changed(self):
        self.invalidate_draw()
        self.request_redraw()

    def _expanded_changed(self):
        height_diff  = self.body_bounds[1]
        if self.expanded:
            self.y -= height_diff
            self._add_io_fields()
            self._window_buttons.components[0].normal_glyph = "gray_chevron_down_button"
            self._window_buttons.components[0].over_glyph = "gray_chevron_down_button_over"
        else:
            self.y += height_diff
            self._remove_io_fields()
            self._window_buttons.components[0].normal_glyph = "gray_chevron_right_button"
            self._window_buttons.components[0].over_glyph = "gray_chevron_right_button_over"
        self.bounds = self.box_bounds
        self.invalidate_draw()
        self.request_redraw()

    @on_trait_change('graph_node')
    def _graph_node_changed(self):
        self._label = self.graph_node.label_name
        self.create_io_fields()
        self._remove_io_fields()
        if self.expanded:
            self._add_io_fields()
        self.bounds = self.box_bounds
        try: self.remove(self._window_buttons)
        except: pass
        self.add(self._window_buttons)
        self.invalidate_draw()
        self.request_redraw()

    #--- Trait property access -------------------------------------------

    def _get_label(self):
        """ If the specified label is too long, truncate it and add '...'
        """
        max_len = self._style.title_maximum_length
        if len(self._label) > max_len:
            return self._label[:max_len-3] + '...'
        else:
            return self._label

    def _get_body_bounds(self):
        """ Compute the width and height of the body.  If expanded is True
            then we need to layout the input and output cells to determine
            the width and height.  Otherwise, return 0,0.
        """
        if self.input_fields:
            max_input_width = max([cell.width for cell in self.input_fields])
        else:
            max_input_width = 0
        if self.output_fields:
            max_output_width = max([cell.width for cell in self.output_fields])
        else:
            max_output_width = 0
        width = max_input_width + max_output_width + 2*self._style.corner_radius + self.cell_padding
        height = max(len(self.input_fields), 
                     len(self.output_fields)) * (self.cell_padding + self.cell_height)
        # Account for space at bottom and at the top
        height += 2*self._style.corner_radius
        return [width, height]

    def _get_sash_bounds(self):
        """ Compute the bounds of the sash. """
        corner_width = self._style.corner_radius * 2
        buttons_width = self._window_buttons.width
        separation_width = 25
        metrics = self._font_metrics_provider
        metrics.set_font(self._style.title_font)
        x, y, tx, ty = metrics.get_text_extent(self.label)
        width = corner_width + tx + separation_width + buttons_width
        height = self._style.sash_height
        return [width, height]

    def _get_box_bounds(self):
        """ Compute the bounds on the canvas box. """
        sash = self.sash_bounds
        body = self.body_bounds

        width = max(sash[0], body[0])
        height = sash[1]
        if self.expanded:
            height += body[1]
        return [width, height]

    def _get_top_center(self):
        """ Return the coords of the top middle of the box.
        """
        return [self.x + self.width/2.0, self.y2+1]

    def _get_bottom_center(self):
        """ Return the coords of the bottom middle of the box.
        """
        return [self.x + self.width/2.0, self.y]

    #--- Private drawing methods -----------------------------------------

    def _draw_box(self, gc, view_bounds=None, mode="default"):
        """ Draw the "window" style of our component.
        """

        gc.save_state()

        # Choose the drawing style, if availabe
        if hasattr(self.container, 'style_manager'):
            if self.selection_state in ['selected', 'coselected']:
                self._style = self.container.style_manager.box_selected_style
            elif self.dimmed:
                self._style = self.container.style_manager.box_dimmed_style
            elif self.flagged:
                self._style = self.container.style_manager.box_flagged_style
            else:
                self._style = self.container.style_manager.box_normal_style

        self._draw_rounded(gc, view_bounds, mode)
        self._draw_sash(gc, view_bounds, mode)
        gc.restore_state()

    def _draw_group_rounded(self, gc, view_bounds=None, mode="default"):
        """ Draw the borders of the function as a rounded rectangle.
            Color, corner_radius, etc. are all taken from a style object.
        """
        x = self.x
        y = self.y
        w = self.width
        h = self.height
        border = self.border
        
        shadow1 = (x+border/2, x+border/2+w, y-border/2, y-border/2+h)
        shadow2 = (x+border, x+border+w, y-border, y-border+h)
        main = (x, x+w, y, y+h)
        for x1, x2, y1, y2 in [shadow2, shadow1, main]:
            gc.save_state()
    
            # Set up the styles.
            gc.set_fill_color(self._style.window_fill_color_)
            gc.set_stroke_color(self._style.window_border_color_)
            gc.set_line_width(self._style.window_border_width)

            radius = self._style.corner_radius
            gc.begin_path()
            gc.move_to(self.x+radius, y1)
            gc.arc_to(x2, y1, x2, y1+radius, radius)
            gc.arc_to(x2, y2, x1, y2, radius)
            gc.arc_to(x1, y2, x1, y1, radius)
            gc.arc_to(x1, y1, x2, y1, radius)
            gc.draw_path()

            gc.restore_state()


    def _draw_rounded(self, gc, view_bounds=None, mode="default"):
        """ Draw the borders of the function as a rounded rectangle.
            Color, corner_radius, etc. are all taken from a style object.
        """
        gc.save_state()

        # Set up the styles.
        gc.set_fill_color(self._style.window_fill_color_)
        gc.set_stroke_color(self._style.window_border_color_)
        gc.set_line_width(self._style.window_border_width)

        # Draw the rounded rect.
        radius = self._style.corner_radius
        gc.begin_path()
        gc.move_to(self.x+radius, self.y)
        gc.arc_to(self.x2, self.y, self.x2, self.y+radius, radius)
        gc.arc_to(self.x2, self.y2, self.x, self.y2, radius)
        gc.arc_to(self.x, self.y2, self.x, self.y, radius)
        gc.arc_to(self.x, self.y, self.x2, self.y, radius)
        gc.draw_path()

        gc.restore_state()

    def _draw_sash(self, gc, view_bounds=None, mode="default"):
        """ Draw the "window sash" at the top of the function box.
            Color, corner_radius, etc. are all taken from a style object.
        """
        gc.save_state()

        # Set up the styles.
        gc.set_fill_color(self._style.sash_fill_color_)
        gc.set_stroke_color(self._style.sash_border_color_)
        gc.set_line_width(self._style.sash_border_width)

        # Draw the sash with rounded top corners and square bottom corners.
        lower, upper = self.y2-self._style.sash_height, self.y2
        left, right = self.x, self.x2

        radius = self._style.corner_radius
        gc.begin_path()
        gc.move_to(left, lower)
        gc.line_to(right, lower)
        gc.arc_to(right, upper, right-radius, upper, radius)
        gc.arc_to(left, upper, left, upper-radius, radius)
        gc.line_to(left, lower)
        gc.draw_path()

        # Now draw the title text.
        gc.set_fill_color(self._style.title_color_)
        gc.set_font(self._style.title_font)

        # Show text at the same scale as graphics context
        scale = get_scale(gc)
        pos = (scale * (self.x + self._style.corner_radius + self._style.title_x_offset),
               scale * (self.y2 - self._style.sash_height + self._style.title_y_offset))
        gc.show_text(self.label, pos)

        gc.restore_state()

    #--- Private methods -------------------------------------------------

    def _update_io_fields(self):
        pass

#EOF


