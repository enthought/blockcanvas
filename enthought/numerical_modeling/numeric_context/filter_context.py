#-------------------------------------------------------------------------------
#
#  Defines an abstract base class for a derived numberic context which filter
#  their data in some way.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines an abstract base class for a derived numberic context which filter
    their data in some way.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Instance, Property, Undefined

from a_numeric_filter \
    import ANumericFilter

from context_modified \
    import ContextModified

from derivative_context \
    import DerivativeContext

#-------------------------------------------------------------------------------
#  'FilterContext' class:
#-------------------------------------------------------------------------------

class FilterContext ( DerivativeContext ):
    """ Defines an abstract base class for a derived numberic context which
        filter their data in some way.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask (actually defined in each subclass):
    # context_selection = Property

    # The filter being applied to the context:
    context_filter = Instance( ANumericFilter )

    #-- Private Properties -----------------------------------------------------

    # Current selection mask:
    _mask = Property

    #-- 'ANumericContext' Class Method Overrides -------------------------------

    #---------------------------------------------------------------------------
    #  Prints the context structure:
    #---------------------------------------------------------------------------

    def dump_context ( self, indent = 0 ):
        """ Prints the context structure.
        """
        filter = ''
        mf     = self.context_filter
        if mf is not None:
            filter = ', %s( %08X )' % ( mf.__class__.__name__, id( mf ) )
        print '%s%s( %08X%s )' % (
              ' ' * indent, self.__class__.__name__, id( self ), filter )
        self.context.dump_context( indent + 3 )

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the '_mask' property:
    #---------------------------------------------------------------------------

    def _get__mask ( self ):
        if self._cur_mask is Undefined:
            if self.context_filter is not None:
                self._cur_mask = self.context_filter( self.context )
            else:
                self._cur_mask = None

        return self._cur_mask

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the context modified event:
    #---------------------------------------------------------------------------

    def _context_is_modified ( self, event ):
        """ Handles the context modified event.
        """
        if event.reset:
            self._cur_mask = Undefined
        elif self.context_filter is not None:
            self.context_filter.context_has_changed( self.context,
                                                     event.all_modified )

        super( FilterContext, self )._context_is_modified( event )

    #---------------------------------------------------------------------------
    #  Handles the context filter being changed:
    #---------------------------------------------------------------------------

    def _context_filter_changed ( self, old, new ):
        """ Handles the context filter being changed.
        """
        self._updated_changed_for_context_filter()

    def _updated_changed_for_context_filter ( self ):
        if self._cur_mask is not Undefined:
            self._cur_mask = Undefined
            self.post_context_modified( ContextModified( reset = True ) )

