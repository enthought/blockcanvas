# Enthought Library imports
from enthought.block_canvas.function_tools.function_variables import Variable
from enthought.enable.api import ColorTrait, Container
from enthought.traits.api import Any, Bool, Enum, Float, Instance, Tuple

# Local imports
from edit_field import EditField
from enable_box_field import EnableBoxField
from enable_bullet import Bullet

def is_a_context_variable(obj):
    """ Check if an object is a ContextVariable instance or something close
    enough to it for our purposes.
    """
    # Do a duck-type check rather than importing.
    return (hasattr(obj, 'name') and hasattr(obj, 'value'))


class IOField(Container):
    """
        A container that holds a variable's icon, label, and binding info.
    """

    #---------------------------------------------------------------------
    # Public traits
    #---------------------------------------------------------------------

    # The variable and binding that this text field represents
    variable = Instance(Variable)

    # Does this field represent an input or output?
    type = Enum("input", "output")

    # Has this field been selected by the wiring tool?
    selected = Bool(False)

    # Wiring target icon for this input/output
    icon = Instance(Bullet)

    # Label for this variable
    label = Instance(EditField)

    # The x offset from the edge of the IOField so that we won't
    # lose mouse enter events.
    x_offset = Float(2.0)

    # The EnableBox that contains this field
    # This box ties the graph_node (FunctionCall/GeneralExpression)
    # to the visual elements on the screen.
    box = Any

    # Binding information for the variable
    value = Instance(EnableBoxField)

    cell_height = Float(15.0)
    label_width = Float(25.0)

    highlight_color = (.5, .5, .5, .25)
    border_visible = Bool(False)

    # Bullet style information
    # FIXME: should be in style_manager when we figure out how to look these
    # styles up over several layers.
    bullet_input_color = Tuple((0.7, 0.7, 0.7, 0.8))
    bullet_output_color = Tuple((0.7, 0.7, 0.7, 0.8))


    #---------------------------------------------------------------------
    # Public methods
    #---------------------------------------------------------------------

    def __init__(self, variable, *args, **kwargs):
        super(IOField, self).__init__(*args, **kwargs)
        self.variable = variable
        self.add(self.icon)
        self.add(self.label)
        self.add(self.value)
        self.width = self.icon.width + self.label.width + self.value.width + 2*self.x_offset
        if self.type == "input":
            self.icon.position = [self.x_offset,0]
            self.label.position = [self.icon.x2,0]
            self.value.position = [self.label.x2, 0]
        else:
            self.label.position = [0,0]
            self.value.position = [self.label.x2, 0]
            self.icon.position = [self.value.x2+self.x_offset, 0]
        self.bgcolor = "clear"

    def clear_selected(self):
        self.selected = False
        self.icon.bullet_state = 'up'

    def set_selected(self):
        if not self.selected:
            self.selected = True

    #---------------------------------------------------------------------
    # Interactor interface
    #---------------------------------------------------------------------

    def normal_mouse_enter(self, event):
        if self._box_on_top(event):
            self.box.container.add_wiring_tool()
            event.handled = True

    def normal_mouse_leave(self, event):
        if self._box_on_top(event):
            self.box.container.remove_wiring_tool()
            event.handled = True

    def _box_on_top(self, event):
        """ Checks to see if the box that holds this field is on top
            of all the other possible boxes in that location on the canvas.
            returns False if box has no container or if the box isn't on top.
        """
        canvas_x = event.x + self.box.x
        canvas_y = event.y + self.box.y
        block_canvas = self.box.container
        if block_canvas:
            components = block_canvas.components_at(canvas_x, canvas_y)
            for c in components:
                if c == self.box:
                    return True
        return False

    def normal_left_up(self, event):
        """ FIXME: Hack to make sure that selection tool doesn't get
            this event and add the function box to the selection.
        """
        event.handled = True

    def normal_drag_over(self, event):
        """ Check the drag event for ContextVariable payloads.
        """
        if is_a_context_variable(event.obj):
            result = 'copy'
        else:
            result = 'none'
        event.window.set_drag_result(result)
        event.handled = (result == 'copy')

    def normal_dropped_on(self, event):
        """ Handle dropping onto this field for ContextVariable payloads.
        """
        if is_a_context_variable(event.obj):
            result = 'copy'
            from enthought.block_canvas.app.scripting import app
            app.update_function_variable_binding(self.box.graph_node,
                self.variable, event.obj.name)
        else:
            result = 'none'
        event.window.set_drag_result(result)
        event.handled = (result == 'copy')


    #---------------------------------------------------------------------
    # Trait Listeners
    #---------------------------------------------------------------------

    #---- Trait default initializers -------------------------------------

    def _icon_default(self):
        if self.type == "input":
            bullet = Bullet(color=self.bullet_input_color)
        else:
            bullet = Bullet(color=self.bullet_output_color)
        return bullet

    def _label_default(self):
        return EditField( text = self.variable.name,
                          bgcolor = "clear",
                          can_edit = False )

    def _value_default(self):
        str_binding = str(self.variable.binding)
        return EnableBoxField( variable=self.variable,
                               height=self.cell_height,
                               type=self.type,
                               box=self.box )

    #--- Trait listeners -------------------------------------------------


    def variable_binding_changed(self):
        self.value.text = str(self.variable.binding)

    def _variable_changed(self, old, new):
        self.label.text = new.name
        self.value.text = str(new.binding)

    def _selected_changed(self, old, new):
        if self.selected:
            self.bgcolor = self.highlight_color
            self.icon.event_state = 'selected'
        else:
            self.bgcolor = 'clear'
            self.icon.event_state = 'normal'


if (__name__=='__main__'):
    from enthought.enable.api import Window
    from enthought.enable.api import Container
    from enthought.enable.example_support import DemoFrame, demo_main
    from enthought.block_canvas.function_tools.function_variables import InputVariable

    class MyFrame(DemoFrame):
        def _create_window(self):
            input = InputVariable(name='foo', default=3)

            box = IOField(input, position=[50,300], bounds=[150,15])

            container = Container(bounds=[800,600])
            container.add(box)
            return Window(self, -1, size=[800, 600], component=container)

    demo_main(MyFrame)
