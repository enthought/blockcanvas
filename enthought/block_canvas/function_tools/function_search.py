""" Tool for searching for functions within a set of python modules.
"""

# Standard library imports
import re

# Enthought library imports.
from enthought.traits.api import HasTraits, List, Str, on_trait_change, Bool

# Local imports

# Global variables
#NEW_FUNC_NAME = 'Add new function'


class FunctionSearch(HasTraits):
    """ Very simple function searching.

        fixme: This is really a general search mechanism.  It has nothing
               specific to searching functions in it.  It really searches
               for names found within packages...

        fixme: Should do full text searches of docstrings as well.  We should
               use an indexer for this (pylucene?)
    """

    ##########################################################################
    # FunctionSearch traits
    ##########################################################################

    # The search term.  This pattern will match *anywhere* in the name or
    # module of a function (depending on how the search flags are set).
    search_term = Str

    # The search results in a form suitable for display.
    # List(CallableObject)
    search_results = List

    # The filters which are applied against the functions' names. Unlike
    # search_term, these filters match exactly -- not anywhere in the
    # searched text.
    name_filters = Str("_*, *test*")

    # The filters which are applied against the functions' package. Unlike
    # search_term, these filters match exactly -- not anywhere in the
    # searched text.
    module_filters = Str("*tests*, *retired*, *.setup")

    # Should we search for pattern matches in the function name?
    search_name = Bool(True)

    # Should we search for pattern matches in the function module?
    search_module = Bool(True)

    # List of objects that have module and name as string attributes.
    all_functions = List


    #########################################################################
    # object interface
    #########################################################################

    def __init__(self, **traits):
        """ fixme: This is here because the on_trait_change decorators don't
                   fire for initialization and we want do_search to fire
                   immediately.
        """

        super(FunctionSearch, self).__init__(**traits)
        self.do_search()


    ##########################################################################
    # FunctionSearch interface
    ##########################################################################

    @on_trait_change('search_term', 'name_filters', 'module_filters',
                     'search_name', 'search_module', 'all_functions')
    def do_search(self):
        """ Perform search using the current search term
        """

        items = self._match_anywhere()
        items = self._move_leading_matches_to_front(items)
        items = self._filter_unwanted_functions(items)

        self.search_results = items

    def _match_anywhere(self):
        """ Match search term to function name and/or module name, by
            matching the search patterns anywhere within the strings.
        """
        items = []
        # First, match filters anywhere within function name and module.
        filters = regex_from_str(self.search_term, match_anywhere=True)
        for function in self.all_functions:
            for filter in filters:
                if (self.search_name and
                    filter.match(function.name) is not None):
                    items.append(function)
                    break
                elif (self.search_module and
                      filter.match(function.module) is not None):
                    items.append(function)
                    break

        return items

    def _move_leading_matches_to_front(self, items):
        """ Move functions that match at the beginning of the function name
            to the front of the list.  The returned list is sorted
            alphabetically otherwise.
        """
        # leading will hold these functions anditems will hold all the others.
        leading = []
        filters = regex_from_str(self.search_term, match_anywhere=False)

        # iterate over a copy of the list because we are going to modify
        # the original in the loop.
        for function in items[:]:
            for filter in filters:
                if (self.search_name and
                    filter.match(function.name) is not None):
                    items.remove(function)
                    leading.append(function)
                    break

        # Sort the individual list.
        def cmp_name(x,y):
            """ Compare the name of the functions, ignoring case
            """
            return cmp(x.name.lower(), y.name.lower())

        # Now, reconstruct the list with leading functions first.
        result = sorted(leading, cmp=cmp_name) + sorted(items, cmp=cmp_name)
        return result

    def _filter_unwanted_functions(self, items):
        """ And remove out any functions that match the filters.
        """
        for filter in regex_from_str(self.name_filters, match_anywhere=False):
            items = [ function for function in items
                          if filter.match(function.name) is None ]
        for filter in regex_from_str(self.module_filters, match_anywhere=False):
            items = [ function for function in items
                          if filter.match(function.module) is None ]

        return items

##############################################################################
# Utilitiy functions
##############################################################################

def regex_from_str(str, match_anywhere=False):
    """ Maps a filter string into a set of regular expression objects.

        The string can contain a series of comma separated search terms.
        Use '*' to do a wildcard match to characters in a string much
        like a filename match.  If match_anywhere is true, the search
        terms are will match anywhere within a searched string.
    """

    f = []
    for filter in str.split(','):
        str = filter.strip().replace("*", ".*")

        # Match the string anywhere within the name.
        if match_anywhere:
            str = '.*'+str+'.*'

        # If re barfs, just match everything
        # fixme: This is dangerous, because we use this in places,
        #        where we wouldn't want to match anything on failure.
        #        refactor this up so that the calling function can make
        #        this decision.
        try:
            f.append(re.compile(str, re.IGNORECASE))
        except:
            f.append(re.compile(".*"))

    return f


if __name__ == "__main__":
    # Not really needed, but handy.
    from function_library import BasicFunction

    # Set up a (very) small library (list) of functions.
    library = [BasicFunction(module=module, name=name) for module, name in
                  [('foo','bar'), ('big.bad','wolf')]]
    print 'full library:', library

    # Default search should return everything.
    search = FunctionSearch(all_functions=library)
    print 'no search term:', search.search_results

    # 'ba' should return everything as well because both functions match.
    search.search_term = 'ba'
    print search.search_term,
    print search.search_results

    # 'foo' will only match one function.
    search.search_term = 'foo'
    print search.search_term,
    print search.search_results
