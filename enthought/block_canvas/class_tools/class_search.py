""" Tool for searching for functions within a set of python modules.
"""

# Standard library imports
import re

# Enthought library imports.
from enthought.traits.api import HasTraits, List, Str, on_trait_change, Bool

from enthought.block_canvas.function_tools.function_search import regex_from_str

# Local imports

# Global variables
#NEW_FUNC_NAME = 'Add new function'


class ClassSearch(HasTraits):
    """ Very simple class searching.

        fixme: This is really a general search mechanism.  It has nothing
               specific to searching functions in it.  It really searches
               for names found within packages...

        fixme: should be the same search for functions as well as classes.
               
        fixme: Should do full text searches of docstrings as well.  We should
               use an indexer for this (pylucene?)
    """

    ##########################################################################
    # ClassSearch traits
    ##########################################################################

    # The search term.  This pattern will match *anywhere* in the name or
    # module of a class (depending on how the search flags are set).
    search_term = Str

    # The search results in a form suitable for display.
    # List(CallableObject)
    search_results = List

    # The filters which are applied against the class names. Unlike
    # search_term, these filters match exactly -- not anywhere in the 
    # searched text.
    name_filters = Str("_*, *test*")

    # The filters which are applied against the class package. Unlike
    # search_term, these filters match exactly -- not anywhere in the 
    # searched text.
    module_filters = Str("*tests*, *retired*, *.setup")

    # Should we search for pattern matches in the class name?
    search_name = Bool(True)
    
    # Should we search for pattern matches in the class module?
    search_module = Bool(True)
    
    # List of objects that have module and name as string attributes.
    all_classes = List

    
    #########################################################################
    # object interface
    #########################################################################

    def __init__(self, **traits):
        """ fixme: This is here because the on_trait_change decorators don't 
                   fire for initialization and we want do_search to fire
                   immediately.
        """

        super(ClassSearch, self).__init__(**traits)
        self.do_search()
        

    ##########################################################################
    # FunctionSearch interface
    ##########################################################################

    @on_trait_change('search_term', 'name_filters', 'module_filters', 
                     'search_name', 'search_module', 'all_classes')
    def do_search(self):
        """ Perform search using the current search term
        """

        items = self._match_anywhere()
        items = self._move_leading_matches_to_front(items)                    
        items = self._filter_unwanted_classes(items)
            
        self.search_results = items

    def _match_anywhere(self):
        """ Match search term to class name and/or module name, by 
            matching the search patterns anywhere within the strings.
        """
        items = []
        # First, match filters anywhere within function name and module.
        filters = regex_from_str(self.search_term, match_anywhere=True)
        for a_class in self.all_classes:
            for filter in filters:                   
                if (self.search_name and 
                    filter.match(a_class.name) is not None):
                    items.append(a_class)
                    break
                elif (self.search_module and 
                      filter.match(a_class.module) is not None):
                    items.append(a_class)
                    break

        return items

    def _move_leading_matches_to_front(self, items):
        """ Move classes that match at the beginning of the function name
            to the front of the list.  The returned list is sorted 
            alphabetically otherwise.            
        """    
        # leading will hold these functions anditems will hold all the others.
        leading = []
        filters = regex_from_str(self.search_term, match_anywhere=False)
        
        # iterate over a copy of the list because we are going to modify
        # the original in the loop.
        for a_class in items[:]:
            for filter in filters:                   
                if (self.search_name and 
                    filter.match(a_class.name) is not None):
                    items.remove(a_class)
                    leading.append(a_class)
                    break
                    
        # Sort the individual list.
        def cmp_name(x,y):
            """ Compare the name of the classes, ignoring case
            """
            return cmp(x.name.lower(), y.name.lower())
        
        # Now, reconstruct the list with leading functions first.    
        result = sorted(leading, cmp=cmp_name) + sorted(items, cmp=cmp_name)
        return result
        
    def _filter_unwanted_classes(self, items):
        """ And remove out any functions that match the filters.
        """
        for filter in regex_from_str(self.name_filters, match_anywhere=False):
            items = [ a_class for a_class in items
                          if filter.match(a_class.name) is None ]
        for filter in regex_from_str(self.module_filters, match_anywhere=False):
            items = [ a_class for a_class in items
                          if filter.match(a_class.module) is None ]
        
        return items
        
if __name__ == "__main__":

    # Not really needed, but handy.
    from class_library import MinimalClassInfo
    
    # Set up a (very) small library (list) of functions.
    library = [MinimalClassInfo(module=module, name=name) for module, name in 
                  [('foo','bar'), ('big.bad','wolf')]]
    print 'full library:', library

    # Default search should return everything.
    search = ClassSearch(all_classes=library)
    print 'no search term:', search.search_results
    
    # 'ba' should return everything as well because both classes match.
    search.search_term = 'ba'
    print search.search_term, 
    print search.search_results
    
    # 'foo' will only match one classes.
    search.search_term = 'foo'
    print search.search_term, 
    print search.search_results
