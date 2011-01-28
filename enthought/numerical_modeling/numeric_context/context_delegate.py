#-------------------------------------------------------------------------------
#
#  Delegate base class that can be used to customize various policies of a
#  numeric context via subclassing.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Delegate base class that can be used to customize various policies of a
    numeric context via subclassing.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy import ndarray, nan

from enthought.traits.api \
    import Undefined

#-------------------------------------------------------------------------------
#  'ContextDelegate' class:
#-------------------------------------------------------------------------------

class ContextDelegate ( object ):
    """ Base class for the delegate class a NumericContext uses to implement
        various policy decisions. The methods of this class define the delegate
        interface, as well as provide the default implementation.
    """

    #-- ContextDelegate Interface ----------------------------------------------

    def default_value_for ( self, name, value ):
        """ Returns the default array value to use for a specified value.
        """
        if isinstance( value, ndarray ):
            try:
                value = value.flat[0]
            except:
                return Undefined

        if isinstance( value, float ):      return nan
        if isinstance( value, int ):        return 0
        if isinstance( value, basestring ): return ''
        if isinstance( value, bool ):       return False
        if isinstance( value, complex ):    return 0j

        return None

# Create a default context delegate:
default_context_delegate = ContextDelegate()

