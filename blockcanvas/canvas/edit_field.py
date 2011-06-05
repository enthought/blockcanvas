# Local imports
from helper import get_scale

# Enthought Library Imports
from enable.api import Component
from enable.colors import ColorTrait
from enable.font_metrics_provider import font_metrics_provider
from enable.trait_defs.api import RGBAColor
from kiva.trait_defs.api import KivaFont
from traits.api import (Any, Bool, Dict, Event, Int, List, Property)


class EditField(Component):
    """ A simplified single-line editable text entry field for Enable.
    """

    #---------------------------------------------------------------------
    # Traits
    #---------------------------------------------------------------------

    # The text on display - with appropriate line breaks
    text = Property(depends_on=['_text_changed'])

    # The list of characters in this text field
    _text = List()

    # Even that fires when the text changes
    _text_changed = Event

    # The current index into the list of characters
    # This corresponds to the user's position
    index = Int(0)

    # Should we draw the cursor in the box?  This only occurs
    # when someone is in edit mode.
    _draw_cursor = Bool(False)

    # The font we're using - must be monospaced
    font = KivaFont("Courier 12")

    # Toggle normal/highlighted color of the text
    text_color = RGBAColor((0,0,0,1.0))
    highlight_color = RGBAColor((.65,0,0,1.0))

    # Toggle normal/highlighted background color
    bgcolor = RGBAColor((1.0,1.0,1.0,1.0))
    highlight_bgcolor = ColorTrait("lightgray")

    # The text offset
    offset = Int(3)

    # The object to use to measure text extents
    metrics = Any

    # Events that get fired on certain key pressed events
    accept = Event
    cancel = Event

    # Can we edit this text field?
    can_edit = Bool(True)

    #---------------------------------------------------------------------
    # Public methods
    #---------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super(EditField, self).__init__(*args, **kwargs)

        if self.metrics is None:
            self.metrics = font_metrics_provider()

        # If no bounds have been set, make sure it is wide enough to
        # display the text
        if self.height == 0 and self.width == 0 and len(self._text) > 0:
            self.update_bounds()

    def update_bounds(self):
            w, h = self.metrics.get_text_extent(self.text)[2:4]
            self.width = w + 2*self.offset
            self.height = h + 2*self.offset

    #---------------------------------------------------------------------
    # Interactor interface
    #---------------------------------------------------------------------

    def normal_left_dclick(self, event):
        # If we can't edit, just return.
        if not self.can_edit:
            return

        event.window.set_pointer('ibeam')
        self.event_state = 'edit'
        self._acquire_focus(event.window)
        event.handled = True
        self.request_redraw()

    def edit_left_up(self, event):
        self.event_state = "normal"
        event.handled = True
        self.request_redraw()

    def normal_character(self, event):
        # handle normal text entry
        char = event.character
        old_len = len(self._text)

        self._text.insert(self.index, char)
        self.index += 1
        self._text_changed = True

        if old_len != len(self._text):
            self.update_bounds()

        event.handled = True
        self.invalidate_draw()
        self.request_redraw()

    def normal_key_pressed(self, event):
        char = event.character
        old_len = len(self._text)

        #Normal characters
        if len(char) == 1:
            # leave unhandled, and let character event be generated
            return

        #Deletion
        elif char == "Backspace":
            if self.index > 0:
                del self._text[self.index-1]
                self.index -= 1
                self._text_changed = True
        elif char == "Delete":
            if self.index < len(self._text):
                del self._text[self.index]
                self._text_changed = True

        #Cursor Movement
        elif char == "Left":
            if self.index > 0:
                self.index -= 1
        elif event.character == "Right":
            if self.index < len(self._text):
                self.index += 1
        elif event.character == "Home":
            self.index = 0
        elif event.character == "End":
            self.index = len(self._text)
        elif event.character == "Enter":
            self.accept = event
        elif char == "Escape":
            self.cancel = event

        if old_len != len(self._text):
            self.update_bounds()

        event.handled = True
        self.invalidate_draw()
        self.request_redraw()


    #---------------------------------------------------------------------
    # Component interface
    #---------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds, mode="default"):

        gc.save_state()

        self.set_font(gc)
        scale = get_scale(gc)
        x = scale * (self.x + self.offset)
        y = scale * self.y
        gc.show_text_at_point(self.text, x, y)

        if self._draw_cursor:
            x += self.metrics.get_text_extent(self.text[:self.index])[2]
            y2 = self.y2 - self.offset
            gc.set_line_width(2)
            gc.set_stroke_color((0,0,0,1.0))
            gc.begin_path()
            gc.move_to(x, y)
            gc.line_to(x, y2)
            gc.stroke_path()

        gc.restore_state()


    def set_font(self, gc):
        gc.set_font(self.font)
        gc.set_fill_color(self.text_color)

    #---------------------------------------------------------------------
    # TextField interface
    #---------------------------------------------------------------------

    def _acquire_focus(self, window):
        self._draw_cursor = True
        self.border_visible = True
        window.focus_owner = self
        window.on_trait_change(self._focus_owner_changed, "focus_owner")
        self.request_redraw()

    def _focus_owner_changed(self, obj, name, old, new):
        if old == self and new != self:
            obj.on_trait_change(self._focus_owner_changed, "focus_owner",
                                remove=True)
            self._draw_cursor = False
            self.border_visible = False
            self.request_redraw()

    #---------------------------------------------------------------------
    # Property get/set and Trait event handlers
    #---------------------------------------------------------------------

    def _get_text(self):
        """ Return the text to be displayed in the text field. """
        return "".join(self._text)

    def _set_text(self, val):
        """ Set the _text given a string. """
        self.index = 0
        if val == "":
            self._text = []
        else:
            self._text = list(val)

    def _accept_changed(self, old, new):
        new.window.focus_owner = None

    def _cancel_changed(self, old, new):
        new.window.focus_owner = None

# EOF
