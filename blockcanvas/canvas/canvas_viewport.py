
# Enthought library imports
from enable.api import Viewport
from enable.tools.hover_tool import HoverTool
from traits.api import Bool, Instance

# Local imports
from viewport_toolbar import HoverToolbar


class CanvasViewport(Viewport):

    # Enable ViewportZoomTool
    enable_zoom = True

    # Should we turn on the auto-hide feature on the toolbar?
    auto_hide = Bool(False)

    # Hover Tool - used when auto-hide is True
    hovertool = Instance(HoverTool)
    hovertool_added = False

    # Hover Toolbar - is always visible when auto-hide is False
    toolbar = Instance(HoverToolbar)
    toolbar_added = False

    def __init__(self, *args, **kw):
        super(CanvasViewport, self).__init__(*args, **kw)
        self.hovertool = HoverTool(self, area_type="top", callback=self.add_toolbar)
        self.toolbar = HoverToolbar(self)
        self.add_toolbar()

    def center_viewport(self):
        """ Center viewports around the container's contents.
        """

        if not self.component or not self.component.graph_controller:
            return
        nodes = self.component.graph_controller._nodes.values()
        if len(nodes) > 0:
            x = min([node.x for node in nodes])
            y = min([node.y for node in nodes])
            x2 = max([node.x2 for node in nodes])
            y2 = max([node.y2 for node in nodes])
            width, height = self.view_bounds
            view_pos = [x - (width - (x2-x))/2.0, y - (height - (y2-y))/2.0]
            self.view_position = view_pos

    def add_toolbar(self):
        if not self.toolbar_added:
            self.overlays.append(self.toolbar)
            self.toolbar_added = True
            self.request_redraw()

    def remove_toolbar(self):
        if self.toolbar_added and self.auto_hide:
            self.overlays.remove(self.toolbar)
            self.toolbar_added = False
            self.request_redraw()

    def add_hovertool(self):
        if not self.hovertool_added:
            self.tools.append(self.hovertool)
            self.hovertool_added = True

    def remove_hovertool(self):
        if self.hovertool_added:
            self.tools.remove(self.hovertool)
            self.hovertool_added = False

    def _component_changed(self, old, new):
        """ When the component changes, make sure our graph_updated function
            is synced with its controller's graph_updated event.
        """
        self.bgcolor = new.bgcolor
        Viewport._component_changed(self, old, new)

    def _bgcolor_changed_for_component(self, old, new):
        self.bgcolor = new

    def _auto_hide_changed(self, old, new):
        if self.auto_hide:
            self.remove_toolbar()
            self.add_hovertool()
        else:
            self.remove_hovertool()
            self.add_toolbar()

    def _bounds_changed(self, old, new):
        """ Update the layout of the attached toolbar
        """
        if self.toolbar_added:
            self.toolbar._layout_needed = True
        super(CanvasViewport, self)._bounds_changed(old, new)

    def _bounds_items_changed(self, event):
        if self.toolbar_added:
            self.toolbar._layout_needed = True
        super(CanvasViewport, self)._bounds_items_changed(event)



