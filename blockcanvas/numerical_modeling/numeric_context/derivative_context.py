#-------------------------------------------------------------------------------
#
#  Defines the abstract base class for all numeric contexts which connect
#  to another numeric context.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines the abstract base class for all numeric contexts which connect
    to another numeric context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Instance, Property, TraitDictEvent

from a_numeric_context \
    import ANumericContext

from constants \
    import CreateContext

from context_modified \
    import ContextModified

from error \
    import NumericContextError

#-------------------------------------------------------------------------------
#  'DerivativeContext' class:
#-------------------------------------------------------------------------------

class DerivativeContext ( ANumericContext ):
    """ Defines the abstract base class for all numeric contexts which connect
        to another numeric context.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Context being derived from:
    context = Instance( ANumericContext )

    # The name of the context:
    context_name = Property( transient = True )

    # List of array descriptor items:
    context_items = Property( transient = True )

    # List of available data item names in the current group:
    context_names = Property

    # List of available data item names in the entire context:
    context_all_names = Property

    # The 'name' of the current context group (may be a tuple representing
    # the shape of the group's contents:
    context_group = Property( transient = True )

    # The array indices:
    context_indices = Property

    # Base context reference:
    context_base = Property

    # The ContextDelegate the context uses to handle various policy decisions:
    context_delegate = Property

    # The list of all sub_context names:
    sub_context_names = Property

    # Whether to buffer 'dict_modified' and 'context_modified' events. When
    # true, no events are fired, and when reverted to false, one pair of event
    # fires that represents the net change since 'defer_events' was set.
    defer_events = Property( depends_on = 'context_base.defer_events' )

    #-- 'object' Class Method Overrides ----------------------------------------

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, context = None, **traits ):
        """ Initializes the object.
        """
        super( DerivativeContext, self ).__init__( **traits )
        if context is not None:
            self.context = context

    def __setstate__ ( self, state ):
        state.pop( '__traits_version__', None )
        self.set( **state )


    #-- 'DerivativeContext' Class Methods --------------------------------------

    #---------------------------------------------------------------------------
    #  Inserts a new context before this context:
    #---------------------------------------------------------------------------

    def insert_context ( self, context ):
        """ Inserts a new context before this context.
        """
        context.context, self.context = self.context, context

    #---------------------------------------------------------------------------
    #  Removes a specified context from a context chain:
    #---------------------------------------------------------------------------

    def remove_context ( self, context ):
        """ Removes a specified context from a context chain.
        """
        if context is not None:
            if context is self.context:
                self.context = context.context
            else:
                self.context.remove_context( context )

    #---------------------------------------------------------------------------
    #  Hooks a context into the pipeline (if necessary):
    #---------------------------------------------------------------------------

    def hook_context ( self, context ):
        """ Hooks a context into the pipeline (if necessary).
        """
        if (context is not None) and (context.context is self.context):
            self.context = context
        return context

    #---------------------------------------------------------------------------
    #  Creates a new context of the specified type (if necessary):
    #---------------------------------------------------------------------------

    def create_context ( self, mode ):
        """ Creates a new context of the specified type (if necessary).
        """
        if mode != CreateContext:
            return self

        return self.__class__( context = self )

    #-- 'ANumericContext' Class Method Overrides -------------------------------

    #---------------------------------------------------------------------------
    #  Prints the context structure:
    #---------------------------------------------------------------------------

    def dump_context ( self, indent = 0 ):
        print '%s%s( %08X )' % (
              ' ' * indent, self.__class__.__name__, id( self ) )
        self.context.dump( indent + 3 )

    #---------------------------------------------------------------------------
    #  Gets/Sets the contents of a specified context group:
    #
    #  Must be overridden in subclasses.
    #---------------------------------------------------------------------------

    def context_group_for ( self, name, names = None ):
        """ Gets/Sets the contents of a specified context group.
        """
        return self.context_base.context_group_for( name, names )

    #---------------------------------------------------------------------------
    #  Returns whether a context contains a specified context in its pipeline:
    #---------------------------------------------------------------------------

    def contains_context ( self, context ):
        """ Returns whether a context contains a specified context in its
            pipeline.
        """
        return ((self is context) or self.context.contains_context( context ))

    #---------------------------------------------------------------------------
    #  Returns the value of a specified item:
    #---------------------------------------------------------------------------

    def get_context_data ( self, name ):
        """ Returns the value of a specified item.
        """
        return self.context.get_context_data( name )

    #---------------------------------------------------------------------------
    #  Gets the value of a currently undefined item:
    #---------------------------------------------------------------------------

    def get_context_undefined ( self, name, value ):
        """ Gets the value of a currently undefined item.
        """
        return self.context.get_context_undefined( name, value )

    #---------------------------------------------------------------------------
    #  Sets the value of a specified item:
    #---------------------------------------------------------------------------

    def set_context_data ( self, name, value ):
        """ Sets the value of a specified item.
        """
        self.context.set_context_data( name, value )

    #---------------------------------------------------------------------------
    #  Sets the value of a currently undefined item:
    #---------------------------------------------------------------------------

    def set_context_undefined ( self, name, value ):
        """ Sets the value of a currently undefined item.
        """
        self.context.set_context_undefined( name, value )

    #---------------------------------------------------------------------------
    #  Returns the context base any upstream contexts should use:
    #---------------------------------------------------------------------------

    def get_context_base ( self ):
        """ Returns the context base any upstream contexts should use.
        """
        return self.context_base

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
        return self.context.bind_dynamic( value, trait_name )

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_base' property:
    #---------------------------------------------------------------------------

    def _get_context_base ( self ):
        if (self._context_base is None) and (self.context is not None):
            self._context_base = self.context.get_context_base()

        return self._context_base

    #---------------------------------------------------------------------------
    #  Implementation of the properties based on 'context_base':
    #---------------------------------------------------------------------------

    def _get_context_name ( self ):
        return self.context_base.context_name

    def _set_context_name ( self, name ):
        self.context_base.context_name = name

    def _get_context_items ( self ):
        return self.context_base.context_items

    def _set_context_items ( self, items ):
        self.context_base.context_items = items

    def _get_context_names ( self ):
        return self.context_base.context_names

    def _get_context_all_names ( self ):
        return self.context_base.context_all_names

    def _get_context_group ( self ):
        return self.context_base.context_group

    def _set_context_group ( self, group ):
        self.context_base.context_group = group

    def _get_context_indices ( self ):
        return self.context_base.context_indices

    def _get_context_delegate ( self ):
        return self.context_base.context_delegate

    def _set_context_default_value ( self, delegate ):
        self.context_base.context_delegate = delegate

    def _get_sub_context_names ( self ):
        return self.context_base.sub_context_names

    #---------------------------------------------------------------------------
    #  Implementation of the 'defer_events' property:
    #---------------------------------------------------------------------------

    def _get_defer_events ( self ):
        #FIXME: Sometimes context_base is None:
        if self.context_base != None:
            return self.context_base.defer_events
        else:
            return False

    def _set_defer_events ( self, x ):
        if self.context_base != None:
            self.context_base.defer_events = x
        return

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the underlying context being changed:
    #---------------------------------------------------------------------------

    def _context_changed ( self, old, new ):
        """ Handles the underlying context being changed.
        """
        self._context_base = None

        cm = ContextModified( reset = True )
        dm = TraitDictEvent()

        if old is not None:
            cm.removed = [ item.name for item in old.context_items ]
            old.on_trait_change( self._context_is_modified, 'context_modified',
                                 remove = True )

            dm.removed = dict( old )
            old.on_trait_change( self._dict_is_modified, 'dict_modified',
                                 remove = True )

        if new is not None:
            cm.added = [ item.name for item in new.context_items ]
            new.on_trait_change( self._context_is_modified, 'context_modified' )

            dm.added = dict( new )
            new.on_trait_change( self._dict_is_modified, 'dict_modified' )

        self._context_is_modified( cm )
        self._dict_is_modified( dm )

    #---------------------------------------------------------------------------
    #  Handles the 'context_base' trait on the current 'context' being changed:
    #---------------------------------------------------------------------------

    def _context_base_changed_for_context ( self ):
        """ Handles the 'context_base' trait on the current 'context' being
            changed.
        """
        self._context_base = None

    #---------------------------------------------------------------------------
    #  Handles the 'context_name' trait on the current context being changed:
    #---------------------------------------------------------------------------

    def _context_name_changed_for_context ( self, other, trait, old, new ):
        self.trait_property_changed( 'context_name', old, new )

    #---------------------------------------------------------------------------
    #  Handles the 'context_group' trait on the current context being changed:
    #---------------------------------------------------------------------------

    def _context_group_changed_for_context ( self, other, trait, old, new ):
        self.trait_property_changed( 'context_group', old, new )

    #---------------------------------------------------------------------------
    #  Handles the 'context_modified' and 'dict_modified' events being fired:
    #---------------------------------------------------------------------------

    def _context_is_modified ( self, event ):
        """ Handles the 'context_modified' event being fired.
        """
        self.post_context_modified( event )

    def _dict_is_modified( self, event ):
        """ Handles the 'dict_modified' event being fired.
        """
        self.post_dict_modified( event )

    #-- Mapping Object Interface -----------------------------------------------

    def __getitem__ ( self, name ):

        # Intercept context items that are valid dictionary entries (e.g.
        # SubContextItems have names that aren't in our dictionary)
        if name in self.context_names and name in self:
            return self.get_context_data( name )

        # Handle the special '__context__' name as a reference to ourself:
        elif name == '__context__':
            return self

        # Return the requested item:
        else:
            return self.context_base.__getitem__( name )

    def __setitem__ ( self, name, value ):

        # Intercept context items that are valid dictionary entries (e.g.
        # SubContextItems have names that aren't in our dictionary)
        if name in self.context_names and name in self:
            self.set_context_data( name, value )

        # Check for and handle a name already in the base context:
        elif name in self.context_base:
            self.context_base.__setitem__( name, value )

        # Otherwise, must be a new, undefined, name being added to the context:
        else:
            self.context.set_context_undefined( name, value )

    def __delitem__ ( self, name ):
        self.context_base.__delitem__( name )

    def keys ( self ):
        return self.context_base.keys()

    # Pass-through to 'context_base' for efficiency
    def __contains__ ( self, *a, **kw ):
        return self.context_base.__contains__( *a, **kw )
    def __iter__ ( self, *a, **kw ):
        return self.context_base.__iter__( *a, **kw )
    def iteritems ( self, *a, **kw ):
        return self.context_base.iteritems( *a, **kw )
