#-------------------------------------------------------------------------------
#  
#  Defines a concrete derived numeric context that defers propagation of
#  all upstream context events to a future point in time. The purpose is to
#  allow iterative computations from triggering large numbers of events,
#  most of which do not need to be immediately processed by downstream
#  contexts. This class is related to the TraitsContext, but is intended
#  to be used closer to the root context to improve performance.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines a concrete derived numeric context that defers propagation of
    all upstream context events to a future point in time. The purpose is to
    allow iterative computations from triggering large numbers of events,
    most of which do not need to be immediately processed by downstream
    contexts. This class is related to the TraitsContext, but is intended
    to be used closer to the root context to improve performance.
"""

# FIXME 'DeferredContext' and 'ANumericContext.defer_events' are similar
# solutions to the same problem. Do we need them both? Should one approach
# subsume the other? How can we at least reuse code between them?

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Int, Any, Undefined, Bool

from enthought.util.wx.do_later \
    import do_after

from context_modified \
    import ContextModified
    
from derivative_context \
    import DerivativeContext
    
#-------------------------------------------------------------------------------
#  'DeferredContext' class:
#-------------------------------------------------------------------------------

class DeferredContext ( DerivativeContext ):
    """ Defines a concrete derived numeric context that defers propagation of
        all upstream context events to a future point in time. The purpose is to
        allow iterative computations from triggering large numbers of events,
        most of which do not need to be immediately processed by downstream
        contexts. This class is related to the TraitsContext, but is intended
        to be used closer to the root context to improve performance.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Number of milliseconds to defer event propagation. If the value is less
    # than or equal to zero, events are propagated immediately; otherwise the
    # value specifies the propagation delay. Note that if deferred, the events
    # will always be deferred until the currently running code returns to the
    # event dispatch loop, so it is not necessary to set this
    # to a larger number to correctly handle long running calculations:
    context_propagation_delay = Int( 1 )

    #-- Private Traits ---------------------------------------------------------

    _cur_mask         = Any( Undefined )
    _context_reset    = Bool( False )
    _context_modified = Any( {} )
    _context_added    = Any( {} )
    _context_removed  = Any( {} )
    _context_changed  = Any( {} )
    # TODO Use sets instead of dicts (new in 2.4)

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the context modified event:
    #---------------------------------------------------------------------------

    def _context_is_modified ( self, event ):
        """ Handles the context modified event.
        """
        if self.context_propagation_delay <= 0:
            super( DeferredContext, self )._context_is_modified( event )
        else:
            if event.reset:
                self._context_reset    = True
                self._context_modified = {}
            elif not self._context_reset:
                self._context_modified.update( dict.fromkeys( event.modified ) )

            self._context_changed.update( dict.fromkeys( event.changed ) )

            self._move_dict_items( self._context_removed,
                                   self._context_added, event.removed )

            self._move_dict_items( self._context_added,
                                   self._context_removed, event.added )

            # (Is this correct? cf. 'event.merge_context_modified_events'...)

            do_after( self.context_propagation_delay,
                      self._propagate_context_modified )

    #-- Private Methods --------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Updates the set of items being added or removed:
    #---------------------------------------------------------------------------

    def _move_dict_items ( self, to_dict, from_dict, names ):
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
        self.post_context_modified( ContextModified(
            reset    = self._context_reset,
            modified = self._context_modified.keys(),
            added    = self._context_added.keys(),
            removed  = self._context_removed.keys(),
            changed  = self._context_changed.keys()
        ) )

        self._context_reset    = False
        self._context_modified = {}
        self._context_added    = {}
        self._context_removed  = {}
        self._context_changed  = {}

