#-------------------------------------------------------------------------------
#  
#  Defines a concrete termination class intended for use with Traits UI
#  based user interfaces or other Traits-based clients connected to the
#  numeric context. It exposes array context items as traits and optionally
#  defers trait notifications until the current computation ends and
#  control returns to the main event dispatch loop. This prevents screen
#  updates from triggering as a result of intermediate or repeated
#  calculations.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines a concrete termination class intended for use with Traits UI
    based user interfaces or other Traits-based clients connected to the
    numeric context. It exposes array context items as traits and optionally
    defers trait notifications until the current computation ends and
    control returns to the main event dispatch loop. This prevents screen
    updates from triggering as a result of intermediate or repeated
    calculations.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Any, Bool, Int, Property

from enthought.util.wx.do_later \
    import do_after

from context_modified \
    import ContextModified
    
from termination_context \
    import TerminationContext
    
#-------------------------------------------------------------------------------
#  'TraitsContext' class:
#-------------------------------------------------------------------------------

class TraitsContext ( TerminationContext ):
    """ Defines a concrete termination class intended for use with Traits UI
        based user interfaces or other Traits-based clients connected to the
        numeric context. It exposes array context items as traits and optionally
        defers trait notifications until the current computation ends and
        control returns to the main event dispatch loop. This prevents screen
        updates from triggering as a result of intermediate or repeated
        calculations.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Number of milliseconds to defer trait notifications. If the value is less
    # than or equal to zero, notifications are sent immediately; otherwise the
    # value specifies the notification delay. Note that if deferred, the
    # notifications will always be deferred until the currently running code
    # returns to the event dispatch loop, so it is not necessary to set this
    # to a larger number to correctly handle long running calculations:
    context_notification_delay = Int( 0 )

    #-- Private Traits ---------------------------------------------------------

    _context_reset    = Bool( False )
    _context_modified = Any( {} )
    _context_added    = Any( {} )
    _context_removed  = Any( {} )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the context modified event:
    #---------------------------------------------------------------------------

    def _context_is_modified ( self, event ):
        """ Handles the context modified event.
        """
        if self.context_notification_delay <= 0:
            self._process_context_modified_event( event )
        else:
            if event.reset:
                self._context_reset    = True
                self._context_modified = {}
            elif not self._context_reset:
                self._context_modified.update( dict.fromkeys( event.modified ) )

            self._context_added_removed( self._context_removed,
                                         self._context_added, event.removed )

            self._context_added_removed( self._context_added,
                                         self._context_removed, event.added )

            do_after( self.context_notification_delay,
                      self._propagate_context_modified )

        super( TraitsContext, self )._context_is_modified( event )

    #-- Private Methods --------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Updates the set of items being added or removed:
    #---------------------------------------------------------------------------

    def _context_added_removed ( self, to_dict, from_dict, names ):
        """ Updates the set of items being added or removed.
        """
        # Add names to the 'to' dict, and remove them from the 'from' dict:
        for name in names:
            to_dict[ name ] = None
            from_dict.pop( name, None )

    #---------------------------------------------------------------------------
    #  Propagate the pending event:
    #---------------------------------------------------------------------------

    def _propagate_context_modified ( self ):
        """ Propagate the pending event.
        """
        self._process_context_modified_event( ContextModified(
            reset    = self._context_reset,
            modified = self._context_modified.keys(),
            added    = self._context_added.keys(),
            removed  = self._context_removed.keys()
        ) )

        self._context_reset    = False
        self._context_modified = {}
        self._context_added    = {}
        self._context_removed  = {}

    #---------------------------------------------------------------------------
    #  Handles the context modified event:
    #---------------------------------------------------------------------------

    def _process_context_modified_event ( self, event ):
        """ Handles the context modified event.
        """
        for name in event.added:
            self.add_trait( name,
                            Property( TraitsContext._trait_value_get,
                                      TraitsContext._trait_value_set ) )

        if event.reset:
            names = self.context_all_names
        else:
            names = event.modified
        for name in names:
            self.trait_property_changed( name, None, self.get_dotted( name ) )

        for name in event.removed:
            self.remove_trait( name )

    #---------------------------------------------------------------------------
    #  'fake' trait Property handlers:
    #---------------------------------------------------------------------------

    def _trait_value_get ( self, name ):
        return self.context.get_dotted( name )

    def _trait_value_set ( self, name, value ):
        self.context.set_dotted( name, value )

