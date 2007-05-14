#-------------------------------------------------------------------------------
#  
#  Defines an array value contained in the context.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines an array value contained in the context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Str, Property

from a_numeric_item \
    import ANumericItem
    
from context_modified \
    import ContextModified
    
#-------------------------------------------------------------------------------
#  'ContextItem' class:
#-------------------------------------------------------------------------------

class ContextItem ( ANumericItem ):
    """ Defines an array value contained in the context.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the context trait for this item:
    name = Str

    # The current value of the associated numeric array:
    data = Property

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'data' property:
    #---------------------------------------------------------------------------

    def _get_data ( self ):
        return self.context.context_data[ self.name ]

    def _set_data ( self, value ):
        self.context.context_data[ self.name ] = value
        # ('self.context' might have just removed us)
        if self.context is not None:
            self.context.post_context_modified(
                ContextModified( modified = [ self.name ] )
            )
