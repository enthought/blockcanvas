""" traits.ui editor for displaying a Block on a Enable Canvas.
"""

# Enthought library imports
from traits.api import Instance
from traitsui.api import BasicEditorFactory, Editor
from enable.api import Scrolled
from enable.tools.api import ViewportPanTool
from enable.api import Window

# Block canvas imports
from enthought.block_canvas.canvas.canvas_viewport import CanvasViewport


class _BlockEditor(Editor):

    #########################################################################
    # Editor traits
    #########################################################################

    # fixme: If I don't set this, then my container doesn't fill the window?
    scrollable = True

    #########################################################################
    # _BlockEditor traits
    #########################################################################

    # The scrolling container which contains the container and the canvas_view
    scrolled = Instance(Scrolled)

    # The viewport into the canvas
    canvas_view = Instance(CanvasViewport)

    # Hold onto the window so that we get resize events.
    _window = Instance(Window)

    # these are required by some backends
    border_size = 0
    layout_style = 0

    #########################################################################
    # Editor interface
    #########################################################################

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        canvas = self.value
        viewport = CanvasViewport(component=canvas, view_position=[0,0])
        viewport.tools.append(ViewportPanTool(viewport, drag_button='right'))
        viewport.max_zoom = 1.0
        viewport.min_zoom = 0.2
        self.canvas_view = viewport

        self.scrolled = Scrolled(canvas,
                                 fit_window = True,
                                 inside_padding_width = 0,
                                 mousewheel_scroll = False,
                                 always_show_sb = True,
                                 continuous_drag_update = True,
                                 viewport_component=viewport)

        self._window = Window(parent, -1, component=self.scrolled)
        self.control = self._window.control

    def update_editor(self):
        if self.value != self.canvas_view.component:
            self.canvas_view.component = self.value
            self.value.graph_controller.position_nodes()
            self.canvas_view.invalidate_draw()
            self.canvas_view.request_redraw()


class BlockEditor(BasicEditorFactory):
    """ Traits editor factory for the BlockEditor.
    """

    #########################################################################
    # BasicEditorFactory interface
    #########################################################################

    # The editor class to be created:
    klass = _BlockEditor

    def simple_editor ( self, ui, object, name, description, parent ):
        return self.klass( parent,
                           factory     = self,
                           ui          = ui,
                           object      = object,
                           name        = name,
                           description = description)


