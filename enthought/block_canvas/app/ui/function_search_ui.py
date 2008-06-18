""" Display/Search a list of Python functions.

    Specialized function search UI gui that is customized to this application.
    Note that this view is actually of the Application object instead of just
    the FunctionSearch object, because it needs to access multiple things on
    the application including the FunctionLibrary, the Canvas, and the HTML
    Window.
    
    GUI code for instrument search.

    fixme: Need to split out Add New Function stuff into a different class
           so that it is more easily tested.
    fixme: Get drag/drop and double click working.
    fixme: Not been tested against a library with extension functions in it.
"""

# Enthought library imports.
from enthought.traits.api import Any, Property, Event, Str, Font, Bool, \
                                 List, Instance, cached_property
from enthought.traits.ui.api import View, VGroup, VSplit, HGroup, Item, \
                            Handler, Label, Group, InstanceEditor, TabularEditor
from enthought.traits.ui.menu import NoButtons, OKCancelButtons
from enthought.pyface.api import error

from enthought.pyface.image_resource import ImageResource

# Block Canvas imports
from enthought.block_canvas.function_tools.i_minimal_function_info import \
    MinimalFunctionInfo
from enthought.block_canvas.function_tools.local_function_info import LocalFunctionInfo
from enthought.block_canvas.function_tools.python_function_info import PythonFunctionInfo
from enthought.block_canvas.function_tools.function_call import FunctionCall
from enthought.block_canvas.function_tools.function_search_ui import \
    FunctionSearchUIHandler, SearchTableAdapter
from enthought.block_canvas.function_tools.general_expression import GeneralExpression


# App imports
# fixme: These should become pyface controls.
from enthought.block_canvas.ui.search_editor import SearchEditor
from enthought.block_canvas.ui.hyperlink_editor import HyperlinkEditor

# Local imports
from function_search_preferences_ui import function_search_preferences_view
from enthought.block_canvas.app import scripting


### FIXME:  This is a cut and paste from the application,
### but we have a copy here to avoid circular imports.
# A global object to represent a new function.  We're cheating
# here a bit and putting labels in the correct "columns" (name,
# module) to get the UI that we want.  The UI classes below have
# some code to special case this class.
NEW_FUNCTION_ENTRY = MinimalFunctionInfo(name="Add New Function",
                                         module="Create a new function")

NEW_EXPR_ENTRY = MinimalFunctionInfo(name="Add New Expressions",
                                     module="Create a new expression block")


##############################################################################
# AppFunctionSearchUIHandler
#
# It's customized for the app object insted of directly sitting on the 
# FunctionSearch object.
##############################################################################

class AppFunctionSearchUIHandler(FunctionSearchUIHandler):
    """ Handler for the function search user interface.
    
        This class:        
            1) customizes the list of functions displayed so that a 
               "New Function" item is at the top of the list.
            2) Adds function library configuration to the preferences page.
            3) Adds functions to the canvas when they are double-clicked.
    """
    
    ##########################################################################
    # AppFunctionSearchUIHandler traits
    ##########################################################################
    
    # The application object we are pointing at.
    # It is any, because this UI is serving multiple different app types
    # currently.
    app = Any
    
    # List of search results with NEW_FUNCTION_ENTRY and NEW_EXPR_ENTRY always
    # at front.
    search_results = List

        
    ##########################################################################
    # FunctionSearchUIHandler traits
    ##########################################################################

    # View used for the preferences dialog
    # A customized preferences dialog for the app is used here.
    preferences_view = function_search_preferences_view


    ##########################################################################
    # AppFunctionSearchUIHandler interface
    ##########################################################################

    def handler_preferences_changed(self, info):
        """ Display the Search preference settings as modal dialog.
            fixme: Shouldn't have to override this function.  Instead set
                   preferences_view trait.
        """
        info.object.edit_traits(function_search_preferences_view,
                                kind='livemodal')

    ### trait initializers ###################################################
    
    def _app_default(self):
        """ Default to the application set in the scripting module.
            fixme: This can go away once we completely switch to the workbench.
        """
        return scripting.app

    ### trait handlers #######################################################

    def _selected_changed(self, value):
        """ Update the html window with selected function's documentation.
        """
        if not value:
            return
        
        if value == NEW_FUNCTION_ENTRY:
            msg = "Create an editable, user defined function."
            self.app.html_window_set_text(msg)
        elif value == NEW_EXPR_ENTRY:
            msg = "Create a block of expressions."
            self.app.html_window_set_text(msg)
        else:
            self.app.html_window_set_function_help(value.name, value.module)


    def _dclicked_changed(self, event):
        """ Add the double clicked FunctionCall object to the code/canvas.
        
            The added function is also marked as selected.
        """
        self.app.add_function_object_to_model(event.item)

    def _column_clicked_changed(self, event):
        """ Sort the functions based on the clicked column.  Reverse the
            order of the sort each time the column is clicked.
        """
        
        # Call the super class which handles sorting list in correct order.
        super(AppFunctionSearchUIHandler, self)._column_clicked_changed(event)
        
        # Now ensure the "add new ..." entries are always first in UI.
        values = event.editor.value
        values.remove(NEW_FUNCTION_ENTRY)
        values.remove(NEW_EXPR_ENTRY)
        values.insert(0, NEW_FUNCTION_ENTRY)
        values.insert(1, NEW_EXPR_ENTRY)


    ### property get/set methods #############################################        
    
    def object_search_results_changed(self, info):
        """ Append the "new function" place holder function onto the results.
        """
        function_results = info.object.search_results
        self.search_results = ([NEW_FUNCTION_ENTRY, NEW_EXPR_ENTRY]
            + function_results)
        


