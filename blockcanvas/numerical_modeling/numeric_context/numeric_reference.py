#-------------------------------------------------------------------------------
#
#  A named reference to a single numeric context array value.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" A named reference to a single numeric context array value.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Instance, Str, Property

#-------------------------------------------------------------------------------
#  'NumericReference' class:
#-------------------------------------------------------------------------------

class NumericReference ( HasPrivateTraits ):
    """ A named reference to a single numeric context array value.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The context this is a reference to:
    context = Instance( 'blockcanvas.model.numeric_context.a_numeric_context.'
                        'ANumericContext' )

    # The name of the context item this is a reference to:
    name = Str

    # The value of the context item:
    value = Property

    #-- Property Implementations -----------------------------------------------

    def _get_value ( self ):
        return self.context[ self.name ]

    def _set_value ( self, value ):
        self.context[ self.name ] = value

    #-- Event Handlers ---------------------------------------------------------

    def _context_modified_changed_for_context ( self, event ):
        if ((event.reset and (self.name in self.context.context_names)) or
            (self.name in event.modified)):
            self.trait_property_changed( 'value', None, self.value )

