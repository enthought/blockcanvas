""" Provides a view for searching functions found in the applications
    function library.

    fixme: We aren't savings to function search preferences here
           between runs of the application.
"""

# Enthought Library imports
from traits.api import HasTraits, Instance, Property, Any, \
                                 on_trait_change
from traitsui.api import View, Item, InstanceEditor
from pyface.workbench.api import View as WorkbenchView

# Block Canvas imports
from blockcanvas.function_tools.function_search import FunctionSearch
from blockcanvas.app.ui.function_search_ui import \
    function_search_view, AppFunctionSearchUIHandler
from blockcanvas.app.workbench_app.application import Application

# Local imports
from traits_ui_view import TraitsUIView


class AppFunctionSearch(FunctionSearch):
    """ Simple Model that includes a function search object as the
        model for the View.
    """

    # The application that holds the function library
    app = Any #Instance(Application)

    ##########################################################################
    # HasTraits Interface
    ##########################################################################

    def trait_view(self, name=None, view_element=None):
        # fixme: We don't want to modify the original views handler.
        #        This is sketchy and should be replaced by a better
        #        approach.
        view = function_search_view.clone_traits()
        handler = AppFunctionSearchUIHandler(app=self.app)
        view.handler = handler
        return view

    @on_trait_change('app.function_library')
    def _update_functions(self):
        """ If the library changes, ensure we have our library updated.

            fixme: If we go to the query mechanism, this would go away...
        """
        self.all_functions = self.app.function_library.functions


class FunctionSearchView(WorkbenchView):
    """ View for searching for functions in an application.
    """

    ###########################################################################
    # 'IWorkbenchPart' interface.
    ###########################################################################

    def create_control(self, parent):
        """ Creates the toolkit-specific control that represents the view.

        'parent' is the toolkit-specific control that is the view's parent.

        """
        app = self.window.workbench.app
        function_search = AppFunctionSearch(app=app)
        ui = function_search.edit_traits(parent=parent, kind='subpanel')

        return ui.control