class AppSearchTableAdapter(SearchTableAdapter):
    """ Augment the Standard adapter so that it bolds the first two entries.
    """

    ##########################################################################
    # AppSeachTabularAdapter traits
    ##########################################################################
    
    # Font for bolding the "add new function" row in table
    # fixme: Make system dependent (lookup standard font and apply bold to it)
    bold_font = Font("Arial 9 Bold Italic")


    ##########################################################################
    # TabularAdapter interface
    ##########################################################################

    def get_font(self, object, trait, row):
        """ The Add new function item should appear in bold.
        
            "Add new function" is always in the first row, so we can simply
            make that row bold.             
        """
        if row <= 1:
            font = self.bold_font
        else:
            font = self.normal_font
        
        return font            


    ### Private methods ######################################################
    
    def _get_tooltip(self):
        """ Tooltip text is the firt line of the doc-string for the function.

            We specialize this so that it can return a different tooltip if
            one of our NEW_*_ENTRY is selected.  Otherwise, hand off the work
            to our base class.
        """
        if self.item is NEW_FUNCTION_ENTRY:
            short_description = "Create an editable user defined function."
        elif self.item is NEW_EXPR_ENTRY:
            short_description = "Create a block of expressions."
        else:
            short_description = super(AppSearchTableAdapter, self)._get_tooltip()
            
        return short_description


##############################################################################
# Search View for FunctionSearch class
#
# Note: Both the of these UIs are largely copied from the function_search_ui
#       UI definitions.  I wish I knew of a better way to re-use chunks of
#       UIs, but I don't.
##############################################################################

# Images used in adapter.
# fixme: Set this up correctly.
#images = [ImageResource('function_variable')]

function_search_view = \
      View(
           VGroup(
               VSplit(
                      VGroup(
                             HGroup(
                                    Item('search_term',
                                         show_label=False,
                                         springy=True,
                                         editor=SearchEditor(text="Search for functions"),
                                    ),
                                    Item('handler.preferences',
                                         show_label=False,
                                         editor=HyperlinkEditor(text="Search\nSettings",
                                                tooltip="Advanced search settings")
                                    ),
                             ),
                             Item('handler.search_results',
                                  show_label=False,
                                  # This line is customized to use our adapter.
                                  editor=TabularEditor(adapter=AppSearchTableAdapter(),
                                                       selected='handler.selected',
                                                       dclicked='handler.dclicked',
                                                       column_clicked='handler.column_clicked',
                                                       editable=False,
                                                       #images=images
                                  ),
                                  springy=True,
                                  resizable=True,
                             ),
                             id='search_results_view'
                        ),
                        id='search_panel_split',
               ),
           ),
           id='search_view',
           resizable=True,
           buttons=NoButtons,
           handler=AppFunctionSearchUIHandler
    )


if __name__ == "__main__":
    
    from enthought.block_canvas.function_tools.function_library import FunctionLibrary
    
    from enthought.block_canvas.app import app
    
    
    library = FunctionLibrary(modules=['os','cp.rockphysics'])
    this_app = app.Application(function_library=library)
    

    this_app.function_search.edit_traits(view=function_search_view)
