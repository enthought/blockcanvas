#-------------------------------------------------------------------------------
#  
#  Defines an abstract base class for accessing an item in a numeric context.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines an abstract base class for accessing an item in a numeric context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasPrivateTraits, Instance, List, Any, Str, RGBAColor
    
from enthought.util.scipyx \
    import NaN
    
from a_numeric_context import ANumericContext

#-------------------------------------------------------------------------------
#  'ANumericItem' class:
#-------------------------------------------------------------------------------

class ANumericItem ( HasPrivateTraits ):
    """ Defines an abstract base class for accessing an item in a
        NumericContext.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The context containing this item:
    context = Instance( ANumericContext )

    # The list of groups the item belongs to:
    groups = List

    # Name of the context trait for this item (implemented in each subclass):
    #name = Property

    # The current value of the associated numeric array (implemented in each
    # subclass):
    #data = Property

    # Value to be substituted in reduction filters when 'use_value' is True:
    value = Any( NaN )

#-- View related ---------------------------------------------------------------

    # User interface label:
    label = Str

    # String formatting rule:
    format = Str( '%.3f' )

    # Foreground color (intended use: text color, plot line color):
    foreground_color = RGBAColor( 'black' )

    # Background color (intended use: text background color, plot fill color):
    background_color = RGBAColor( 'white' )

