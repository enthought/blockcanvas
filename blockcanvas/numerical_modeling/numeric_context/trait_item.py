#-------------------------------------------------------------------------------
#
#  Defines an array value contained in an external object trait.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines an array value contained in an external object trait.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Instance, Str, Property

from a_numeric_item \
    import ANumericItem

from context_modified \
    import ContextModified

#-------------------------------------------------------------------------------
#  'TraitItem' class:
#-------------------------------------------------------------------------------

class TraitItem ( ANumericItem ):
    """ Defines an array value contained in an external object trait.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Object containing the array:
    object = Instance( HasTraits )

    # Id of the array trait:
    id = Str

    # Name of the context trait for this item:
    name = Property

    # The current value of the associated numeric array:
    data = Property

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'data' property:
    #---------------------------------------------------------------------------

    def _get_data ( self ):
        return getattr( self.object, self.id )

    def _set_data ( self, value ):
        setattr( self.object, self.id, value )

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        return self._name or self.id

    def _set_name ( self, name ):
        old = self.name
        if name != old:
            self._name = name
            if self.context is not None:
                self.post_context_modified(
                    ContextModified( removed = [ old ], added = [ name ] )
                )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the 'object' trait being changed:
    #---------------------------------------------------------------------------

    def _object_changed ( self, old, new ):
        """ Handles the 'object' trait being changed.
        """
        if self.context is not None:
            self._set_listener( old, self.id, True )
            self._set_listener( new, self.id, False )

    #---------------------------------------------------------------------------
    #  Handles the 'id' trait being changed
    #---------------------------------------------------------------------------

    def _id_changed ( self, old, new ):
        """ Handles the 'id' trait being change.
        """
        if self.context is not None:
            self._set_listener( self.object, old, True )
            self._set_listener( self.object, new, False )

    #---------------------------------------------------------------------------
    #  Handles the 'context' trait being changed:
    #---------------------------------------------------------------------------

    def _context_changed ( self, context ):
        self._set_listener( self.object, self.id, context is None )

    #-- Private Methods --------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Adds/Removes a listener on the specified object trait:
    #---------------------------------------------------------------------------

    def _set_listener ( self, object, name, remove ):
        """ Adds/Removes a listener on the specified object trait.
        """
        if (object is not None) and (name != ''):
            object.on_trait_change( self._data_updated, name, remove = remove )

    #---------------------------------------------------------------------------
    #  Handles the data associated with this item being changed:
    #---------------------------------------------------------------------------

    def _data_updated ( self, object, name, old, new ):
        """ Handles the data associated with this item being changed.
        """
        self.post_context_modified( ContextModified( modified = [ self.name ] ))
