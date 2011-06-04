#-------------------------------------------------------------------------------
#
#  Creates a special sort filter which defines a sorting order for the
#  elements of a context's arrays based on a specified Python expression.
#  The result of the expression can be used to sort the elements in either
#  ascending or descending order.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Creates a special sort filter which defines a sorting order for the
    elements of a context's arrays based on a specified Python expression.
    The result of the expression can be used to sort the elements in either
    ascending or descending order.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Enum

from enthought.traits.ui.api \
    import View

from expression_filter \
    import ExpressionFilter

#-------------------------------------------------------------------------------
#  'SortFilter' class:
#-------------------------------------------------------------------------------

class SortFilter ( ExpressionFilter ):
    """ Creates a special sort filter which defines a sorting order for the
        elements of a context's arrays based on a specified Python expression.
        The result of the expression can be used to sort the elements in either
        ascending or descending order.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Sort mode:
    mode = Enum( 'ascending', 'descending', event = 'modified' )

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( 'name', 'filter', 'mode' )

    #-- 'ANumericFilter' Class Overrides ---------------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #---------------------------------------------------------------------------

    def __call__ ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        if self.enabled:
            values = self.evaluate( context )
            if values is not None:
                values = zip( range( len( values ) ), values )
                if self.mode == 'ascending':
                    values.sort( lambda l, r: cmp( l[1], r[1] ) )
                else:
                    values.sort( lambda l, r: cmp( r[1], l[1] ) )

                return [ v[0] for v in values ]

        return None

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #---------------------------------------------------------------------------

    def evaluate ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        try:
            return self._block.evaluate( context )
        except:
            return None

