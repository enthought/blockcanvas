#-------------------------------------------------------------------------------
#
#  Defines the root of a numeric context 'pipeline'.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the root of a numeric context 'pipeline'.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import logging
logger = logging.getLogger( __name__ )

from numpy \
    import ndarray, arange, array, empty

from enthought.traits.api \
    import HasTraits, Instance, Str, List, Property, Undefined, \
           TraitDictEvent, TraitError, Dict, Bool

from enthought.util.dict \
    import sub_dict

from enthought.util.sequence \
    import concat, disjoint


from a_numeric_context \
    import ANumericContext

from a_numeric_item \
    import ANumericItem

from constants \
    import empty_group, NonPickleable

from event_dict \
    import EventDict

from context_delegate \
    import ContextDelegate, default_context_delegate

from context_item \
    import ContextItem

from context_modified \
    import ContextModified

from error \
    import NumericContextError

from sub_context_item \
    import SubContextItem

#-------------------------------------------------------------------------------
#  'NumericContext' class:
#-------------------------------------------------------------------------------

class NumericContext ( ANumericContext ):
    """ Defines the root of a numeric context 'pipeline'.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The context dictionary:
    context_data = Instance( EventDict, (), allow_none = False )

    # The name of the context:
    context_name = Str( 'Context' )

    # List of array descriptor items:
    context_items = List( ANumericItem, transient = True )

    # List of available data item names in the current group:
    context_names = Property( transient = True )

    # List of available data item names in the entire context:
    context_all_names = Property( transient = True )

    # The 'name' of the current context group (may be a tuple representing
    # the shape of the group's contents:
    context_group = Property( transient = True )

    # A list of all currently defined groups:
    context_groups = Property( transient = True )

    # The array indices:
    context_indices = Property( transient = True )

    # The ContextDelegate the context uses to handle various policy decisions:
    context_delegate = Instance( ContextDelegate )

    # The list of all sub_context names:
    sub_context_names = Property( transient = True )

    # Initializing private traits so as to help in unpickling.
    _context_items    = Dict( transient = True )
    _context_groups   = Dict
    _sub_contexts     = Dict
    
    # Map to keep track of dynamic bindings, indexed by name and value bound
    _dynamic_bindings = Dict

    # Whether to buffer 'dict_modified' and 'context_modified' events. When
    # true, no events are fired, and when reverted to false, one pair of events
    # fire that represents the net change since 'defer_events' was set.
    defer_events = Property( depends_on = 'context_data.defer_events' )

    # Whether to withhold events entirely.
    _no_events = Bool( False )

    #-- 'object' Class Method Overrides ----------------------------------------

    #---------------------------------------------------------------------------
    #  Initialize the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, **traits ):
        """ Initialize the object.
        """
        super( NumericContext, self ).__init__( **traits )
        self.init()

    #---------------------------------------------------------------------------
    #  Initializes the initial state of the object:
    #---------------------------------------------------------------------------

    def init ( self ):
        """ Initializes the initial state of the object.
        """

        self._context_items  = {}
        self._context_groups = {}
        self._sub_contexts   = {}

        self._context_data_changed( None, self.context_data )

        # FIXME The 'depends_on' argument to 'Property' doesn't seem to work
        # properly in traits 2.0 (but dmorrill says it's fixed in 2.1).
        self.context_data.on_trait_change( self._defer_events_changed,
                                           'defer_events' )

    #---------------------------------------------------------------------------
    #  Clears the internal state of the object:
    #---------------------------------------------------------------------------

    def dispose ( self ):
    	""" Clears the interal state of the object to ensure all memory is
	    released. If this is not called, circular references can confuse
	    pythons garbage collection and memory will be 'leaked'
	"""

	# FIXME: should this call dispose on sub_contexts?
	#  maybe, if the refcount is low enough, otherwise other uses
	#  of the subcontext would lose its data

	self.context_data.clear()
	self._dynamic_bindings.clear()
	if self._dict is not None:
	    self._dict.clear()
	self._sub_contexts.clear()
	self.context_delegate = None

    #---------------------------------------------------------------------------
    #  Handle saving/restoring the object's state:
    #---------------------------------------------------------------------------
    # FIXME Revisit this pickling policy when Traits 2.1 becomes available.

    def correct_state_items( self, state ):
        """ Correction on state saved in old pickles.

            In some pickles, 'context_data' is saved as a dict, when now it is
            expected to be a EventDict.
            
        """
        
        context_data = state.pop( 'context_data', None )
        if context_data != None:
            if not isinstance( context_data, EventDict ):
                if isinstance( context_data, dict ):
                    context_data = EventDict( context_data )
                else:
                    context_data  = EventDict()
            state[ 'context_data' ] = context_data

        return
    
    def __getstate__ ( self ):
        state = super( NumericContext, self ).__getstate__()

        # Save non-transient traits (Traits 2.1 will do this for us):
        for k in HasTraits.get( self, transient = True ):
            if k in state:
                del state[ k ]

        # Filter out any unpickleable data from the context dictionary:
        if 'context_data' in state:
            state[ 'context_data' ] = state[ 'context_data' ].copy()
            for k, v in state[ 'context_data' ].items():
                if isinstance( v, NonPickleable ):
                    del state[ 'context_data' ][k]

        # Return the saveable state:
        state[ '__numeric_context_version__' ] = 1
        
        return state

    def __setstate__ ( self, state ):
        version = state.pop( '__numeric_context_version__', 0)

        if version < 1:
            self.correct_state_items( state )
            
            k = '__numeric_context_saved_bindings__'
            if k in state:
                state[ '_dynamic_bindings' ] = state.pop( k )

        super( NumericContext, self ).__setstate__( state )

        # Setup event handlers for dynamic bindings
        for k, d in self._dynamic_bindings.items():
            # Each dict shows up twice: once under its dictionary name and once
            # under its value. Only act once per dict (by assuming that the
            # values aren't subtypes of 'basestring'...)
            if isinstance( k, basestring ):
                d[ 'value' ].on_trait_change( self._dynamic_binding_handler,
                                              d[ 'trait_name' ] )
               
        # We maintain various things like context items and event listeners
        # that don't survive a pickling. These get setup in response to the
        # dictionary changing, so let's reuse that mechanism to set them up
        # again -- 'init' clears some caches and calls '_context_data_changed'.
        self._no_events = True
        try:
            self.init()
        finally:
            self._no_events = False

    #-- 'ANumericContext' Class Method Overrides -------------------------------

    #---------------------------------------------------------------------------
    #  Post events:
    #---------------------------------------------------------------------------

    def post_dict_modified ( self, event ):
        if not self._no_events:
            super( NumericContext, self ).post_dict_modified( event )

    def post_context_modified ( self, event ):
        if not self._no_events:
            super( NumericContext, self ).post_context_modified( event )

    #---------------------------------------------------------------------------
    #  Returns the value of a specified item:
    #---------------------------------------------------------------------------

    def get_context_data ( self, name ):
        """ Returns the value of a specified item.
        """
        return self.__getitem__( name )

    #---------------------------------------------------------------------------
    #  Gets the value of a currently undefined item:
    #---------------------------------------------------------------------------

    def get_context_undefined ( self, name, value ):
        """ Gets the value of a currently undefined item.
        """
        # If there is no current group:
        current_group = self._current_context_group()
        default_value = self.context_delegate.default_value_for( name, value )
        if (current_group is empty_group) or (default_value is Undefined):
            # Simply store the value to define it:
            self.__setitem__( name, value )

            # Indicate the value could not be expanded into an array:
            return Undefined

        # Otherwise, create a new array with the shape of the current group
        # and fill it with the correct default value for the specified name
        # and value:
        if   isinstance( value, ndarray ): dtype = value.dtype
        elif isinstance( value, float ):   dtype = float
        elif isinstance( value, int ):     dtype = int
        elif isinstance( value, bool ):    dtype = bool
        elif isinstance( value, complex ): dtype = complex
        else: dtype = object
        new_value = empty( shape = current_group[0], dtype = dtype )
        new_value.fill( self.context_delegate.default_value_for( name, value ) )
        return new_value

    #---------------------------------------------------------------------------
    #  Sets the value of a specified item:
    #---------------------------------------------------------------------------

    def set_context_data ( self, name, value ):
        """ Sets the value of a specified item.
        """
        return self.__setitem__( name, value )

    #---------------------------------------------------------------------------
    #  Sets the value of a currently undefined item:
    #---------------------------------------------------------------------------

    def set_context_undefined ( self, name, value ):
        """ Sets the value of a currently undefined item.
        """
        self.__setitem__( name, value )

    #---------------------------------------------------------------------------
    #  Returns the substitution 'value' associated with a particular trait:
    #---------------------------------------------------------------------------

    def context_value_for ( self, name ):
        """ Returns the substitution 'value' associated with a particular trait.
        """
        return self._context_items[ name ].value

    #---------------------------------------------------------------------------
    #  Gets/Sets the contents of a specified context group:
    #
    #  Must be overridden in subclasses.
    #---------------------------------------------------------------------------

    def context_group_for ( self, name = None, names = None ):
        """ Gets/Sets the contents of a specified context group.
        """
        # If an array was specified as the group name, use its shape as the
        # name:
        if name is None:
            name = self.context_group
        elif self.is_valid_array( name ):
            name = name.shape

        # If this is just a query:
        if names is None:
            # Return the list of items in the specified group:
            return self._context_groups.get( name, empty_group )[1][:]

        # Only allow changing groups whose name is a string (not a shape):
        if not isinstance( name, basestring ):
            raise NumericContextError( "Can only modify a group with a string "
                      "name, but '%s' was specified." % ( name, ) )

        # Delete the old contents of the group (if any):
        old_group = self._context_groups.get( name, empty_group )
        for cur_name in old_group[1]:
            self._context_items[ cur_name ].groups.remove( name )

        if len( names ) == 0:
            # If empty list of names, delete the group (if any):
            self._context_groups.pop( name, None )

            # If the current group was just deleted, reset it:
            if name == self.context_group:
                self.context_group = None
        else:
            # Otherwise, verify all items have the same shape:
            shape = None
            for cur_name in names:
                if shape is None:
                    shape = self[ cur_name ].shape
                elif shape != self[ cur_name ].shape:
                    raise NumericContextError( 'All items in a group must have '
                                               'the same shape.' )

            # Define the group:
            self._context_groups[ name ] = ( shape, names[:] )

            # Add the group name to the list of groups each item is in:
            for cur_name in names:
                self._context_items[ cur_name ].groups.append( name )

            # If the current group was just modified, reset the context:
            if name == self.context_group:
                self.post_context_modified( ContextModified( reset = True ) )

    #---------------------------------------------------------------------------
    #  Returns whether a context contains a specified context in its pipeline:
    #---------------------------------------------------------------------------

    def contains_context ( self, context ):
        """ Returns whether a context contains a specified context in its
            pipeline.
        """
        return (self is context)

    #---------------------------------------------------------------------------
    #  Dynamic bindings
    #---------------------------------------------------------------------------
    # TODO Clean up?

    def bind_dynamic ( self, value, trait_name ):
        """ Create a dynamic binding to the trait named 'trait_name' on 'value'.

            Dynamic bindings maintain the invariant

                self[ getattr( value, trait_name ) ] == value

            when either 'getattr( value, trait_name )' is changed or when
            'value' is renamed within 'self.context_data'. An odd consequence
            of this is that a dynamically bound value can't be stored under
            multiple names simultaneously.

            Assumes the 'value' and 'getattr( value, trait_name )' domains are
            disjoint and hashable. (A convenient and probably acceptable
            restriction.)

            See the unit tests for more details.

            NOTE: A context with dynamic bindings is (arguably) no longer a
            dictionary because it might violate substitutability. Consider:

                d['a'] = x
                d['b'] = x
                assert 'a' in d and 'b' in d

            Although we have no set of "mapping object axioms" specifying
            minimal behavior, I think most users would expect the above assert
            to always hold for mapping objects, but it can fail if 'd' is a
            numeric context with a dynamic binding for 'x'.
        """
        name = getattr( value, trait_name )
        assert value not in self._dynamic_bindings
        assert name not in self._dynamic_bindings

        value.on_trait_change( self._dynamic_binding_handler, trait_name )

        for k,v in self.items():
            if v is value and k != name:
                del self[ k ]
        self[ name ] = value
        self._dynamic_bindings[ name ] = self._dynamic_bindings[ value ] = \
            dict( name = name, value = value, trait_name = trait_name )

    def _dynamic_binding_handler ( self, value, trait_name, old_name,
                                   new_name ):

        if new_name not in self:
            self[ new_name ] = value
        else:
            # Remove dynamically bound objects that try to overwrite existing
            # items in 'context_data'.
            logger.warn( '\n'.join( [
                'Dynamic binding tried to overwrite existing mapping in'
                    'dictionary; dropping dynamic binding.',
                '  %r trait on %r changed from %r to %r' %
                    ( trait_name, value, old_name, new_name ),
                '  Existing mapping: %r:%r' % ( new_name, self[ new_name ] ),
            ] ) )
            del self[ old_name ]

        # Alternatively, we could use VetoableEvents to prevent a trait from
        # causing this problem in the first place. Since traits aren't
        # vetoable, 'bind_dynamic' could take an optional vetoable event
        # argument in addition to a trait, and then we could listen for
        # vetoable events instead of irrefutable trait change notifications.

    def _rebind_dynamic ( self, value, new_name ):
        """ Rename a dynamic binding created by 'bind_dynamic'.
        """
        d = self._dynamic_bindings[ value ]
        old_name = d['name']
        if new_name != old_name:

            self._unbind_dynamic( value, d['trait_name'] )

            # (bind_dynamic updates 'context_data')
            if getattr( value, d['trait_name'] ) != new_name:
                setattr( value, d['trait_name'], new_name )

            self.bind_dynamic( value, d['trait_name'] )

    def _unbind_dynamic ( self, value, trait_name, remove=True ):
        """ Remove a dynamic binding created by 'bind_dynamic'.
        """
        d = self._dynamic_bindings[ value ]
        del self._dynamic_bindings[ value ]
        del self._dynamic_bindings[ d['name'] ]
        value.on_trait_change( self._dynamic_binding_handler, trait_name,
                               remove=True )
        if remove:
            assert self.pop( d['name'] ) == value

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_names' property:
    #---------------------------------------------------------------------------

    def _get_context_names ( self ):
        # note: We return the actual list, rather than a copy, since we assume
        # the requester will not modify the list. If this proves not to be the
        # case, add a '[:]' to the end of the next line:
        return self._current_context_group()[1]

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_all_names' property:
    #---------------------------------------------------------------------------

    def _get_context_all_names ( self ):
        return self._context_items.keys()

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_group' property:
    #---------------------------------------------------------------------------

    def _get_context_group ( self ):
        if self._context_group is None:
            longest_group = -1
            group         = None
            for cur_group, group_info in self._context_groups.items():
                if group_info[0][0] > longest_group:
                    longest_group = group_info[0][0]
                    group         = cur_group

            self._context_group = group

        return self._context_group

    def _set_context_group ( self, group ):
        if self.is_valid_array( group ):
            group = group.shape

        if (group is not None) and (group not in self._context_groups):
            raise TraitError, "There is no group for '%s'" % group

        old = self._context_group
        if group != old:
            self._context_group = group
            self.post_context_modified( ContextModified( reset = True ) )
            self.trait_property_changed( 'context_group', old, group )

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_groups' property:
    #---------------------------------------------------------------------------

    def _get_context_groups ( self ):
        return self._context_groups.keys()

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_indices' property:
    #---------------------------------------------------------------------------

    def _get_context_indices ( self ):
        if len( self.context_items ) > 0:
            return arange( self._current_context_group()[0][0] )

        return array( [] )

    #---------------------------------------------------------------------------
    #  Implementation of the 'sub_context_names' property:
    #---------------------------------------------------------------------------

    def _get_sub_context_names ( self ):
        return concat( self._sub_contexts.values() )

    #---------------------------------------------------------------------------
    #  Implementation of the 'defer_events' property:
    #---------------------------------------------------------------------------

    def _get_defer_events ( self ):
        return self.context_data.defer_events

    def _set_defer_events ( self, x ):
        self.context_data.defer_events = x

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Returns the default value for the 'context_delegate' trait:
    #---------------------------------------------------------------------------

    def _context_delegate_default ( self ):
        """ Returns the default value for the 'context_delegate' trait.
        """
        return default_context_delegate

    #---------------------------------------------------------------------------
    #  Handle the 'context_data' trait being changed:
    #---------------------------------------------------------------------------

    def _dict_is_modified( self, event ):
        """ Fires when 'context_data' fires 'dict_modified'.
        """
        assert disjoint( event.added, event.changed, event.removed )

        # How much can we optimize this while keeping it maintainable?

        # If the dictionary has changed, then we are dirty. (I think this is
        # the only place we have to do this...)
        self.dirty = True

        # These become attributes on a ContextModified event we create below.
        # Leave them as normal sets until the end to avoid excessive trait
        # validation.
        added    = set()
        modified = set()
        removed  = set()
        changed  = set()

        # The following three loops duplicate code: the body of 'changed' is
        # simply the body of 'removed' followed by the body of 'added',
        # followed by some logic for group maintenance. It would be better to
        # abstract out the two shared chunks, but I keep waiting for a higher
        # level insight that will greatly simplify this logic and eliminate the
        # need to repeat code in the first place.

        for name, new in event.added.iteritems():

            # Rebind renamed dynamic bindings
            if hashable( new ) and new in self._dynamic_bindings:
                self._rebind_dynamic( new, name )

            # Add new data
            if self.is_valid_array( new ):
                added.update(
                    self._add_context_items( ContextItem( name = name ) )
                )
            elif isinstance( new, ANumericContext ):
                added.update( self._add_sub_context( name, new ) )
                changed.add( name )
            else:
                changed.add( name )

        for name, old in event.changed.iteritems():
            new = self.context_data[ name ]

            # Short-circuit if possible
            if new is old:
                continue

            # Unbind dynamic bindings
            if hashable( old ) and old in self._dynamic_bindings:
                d = self._dynamic_bindings[ old ]
                self._unbind_dynamic( old, d['trait_name'], remove=False )

            # Remove old data
            if name in self._context_items:
                removed.update(
                    self._remove_context_items( self._context_items[ name ],
                                                delete = False )
                )
            elif isinstance( old, ANumericContext ):
                removed.update( self._remove_sub_context( name, old ) )
                changed.add( name )
            else:
                changed.add( name )

            # Rebind dynamic bindings
            if hashable( new ) and new in self._dynamic_bindings:
                self._rebind_dynamic( new, name )

            # Add new data
            if self.is_valid_array( new ):
                added.update(
                    self._add_context_items( ContextItem( name = name ) )
                )
            elif isinstance( new, ANumericContext ):
                added.update( self._add_sub_context( name, new ) )
                changed.add( name )
            else:
                changed.add( name )

            # Update an item's group if it changes shape
            if ( self.is_valid_array( new ) and self.is_valid_array( old ) and
                    new.shape != old.shape ):

                context_groups = self._context_groups
                item           = self._context_items[ name ]

                for group in item.groups:
                    n, names = context_groups[ group ]
                    names.remove( name )
                    if len( names ) == 0:
                        del context_groups[ group ]

                group       = new.shape
                item.groups = [ group ]
                context_groups.setdefault(
                    group, ( group, [] ) )[1].append( name )

        for name, old in event.removed.iteritems():

            # Unbind dynamic bindings
            if hashable( old ) and old in self._dynamic_bindings:
                d = self._dynamic_bindings[ old ]
                self._unbind_dynamic( old, d['trait_name'], remove=False )

            # Remove old data
            if name in self._context_items:
                removed.update(
                    self._remove_context_items( self._context_items[ name ],
                                                delete = False )
                )
            elif isinstance( old, ANumericContext ):
                removed.update( self._remove_sub_context( name, old ) )
                changed.add( name )
            else:
                changed.add( name )

        # Calculate context event
        modified |= added & removed
        added    -= modified
        removed  -= modified
        cm = ContextModified(
            added    = list( added ),
            modified = list( modified ),
            removed  = list( removed ),
            changed  = list( changed ),
        )

        # Fire events
        self.post_dict_modified( event )
        self.post_context_modified( cm )

    def _context_data_changed ( self, old, new ):
        """ Fires when 'context_data' is changed.
        """

        if old is None:
            old = {}
        else:
            old.on_trait_event( self._dict_is_modified, 'dict_modified',
                                remove = True )

        new.on_trait_event( self._dict_is_modified, 'dict_modified' )

        old_keys = set( old )
        new_keys = set( new )
        added   = sub_dict( new, new_keys - old_keys )
        removed = sub_dict( old, old_keys - new_keys )
        changed = sub_dict( old, new_keys & old_keys )

        self._dict_is_modified(
            TraitDictEvent( added=added, changed=changed, removed=removed )
        )

    #---------------------------------------------------------------------------
    #  Handles the 'context_items' trait being changed:
    #---------------------------------------------------------------------------

    def _context_items_changed ( self, old, new ):
        """ Handles the 'items' trait being changed.
        """
        self.post_context_modified( ContextModified(
            removed = self._remove_context_items( *old ),
            added   = self._add_context_items( *new ),
        ) )

    def _context_items_items_changed ( self, event ):
        if not self._no_update:
            self.post_context_modified( ContextModified(
                removed = self._remove_context_items( *event.removed ),
                added   = self._add_context_items( *event.added ),
            ) )

    #---------------------------------------------------------------------------
    #  Handles a sub-context being modified:
    #---------------------------------------------------------------------------

    def _sub_context_modified ( self, sub_context, name, old, event ):
        """ Handles a sub-context being modified.
        """
        ci = self._context_items

        # Create the context modified event wewill use for all changes:
        cm = ContextModified()

        # Iterate over each name the sub-context has been bound to in our
        # context:
        for name in self._sub_contexts[ sub_context ]:
            # Compute the common prefix for all sub-context items under the
            # current name:
            prefix = name + '.'

            # Create the list of modified name within our context:
            modified = [ (prefix + n) for n in event.modified ]

            # If the sub-context was reset, add all of the items in the
            # sub-context's current group to the modified list (avoiding dups):
            if event.reset:
                for n in sub_context.context_names:
                    n2 = prefix + n
                    if n2 not in modified:
                        modified.append( n2 )

            # Add all modified items to the event:
            cm.modified.extend( modified )

            # Add and remove all of the added and removed sub-context items
            # to our context and the event using the 'extended' name for our
            # context:
            cm.removed.extend( self._remove_context_items( *[
                ci[ prefix + n ] for n in event.removed
            ] ) )
            cm.added.extend( self._add_context_items( *[
                SubContextItem( context          = self,
                                sub_context_name = name,
                                sub_name         = n ) for n in event.added
            ] ) )

        # Finally, post the event:
        self.post_context_modified( cm )

    #-- Mapping Object Interface -----------------------------------------------

    # A thin layer around 'context_data'. Try to consolidate most of our
    # mapping object logic in '_dict_is_modified'.

    def __getitem__ ( self, name ):

        # Intercept context items that are valid dictionary entries (e.g.
        # SubContextItems have names that aren't in our dictionary)
        if name in self._context_items and name in self:
            return self._context_items[ name ].data

        # Try to delegate to 'context_data', handling magic name '__context__'
        else:
            try:
                return self.context_data[ name ]
            except KeyError:
                if name == '__context__':
                    return self
                else:
                    raise

    def __setitem__ ( self, name, value ):

        # Intercept context items that are valid dictionary entries (e.g.
        # SubContextItems have names that aren't in our dictionary)
        if name in self._context_items and name in self:
            self._context_items[ name ].data = value

        # Prohibit magic name '__context__'
        elif name == '__context__':
            raise ValueError( "Can't set magic name '__context__'" )

        # Delegate to 'context_data'
        else:
            self.context_data[ name ] = value

    def __delitem__ ( self, name ):

        # Try to delegate to 'context_data', handling magic name '__context__'
        try:
            del self.context_data[ name ]
        except KeyError:
            if name == '__context__':
                raise ValueError( "Can't delete magic name '__context__'" )
            else:
                raise

    def keys ( self ):
        return self.context_data.keys()

    # Optimization: Pass-through directly to 'context_data'
    def __contains__ ( self, *a, **kw ):
        return self.context_data.__contains__( *a, **kw )
    def __iter__ ( self, *a, **kw ):
        return self.context_data.__iter__( *a, **kw )
    def iteritems ( self, *a, **kw ):
        return self.context_data.iteritems( *a, **kw )

    #-- Private Methods --------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Returns the contents of the current context group, which is a tuple of
    #  form: ( shape, [ name1, name2, ..., namen ] ), where 'shape' is the
    #  shape of all items in the group, and 'namei' is the name of an item in
    #  the group:
    #---------------------------------------------------------------------------

    def _current_context_group ( self ):
        """ Returns the contents of the current context group.
        """
        return self._context_groups.get( self.context_group, empty_group )

    #---------------------------------------------------------------------------
    #  Removes a list of context items:
    #---------------------------------------------------------------------------

    def _remove_context_items ( self, *items, **kw ):
        """ Removes a list of context items.
        """
        # Default parameters
        delete = kw.get( 'delete', True )

        self._no_update = True
        try:
            context_items_list = self.context_items
            context_items      = self._context_items
            context_groups     = self._context_groups
            context_data       = self.context_data

            removed = []
            for item in items:
                name = item.name
                removed.append( name )
                for group in item.groups:
                    n, names = context_groups[ group ]
                    names.remove( name )
                    if len( names ) == 0:
                        del context_groups[ group ]

                item.context = None
                item.groups  = []

                del context_items[ name ]

                # Non-sub-context items are in our dictionary
                if not isinstance(item, SubContextItem) and delete:
                    del context_data[ name ]

                if item in context_items_list:
                    context_items_list.remove( item )

            return removed
        finally:
            self._no_update = False

    #---------------------------------------------------------------------------
    #  Adds a list of context items:
    #---------------------------------------------------------------------------

    def _add_context_items ( self, *items ):
        """ Adds a list of context items.
        """
        self._no_update = True
        try:
            context_items_list = self.context_items
            context_items      = self._context_items
            context_groups     = self._context_groups
            context_data       = self.context_data

            added = []
                
            for item in items:
                if item not in context_items_list:
                    context_items_list.append( item )

                item.context = self
                name         = item.name
                context_items[ name ] = item
                added.append( name )

                # Keep non-sub-context items in our dictionary
                if not isinstance(item, SubContextItem):
                    context_data.setdefault( name, Undefined )

                group = item.data.shape
                item.groups.append( group )
                context_groups.setdefault( group,
                                           ( group, [] ) )[1].append( name )

            return added
        finally:
            self._no_update = False

    #---------------------------------------------------------------------------
    #  Removes an existing sub-context from the context:
    #---------------------------------------------------------------------------

    def _remove_sub_context ( self, name, sub_context ):
        """ Removes an existing sub-context from the context.
        """
        # Remove the sub-context from the current set of sub-contexts:
        names = self._sub_contexts.get( sub_context )
        if names is not None:
            names.remove( name )
            if len( names ) == 0:
                del self._sub_contexts[ sub_context ]

            # Remove the event listener:
            sub_context.on_trait_change( self._sub_context_modified,
                                         'context_modified', remove = True )

            # Remove all the sub-context items and update the context modified
            # event:
            cig    = self._context_items.get
            prefix = name + '.'
            return self._remove_context_items( *[
                cig( prefix + name )
                for name in sub_context.context_all_names
            ] )

        else:
            return []

    #---------------------------------------------------------------------------
    #  Adds a new sub-context to the context:
    #---------------------------------------------------------------------------

    def _add_sub_context ( self, name, sub_context ):
        """ Adds a new sub-context to the context.
        """
        if not sub_context.contains_context( self ):
            # Add the event listener:
            sub_context.on_trait_change( self._sub_context_modified,
                                         'context_modified' )

            # Add the sub-context to the current set of sub-contexts:
            self._sub_contexts.setdefault( sub_context, [] ).append( name )

            # Add the sub-context items and update the context modified event:
            return self._add_context_items( *[
                SubContextItem( context          = self,
                                sub_context_name = name,
                                sub_name         = sub_name )
                for sub_name in sub_context.context_all_names
            ] )
        else:
            return []


    #---------------------------------------------------------------------------
    #  Add more dynamic bindings in state dictionary
    #---------------------------------------------------------------------------

    def _add_dynamic_bindings_to_state_dict(self, state, value, trait_name):
        """ Add dynamic bindings to state dictionary

            Parameters:
            -----------
            state: Dict
            value: Any
            trait_name: Str

        """

        if not state.has_key('__numeric_context_saved_bindings__'):
            state['__numeric_context_saved_bindings__'] = {}
        saved_bindings = state['__numeric_context_saved_bindings__']

        # Get name of the value to be used for dynamic binding
        name = getattr(value, trait_name)

        # Build dynamic_bindings and add them to saved_bindings
        if not value in saved_bindings and not name in saved_bindings:
            dict_value = dict(name = name, value=value, trait_name= trait_name)

            saved_bindings[name] = dict_value
            saved_bindings[value] = dict_value

        return


    def _add_all_items_as_dynamic_bindings_to_state(self, state, context_items):
        """ Add all NumericContext-keys as dynamic bindings to state
            dictionary

            Parameters:
            -----------
            state: Dict
            context_items: Dict
                context_items of the NumericContext

        """

        for k,v in context_items.items():
            if isinstance(v, NumericContext):
                v.context_name = k
                self._add_dynamic_bindings_to_state_dict(state,v,'context_name')

        return


# fixme: What to do about 'magically_bound_names'...
# Tell the world that we magically provide the name '__context__'
#magically_bound_names.add('__context__')

#-------------------------------------------------------------------------------
#  Utilities:
#-------------------------------------------------------------------------------

# TODO Where should this live?
def hashable ( x ):
    try:
        hash(x)
        return True
    except TypeError:
        return False
