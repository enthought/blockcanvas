#-------------------------------------------------------------------------------
#
#  Defines a concrete class for a derived, filtered numeric context which
#  reduces the data it receives from its upstream context via a numeric
#  boolean mask.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines a concrete class for a derived, filtered numeric context which
    reduces the data it receives from its upstream context via a numeric
    boolean mask.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import compress, nonzero, put, putmask

from enthought.traits.api \
    import Bool, Property, Undefined

from constants \
    import CreateContext

from filter_context \
    import FilterContext

#-------------------------------------------------------------------------------
#  'ReductionContext' class:
#-------------------------------------------------------------------------------

class ReductionContext ( FilterContext ):
    """ Defines a concrete class for a derived, filtered numeric context which
        reduces the data it receives from its upstream context via a numeric
        boolean mask.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    context_selection = Property

    # Should filtered out values be set to a specified value, rather than
    # discarded?
    use_value = Bool( False )

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

        if self.use_value:
            temp = data.copy()
            putmask( temp, mask == 0, self.context_value_for( name ) )
            return temp

        return compress( mask, data, axis = 0 )

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

        if self.use_value:
            temp = data.copy()
            putmask( temp, mask == 0, self.context_value_for( name ) )
            return temp

        return compress( mask, data, axis = 0 )

    #---------------------------------------------------------------------------
    #  Sets the value of a specified item:
    #---------------------------------------------------------------------------

    def set_context_data ( self, name, value ):
        """ Sets the value of a specified item.
        """
        mask = self._mask
        if mask is not None:
            data = self.context.get_context_data( name )
            put( data, nonzero( mask ), value )
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
            super( ReductionContext, self ).set_context_undefined( name, value )
        else:
            data = self.context.get_context_undefined( name, value )
            if data is not Undefined:
                put( data, nonzero( mask ), value )
                self.context.set_context_undefined( name, data )

    #---------------------------------------------------------------------------
    #  Gets a ReductionContext associated with the context:
    #---------------------------------------------------------------------------

    def get_reduction_context ( self, mode = CreateContext ):
        """ Gets a ReductionContext associated with the context.
        """
        return self.create_context( mode )

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_selection' property:
    #---------------------------------------------------------------------------

    def _get_context_selection ( self ):
        context_mask = self.context.context_selection
        self_mask    = self._mask
        if (self_mask is None) or (context_mask is None):
            return context_mask

        return compress( self_mask, context_mask, axis = 0 )

