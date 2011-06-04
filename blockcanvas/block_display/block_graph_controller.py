""" This controller class coordinates actions on the canvas with the underlying
    block it represents.
"""

# Numpy imports
from numpy import inf

# Enthought library imports:
from traits.api import (Any, Bool, Dict, HasTraits,
                                  Instance, List, on_trait_change, TraitListEvent)
from traits.protocols.api import adapt

from enable.api import Component, Container
from blockcanvas.app import scripting
from blockcanvas.canvas.enable_line import EnableLine
from blockcanvas.function_tools.i_minimal_function_info import \
    IMinimalFunctionInfo

# Local imports:
from execution_model import ExecutionModel
from block_node_factory import BlockNodeFactory
from row_layout_engine import RowLayoutEngine


class BlockGraphController(HasTraits):
    """ The controller between the execution model and the canvas (view).
    """

    #########################################################################
    # BlockGraphController Traits
    #########################################################################

    # The execution model
    execution_model = Instance(ExecutionModel)

    # Enable canvas that displays the graph - The Block Canvas
    canvas = Instance(Container)

    # The box factory
    factory = Instance(BlockNodeFactory)

    # Engine used to layout blocks for display
    layout_engine = Instance(RowLayoutEngine)

    # Edited function
    edited_function = Any

    # Event that we fire whenever the graph has been updated, i.e. new blocks
    # are added or old ones removed.
    gap = List([50,100])

    # Saved box positions from file
    saved_node_positions = Dict

    # The boxes on the canvas
    # FIXME:  Will also have to handle Groups and Expressions
    _nodes = Dict(Any, Component)

    # The lines between boxes
    _edges = List(Component)

    # Do we need to rebuild the graph?
    _rebuild_graph = Bool(True)

    #########################################################################
    # BlockGraphController Interface
    #########################################################################

    def dim_not_active ( self, active_uuids ):
        """ Given an iterable (preferably a set, for speed) of block uuids, dim
            nodes whose uuids are not in the set.
        """
        for graph_node, box in self._nodes.items():
            if graph_node.uuid not in active_uuids:
                box.dimmed = True

        # To support unit tests, check if the canvas is not None:
        if self.canvas is not None:
            self.canvas.request_redraw()

    def flag_node ( self, graph_node ):
        """ Flag the box on the canvas representing the specified Block
        """
        if graph_node in self._nodes:
            self._nodes[ graph_node ].flagged = True

        # To support unit tests, check if the canvas is not None:
        if self.canvas is not None:
            self.canvas.request_redraw()

    def handle_drop ( self, event ):
        """ Item has been dropped on canvas.
        This is currently called from BlockCanvas._container_handle_mouse_event
        """
        dragged_obj = self._unpack_drag_event( event )
        if dragged_obj is not None:
            from blockcanvas.app.scripting import app
            app.add_function_object_to_model(dragged_obj, event.x, event.y)
        else:
            event.window.set_drag_result( "none" )

    def undim_all ( self ):
        """ Undim all nodes in the block canvas.
        """
        for node in self._nodes.values():
            node.dimmed = False

        # To support unit tests, check if the canvas is not None:
        if self.canvas is not None:
            self.canvas.request_redraw()

    def unflag_all ( self ):
        """ Unflag all nodes in the block canvas.
        """
        for node in self._nodes.values():
            node.flagged = False

        # To support unit tests, check if the canvas is not None:
        if self.canvas is not None:
            self.canvas.request_redraw()

    def verify_drag ( self, event ):
        """ Determine whether the item being dragged is allowed on the canvas.
        currently called from BlockCanvas._container_handle_mouse_event
        """
        if self._unpack_drag_event( event ) is not None:
            event.window.set_drag_result( "copy" )
        else:
            event.window.set_drag_result( "none" )

    def expand_boxes(self):
        """ Expands all the boxes.
        """
        for node, box in self._nodes.items():
            box.expanded = True
        self.position_nodes()

    def collapse_boxes(self):
        """ Collapse all the boxes.
        """
        for node, box in self._nodes.items():
            box.expanded = False
        self.position_nodes()

    def scale_and_center(self):
        """ Sets the zoom factor and centers the viewport to ensure that all
            boxes are visible.
        """
        if not self.execution_model.dep_graph:
            return

        (x, y, x2, y2) = self.canvas._bounding_box
        width = x2 - x + 1
        height = y2 - y + 1

        viewport = self.canvas.viewports[0]
        bounds = viewport.bounds[:]
        bounds[1] -= viewport.toolbar.toolbar_height
        if hasattr(viewport, "zoom_tool"):
            min_zoom = viewport.zoom_tool.min_zoom
            max_zoom = viewport.zoom_tool.max_zoom
        else:
            max_zoom = inf
            min_zoom = -inf

        if width != 0:
            x_scale = float(bounds[0]) / float(width)
            x_scale = self.limit_scale(x_scale, min_zoom, max_zoom)
        else:
            x_scale = max_zoom
        if height != 0:
            y_scale = float(bounds[1]) / float(height)
            y_scale = self.limit_scale(y_scale, min_zoom, max_zoom)
        else:
            y_scale = max_zoom

        min_scale = min(x_scale, y_scale)
        viewport.zoom = min_scale
        viewport.view_bounds = [bounds[0]/min_scale, bounds[1]/min_scale]

        # If the bounding box is less than the bounds, then center
        if width <= bounds[0] or height <= bounds[1]:
            viewport.center_viewport()
        else:
            viewport.view_position = [0,0]

    def limit_scale(self, scale, min_scale=-inf, max_scale=inf):
        """ Returns a valid scale for the viewport by limiting it to being
            between **min_scale** and **max_scale**
        """
        if scale < min_scale:
            return min_scale
        elif scale > max_scale:
            return max_scale
        else:
            return scale

    def update_nodes(self, added=[], removed=[], modified=[]):
        """ Update the nodes in the canvas based on changes in the graph.
        """

        graph = self.execution_model.dep_graph
        # Destroy old nodes
        for node, box in self._nodes.items():
            uuid = node.uuid
            if (uuid in removed) or self._rebuild_graph:
                # Remove and delete box
                self.canvas.remove(box)
                del self._nodes[node]
            elif uuid in modified:
                # Keep the box, change the graph_node
                for n in graph:
                    if uuid == n.uuid:
                        manually_update = (box.graph_node is n)
                        box.graph_node = n
                        if manually_update:
                            # The contents may have changed, but the object
                            # identity didn't.
                            box._graph_node_changed()
                        box.request_redraw()
                        break

        for node in graph:
            uuid = node.uuid
            if uuid in added or self._rebuild_graph:
                box = self.factory.make_component(node)
                self._nodes[node] = box
                self.position_in_viewport(box)
                self.canvas.add(self._nodes[node])

        # Replace old edges with new edges
        # fixme: This could be done "intelligently", but would the speed
        #        benefit (if there even was one) be worth it?
        self.canvas.remove(*self._edges)
        self._edges = []
        for dest, sources in graph.items():
            for source in sources:
                if self._nodes.has_key(source) and self._nodes.has_key(dest):
                    line = EnableLine(start_node=self._nodes[source],
                                      end_node=self._nodes[dest])
                    self._edges.append(line)
        self.canvas.add(*self._edges)

        # We've (possibly) rebuilt the graph, so we don't need to again
        self._rebuild_graph = False

    def position_nodes(self):

        hierarchy = self.layout_engine.organize_rows(self.execution_model.dep_graph)
        if not hierarchy:
            return

        ## FIME:  Hack for Mac
        ## On the initial layout, the boxes haven't been created yet.
        if not self._nodes:
            self.update_nodes([self.execution_model.dep_graph.keys()],[],[])

        x_gap = self.gap[0]
        y_gap = self.gap[1]

        max_length = 0
        max_on_row = 0
        total_height = 0
        for row in hierarchy:
            row_length = 0
            row_height = 0
            for func in row:
                n = self._nodes[func]
                row_length += n.bounds[0] + x_gap
                if n.bounds[1] > row_height:
                    row_height = n.bounds[1]
            if row_length > max_length:
                max_length = row_length
                max_on_row = len(row)
            row_height += y_gap
            total_height += row_height
        avg_space = max_length / max_on_row

        for i, row in enumerate(hierarchy):
            x_pos =  max_length / (len(row) + 1)
            if i > 0:
                y = self._find_min_y(hierarchy[i-1])
            else:
                y = total_height

            # Initial positions
            for graph_node in row:
                n = self._nodes[graph_node]
                uuid = graph_node.uuid
                saved = self.saved_node_positions
                if uuid in saved:
                    n.x = saved[uuid][0]
                    n.y = saved[uuid][1]
                else:
                    row_y = y - n.bounds[1] - y_gap
                    n.y = row_y
                    n.x = x_pos
                    x_pos = x_pos + n.bounds[0] + x_gap
        self.scale_and_center()

    def _find_min_y(self, graph_nodes):
        """ Given a list of graph nodes, return the highest y coordinate of the
            corresponding EnableBoxes.
            Returns -1 if none of the graph nodes exist in _nodes.
        """

        if len(graph_nodes) > 0:
            try:
                return min([ self._nodes[gn].y for gn in graph_nodes
                             if gn in self._nodes ])
            except ValueError:
                return -1
        else:
            return -1


    def position_in_viewport(self, component):
        """ Places a component at the top center of the canvas
            just below the toolbar.
        """

        # Set initial position based on viewport
        if self.canvas.viewports:
            vp = self.canvas.viewports[0]
            #FIXME:  If we're starting with a blank canvas, the view_bounds and view_position
            #        haven't been set yet.
            if vp.view_bounds == [0,0]:
                x_pos = vp.bounds[0]/2 - component.width/2
                y_pos = vp.bounds[1] - component.outer_height - vp.toolbar.toolbar_height
            else:
                x_pos = vp.view_position[0] + vp.view_bounds[0]/2 - component.width/2
                y_pos = vp.view_position[1] + vp.view_bounds[1] - component.outer_height - vp.toolbar.toolbar_height
            component.position = [x_pos, y_pos]

    def assign_binding(self, graph_node, variable, name):
        """ Assign the binding of a variable for a graph node to a particular
        name.
        """
        scripting.app.assign_binding(graph_node, variable, name)


    ### private interface ####################################################

    def _unpack_drag_event ( self, event ):
        """ Inspect object and see if it can be dropped here.  If so, return
            the droppable object.  Otherwise, return None.
        """

        # fixme: poor man's interface checking for IBasicFunctionInfo.
        # fixme: This will not work for a LocalFunctionInfo, and it should...
        # fixme: This was for plotting...
        #elif isinstance( event.obj, BlockVariable ):
        #    result = event.obj

        # If it supports the IMinimalFunctionInfo interface, we're good.
        try:
            result = adapt(event.obj, IMinimalFunctionInfo)
        except NotImplementedError:
            result = None

        return result

    ### trait defaults #######################################################

    def _layout_engine_default ( self ):
        """ By default use the RowLayoutEngine with center justification
            for blocks.
        """
        return RowLayoutEngine()

    def _factory_default( self ):
        """ By default the controller for the BlockNodeFactory is self. """

        return BlockNodeFactory( controller = self )

    ### trait change handlers ################################################

    def _canvas_changed ( self, old, new ):
        """ If the display canvas changes, update the canvas
        """
        if new:
            new.graph_controller = self

    @on_trait_change("execution_model.statements_items")
    def _statements_items_changed(self, name, event):
        """ Listed for added or removed functions from the model.
        """
        if isinstance(event, TraitListEvent):
            added = [func.uuid for func in event.added]
            removed = [func.uuid for func in event.removed]
            self.update_nodes(added, removed)

# EOF
