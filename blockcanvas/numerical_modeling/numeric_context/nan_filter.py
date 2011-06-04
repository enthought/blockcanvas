#-------------------------------------------------------------------------------
#
#  Creates a filter for any element in all arrays of a context which are
#  NaNs (or its inverse: the elements which do not contain a NaN for any
#  of a context's arrays).
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Creates a filter for any element in all arrays of a context which are
    NaNs (or its inverse: the elements which do not contain a NaN for any
    of a context's arrays).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy import isfinite, logical_not

from traits.api \
    import Bool

from a_numeric_filter \
    import ANumericFilter

#-------------------------------------------------------------------------------
#  'NaNFilter' class:
#-------------------------------------------------------------------------------

class NaNFilter ( ANumericFilter ):
    """ Creates a filter for any element in all arrays of a context which are
        NaNs (or its inverse: the elements which do not contain a NaN for any
        of a context's arrays).
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Should the values be inverted (0 <--> 1)?
    invert = Bool( True, event = 'modified' )

    #-- 'ANumericFilter' Class Overrides ---------------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #---------------------------------------------------------------------------

    def evaluate ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        result = None
        for name in context.context_names:
            if result is None:
                result = isfinite( context[ name ] )
            else:
                result = result & isfinite( context[ name ] )

        if self.invert or (result is None):
            return result

        return logical_not( result )

    #---------------------------------------------------------------------------
    #  Returns whether a specified set of context changes affects the filter:
    #---------------------------------------------------------------------------

    def context_changed ( self, context, names ):
        """ Returns whether a specified set of context changes affects the filter.
        """
        if self.enabled:
            context_names = context.context_names
            for name in names:
                if name in context_names:
                    return True

        return False

