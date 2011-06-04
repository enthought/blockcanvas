# Enthought Library imports
from traitsui.api import View, Item
from traits.api import Any
from pyface.workbench.traits_ui_editor import TraitsUIEditor
from blockcanvas.block_display.block_editor import BlockEditor


class ExperimentCanvasEditor(TraitsUIEditor):
    """ Canvas Editor for an Experiment object.
    """

    ##########################################################################
    # TraitsUIEditor traits
    ##########################################################################

    # ??? Wny does this have to be a string?  Can't this be a view.
    # The name of the traits UI view used to create the UI (if not specified,
    # the default traits UI view is used).
    view = Any

    ##########################################################################
    # TraitsUIEditor interface
    ##########################################################################

    #fixme: Need an override for the name.

    def _view_default(self):
        """ Create a Traits UI view of the canvas in an experiment.  Use the
            controller as the controller for the Block Editor.
        """
        view=View(Item('canvas',
                       show_label=False,
                       # FIXME:  need a new way to control the canvas
                       # not using BlockEditor
                       editor=BlockEditor(controller=self.obj.controller),
                 ),
             )

        return view
