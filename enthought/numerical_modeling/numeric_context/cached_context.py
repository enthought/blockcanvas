#-------------------------------------------------------------------------------
#  
#  Defines a termination numeric context which passes all of the data it
#  receives from its upstream numeric context through unchanged, and also
#  caches the values to avoid having to constantly recalculate  upstream
#  values.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines a termination numeric context which passes all of the data it
    receives from its upstream numeric context through unchanged, and also
    caches the values to avoid having to constantly recalculate  upstream
    values.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Undefined

from termination_context \
    import TerminationContext

#-------------------------------------------------------------------------------
#  'CachedContext' class:
#-------------------------------------------------------------------------------

class CachedContext ( TerminationContext ):
    """ Defines a termination numeric context which passes all of the data it
        receives from its upstream numeric context through unchanged, and also
        caches the values to avoid having to constantly recalculate  upstream
        values.
    """

    #-- 'ANumericContext' Class Methods Overrides ------------------------------

    #---------------------------------------------------------------------------
    #  Returns the value of a specified item:
    #---------------------------------------------------------------------------

    def get_context_data ( self, name ):
        """ Returns the value of a specified item.
        """
        cache = self._context_cache
        if cache is None:
            self._context_cache = cache = {}

        result = cache.get( name, Undefined )
        if result is Undefined:
            cache[ name ] = result = self.context.get_context_data( name )

        return result

    #---------------------------------------------------------------------------
    #  Sets the value of a specified item:
    #---------------------------------------------------------------------------

    def set_context_data ( self, name, value ):
        """ Sets the value of a specified item.
        """
        if self._context_cache is not None:
            self._context_cache.pop( name, None )

        super( CachedContext, self ).set_context_data( name, value )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the context modified event:
    #---------------------------------------------------------------------------

    def _context_is_modified ( self, event ):
        """ Handles the context modified event.
        """
        if event.reset:
            self._context_cache = {}

        else:
            cache = self._context_cache
            if cache is not None:
                for name in event.modified:
                    cache.pop( name, None )

                for name in event.removed:
                    cache.pop( name, None )

        super( CachedContext, self )._context_is_modified( event )

