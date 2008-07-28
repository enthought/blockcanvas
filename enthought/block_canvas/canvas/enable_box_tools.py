
# Enthought library imports
from enthought.enable.api import BaseTool
from enthought.enable.tools.api import DragTool
from enthought.traits.api import Any, Event, Bool, Float, Int, List, Tuple


class BoxResizeTool(DragTool):

    _last_drag_pos = Tuple

    def drag_start(self, event):
        event.window.set_mouse_owner(self, event.net_transform(),
                                     history=event.dispatch_history)
        self._last_drag_pos = (event.x, event.y)
        event.handled = True

    def drag_cancel(self, event):
        self.drag_end(event)

    def drag_end(self, event):
        event.window.set_mouse_owner(None)
        event.handled = True
        self.component.request_redraw()

    def dragging(self, event):
        """ Implements the resize behavior while the user is dragging on
            an edge of the box
        """

        # Resizing, ensure that the box does not get smaller than the 
        # minimum bounds
        component = self.component
        xmin, ymin = component.normal_bounds
        if component.resizable_y:
            y_diff = self._last_drag_pos[1] - event.y
            if ymin < component.height + y_diff:
                component.y -= y_diff
                component.height += y_diff
        if component.resizable_x:
            x_diff = event.x - self._last_drag_pos[0]
            component.width = max(component.width + x_diff, xmin)
        self._last_drag_pos = (event.x, event.y)

        event.handled = True
        component.request_redraw()


class BoxMoveTool(DragTool):

    # The number of pixels to move if the mouse is outside of the viewport
    move_amount = Int(30)

    # The number of seconds between each staggered move when the the mouse
    # is outside of the viewport
    move_delay = Int(0.02)

    # This event is how the Enable timer notifies us.     
    timer = Event()

    # Override the inherited value of this from DragTool
    end_drag_on_leave = False

    # Whether or not the timer has been set
    _timer_set = Bool(False)

    # The enable Window through which we set the timer
    _timer_window = Any()
    
    # The amount by which to drag the box in the X and Y directions when the
    # mouse is outside of the viewport.  Unlike move_amount, these are signed
    # values that depend on where the mouse is relative to the viewport.
    _timer_drag_x = Int()
    _timer_drag_y = Int()

    # The offset of the mouse down position from the component's position
    # when drag is initiated.
    _component_offset = Tuple

    def drag_start(self, event):
        """ Prepare for potential drag operation.

            Save out the current location as well as the mouse position from
            the event.
        """
        # If the item is not already selected, make sure it is
        mgr = self.component.selection_manager
        if self.component not in mgr.selection:
            mgr.add_subtract_mode = (event.control_down or event.shift_down)
            mgr.select_item(self.component)

        self._component_offset = (event.x - self.component.x, 
                                  event.y - self.component.y)
        event.handled = True

    def dragging(self, event):
        # Check to see if the event fell outside the viewport, if so, then
        # start a timer (if it has not been started already).  If a timer has
        # been started and the event fell back inside the bounds, then get
        # rid of it.
        
        # Use the position in global coordinates.
        # FIXME: can we avoid reaching into the protected _pos_stack list?
        x, y = event._pos_stack[0]
        viewport = self.component.container.viewports[0]
        vx, vy = viewport.position
        vw, vh = viewport.bounds
        vx2 = vx + vw - 1
        vy2 = vy + vh - 1

        unset_timer = True
        if (x > vx2) or (x < vx): 
            if not self._timer_set:
                self._start_timer(event.window)
                if x < vx:
                    self._timer_drag_x = -self.move_amount
                else:
                    self._timer_drag_x = self.move_amount
            unset_timer = False
        else:
            self._timer_drag_x = 0
            
        if (y > vy2) or (y < vy):
            if not self._timer_set:
                self._start_timer(event.window)
                if y < vy:
                    self._timer_drag_y = -self.move_amount
                else:
                    self._timer_drag_y = self.move_amount
            unset_timer = False
        else:
            self._timer_drag_y = 0

        # If both x and y fell inside the viewport, turn off the timer
        if unset_timer:
            self._timer_set = False

        # It is important to check self._timer_set because we may actually
        # get mouse_move (and therefore dragging) events while the timer is
        # set due to the way that WX prioritizes events.
        if not self._timer_set:

            delta_x = event.x - self.component.x - self._component_offset[0]
            delta_y = event.y - self.component.y - self._component_offset[1]
            self._move_component(delta_x, delta_y)

        event.handled = True
        return

    def _start_timer(self, window):
        window.set_timer_interval(self, self.move_delay)
        self._timer_window = window
        self._timer_set = True

    def _end_timer(self, window):
        if window:
            window.set_timer_interval(self, None)
        self._timer_window = None
        self._timer_set = False

    def drag_cancel(self, event):
        """ A drag cancel is the same as a drag end.
        """
        self.drag_end(event)

    def drag_end(self, event):
        """ Release the mouse owner and notifiy the selection manager that we
            are done dragging.
        """
        if self._timer_set:
            self._end_timer(self._timer_window)
        self.component._lock_selection = True
        event.window.set_mouse_owner(None)
        event.handled = True

    def _timer_fired(self):
        # FIXME: Sometimes a timer will be left running; it's not clear what
        # sequence of events leads to this, but this will catch it and remove
        # the timer.
        if not self._timer_set:
            self._end_timer(self._timer_window)
        else:
            self._move_component(self._timer_drag_x, self._timer_drag_y)

    #def lost_focus(self, window):
    #    # Called by the window when we are no longer the mouse owner
    #    print "lost focus on window", window
    #    self._end_timer(window)

    def _move_component(self, delta_x, delta_y, notify_mgr=True):
        """ Moves our component by delta_x and delta_y.  Adjusts the viewport
        properly if the component or the set of selections moves outside
        the viewport.
        """
        self.component.x += delta_x
        self.component.y += delta_y

        if not notify_mgr:
            return

        mgr = self.component.selection_manager

        # Scroll the viewports if necessary
        min_x = min(mgr.selection, key=lambda c: c.x).x
        min_y = min(mgr.selection, key=lambda c: c.y).y
        max_x = max(mgr.selection, key=lambda c: c.x2).x2
        max_y = max(mgr.selection, key=lambda c: c.y2).y2
        for vp in self.component.container.viewports:
            # If the entire selection can't fit within the viewport's bounds,
            # don't bother scrolling it
            for minval, maxval, ndx in [(min_x, max_x, 0), (min_y, max_y, 1)]:
                if maxval - minval < vp.view_bounds[ndx]:
                    if minval < vp.view_position[ndx]:
                        vp.view_position[ndx] = minval
                    elif maxval > vp.view_position[ndx] + vp.view_bounds[ndx]:
                        vp.view_position[ndx] = maxval - vp.view_bounds[ndx]

        # Notify selection manager
        if len(mgr.selection) > 0:
            mgr.move_selection(delta_x, delta_y, source=self.component)

        self.component.invalidate_draw()
        self.component.request_redraw()


class BoxSelectionTool(BaseTool):
    """
    Handles a box being clicked and selected.
    """
    
    def normal_left_up(self, event):
        """ Mouse went down and came straight up on item.

            This will either add or remove the mouse from the selection based
            on control key settings.
        """
        
        event.handled = True

        # Make sure that this left up event is not after a drag
        if self.component._lock_selection:
            self.component._lock_selection = False
            return 

        # Hand event into selection_manager to make decision on selection.
        mgr = self.component.selection_manager
        if mgr is not None:
            mgr.add_subtract_mode = (event.control_down or
                                     event.shift_down)
            mgr.select_item(self.component)


