#-------------------------------------------------------------------------------
#  
#  Defines a filter specified by an explicit mask.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines a filter specified by an explicit mask.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Str, Array
    
from a_numeric_filter \
    import ANumericFilter
    
#-------------------------------------------------------------------------------
#  'MaskFilter' class:
#-------------------------------------------------------------------------------

class MaskFilter ( ANumericFilter ):
    """ Defines a filter specified by an explicit mask.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the filter:
    name = Str( 'Mask' )

    # The mask array:
    mask = Array( event = 'modified' )

    #-- 'ANumericFilter' Class Method Overrides --------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #---------------------------------------------------------------------------

    def evaluate ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        return self.mask

