""" Create a Workbench View of an object using a traits UI.
"""

# Enthought library imports
from enthought.traits.api import HasTraits, Instance, Any
from enthought.traits.ui.api import View
from enthought.pyface.workbench.api import View as WorkbenchView

class TraitsUIView(WorkbenchView):
    """ Workbench view of an object using traits UI.
    """

    #### 'IWorkbenchPart' interface ###########################################

    # The part's name (displayed to the user).
    name = ''

    #### 'TraitsUIView' interface ################################################

    # The object we want to use.
    obj = Instance(HasTraits)

    # The traits view to use to visualize item.
    view = Any  # Instance(View) or Str


    ###########################################################################
    # 'IWorkbenchPart' interface.
    ###########################################################################

    def create_control(self, parent):
        """ Creates the toolkit-specific control that represents the view.

        'parent' is the toolkit-specific control that is the view's parent.

        """
        ui = self.obj.edit_traits(parent=parent, kind='subpanel',
                                  view=self.view)
        return ui.control
