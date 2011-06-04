#-------------------------------------------------------------------------------
#
#  Defines a concrete class for a derived, filtered numeric context which
#  passes the data it receives from its upstream context through
#  unmodified, but provides a 'selection mask', which is a numeric boolean
#  array that indicates which data items are in the selection.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines a concrete class for a derived, filtered numeric context which
    passes the data it receives from its upstream context through
    unmodified, but provides a 'selection mask', which is a numeric boolean
    array that indicates which data items are in the selection.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import maximum, sum

from traits.api \
    import Property

from constants \
    import CreateContext

from filter_context \
    import FilterContext

#-------------------------------------------------------------------------------
#  'SelectionContext' class:
#-------------------------------------------------------------------------------

class SelectionContext ( FilterContext ):
    """ Defines a concrete class for a derived, filtered numeric context which
        passes the data it receives from its upstream context through
        unmodified, but provides a 'selection mask', which is a numeric boolean
        array that indicates which data items are in the selection.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    context_selection = Property

    #-- 'ANumericContext' Class Method Overrides -------------------------------

    #---------------------------------------------------------------------------
    #  Gets a ReductionContext associated with the context:
    #---------------------------------------------------------------------------

    def get_reduction_context ( self, mode = CreateContext ):
        """ Gets a ReductionContext associated with the context.
        """
        return self.hook_context( self.context.get_reduction_context( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a MappingContext associated with the context:
    #---------------------------------------------------------------------------

    def get_mapping_context ( self, mode = CreateContext ):
        """ Gets a MappingContext associated with the context.
        """
        return self.hook_context( self.context.get_mapping_context( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a SelectionContext associated with the context:
    #---------------------------------------------------------------------------

    def get_selection_context ( self, mode = CreateContext ):
        """ Gets a SelectionContext associated with the context.
        """
        return self.create_context( mode )

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_selection' property:
    #---------------------------------------------------------------------------

    def _get_context_selection ( self ):
        context_mask = self.context.context_selection
        self_mask    = self._mask
        if self_mask is None:
            return context_mask

        if context_mask is None:
            return self_mask

        if sum( context_mask & self_mask ) == 0:
            return context_mask | self_mask

        return maximum( context_mask, self_mask )

