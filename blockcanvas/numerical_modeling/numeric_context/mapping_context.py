#-------------------------------------------------------------------------------
#
#  Defines a concrete class for a derived, filtered numeric context which
#  reorders the data it receives from its upstream context via a numeric
#  index array.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines a concrete class for a derived, filtered numeric context which
    reorders the data it receives from its upstream context via a numeric
    index array.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy import arange, ones, putmask, take

from enthought.traits.api \
    import Property, Undefined

from constants \
    import CreateContext

from filter_context \
    import FilterContext

#-------------------------------------------------------------------------------
#  'MappingContext' class:
#-------------------------------------------------------------------------------

class MappingContext ( FilterContext ):
    """ Defines a concrete class for a derived, filtered numeric context which
        reorders the data it receives from its upstream context via a numeric
        index array.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    context_selection = Property

    #-- Private Traits ---------------------------------------------------------

    # The inverse of the mapping 'mask':
    _imask = Property

    #-- 'ANumericContext' Class Method Overrides -------------------------------

    #---------------------------------------------------------------------------
    #  Returns the value of a specified item:
    #---------------------------------------------------------------------------

    def get_context_data ( self, name ):
        """ Returns the value of a specified item.
        """
        data = self.context.get_context_data( name )
        mask = self._mask
        if mask is None:
            return data

        return take( data, mask, axis = 0 )

    #---------------------------------------------------------------------------
    #  Gets the value of a currently undefined item:
    #---------------------------------------------------------------------------

    def get_context_undefined ( self, name, value ):
        """ Gets the value of a currently undefined item.
        """
        data = self.context.get_context_undefined( name, value )
        if data is Undefined:
            return data

        mask = self._mask
        if mask is None:
            return data

        return take( data, mask, axis = 0 )

    #---------------------------------------------------------------------------
    #  Sets the value of a specified item:
    #---------------------------------------------------------------------------

    def set_context_data ( self, name, value ):
        """ Sets the value of a specified item.
        """
        data = self.context.get_context_data( name )
        mask = self._imask
        if mask is not None:
            putmask( data, ones( data.shape, bool ), value )
            data = take( data, mask, axis = 0 )
            self.context.set_context_data( name, data )
        else:
            self.context.set_context_data( name, value )

    #---------------------------------------------------------------------------
    #  Sets the value of a currently undefined item:
    #---------------------------------------------------------------------------

    def set_context_undefined ( self, name, value ):
        """ Sets the value of a currently undefined item.
        """
        mask = self._mask
        if mask is None:
            super( MappingContext, self ).set_context_undefined( name, value )
        else:
            data = self.context.get_context_undefined( name, value )
            if data is not Undefined:
                putmask( data, ones( data.shape, bool ), value )
                data = take( data, mask, axis = 0 )
                self.context.set_context_undefined( name, data )

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
        return self.create_context( mode )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the context modified event:
    #---------------------------------------------------------------------------

    def _context_is_modified ( self, event ):
        """ Handles the context modified event.
        """
        if event.reset:
            self._cur_imask = None

        super( MappingContext, self )._context_is_modified( event )

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_selection' property:
    #---------------------------------------------------------------------------

    def _get_context_selection ( self ):
        context_mask = self.context.context_selection
        mask         = self._mask
        if (mask is None) or (context_mask is None):
            return context_mask

        return take( context_mask, mask, axis = 0 )

    #---------------------------------------------------------------------------
    #  Implementation of the '_imask' property:
    #---------------------------------------------------------------------------

    def _get__imask ( self ):
        if (self._cur_imask is None) and (self.context_filter is not None):
            mask = self._mask
            if mask is not None:
                # fixme: Is there a faster way to compute the inverse mask?
                self._cur_imask = imask = arange( len( mask ) )
                for i, j in enumerate( mask ):
                    imask[j] = i

        return self._cur_imask

