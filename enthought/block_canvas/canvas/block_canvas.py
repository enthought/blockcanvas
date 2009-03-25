
# Major library imports
import pickle
import warnings

# Enthought library imports
from enthought.traits.api import Any, Bool, false, Float, Instance
from enthought.enable.api import Canvas

# Local imports
from style_manager import StyleManager
from selection_manager import SelectionManager
from canvas_grid import CanvasGrid
from canvas_box import CanvasBox
from enable_line import EnableLine
from canvas_selection_tool import CanvasSelectionTool
from wiring_tool import WiringTool


class BlockCanvas(Canvas):
    """ Enable container for nodes/lines on the block canvas.
    """

    #---------------------------------------------------------------------
    # DragTool traits
    #---------------------------------------------------------------------
    
    # Override from DragTool base class.  Do not end drag operation
    # upon leaving the component.
    end_drag_on_leave = false

    #---------------------------------------------------------------------
    # Component traits
    #---------------------------------------------------------------------

    bgcolor = "white"

    #---------------------------------------------------------------------
    # BlockCanvas traits
    #---------------------------------------------------------------------

    # Controller that manages delete, drag/drop etc.
    graph_controller = Any

    # Style manager which components query for style information
    style_manager = Instance(StyleManager, ())

    # Keep track of which items in the container are selected
    selection_manager = Instance(SelectionManager, ())
    
    # Tool used to wire outputs to inputs, only enabled when 
    # user enters a box.  Disabled after the wiring tool finishes
    # dragging.
    wiring_tool_enabled = Bool(False)
    wiring_tool = Instance(WiringTool)

    _initial_layout_needed = Bool(True)

    def __init__(self, *args, **kw):
        super(BlockCanvas, self).__init__(*args, **kw)
        # FIXME: Removing selection tool until we have better handle on
        #        events on canvas.
        #self.tools.append(CanvasSelectionTool(self))
        self.wiring_tool = WiringTool(component=self)
        self.wiring_tool.component = self
        self.underlays.append(CanvasGrid(component=self))

    def get_bounding_box(self):
        x,y = self.bounds_offset
        w,h = self.bounds
        return (x, y, x+w, y+h)

    def load_layout(self, filename):
        """ Loads the layout of the canvas from the given filename.
        """
        if filename == "":
            return

        try:
            file = open(filename, 'r')
            self.graph_controller.saved_node_positions = pickle.load(file)
            self._initial_layout_needed = False
        except:
            warnings.warn('Unable to load layout file "%s";'
                          'using default layout.' % filename) 
        finally:
            try:
                file.close()
            except:
                pass

    def save_layout(self, filename):
        """ Save the layout of the canvas to the given filename.
        """
        id_position_map = {}
        for graph_node, node in self.graph_controller._nodes.items():
            id_position_map[graph_node.uuid] = (node.x, node.y)

        file = open(filename, 'w')
        pickle.dump(id_position_map, file)
        file.close()

    #---------------------------------------------------------------------
    # Container interface.
    #---------------------------------------------------------------------

    def draw(self, gc, view_bounds, mode="normal"):
        # Reorganize the components on the canvas
        # Draw order should be: Lines, Boxes, Selected Boxes
        if self._initial_layout_needed and self.graph_controller is not None:
            self.graph_controller.position_nodes()
            self._initial_layout_needed = False
        selected = []
        boxes = []
        lines = []
        other = []
        for c in self.components:
            if isinstance(c, CanvasBox):
                if c.selection_state in ['selected', 'coselected']:
                    selected.append(c)
                else:
                    boxes.append(c)
            elif isinstance(c, EnableLine):
                lines.append(c)
            else:
                other.append(c)
        self._components = lines + boxes + selected + other
        super(BlockCanvas, self).draw(gc, view_bounds, mode)

    def remove(self, *components):
        """ Overridden so that a removal causes a redraw automatically. This
            allows components to remove themselves from the container.
        """

        super(BlockCanvas, self).remove(*components)
        if len(components) == 1:
            self.request_redraw()

    def _container_handle_mouse_event(self, event, suffix):
        """ Overridden to enable drag/drop events.
            fixme: Should I mark events as handled?
        """
        if suffix == "dropped_on":
            self.graph_controller.handle_drop(event)
        elif suffix == "drag_over":
            self.graph_controller.verify_drag(event)

        if not event.handled:
            super(BlockCanvas, self)._container_handle_mouse_event(event, suffix)

    #---------------------------------------------------------------------
    # BlockCanvasContainer interface
    #---------------------------------------------------------------------

    def add_wiring_tool(self):
        if not self.wiring_tool_enabled:
            self.overlays.append(self.wiring_tool)
            self.wiring_tool_enabled = True
            
    def remove_wiring_tool(self):
        if self.wiring_tool_enabled:
            self.overlays.remove(self.wiring_tool)
            self.wiring_tool_enabled = False

    ### Trait listeners #####################################################

    def _graph_controller_changed(self, old, new):
        if old is not None:
            old.container = None

        if new is not None:
            new.container = self

# EOF
