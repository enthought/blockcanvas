# Enthought Library imports
from enthought.block_canvas.function_tools.function_variables import Variable
from enthought.traits.api import Any, Bool, Instance, on_trait_change, Str

# Local imports
from edit_field import EditField

class EnableBoxField(EditField):
    """
        A draggable/droppable component that will represent
        inputs and outputs in the enable blocks on the canvas.
    """

    #---------------------------------------------------------------------
    # Public traits
    #---------------------------------------------------------------------

    # Are multiple lines of text allowed?
    multiline = Bool(False)

    # Is this field flagged?
    flagged = Bool(False)

    # Text - used when renaming variables by typing in the text field.
    unmodified_text = Str

    # The variable and binding that this text field represents
    variable = Instance(Variable)

    # The EnableBox that holds this text field
    # This box ties the graph_node (FunctionCall/GeneralExpression)
    # to the visual elements on the screen.
    box = Any

    #---------------------------------------------------------------------
    # Public methods
    #---------------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        super(EnableBoxField, self).__init__(*args, **kwargs)
        self.set_font(self.metrics)
        self.update_bounds()
        self.bgcolor = "clear"
    
    def update_bounds(self):
        # Update the bounds on the text field and the bounds on the containers
        self.set_font(self.metrics)
        x, y, width, height = self.metrics.get_text_extent(self.text)
        self.width = width + 2*self.offset
        if self.box:
            self.box.position_cells()

    def set_font(self, gc):
        color = self.text_color
        if self.flagged:
            color = self.highlight_color
        gc.set_font(self.font)
        gc.set_fill_color(color)


    @on_trait_change('variable.binding')
    def variable_binding_changed(self, event=None):
        if self.box and self.metrics:
            self._build_text()

    #---------------------------------------------------------------------
    # Trait Listeners
    #---------------------------------------------------------------------

    @on_trait_change('variable.satisfied')
    def _variable_satisfied_changed(self):
        """ When an (usually) InputVariable changes its satisfied status, flag
        ourselves as appropriate.
        """
        flagged = not self.variable.satisfied
        if flagged != self.flagged:
            self.flagged = flagged
            self.request_redraw()

    def _accept_changed(self, old, new):
        # Rename the variable when the accept event has been fired.
        # This event should only be fired when <Enter> is pressed
        # when the text field has focus.
        self._try_rename()

    def _acquire_focus(self, window):
        self.bgcolor = "white"
        self._draw_cursor = True
        window.focus_owner = self
        window.on_trait_change(self._focus_owner_changed, "focus_owner")
        self.request_redraw()

    def _focus_owner_changed(self, obj, name, old, new):
        # If we lose focus, rename the variable or reset the text
        if old == self and new != self:
            self._draw_cursor = False
            self.bgcolor = "clear"
            if self.text != self.unmodified_text:
                self._try_rename()

    def _try_rename(self):
        if self.text:
            # Try to change the function definition's binding
            old_var = self.unmodified_text.strip()
            new_var = self.text.strip()
            from enthought.block_canvas.app.scripting import app
            app.update_function_variable_binding(self.box.graph_node, self.variable, new_var)
            
    def _set_text(self, val):
        super(EnableBoxField, self)._set_text(val)
        self.unmodified_text = self.text
        self.request_redraw()

    def _variable_changed(self, old, new):
        self._build_text()

    def _build_text(self):
        if self.variable:
            self.text = str(self.variable.binding)
        else:
            self.text = ''

#EOF
