#-------------------------------------------------------------------------------
#
#  Defines a filter which aggregates the results of several contained filters
#  into a single composite filter. It supports four different compositing
#  rules: and, or, min, and max.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines a filter which aggregates the results of several contained
    filters into a single composite filter. It supports four different
    compositing rules: and, or, min, and max.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy import maximum, minimum

from traits.api \
    import List, Property, Enum

from a_numeric_filter \
    import ANumericFilter

#-------------------------------------------------------------------------------
#  'AggregateFilter' class:
#-------------------------------------------------------------------------------

class AggregateFilter ( ANumericFilter ):
    """ Defines a filter which aggregates the results of several contained
        filters into a single composite filter. It supports four different
        compositing rules: and, or, min, and max.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Sub-filters whose values are combined together:
    filters = List( ANumericFilter )

    # Name of the filter:
    name = Property

    # Combining rule to apply:
    rule = Enum( 'and', 'or', 'min', 'max', cols = 2 )

    #-- 'object' Class Overrides -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, *filters, **traits ):
        """ Initializes the object.
        """
        self.filters = list( filters )
        super( AggregateFilter, self ).__init__( **traits )

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        if self._name:
            return self._name

        return getattr( self, '_get_name_' + self.rule )()

    def _set_name ( self, value ):
        old        = self.name
        self._name = value
        if value != old:
            self.trait_property_changed( 'name', old, value )

    #-- Private Methods --------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Helper methods for constructing the filter name:
    #---------------------------------------------------------------------------

    def _get_name_and ( self ):
        return self._get_name_using( '(%s)', ') and (', 2 )

    def _get_name_or ( self ):
        return self._get_name_using( '(%s)', ') or (', 2 )

    def _get_name_min ( self ):
        return self._get_name_using( 'min( %s )', ', ', 1 )

    def _get_name_max ( self ):
        return self._get_name_using( 'max( %s )', ', ', 1 )

    def _get_name_using ( self, wrapper, separator, threshold ):
        names  = [ f.name for f in self.filters if f.enabled ]
        result = separator.join( names )
        if len( names ) >= threshold:
            return wrapper % result

        if result != '':
            return result

        return 'None'

    #---------------------------------------------------------------------------
    #  Connect/Disconnect events for a specified list of filters:
    #---------------------------------------------------------------------------

    def _listen_to_filters ( self, filters, remove = False ):
        for filter in filters:
            filter.on_trait_change( self._filter_updated, 'updated',
                                    remove = remove )
            filter.on_trait_change( self._name_updated, 'name',
                                    remove = remove )

    #---------------------------------------------------------------------------
    #  Handles a sub-filter being updated:
    #---------------------------------------------------------------------------

    def _filter_updated ( self ):
        """ Handles a sub-filter being updated.
        """
        self.updated = True
        self._name_updated()

    #---------------------------------------------------------------------------
    #  Handles a sub-filter's name being updated:
    #---------------------------------------------------------------------------

    def _name_updated ( self ):
        """ Handles a sub-filter's name being updated.
        """
        if not self._name:
            self.trait_property_changed( 'name', self._name, self.name )

    #---------------------------------------------------------------------------
    #  Implementation of the various 'evaluate' combining rules:
    #---------------------------------------------------------------------------

    def _and_rule ( self, mask1, mask2 ):
        return mask1 & mask2

    def _or_rule ( self, mask1, mask2 ):
        return mask1 | mask2

    def _max_rule ( self, mask1, mask2 ):
        return maximum( mask1, mask2 )

    def _min_rule ( self, mask1, mask2 ):
        return minimum( mask1, mask2 )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the 'rule' trait being changed:
    #---------------------------------------------------------------------------

    def _rule_changed ( self, old, new ):
        """ Handles the 'rule' trait being changed.
        """
        self.updated = True
        self._name_updated()

    #---------------------------------------------------------------------------
    #  Handles the sub-filters being changed:
    #---------------------------------------------------------------------------

    def _filters_changed ( self, old, new ):
        """ Handles the sub-filters being changed.
        """
        self._listen_to_filters( old, True  )
        self._listen_to_filters( new, False )
        self.updated = True
        self._name_updated()

    def _filters_items_changed ( self, event ):
        """ Handles the sub-filters being changed.
        """
        self._listen_to_filters( event.removed, True  )
        self._listen_to_filters( event.added,   False )
        self.updated = True
        self._name_updated()

    #-- 'ANumericFilter' Class Overrides ---------------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #---------------------------------------------------------------------------

    def evaluate ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        mask   = None
        method = getattr( self, '_%s_rule' % self.rule )
        for filter in self.filters:
            maski = filter( context )
            if maski is not None:
                if mask is None:
                    mask = maski
                else:
                    mask = method( mask, maski )

        return mask

    #---------------------------------------------------------------------------
    #  Returns whether a specified set of context changes affects the filter:
    #---------------------------------------------------------------------------

    def context_changed ( self, context, names ):
        """ Returns whether a specified set of context changes affects the filter.
        """
        if self.enabled:
            for filter in self.filters:
                if filter.context_changed( context, names ):
                    return True

        return False

# Define 'FilterSet' as an alias for 'AggregateFilter':
FilterSet = AggregateFilter

