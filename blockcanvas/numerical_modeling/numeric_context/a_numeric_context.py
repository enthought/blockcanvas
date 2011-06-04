#-------------------------------------------------------------------------------
#
#  Defines the abstract base class for all numeric context subclasses.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the abstract base class for all numeric context subclasses.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import copy

from numpy import ndarray

from blockcanvas.numerical_modeling.numeric_context.event \
    import single_event

from traits.api \
    import HasPrivateTraits, Constant, Event, TraitDictEvent, Undefined, \
           Property, Bool

from constants \
    import QueryContext, CreateContext

from context_modified \
    import ContextModified

from event \
    import merge_context_modified_events, merge_trait_dict_events

from numeric_reference \
    import NumericReference

from UserDict \
    import DictMixin

#-------------------------------------------------------------------------------
#  Utilities:
#-------------------------------------------------------------------------------

# XXX Just use 'event.single_event' once 'ANumericContext.defer_events' works
#def single_event(f):
#    def g(self, *args, **kw):
#        if hasattr(self, 'context_data'): # (Coupling!)
#            x = self.context_data
#        else:
#            x = self.context_base
#        old = x.defer_events
#        x.defer_events = True
#        try:
#            return f(self, *args, **kw)
#        finally:
#            x.defer_events = old
#    return g

#-------------------------------------------------------------------------------
#  Define a trait to handle setting undefined context attributes:
#-------------------------------------------------------------------------------

def get_undef ( object, name ):
    return object.__getitem__( name )

def set_undef ( object, name, value ):
    object.__setitem__( name, value )

Undefed = Property( get_undef, set_undef )

#-------------------------------------------------------------------------------
#  'ANumericContext' class:
#-------------------------------------------------------------------------------

