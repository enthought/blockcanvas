# Standard Library imports
import copy

# Enthought Library imports
from traits.api import Any, Bool, Instance, Int, List, Tuple
from enable.api import AbstractOverlay
from enable.tools.api import DragTool
from enable.trait_defs.rgba_color_trait import RGBAColor
from pyface.action.api import Group, MenuManager

# Local imports
from canvas_box import CanvasBox
from io_field import IOField
from wiring_menu_actions import AddSuffixAction, ChangeSuffixAction


class WiringTool(AbstractOverlay, DragTool):
    """ A tool that enables the user to wire inputs and outputs on the canvas.
    """

    #---------------------------------------------------------------------
    # WiringTool traits
    #---------------------------------------------------------------------

    # The width of the line being drawn
    line_width = Int(2)

    # The color of the line
    line_color = RGBAColor((0.5, 0.5, 0.5, 0.8))

    # Should we draw the line and icon?
    draw_line  = Bool(False)

    # (x,y) coordinates for the start of line.
    _start_pos = Tuple

    # (x,y) coordinates for the end of line.
    _end_pos = Tuple

    # References to the beginning and ending of the Input/Output Fields
    # that are being hooked up.
    _start_field = Instance(IOField)
    _end_field = Instance(IOField)

    # The selected fields
    input_selected_fields = List(IOField)
    output_selected_fields = List(IOField)

    # The Context Menu - brought up by right clicking on selected fields
    menu = Instance(MenuManager)
    edit_group = Any

    def __init__(self, *args, **kwargs):
        self.make_menu()
        super(WiringTool, self).__init__(*args, **kwargs)
        self.input_selected_fields = []
        self.output_selected_fields = []
        return

    def make_menu(self):
        self.edit_group = Group(
            AddSuffixAction(),
            ChangeSuffixAction(),
            )

        self.menu = MenuManager(self.edit_group)

    #---------------------------------------------------------------------
    # Interactor traits
    #---------------------------------------------------------------------

    def normal_left_down(self, event):
        """ Add this box_field to the selection.
        """
        field = self._get_underlying_box_field(event.x, event.y)
        if field:
            # Toggle selection - if already selected, then un-select
            if field.selected:
                self.remove_from_selection(field)
            else:
                self.add_to_selection(field)
        else:
            self.clear_selection()
            event.window.focus_owner = self.component
        event.handled = True
        self.request_redraw()

    def normal_left_dclick(self, event):
        """ Edit the name of this input/output.
        """
        field = self._get_underlying_box_field(event.x, event.y)
        if not field:
            return
        text_field = field.value
        self.event_state = "edit"
        text_field.normal_left_dclick(event)
        try: self.remove_from_selection(field)
        except: pass
        event.handled = True

    def edit_left_up(self, event):
        """ FIXME?  This is just to capture the event and pass it down
            into the EditField.
        """
        field = self._get_underlying_box_field(event.x, event.y)
        if not field:
            event.window.focus_owner = self.component
        field.value.edit_left_up(event)
        self.event_state = "normal"
        event.handled = True


    def normal_right_down(self, event):
        """ Right click will bring up a dialog to edit the
            prefix/suffix of the selected variables.
        """
        field = self._get_underlying_box_field(event.x, event.y)
        if field:
            selected_fields = self.input_selected_fields + self.output_selected_fields
            if field in selected_fields:
                for group in self.menu.groups:
                    for action_item in group.items:
                        action = action_item.action
                        action.container = self.component
                        action.selected_fields = selected_fields
                menu = self.menu.create_menu(event.window.control)

                if len(event._pos_stack) > 0:
                    real_x, real_y = event._pos_stack[0]
                else:
                    real_x, real_y = event.x, event.y
                from pyface.api import GUI
                GUI.invoke_later(menu.show, real_x - 10, event.window._flip_y(real_y))
                self.component.request_redraw()
        event.handled = True

    def add_to_selection(self, field):
        if not field.selected:
            field.set_selected()
            if field.type == 'input':
                self.input_selected_fields.append(field)
            else:
                self.output_selected_fields.append(field)

    def remove_from_selection(self, field):
        if field.selected:
            field.clear_selected()
            if field.type == 'input':
                self.input_selected_fields.remove(field)
            else:
                self.output_selected_fields.remove(field)

    #---------------------------------------------------------------------
    # DragTool interface
    #---------------------------------------------------------------------

    def drag_start(self, event):
        field = self._get_underlying_box_field(event.x, event.y)
        if not field:
            return

        self.add_to_selection(field)
        self._start_field = field
        event.window.set_mouse_owner(self, event.net_transform(),
                                     history=event.dispatch_history)
        self._start_pos = self._get_anchor_point(field)
        event.handled = True

    def drag_cancel(self, event):
        event.window.set_mouse_owner(None)
        self.clear_selection()
        self.draw_line = False
        event.handled = True
        self.component.request_redraw()

    def drag_end(self, event):
        field = self._get_underlying_box_field(event.x, event.y)
        if field is self._start_field:
            return

        if field and self._start_field:
            self._end_field = field
            start_type = self._start_field.type
            end_type = self._end_field.type
            field.icon.bullet_state = 'up'
            if ((start_type == 'output' and end_type == 'input') or
                (start_type == 'input' and end_type == 'output')):
                self.add_to_selection(self._end_field)
                if len(self.input_selected_fields) == len(self.output_selected_fields):
                    matches = self.match_inputs2outputs()
                    for input, pairs in matches.items():
                        for pair in pairs:
                            from blockcanvas.app.scripting import app
                            # Set the input (pair[0]) binding to output(pair[1])
                            app.update_function_variable_binding(field.box.graph_node,
                                                                 pair[0],
                                                                 pair[1].binding)
        self.drag_cancel(event)

    def dragging(self, event):
        field = self._get_underlying_box_field(event.x, event.y)
        if field is self._start_field:
            if self.draw_line:
                self.draw_line = False
                self.request_redraw()
            return
        self.draw_line = True
        pos = (event.x, event.y)
        self.clear_end_field()
        if field and self._start_field:
            start_type = self._start_field.type
            if ((start_type == 'input' and field.type == 'output') or
                (start_type == 'output' and field.type == 'input')):
                pos = self._get_anchor_point(field)
                field.icon.bullet_state = "dropping"
                self._end_field = field
        self._end_pos = pos
        event.handled = True
        self.component.request_redraw()

    def match_inputs2outputs(self):
        if len(self.input_selected_fields) == 1:
            input = self.input_selected_fields[0].variable
            output = self.output_selected_fields[0].variable
            return {self.input_selected_fields[0]: [(input, output)]}

        # FIXME: Need better way to match inputs and outputs.
        matches = {}
        for infield in self.input_selected_fields:
            for outfield in self.output_selected_fields:
                input = infield.variable.binding
                output = outfield.variable.binding
                if input.find(output) >= 0 or output.find(input) >= 0:
                    if matches.has_key(infield):
                        matches[infield].append((input, output))
                    else:
                        matches[infield] = [(input, output)]
        return matches

    def clear_end_field(self):
        if self._end_field:
            self._end_field.clear_selected()
            self._end_field = None


    def clear_selection(self):
        selected = self.input_selected_fields + self.output_selected_fields
        for field in selected:
            field.clear_selected()
        self.input_selected_fields = []
        self.output_selected_fields = []
        self._start_field = None
        self._end_field = None
        self.request_redraw()

    #---------------------------------------------------------------------
    # private interface
    #---------------------------------------------------------------------


    def _get_anchor_point(self, field):
        x_pos = field.box.x + field.x + field.icon.x + field.icon.width/2
        y_pos = field.box.y + field.y + field.icon.y + field.icon.height/2
        return (x_pos, y_pos)

    def _get_underlying_box_field(self, x, y):
        """ Returns either the underlying input or output field under the mouse or None.
            BlockCanvas -> CanvasBox ->  IOField -> EnableBoxField
        """
        canvas_components = self.component.components_at( x, y )
        for c in canvas_components:
            if isinstance(c, CanvasBox):
                box_components = c.components_at( x, y )
                for b in box_components:
                    if isinstance(b, IOField):
                        return b
                break
        return None

    #---------------------------------------------------------------------
    # AbstractOverlay interface
    #---------------------------------------------------------------------

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        if not self.draw_line:
            return

        gc.save_state()

        # Set up the styles
        gc.set_stroke_color(self.line_color_)
        gc.set_line_width(self.line_width)

        gc.begin_path()
        gc.move_to(self._start_pos[0], self._start_pos[1])
        gc.line_to(self._end_pos[0], self._end_pos[1])
        gc.draw_path()

        # FIXME: not sure whether this is the way to copy this.
        # Suggestions welcome.
        icon = copy.deepcopy(self._start_field.icon)
        icon.event_state = 'normal'
        icon.position = [self._end_pos[0] - icon.width*0.5, self._end_pos[1] - icon.height*0.5]
        icon.bullet_state = "dragging"
        icon._draw_mainlayer(gc, view_bounds=view_bounds)

        gc.restore_state()

        return

#EOF
