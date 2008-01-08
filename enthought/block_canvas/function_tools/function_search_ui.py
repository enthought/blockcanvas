""" Simple GUI code for function search.

    This is the "minimal" UI for a FunctionSearch object.  For a
    more advanced version, see the block_canvas app directory.
"""

# Enthought library imports.
from enthought.traits.api import Any, Property, Event, Str, Font, Bool
                                 
from enthought.traits.ui.api import View, VGroup, VSplit, HGroup, Item, \
                                    Handler, Label, Group
from enthought.traits.ui.menu import NoButtons, OKCancelButtons

from enthought.traits.ui.wx.extra.tabular_editor import (TabularEditor,
                                                         TabularAdapter)
from enthought.pyface.image_resource import ImageResource
from enthought.etsconfig.api import ETSConfig

# App imports
# fixme: These should become pyface controls.
from enthought.block_canvas.ui.search_editor import SearchEditor
from enthought.block_canvas.ui.hyperlink_editor import HyperlinkEditor

# Local imports
from python_function_info import PythonFunctionInfo

##############################################################################
# Preferences View for FunctionSearch class
##############################################################################

function_search_preferences_view = \
    View(
     
         VGroup(
             Label('Function name filters'),
             Item('name_filters', show_label=False),
             Label('Module/Package name filters'),
             Item('module_filters', show_label=False),
             HGroup(
                 Item('search_name'),
                 Item('search_module'),
             ),
         ),
         title='Function Preferences',         
         width=450,
         height=600,
         resizable=True,
         buttons=OKCancelButtons,
    )


##############################################################################
# FunctionSearch Handler class for UI
##############################################################################

class FunctionSearchUIHandler(Handler):
    """ Handler for the function search user interface.
    """
    
    ##########################################################################
    # FunctionSearchUIHandler traits
    ##########################################################################
    
    # Which order are the rows sorted in? False=ascending, True=descending.
    reverse_sort = Bool(False)
    
    
    ##########################################################################
    # TableEditor callback traits
    ##########################################################################
    
    # Set when a column a row is selected in the table.
    selected = Any
    
    # Set when an item in the table is double clicked.
    dclicked = Any
    
    # Set when a column heading is clicked on.
    column_clicked = Any
    
    # Fires when the preferences button in the UI is clicked on.
    preferences = Event
    
    # View used for the preferences dialog
    preferences_view = Any(function_search_preferences_view)
    
    
    ##########################################################################
    # FunctionSearchUIHandler interface
    ##########################################################################

    def handler_preferences_changed(self, info):
        """ Display the Search preference settings as modal dialog.
        """
        info.object.edit_traits(self.preferences_view,
                                kind='livemodal')


    ### private methods ######################################################

    ### trait handlers #######################################################

    def _column_clicked_changed(self, event):
        """ Sort the functions based on the clicked column.  Reverse the
            order of the sort each time the column is clicked.
        """
        
        #### This is the list of the rows in the table.
        values = event.editor.value

        #### Reverse the sort order.
        self.reverse_sort = not self.reverse_sort
        
        # Sort by the clicked on column's field name and in the correct order.
        fields = [name for label, name in event.editor.adapter.columns]
        field = fields[event.column]
        values.sort(key=lambda x: getattr(x,field), reverse=self.reverse_sort)
                
        
class SearchTableAdapter(TabularAdapter):
    """ Adapter to map the traits of the function items into UI table columns.
    """

    ##########################################################################
    # SearchTabularAdapter traits
    ##########################################################################

    # Font used for rendering text in each row.
    # fixme: Although Arial 10 is the default wx font, we really should
    #       querying something and adding a bold 'style' to it.
    normal_font = Font("Arial 9")


    ##########################################################################
    # TabularAdapter traits
    ##########################################################################
    
    # The columns to display (along with the adapter trait they map to.
    columns = [('Name', 'name'), ('Module', 'module')]

    # Tooltip text to show for a variable.
    tooltip = Property

    # Image displayed next to search item.
    image = Property


    ##########################################################################
    # SearchTableAdapter interface
    ##########################################################################

    ### Private methods ######################################################
    
    def _get_description(self, function_info):
        """ Grab a short text description of the described function.
        
            The first line in the doc-string is returned if it is available.
            Otherwise, an empty string is returned.
        """
        # Create a PythonFunctionInfo for the function.
        # fixme: This seems a little heavy weight to just get the 
        #        doc-string, but it is the shortest path between here
        #        and there...
        # fixme: We should likely do some error handling here...
        func = PythonFunctionInfo(module=function_info.module,
                                  name=function_info.name)
        
        if func.doc_string is "":
            short_description = "No information about this function."
        else:
            # Use the first line as the "short" function description.
            short_description = func.doc_string.splitlines()[0]
                
        return short_description
            
    ##########################################################################
    # TableAdapter interface
    ##########################################################################

    def get_font(self, object, trait, row):
        """ The default font is to tall for the table rows.  sigh...             
        """
        return self.normal_font


    ### Private methods ######################################################

    def _get_tooltip(self):
        """ Tooltip text is the firt line of the doc-string for the function.

            fixme: Add the calling convention as first line to this.
            fixme: Can we format this?  Send it html or something like that?
        """
        return self._get_description(self.item)
        
    def _get_image(self):
        """ Retreive the image for each cell in the table.

            fixme: For now, everything is a "function".  Later, we will
                   add united function and perhaps class.  Or, we may make
                   the icons for different functionality (rockphysics, filters,
                   etc...)
                   Also, we may want to attach images to functions and ask
                   the actual function for its image.
        """

        if self.column == 0:
            result = 'function_variable'
        else:
            result = None
        return result


##############################################################################
# Search View for FunctionSearch class
##############################################################################

# Images used in adapter.
images = [ImageResource('function_variable')]

function_search_view = \
      View(
           VGroup(
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
                         Item('search_results',
                              show_label=False,
                              editor=TabularEditor(adapter=SearchTableAdapter(),
                                                   selected='handler.selected',
                                                   dclicked='handler.dclicked',
                                                   column_clicked='handler.column_clicked',
                                                   editable=False,
                                                   images=images
                              ),
                              springy=True,
                              resizable=True,
                         ),
                         id='search_results_view'
                    ),
                    id='search_panel_split',
           ),
           id='search_view',
           resizable=True,
           buttons=NoButtons,
           handler=FunctionSearchUIHandler
    )


if __name__ == "__main__":
    from function_library import FunctionLibrary
    from function_search import FunctionSearch
    
    library = FunctionLibrary(modules=['os', 'xml'])
    search = FunctionSearch(all_functions=library.functions)
    search.configure_traits(view=function_search_view)
