""" Application specific preferences Dialog.
"""

    #fixme: Perhaps sub-class from the orginal preferences handler?
    #fixme: We need the modules list to be a table or tabular editor.
    #fixme: Half of this dialog is live (filters, etc.) and half is
    #       modal (modules).  That seems a little goofy.

# Enthought library imports.
from enthought.traits.api import List, Str
from enthought.traits.ui.api import View, VGroup, HGroup, Item, \
                                    Handler, Label, Group, ListStrEditor
from enthought.traits.ui.menu import OKCancelButtons

# Local imports
from enthought.block_canvas.app import scripting



class AppFunctionSearchPreferencesUIHandler(Handler):
    """ Handler for the function search preferences.

        This UI combines elements from a FunctionSearch model and a
        FunctionLibary model into one UI.  We keep a local copy of the
        FunctionLibrary.modules so that it isn't updated live.  Only on
        OK do we write the values into the object.
    """

    ##########################################################################
    # AppFunctionSearchUIHandler traits
    ##########################################################################

    # List of modules to be searched.
    # We don't actually want the search to update its library until we've
    # hit "OK", so we keep a shadow list here to prevent that from
    # happening.
    modules = List(Str)


    ##########################################################################
    # Handler interface
    ##########################################################################

    def closed(self, info, ok):
        """ Update the app library modules and persist the data if OK selected.
        """
        if ok:
            # Update the function library with the newly minted functions.
            # fixme: Hour glass or progress as this could take some time...
            # fixme: This should all go through app API functions
            library = scripting.app.function_library
            library.modules=self.modules
            info.object.all_functions = library.functions
            # fixme: update modules and persist the setting to disk.
            #scripting.app.set_function_search_modules(library.modules)
        else:
            # Don't do anything if we cancel...
            pass


    ##########################################################################
    # Handler interface
    ##########################################################################

    ### private default traits ###############################################

    def _modules_default(self):
        """ Try getting the modules from the app function library.

            If it isn't set, then return an empty list.
        """
        try:
            # fixme: use API to grab the modules from disk.
            #modules = scripting.app.get_function_search_modules()
            modules = scripting.app.function_library.modules
        except AttributeError:
            modules = []

        return modules



##############################################################################
# Preferences View object
##############################################################################

function_search_preferences_view = \
    View(
        # fixme: This label isn't all being shown in the window -- only
        #        part of the first line.
         Label("This page specifies how the application will find functions. " \
               "You can specify the paths to search for modules in, and the " \
               "modules which will provide the functions."
         ),
         Group(
               Item('handler.modules',
                    style='custom',
                    # fixme: This guy doesn't work quite right yet.
                    editor=ListStrEditor(horizontal_lines=True), #auto_add=True, horizontal_lines=True),
                    show_label=False
               ),
               label = "Modules to Search",
               show_border=True,
         ),
         VGroup(
             Label('Function name filters'),
             Item('name_filters', show_label=False),
             Label('Module/Package name filters'),
             Item('module_filters', show_label=False),
         ),
         HGroup(
             Item('search_name'),
             Item('search_module'),
         ),
         title='Function Preferences',
         width=300,
         height=400,
         resizable=True,
         buttons=OKCancelButtons,
         handler=AppFunctionSearchPreferencesUIHandler,
    )

if __name__ == "__main__":

    from enthought.block_canvas.function_tools.function_library import FunctionLibrary
    from enthought.block_canvas.app import app


    library = FunctionLibrary(modules=['os','cp.rockphysics'])
    this_app = app.Application(function_library=library)

    # Now create the UI.
    this_app.function_search.edit_traits(function_search_preferences_view)
