#-------------------------------------------------------------------------------
#
#  Creates a filter for all elements specified by a list of array indices
#  (or its inverse: the elements not specified by a list of array indices).
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Creates a filter for all elements specified by a list of array indices
    (or its inverse: the elements not specified by a list of array indices).
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy import ones, zeros

from traits.api \
    import List, Int, Bool

from a_numeric_filter \
    import ANumericFilter

#-------------------------------------------------------------------------------
#  'IndexFilter' class:
#-------------------------------------------------------------------------------

class IndexFilter ( ANumericFilter ):
    """ Creates a filter for all elements specified by a list of array indices
        (or its inverse: the elements not specified by a list of array indices).
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # List of context indices to which the filter applies:
    indices = List( Int )

    # Should the values be inverted (0 <--> 1)?
    invert = Bool( False, event = 'modified' )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the 'indices' trait being changed:
    #---------------------------------------------------------------------------

    def _indices_changed ( self ):
        """ Handles the 'indices' trait being changed.
        """
        self.updated = True

    def _indices_items_changed ( self ):
        """ Handles the 'indices' trait being changed.
        """
        self.updated = True

    #-- 'ANumericFilter' Class Overrides ---------------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #---------------------------------------------------------------------------

    def evaluate ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        if len( self.indices ) == 0:
            return None

        indices = list( context.context_indices )
        if self.invert:
            value  = 0
            result = ones( ( len( indices ), ), bool )
        else:
            value  = 1
            result = zeros( ( len( indices ), ), bool )

        try:
            result[ indices ] = value
        except:
            pass

        return result

