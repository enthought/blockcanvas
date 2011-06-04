# Enthought library imports
from traits.api import HasTraits, implements, Instance

# Application imports
from enthought.block_canvas.canvas.i_canvas_node_factory import ICanvasNodeFactory
from enthought.block_canvas.canvas.canvas_box import CanvasBox
from enthought.block_canvas.function_tools.function_call import FunctionCall
from enthought.block_canvas.function_tools.general_expression import GeneralExpression

class BlockNodeFactory(HasTraits):
    """ A factory that transforms properly decorated blocks (see block_graph.py)
        into EnableBoxes.
    """

    implements(ICanvasNodeFactory)

    # The controller which is passed to the EnableBoxes that are created
    controller = Instance(HasTraits)

    #########################################################################
    # ICanvasNodeFactory interface
    #########################################################################

    def make_component(self, node, old=None, old_position=[]):
        """ Given a Block, return the appropriate EnableBox or raise an error
            if the Block's stmt_type is not supported.
        """
        if isinstance(node, (FunctionCall, GeneralExpression)):
            box = CanvasBox(graph_node=node)
        else:
            raise TypeError, "Node '%s' type is not understood" % node.uuid

        if old is not None:
            # Only use the old_box's position if the new box as the same inputs
            try:
                # We need to operate on copies, not the original inputs
                new_inputs = set(node.inputs)
                old_inputs = set(old.graph_node.inputs)
                if old_position != [] and new_inputs == old_inputs:
                    box.position = old_position
            # If something goes wrong, don't set the position
            except:
                pass

            # The rest of the settings are applied regardless of inputs/outputs
            box.expanded = old.expanded
            if old.selection_state == "selected":
                self.controller.container.selection_manager.selection.insert(0, box)
            elif old.selection_state == "coselected":
                self.controller.container.selection_manager.selection.append(box)

        return box
