#-------------------------------------------------------------------------------
#  
#  Defines a termination numeric context which filters (i.e. reduces) the
#  data it receives from its upstream numeric context using its selection
#  mask.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines a termination numeric context which filters (i.e. reduces) the
    data it receives from its upstream numeric context using its selection
    mask.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import compress, nonzero, put

from enthought.traits.api \
    import Constant, Undefined
    
from termination_context \
    import TerminationContext
    
#-------------------------------------------------------------------------------
#  'SelectionReductionContext' class:
#-------------------------------------------------------------------------------

class SelectionReductionContext ( TerminationContext ):
    """ Defines a termination numeric context which filters (i.e. reduces) the
        data it receives from its upstream numeric context using its selection
        mask.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    context_selection = Constant( None )

    #-- 'ANumericContext' Class Methods Overrides ------------------------------

    #---------------------------------------------------------------------------
    #  Returns the value of a specified item:
    #---------------------------------------------------------------------------

    def get_context_data ( self, name ):
        """ Returns the value of a specified item.
        """
        data = self.context.get_context_data( name )
        mask = self.context.context_selection
        if mask is None:
            return []

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

        mask = self.context.context_selection
        if mask is None:
            return []

        return compress( mask, data, axis = 0 )

    #---------------------------------------------------------------------------
    #  Sets the value of a specified item:
    #---------------------------------------------------------------------------

    def set_context_data ( self, name, value ):
        """ Sets the value of a specified item.
        """
        data = self.context.get_context_data( name )
        mask = self.context.context_selection
        if mask is not None:
            put( data, nonzero( mask ), value )
            self.context.set_context_data( name, data )

    #---------------------------------------------------------------------------
    #  Sets the value of a currently undefined item:
    #---------------------------------------------------------------------------

    def set_context_undefined ( self, name, value ):
        """ Sets the value of a currently undefined item.
        """
        mask = self.context.context_selection
        if mask is None:
            super( SelectionReductionContext, self ).set_context_undefined(
                                                                   name, value )
        else:
            data = self.context.get_context_undefined( name, value )
            if data is not Undefined:
                put( data, nonzero( mask ), value )
                self.context.set_context_undefined( name, data )

