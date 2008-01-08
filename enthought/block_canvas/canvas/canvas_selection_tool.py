from numpy import array, dot

from enthought.traits.api import Bool, Float, Instance, Tuple
from enthought.enable2.tools.api import DragTool

from enable_select_box import EnableSelectBox
from canvas_box import CanvasBox


class CanvasSelectionTool(DragTool):

    # The box which is drawn when the user does a drag-select
    select_box = Instance(EnableSelectBox, ())

    # The threshold on the viewport for panning while making a selection
    # using the select_box.
    select_threshold = Float(1.0)

    # Controls whether or not a partially covered box gets selected.
    partial_select = Bool(False)

    # Override some default, inherited traits
    end_drag_on_leave = False
    capture_mouse = True

    # When the mouse is outside the viewport area, the selection box bounds
    # do not necessarily correspond to the mouse position.  This trait
    # tracks the previous mouse position in global screen coordinates.
    _prev_event_pos = Tuple

    # fixme: This is used to prevent a left up event from clearing the selection
    #        after a drag. We shouldn't have to do this, but Enable events are a
    #        little wonky.
    _lock_selection = Bool

    def drag_start(self, event):
        self.delta_x = 0.0
        self.delta_y = 0.0
        component = self.component
        event.offset_xy(component.x, component.y, caller=component)
        if event.control_down or event.shift_down:
            component.selection_manager.add_substract_mode = True
        else:
            component.selection_manager.unselect_all()
        event.window.set_pointer('cross')
        self.select_box.set_drag_start(event.x, event.y)
        component.add(self.select_box)
        component._layout_needed = False
        self.select_box.component = self.component
        self._prev_event_pos = event._pos_stack[0]
        component.request_redraw()
        event.handled = True
        event.pop(caller=component)

    def dragging(self, event):
        # If the event's coordinates exceed the current view x/y/x2/y2, 
        # then adjust the select_box's dimensions appropriately and
        # set the viewport's view_position.
        
        global_coords = event._pos_stack[0]
        deltax = global_coords[0] - self._prev_event_pos[0]
        deltay = global_coords[1] - self._prev_event_pos[1]
        self._prev_event_pos = global_coords

        event.offset_xy(self.component.x, self.component.y, caller=self.component)
        x = event.x
        y = event.y
        viewport = self.component.viewports[0]
        vx, vy = viewport.view_position
        vw, vh = viewport.view_bounds
        vx2 = vx + vw - 1
        vy2 = vy + vh - 1

        delta = 5
        
        new_vx = vx
        if vx2 < x:
            if deltax > 0:
                x = vx2 + delta
                new_vx = vx + delta
            else:
                x = self.select_box.x2
        elif x < vx:
            if deltax < 0:
                x = vx - delta
                new_vx = vx - delta
            else:
                x = self.select_box.x

        new_vy = vy
        if vy2 < y:
            if deltay > 0:
                y = vy2 + delta
                new_vy = vy + delta
            else:
                y = self.select_box.y2
        elif y < vy:
            if deltay < 0:
                y = vy - delta
                new_vy = vy - delta
            else:
                y = self.select_box.y

        xform = self.component.get_event_transform()
        new_coords = dot(array([x,y,1]), xform)
        x, y = new_coords[:2]
        self.select_box.set_drag_dimensions(x, y)
        event.pop(caller=self.component)

        viewport.view_position = [new_vx, new_vy]
        self.component.request_redraw()

    def drag_cancel(self, event):
        event.window.set_pointer('arrow')
        try:
            self.component.remove(self.select_box)
        except RuntimeError:
            pass
        self.component.request_redraw()
       
    def drag_end(self, event):
        if self.partial_select:
            is_in = self.select_box.is_component_in
        else:
            is_in = self.select_box.is_completely_in
        items = [ c for c in self.component.components 
                  if isinstance(c, CanvasBox) and is_in(c) ]
        self.component.selection_manager.select_items(items)
        self.component.selection_manager.add_subtract_mode = False
        self._lock_selection = True
        self.drag_cancel(event)
        self.component._layout_needed = False

    def clear_left_up(self, event):
        """ On left button up, we clear the selection
        """

        if self._lock_selection:
            self._lock_selection = False
        else:
            self.component.selection_manager.unselect_all()
        self.event_state = "normal"

    def normal_left_down(self, event):
        self.event_state = "clear"

    def normal_key_pressed(self, event):
        self._key_pressed(event)

    def clear_key_pressed(self, event):
        self._key_pressed(event)


    def _key_pressed(self, event):
        """ Set up keyboard shortcuts.
        """
        controller = self.component.graph_controller
        mgr = self.component.selection_manager
        from enthought.block_canvas.app import scripting

        # fixme: Get rid of hard coded keys using KeyBindings.
        if event.control_down and event.character == "g":
            # FIXME: Grouping does not currently work
            pass
        elif event.control_down and event.character == "u":
            # FIXME:  Ungrouping does not currently work
            pass
        elif event.character == "Delete":
            for box in mgr.selection:
                scripting.app.remove_function_from_execution_model(box.graph_node)
        elif event.character == "Esc":
            mgr.unselect_all()


