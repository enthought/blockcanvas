#-------------------------------------------------------------------------------
#
#  Defines an array value contained within a sub-context.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines an array value contained within a sub-context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Property, Str

from a_numeric_item \
    import ANumericItem

#-------------------------------------------------------------------------------
#  'SubContextItem' class:
#-------------------------------------------------------------------------------

class SubContextItem ( ANumericItem ):
    """ Defines an array value contained within a sub-context.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the context trait for this item:
    name = Property

    # Name of the sub-context this item belongs to:
    sub_context_name = Str

    # The name of the item within the sub context:
    sub_name = Str

    # The current value of the associated numeric array:
    data = Property

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'data' property:
    #---------------------------------------------------------------------------

    def _get_data ( self ):
        return self.context.context_data[ self.sub_context_name ] \
            .get_dotted( self.sub_name )

    def _set_data ( self, value ):
        self.context.context_data[ self.sub_context_name ] \
            .set_dotted( self.sub_name, value )

    def _get_name ( self ):
        if self._name is None:
            self._name = '%s.%s' % (self.sub_context_name, self.sub_name )

        return self._name