class ANumericContext ( HasPrivateTraits, DictMixin ):
    """ Defines the abstract base class for all numeric context subclasses.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Define the rule for how to handle undefined traits:
    _ = Undefed

    # Current selection mask (none for the base context):
    context_selection = Constant( None )

    # Fired when any change occurs to the contents of the context. The value is
    # a ContextModified object, which describes all the changes that have
    # occurred:
    context_modified = Event( ContextModified ) # cf. post_context_modified(ev)

    # Fired when any change occurs to the structure of the context's dictionary
    # (or its base context's dictionary, if it doesn't have its own). Unlike
    # 'context_modified', 'dict_modified' only fires when the dictionary itself
    # changes, and not when objects in the dictionary change.
    dict_modified = Event( TraitDictEvent )

    # Whether the context is "dirty" -- just a placeholder until HasDirty is
    # factored out of encode.
    dirty = Bool

    # The name of the context:
    #context_name = Str

    # List of array descriptor items (implemented in subclasses):
    #context_items = List( ANumericItem )

    # List of available data item names in the current group (implemented in
    # subclasses):
    #context_names = List( Str )

    # List of available data item names in the entire context (implemented in
    # subclasses):
    #context_all_names = List( Str )

    # The 'name' of the current context group (may be a tuple representing
    # the shape of the group's contents (implemented in subclasses):
    #context_group = Any

    # The array indices (implemented in subclasses):
    #context_indices = Array

    # The ContextDelegate the context uses to handle various policy decisions:
    #context_delegate = Instance( ContextDelegate )

    # The list of all sub_context names:
    #sub_context_names = List( Str )

    # Whether to buffer 'dict_modified' and 'context_modified' events. When
    # true, no events are fired, and when reverted to false, one pair of event
    # fires that represents the net change since 'defer_events' was set.
    #defer_events = Bool

    #########################################################################
    # 'UserDict' interface
    #########################################################################

    #### operator methods ###################################################

    def __cmp__(self, other):
        if other is None:
            return 1

        result = super(ANumericContext, self).__cmp__(other)
        # FIXME: If we want comparison based on contents being equal, then
        # use the line below instead of the uncommented line underneath it.
        #if result == 0 and len(self) == 0:
        if result == 0:
            result = cmp(id(self), id(other))

        return result


    #---------------------------------------------------------------------------
    #  Post events:
    #---------------------------------------------------------------------------

    def post_dict_modified ( self, event ):
        """ Post a 'dict_modified' event.

            Calling this method instead of directly assigning to
            'dict_modified' enables us to defer events.
        """
        if event.added != {} or event.changed != {} or event.removed != {}:
            if not self.defer_events:

                # Race condition: When 'defer_events' resets to False, we might
                # be just one of many handlers that trigger. If one of the
                # others fires before us and posts a 'dict_modified' event,
                # then we will still have a '_deferred_dict_modified' that
                # precedes it. The incoming event should be merged into our
                # deferred event -- e.g. a chain of deferred events let lose in
                # a pipeline should merge into a single event that emerges from
                # the end of the pipe.

                if self._deferred_dict_modified is not None:
                    merge_trait_dict_events( self._deferred_dict_modified,
                                             event,
                                             self )
                    event = self._deferred_dict_modified
                    self._deferred_dict_modified = None

                self.dict_modified = event
            else:
                merge_trait_dict_events( self._deferred_dict_modified, event )

    def post_context_modified ( self, event ):
        """ Post a 'context_modified' event.

            Calling this method instead of directly assigning to
            'context_modified' enables us to defer events.
        """
        if event.not_empty:
            if not self.defer_events:

                # Race condition -- see explanation in 'post_dict_modified',
                # above.
                if self._deferred_context_modified is not None:
                    merge_context_modified_events(
                        self._deferred_context_modified, event )
                    event = self._deferred_context_modified
                    self._deferred_context_modified = None

                self.context_modified = event
            else:
                merge_context_modified_events( self._deferred_context_modified,
                                               event )

    # FIXME Too many _deferred_foo events ?
    # In DC(NC()), each of DC and NC have their own '_deferred_foo' buffers.
    # This is wrong. They also have their own 'foo_modified' events. This is
    # right. What's the solution?

    def _defer_events_changed ( self ):

        # 'defer_events' is a Property, so we don't get an 'old' for free
        assert ( (self._deferred_dict_modified is None) ==
                 (self._deferred_context_modified is None) )
        old = self._deferred_dict_modified is not None
        new = self.defer_events

        # If 'defer_events' changed, make the transition
        if old != new:
            if self.defer_events:
                self._deferred_dict_modified    = TraitDictEvent()
                self._deferred_context_modified = ContextModified()
            else:
                dm = self._deferred_dict_modified
                cm = self._deferred_context_modified
                self._deferred_dict_modified = None
                self._deferred_context_modified = None
                self.post_dict_modified( dm )
                self.post_context_modified( cm )

    #---------------------------------------------------------------------------
    #  Gets a ReductionContext associated with the context:
    #---------------------------------------------------------------------------

    def get_reduction_context ( self, mode = CreateContext ):
        """ Gets a ReductionContext associated with the context.
        """
        from reduction_context import ReductionContext

        if mode == QueryContext:
            return None

        return ReductionContext( context = self )

    #---------------------------------------------------------------------------
    #  Gets a MappingContext associated with the context:
    #---------------------------------------------------------------------------

    def get_mapping_context ( self, mode = CreateContext ):
        """ Gets a MappingContext associated with the context.
        """
        from mapping_context import MappingContext

        if mode == QueryContext:
            return None

        return MappingContext( context = self )

    #---------------------------------------------------------------------------
    #  Gets a SelectionContext associated with the context:
    #---------------------------------------------------------------------------

    def get_selection_context ( self, mode = CreateContext ):
        """ Gets a SelectionContext associated with the context.
        """
        from selection_context import SelectionContext

        if mode == QueryContext:
            return None

        return SelectionContext( context = self )

    #---------------------------------------------------------------------------
    #  Removes a specified context from a context chain:
    #---------------------------------------------------------------------------

    def remove_context ( self, context ):
        """ Removes a specified context from a context chain.
        """
        pass

    #---------------------------------------------------------------------------
    #  Prints the context structure:
    #---------------------------------------------------------------------------

    def dump_context ( self, indent = 0 ):
        print '%s%s( %08X )' % (
              ' ' * indent, self.__class__.__name__, id( self ) )

    #---------------------------------------------------------------------------
    #  Returns a NumericReference for a specified context item:
    #---------------------------------------------------------------------------

    def get_context_reference ( self, name ):
        return NumericReference( context = self, name = name )

    #---------------------------------------------------------------------------
    #  Returns the context base any upstream contexts should use:
    #---------------------------------------------------------------------------

    def get_context_base ( self ):
        """ Returns the context base any upstream contexts should use.
        """
        return self

    def is_valid_array ( self, value ):
        """ Returns whether a value is of interest to the pipeline.

            The pipeline only operates on numeric arrays with non-zero
            dimension. Different kinds of data simply bypass it.
        """
        return isinstance( value, ndarray ) and value.shape != ()

    #---------------------------------------------------------------------------
    #  Returns the value of a specified item:
    #
    #  Must be overridden in subclasses.
    #---------------------------------------------------------------------------

    def get_context_data ( self, name ):
        """ Returns the value of a specified item.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Gets the value of a currently undefined item:
    #
    #  Must be overridden in subclasses.
    #---------------------------------------------------------------------------

    def get_context_undefined ( self, name, value ):
        """ Sets the value of a currently undefined item.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Sets the value of a specified item:
    #
    #  Must be overridden in subclasses.
    #---------------------------------------------------------------------------

    def set_context_data ( self, name, value ):
        """ Sets the value of a specified item.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Sets the value of a currently undefined item:
    #
    #  Must be overridden in subclasses.
    #---------------------------------------------------------------------------

    def set_context_undefined ( self, name, value ):
        """ Sets the value of a currently undefined item.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Gets/Sets the contents of a specified context group:
    #
    #  Must be overridden in subclasses.
    #---------------------------------------------------------------------------

    def context_group_for ( self, name, names = None ):
        """ Gets/Sets the contents of a specified context group.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Returns whether a context contains a specified context in its pipeline:
    #---------------------------------------------------------------------------

    def contains_context ( self, context ):
        """ Returns whether a context contains a specified context in its
            pipeline.
        """
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Dynamic bindings
    #---------------------------------------------------------------------------

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
        raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Mapping Object Interface:
    #
    #  Subclasses must override
    #    __getitem__
    #    __setitem__
    #    __delitem__
    #    keys
    #  and may want to override other methods like '__contains__', '__iter__',
    #  and 'iteritems' for efficiency.
    #    [http://www.python.org/doc/lib/module-UserDict.html]
    #---------------------------------------------------------------------------

    # "minimum" dict interface -- DictMixin has default behaviors for the rest
    def __getitem__ ( self, name ):        raise NotImplementedError
    def __setitem__ ( self, name, value ): raise NotImplementedError
    def __delitem__ ( self, name ):        raise NotImplementedError
    def keys ( self ):                     raise NotImplementedError

    # Prefer 'DictMixin.get' to 'HasTraits.get'
    get = DictMixin.get

    # Don't generate multiple events
    update = single_event( DictMixin.update )
    clear  = single_event( DictMixin.clear )

    # Construction methods -- DictMixin can't provide these:

    def copy ( self ):
        return copy.copy( self ) # (Uses pickle)

    # Implementing 'fromkeys' doesn't make sense in general since
    # DerivativeContexts don't know what kind of pipeline to build behind them.
    #@classmethod
    #def fromkeys ( cls, keys, value=None): raise NotImplementedError

    #---------------------------------------------------------------------------
    #  Accesses dotted names via the dictionary interface:
    #---------------------------------------------------------------------------

    def get_dotted ( self, name ):
        ''' Get a dotted name that may exist only in a sub-context.

            If there are multiple sub-contexts whose names are dot-prefixes of
            'name' (e.g. "foo.bar" dot-prefixes "foo.bar.baz"), then the
            longest valid match wins. If none matches, a KeyError is raised.
        '''
        if name not in self and '.' in name:
            for x, rest in self._find_dotted( name ):
                try:
                    return x.get_dotted( rest )
                except KeyError:
                    pass
            else:
                raise KeyError( name )
        else:
            return self[ name ]

    def set_dotted ( self, name, value ):
        ''' Set a dotted name that may end up in a sub-context.

            If there are multiple sub-contexts whose names are dot-prefixes of
            'name' (e.g. "foo.bar" dot-prefixes "foo.bar.baz"), then the
            longest match wins. If no dot-prefix of 'name' is a sub-context,
            set name=value in this context.
        '''
        if name not in self and '.' in name:
            try:
                x, rest = iter( self._find_dotted( name ) ).next()
                return x.set_dotted( rest, value )
            except KeyError:
                self[ name ] = value
        else:
            self[ name ] = value

    def has_dotted ( self, name ):
        "Whether 'get_dotted' would succeed."
        try:
            self.get_dotted( name )
            return True
        except KeyError:
            return False

    def _find_dotted ( self, name ):
        # Longest match first
        for i,c in reversed( list( enumerate( name ) ) ):
            if c == '.':
                head, tail = name[:i], name[i+1:]
                if head in self and isinstance( self[ head ], ANumericContext ):
                    yield self[ head ], tail
        else:
            raise KeyError( name )
