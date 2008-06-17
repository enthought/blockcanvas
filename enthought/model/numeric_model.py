#-------------------------------------------------------------------------------
#
#  Classes for defining Traits-based numeric array models efficiently.
#
#  Written by: David C. Morrill
#
#  Date: 09/28/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import scipy as scipy_base

from enthought.enable2.traits.api import RGBAColor

from enthought.traits.api \
    import HasTraits, HasPrivateTraits, Event, List, Str, Instance, Property, \
           Delegate, Expression, Constant, Callable, Enum, Bool, Int, Array, \
           Any, Float, true, false

from enthought.traits.ui.api \
    import View

from numpy import compress, concatenate, array, repeat, newaxis, ones, zeros, \
        less_equal, equal, not_equal, less, logical_and, logical_not, add, \
        putmask, arange, sum, take, maximum, minimum, nan, isfinite

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# get_xxx_model 'mode' values:
QueryModel  = 0    # Query existence of a model
OpenModel   = 1    # Return current model if any; otherwise create one
CreateModel = 2    # Always create a new model

# Create the global dictionary used for 'eval':
eval_globals = {}
for name in dir( scipy_base ):
    eval_globals[ name ] = getattr( scipy_base, name )

#-------------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------------

FilterParam = Float( event = 'modified' ) #, auto_set = False )

#-------------------------------------------------------------------------------
#  'NumericFilter' class (abstract base class):
#-------------------------------------------------------------------------------

class NumericFilter ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the filter (implemented as a Property in each subclass):
    # name = Property

    # Event fired when filter is modified:
    updated = Event

    # Is the filter enabled or disabled?
    enabled = Bool( True, event = 'modified' )

    # Should the value, isbit and color traits be used?
    use_value = Bool( False, event = 'modified' )

    # Value to scale filter results by:
    value = Int( 1, event = 'modified' )

    # Is the value a bit number?
    is_bit = Bool( False, event = 'modified' )

#-- View related ---------------------------------------------------------------

    # Foreground color:
    foreground_color = RGBAColor( 'black', event = 'modified' )

    # Background color:
    background_color = RGBAColor( 'white', event = 'modified' )

    #---------------------------------------------------------------------------
    #  Handles the 'modified' pseudo-event being fired:
    #---------------------------------------------------------------------------

    def _modified_changed ( self ):
        """ Handles the 'modified' pseudo-event being fired.
        """
        self.updated = True

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified model:
    #---------------------------------------------------------------------------

    def __call__ ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        if self.enabled:
            result = self._eval( model )
            if (not self.use_value) or (result is None):
                return result
            result = not_equal( result, 0 )
            scale  = self.value
            if self.is_bit:
                scale = (1 << self.value)
            if scale == 1:
                return result
            return result * scale
        return None

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified model:
    #---------------------------------------------------------------------------

    def _eval ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        return None

    #---------------------------------------------------------------------------
    #  Returns the string representation of the filter:
    #---------------------------------------------------------------------------

    def __str__ ( self ):
        """ Returns the string representation of the filter.
        """
        return self.name

#-------------------------------------------------------------------------------
#  'ExpressionFilter' class:
#-------------------------------------------------------------------------------

class ExpressionFilter ( NumericFilter ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Python expression used to filter the data:
    filter = Expression

    # Name of the filter:
    name = Property

    # Should the value, is_bit and color traits be used? (override):
    use_value = True

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( 'filter' )

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, filter = 'None', **traits ):
        """ Initializes the object.
        """
        self.filter = filter
        super( ExpressionFilter, self ).__init__( **traits )

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        if self._name:
            return self._name
        if not self.enabled:
            return '[%s]' % self.filter.strip()
        return self.filter.strip()

    def _set_name ( self, value ):
        old = self.name
        if value != old:
            self._name = value
            self.trait_property_changed( 'name', old, value )

    #---------------------------------------------------------------------------
    #  Handles the 'filter' expression being changed:
    #---------------------------------------------------------------------------

    def _filter_changed ( self, old, new ):
        """ Handles the 'filter' expression being changed.
        """
        self.updated = True
        self._name_updated()

    #---------------------------------------------------------------------------
    #  Handles the 'enabled' state being changed:
    #---------------------------------------------------------------------------

    def _enabled_changed ( self ):
        """ Handles the 'enabled' state being changed.
        """
        self._name_updated()

    #---------------------------------------------------------------------------
    #  Handles the name being potentially changed:
    #---------------------------------------------------------------------------

    def _name_updated ( self ):
        """ Handles the name being potentially changed.
        """
        if not self._name:
            self.trait_property_changed( 'name', self._name, self.name )

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified model:
    #---------------------------------------------------------------------------

    def _eval ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        try:
            mask = eval( self.filter_, eval_globals, model.name_space )
            if (mask is None) or (mask.dtype == int):
                return mask
            return (mask != 0.0)
        except:
            return None

#-------------------------------------------------------------------------------
#  'SortFilter' class:
#-------------------------------------------------------------------------------

class SortFilter ( ExpressionFilter ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Sort mode:
    mode = Enum( 'ascending', 'descending', event = 'modified' )

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( 'name', 'filter', 'mode' )

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified model:
    #---------------------------------------------------------------------------

    def __call__ ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        if self.enabled:
            values = self._eval( model )
            if values is not None:
                values = zip( range( len( values ) ), values )
                if self.mode == 'ascending':
                    values.sort( lambda l, r: cmp( l[1], r[1] ) )
                else:
                    values.sort( lambda l, r: cmp( r[1], l[1] ) )
                return [ v[0] for v in values ]
        return None

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified model:
    #---------------------------------------------------------------------------

    def _eval ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        try:
            return eval( self.filter_, eval_globals, model.name_space )
        except:
            return None

#-------------------------------------------------------------------------------
#  'IndexFilter' class:
#-------------------------------------------------------------------------------

class IndexFilter ( NumericFilter ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # List of model indices to which the filter applies:
    indices = List( Int )

    # Should the values be inverted (0 <--> 1)?
    invert = Bool( False, event = 'modified' )

    #---------------------------------------------------------------------------
    #  Handles the 'indices' trait being changed:
    #---------------------------------------------------------------------------

    def _indices_changed ( self ):
        """ Handles the 'indices' trait being changed.
        """
        self.updated = True

    def _indices_items_changed ( self ):
        """ Handles the 'indices' trait being changed.
        """
        self.updated = True

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified model:
    #---------------------------------------------------------------------------

    def _eval ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        if len( self.indices ) == 0:
            return None

        indices = list( model.model_indices )
        if self.invert:
            value  = 0
            result = ones( ( len( indices ), ), int )
        else:
            value  = 1
            result = zeros( ( len( indices ), ), int )

        for item in self.indices:
            try:
                result[ indices.index( item ) ] = value
            except:
                pass

        return result

#-------------------------------------------------------------------------------
#  'NaNFilter' class:
#-------------------------------------------------------------------------------

class NaNFilter ( NumericFilter ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Should the values be inverted (0 <--> 1)?
    invert = Bool( True, event = 'modified' )

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified model:
    #---------------------------------------------------------------------------

    def _eval ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        result = None
        for name in model.model_names:
            if result is None:
                result = isfinite( getattr( model, name ) )
            else:
                result = result & isfinite( getattr( model, name ) )

        if self.invert or (result is None):
            return result

        return logical_not( result )

#-------------------------------------------------------------------------------
#  'AggregateFilter' class:
#-------------------------------------------------------------------------------

class AggregateFilter ( NumericFilter ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Sub-filters whose values are combined together:
    filters = List( NumericFilter )

    # Name of the filter:
    name = Property

    # Combining rule to apply:
    rule = Enum( 'and', 'or', 'max', 'min', cols = 2 )

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, *filters, **traits ):
        """ Initializes the object.
        """
        self.filters = list( filters )
        super( AggregateFilter, self ).__init__( **traits )

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        if self._name:
            return self._name

        return getattr( self, '_get_name_' + self.rule )()

    def _set_name ( self, value ):
        old = self.name
        if value != old:
            self._name = value
            self.trait_property_changed( 'name', old, value )

    def _get_name_and ( self ):
        return self._get_name_using( '(%s)', ') and (', 2 )

    def _get_name_or ( self ):
        return self._get_name_using( '(%s)', ') or (', 2 )

    def _get_name_min ( self ):
        return self._get_name_using( 'min( %s )', ', ', 1 )

    def _get_name_max ( self ):
        return self._get_name_using( 'max( %s )', ', ', 1 )

    def _get_name_using ( self, wrapper, separator, threshold ):
        names  = [ f.name for f in self.filters if f.enabled ]
        result = separator.join( names )
        if len( names ) >= threshold:
            return wrapper % result

        if result != '':
            return result

        return 'None'

    #---------------------------------------------------------------------------
    #  Handles the 'rule' trait being changed:
    #---------------------------------------------------------------------------

    def _rule_changed ( self, old, new ):
        """ Handles the 'rule' trait being changed.
        """
        self.updated = True
        self._name_updated()

    #---------------------------------------------------------------------------
    #  Handles the sub-filters being changed:
    #---------------------------------------------------------------------------

    def _filters_changed ( self, old, new ):
        """ Handles the sub-filters being changed.
        """
        self._listen_to_filters( old, True  )
        self._listen_to_filters( new, False )
        self.updated = True
        self._name_updated()

    def _filters_items_changed ( self, event ):
        """ Handles the sub-filters being changed.
        """
        self._listen_to_filters( event.removed, True  )
        self._listen_to_filters( event.added,   False )
        self.updated = True
        self._name_updated()

    #---------------------------------------------------------------------------
    #  Connect/Disconnect events for a specified list of filters:
    #---------------------------------------------------------------------------

    def _listen_to_filters ( self, filters, remove = False ):
        for filter in filters:
            filter.on_trait_change( self._filter_updated, 'updated',
                                    remove = remove )
            filter.on_trait_change( self._name_updated, 'name',
                                    remove = remove )

    #---------------------------------------------------------------------------
    #  Handles a sub-filter being updated:
    #---------------------------------------------------------------------------

    def _filter_updated ( self ):
        """ Handles a sub-filter being updated.
        """
        self.updated = True
        self._name_updated()

    #---------------------------------------------------------------------------
    #  Handles a sub-filter's name being updated:
    #---------------------------------------------------------------------------

    def _name_updated ( self ):
        """ Handles a sub-filter's name being updated.
        """
        if not self._name:
            self.trait_property_changed( 'name', self._name, self.name )

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified model:
    #---------------------------------------------------------------------------

    def _eval ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        mask   = None
        method = getattr( self, '_%s_rule' % self.rule )
        for filter in self.filters:
            maski = filter( model )
            if maski is not None:
                if mask is None:
                    mask = maski
                else:
                    mask = method( mask, maski )

        return mask

    #---------------------------------------------------------------------------
    #  Implementation of the various combining rules:
    #---------------------------------------------------------------------------

    def _and_rule ( self, mask1, mask2 ):
        return mask1 & mask2

    def _or_rule ( self, mask1, mask2 ):
        return mask1 | mask2

    def _max_rule ( self, mask1, mask2 ):
        return maximum( mask1, mask2 )

    def _min_rule ( self, mask1, mask2 ):
        return minimum( mask1, mask2 )

#-------------------------------------------------------------------------------
#  'FilterSet' class:
#-------------------------------------------------------------------------------

class FilterSet ( AggregateFilter ):
    pass

#-------------------------------------------------------------------------------
#  'ANumericItem' class:
#-------------------------------------------------------------------------------

class ANumericItem ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The model containing this item:
    model = Instance( 'ANumericModel', allow_none = True )

    # The current value of the associated numeric array (implemented in each
    # subclass):
    #data = Property

    # Name of the model trait for this item (implemented in each subclass):
    #name = Property

    # Value to be substituted in reduction filters when 'use_value' is True:
    value = Any( nan )

    # Callable function used to extract the data from a multi-dimensional array:
    slicer = Callable

    # Does the value have an associated quantity?
    is_quantity = false

#-- View related ---------------------------------------------------------------

    # User interface label:
    label = Str

    # String formatting rule:
    format = Str( '%.3f' )

    # Foreground color (intended use: text color, plot line color):
    foreground_color = RGBAColor( 'black' )

    # Background color (intended use: text background color, plot fill color):
    background_color = RGBAColor( 'white' )

#-------------------------------------------------------------------------------
#  'NumericItem' class:
#-------------------------------------------------------------------------------

class NumericItem ( ANumericItem ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The current value of the associated numeric array:
    data = Property

    # Name of the model trait for this item:
    name = Property

    # Object containing the array:
    object = Instance( HasTraits )

    # Id of the array trait:
    id = Str

    #---------------------------------------------------------------------------
    #  Implementation of the 'data' property:
    #---------------------------------------------------------------------------

    def _get_data ( self ):
        if self.slicer is None:
            return getattr( self.object, self.id )

        return self.slicer( getattr( self.object, self.id ) )

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        return self._name or self.id

    def _set_name ( self, name ):
        self._name = name

    #---------------------------------------------------------------------------
    #  Handles the 'model' trait being changed:
    #---------------------------------------------------------------------------

    def _model_changed ( self, model ):
        self.object.on_trait_change( self._data_updated, self.id,
                                     remove = (model is None) )

    #---------------------------------------------------------------------------
    #  Handles the data associated with this item being changed:
    #---------------------------------------------------------------------------

    def _data_updated ( self ):
        self.model.trait_property_changed( self.name, None, self.data )
        self.model.model_data_updated = True

#-------------------------------------------------------------------------------
#  'EvaluatedNumericItem' class:
#-------------------------------------------------------------------------------

class EvaluatedNumericItem ( ANumericItem ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The current value of the associated numeric array:
    data = Property

    # Name of the model trait for this item:
    name = Property

    # Expression used to compute the numeric value:
    evaluate = Expression

    #---------------------------------------------------------------------------
    #  Implementation of the 'data' property:
    #---------------------------------------------------------------------------

    def _get_data ( self ):
        if self._data is None:
            if self._busy:
                return None
            self._busy = True
            self._data = eval( self.evaluate_, eval_globals,
                               self.model.name_space )
            self._busy = False
            if self.slicer is not None:
                self._data = self.slicer( self._data )

        return self._data

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        return self._name or self.evaluate

    def _set_name ( self, name ):
        self._name = name

    #---------------------------------------------------------------------------
    #  Handles the 'model' trait being changed:
    #---------------------------------------------------------------------------

    def _model_changed ( self, old, new ):
        """ Handles the 'model' trait being changed.
        """
        if old is not None:
            old.on_trait_change( self._data_updated, 'model_data_updated',
                                 remove = True )
        if new is not None:
            new.on_trait_change( self._data_updated, 'model_data_updated' )

    #---------------------------------------------------------------------------
    #  Handles the data associated with this item being changed:
    #---------------------------------------------------------------------------

    def _data_updated ( self ):
        self._data = None
        self.model.trait_property_changed( self.name, None, self.data )

#-------------------------------------------------------------------------------
#  'ANumericModel' class:
#-------------------------------------------------------------------------------

class ANumericModel ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask (none for the base model):
    model_selection = Constant( None )

    # Event fired when the contents of the model are updated:
    model_updated = Event

    # Fired when some data within the model is updated:
    model_data_updated = Event

    # Event fired when items are added to the model:
    model_added = Event

    # The name space of all values currently contained in the model:
    name_space = Property

    #---------------------------------------------------------------------------
    #  Gets a ReductionModel associated with the model:
    #---------------------------------------------------------------------------

    def get_reduction_model ( self, mode = CreateModel ):
        """ Gets a ReductionModel associated with the model.
        """
        if mode == QueryModel:
            return None
        return ReductionModel( model = self )

    #---------------------------------------------------------------------------
    #  Gets a MappingModel associated with the model:
    #---------------------------------------------------------------------------

    def get_mapping_model ( self, mode = CreateModel ):
        """ Gets a MappingModel associated with the model.
        """
        if mode == QueryModel:
            return None
        return MappingModel( model = self )

    #---------------------------------------------------------------------------
    #  Gets a SelectionModel associated with the model:
    #---------------------------------------------------------------------------

    def get_selection_model ( self, mode = CreateModel ):
        """ Gets a SelectionModel associated with the model.
        """
        if mode == QueryModel:
            return None
        return SelectionModel( model = self )

    #---------------------------------------------------------------------------
    #  Removes a specified model from a model chain:
    #---------------------------------------------------------------------------

    def remove_model ( self, model ):
        """ Removes a specified model from a model chain.
        """
        pass

    #---------------------------------------------------------------------------
    #  Prints the model structure:
    #---------------------------------------------------------------------------

    def dump ( self, indent = 0 ):
        print '%s%s( %08X )' % (
              ' ' * indent, self.__class__.__name__, id( self ) )

    #---------------------------------------------------------------------------
    #  Implementation of the 'name_space' property:
    #---------------------------------------------------------------------------

    def _get_name_space ( self ):
        # fixme: If performance turns out to be a problem, then the result of
        # the following calculation could be cached:
        name_space = { 'model_indices': self.model_indices }
        for item in self.model_items:
            name_space[ item.name ] = getattr( self, item.name )

        return name_space

#-------------------------------------------------------------------------------
#  'NumericModel' class:
#-------------------------------------------------------------------------------

class NumericModel ( ANumericModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # List of array descriptor items:
    model_items = List( ANumericItem )

    # List of available data item names:
    model_names = Property

    # Base model reference:
    model_base = Property

    # The array indices:
    model_indices = Property

    #---------------------------------------------------------------------------
    #  Returns the substitution 'value' associated with a particular trait:
    #---------------------------------------------------------------------------

    def _model_value_for ( self, name ):
        """ Returns the substitution 'value' associated with a particular trait.
        """
        return self._model_items[ name ].value

    #---------------------------------------------------------------------------
    #  Handles the 'model_items' trait being changed:
    #---------------------------------------------------------------------------

    def _model_items_changed ( self ):
        """ Handles the 'items' trait being changed.
        """
        self._model_items = items = {}
        for item in self.model_items:
            items[ item.name ] = item
            self.add_trait( item.name, Property( self._get_data ) )
            item.model = self
        self.model_added = items

    def _model_items_items_changed ( self, event ):
        items = self._model_items
        if items is None:
            self._model_items = items = {}

        for item in event.removed:
            del items[ item.name ]
            item.model = None

        added = event.added
        if len( added ) > 0:
            for item in added:
                items[ item.name ] = item
                self.add_trait( item.name, Property( self._get_data ) )
                item.model = self

            self.model_added = added

    #---------------------------------------------------------------------------
    #  Implementation of the 'names' property:
    #---------------------------------------------------------------------------

    def _get_model_names ( self ):
        return [ item.name for item in self.model_items ]

    #---------------------------------------------------------------------------
    #  Implementation of the 'model_base' property:
    #---------------------------------------------------------------------------

    def _get_model_base ( self ):
        return self

    #---------------------------------------------------------------------------
    #  Implementation of the 'model_indices' property:
    #---------------------------------------------------------------------------

    def _get_model_indices ( self ):
        if len( self.model_items ) > 0:
            return arange( 0, len( self.model_items[0].data ) )
        return array( [] )

    #---------------------------------------------------------------------------
    #  Generic property implementation for retrieving the value of an item:
    #---------------------------------------------------------------------------

    def _get_data ( self, ignore, name ):
        item = self._model_items[ name ]
        if item.is_quantity:
            return unit_manager.convert( self._get_quantity_for( name ) ).data
        return item.data

#-------------------------------------------------------------------------------
#  Helper function for creating a properly terminated NumericModel:
#-------------------------------------------------------------------------------

def NumericPipe ( **traits ):
    return PassThruModel( model = NumericModel( **traits ) )

#-------------------------------------------------------------------------------
#  Helper function for creating a NumericModel pipe based on an object with
#  traits which contain Numeric arrays:
#-------------------------------------------------------------------------------

def NumericObjectModel ( object, **traits ):
    return NumericPipe( model_items = [ NumericItem( object = object,
                                                     id     = name )
                                        for name in object.trait_names()
                                        if object.base_trait( name ).array ],
                        **traits )

#-------------------------------------------------------------------------------
#  Helper function for creating a NumericModel pipe from a list of named arrays:
#-------------------------------------------------------------------------------

def NumericArrayModel ( **arrays ):
    object = HasTraits()
    for name, value in arrays.items():
        object.add_trait( name, Array )
        setattr( object, name, value )
    return NumericPipe( model_items = [ NumericItem( object = object, id = id )
                                        for id in arrays.keys() ] )

#-------------------------------------------------------------------------------
#  Creates a Data Explorer view from a list of named arrays:
#-------------------------------------------------------------------------------

def ArrayExplorer ( format = '%.3f', **arrays ):
    """ Creates a Data Explorer view from a list of named arrays.
    """
    from numeric_model_explorer import NumericModelExplorer

    NumericModelExplorer( model  = NumericArrayModel( **arrays ),
                          format = format,
                          title  = 'Array Explorer' ).edit_traits()

#-------------------------------------------------------------------------------
#  'DerivativeModel' class:
#-------------------------------------------------------------------------------

class DerivativeModel ( ANumericModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Model being filtered:
    model = Instance( ANumericModel )

    # List of array descriptor items:
    model_items = Delegate( 'model' )

    # List of available data item names:
    model_names = Delegate( 'model' )

    # Base model reference:
    model_base = Delegate( 'model' )

    # The base model indices after 'filtering':
    model_indices = Property

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, model = None, **traits ):
        """ Initializes the object.
        """
        super( DerivativeModel, self ).__init__( **traits )
        if model is not None:
            self.model = model

    #---------------------------------------------------------------------------
    #  Inserts a new model before this model:
    #---------------------------------------------------------------------------

    def insert_model ( self, model ):
        """ Inserts a new model before this model.
        """
        model.model, self.model = self.model, model

    #---------------------------------------------------------------------------
    #  Removes a specified model from a model chain:
    #---------------------------------------------------------------------------

    def remove_model ( self, model ):
        """ Removes a specified model from a model chain.
        """
        if model is not None:
            if model is self.model:
                self.model = model.model
            else:
                self.model.remove_model( model )

    #---------------------------------------------------------------------------
    #  Prints the model structure:
    #---------------------------------------------------------------------------

    def dump ( self, indent = 0 ):
        print '%s%s( %08X )' % (
              ' ' * indent, self.__class__.__name__, id( self ) )
        self.model.dump( indent + 3 )

    #---------------------------------------------------------------------------
    #  Implementation of the 'model_indices' property:
    #---------------------------------------------------------------------------

    def _get_model_indices ( self ):
        return self._get_data( None, 'model_indices' )

    #---------------------------------------------------------------------------
    #  Returns the substitution 'value' associated with a particular trait:
    #---------------------------------------------------------------------------

    def _model_value_for ( self, name ):
        """ Returns the substitution 'value' associated with a particular trait.
        """
        return self._model_base._model_value_for( name )

    #---------------------------------------------------------------------------
    #  Handles the underlying model being changed:
    #---------------------------------------------------------------------------

    def _model_changed ( self, old, new ):
        """ Handles the underlying model being changed.
        """
        if old is not None:
            old.on_trait_change( self._reset,     'model_updated',
                                 remove = True )
            old.on_trait_change( self._add_items, 'model_added',
                                 remove = True )
            for item in old.model_items:
                old.on_trait_change( self._reset, item.name, remove = True )

        if new is not None:
            new.on_trait_change( self._reset,     'model_updated' )
            new.on_trait_change( self._add_items, 'model_added' )
            self._add_items( self.model_items )

        self._reset()

    #---------------------------------------------------------------------------
    #  Resets the internal state of the model (i.e. flushes all cached data):
    #---------------------------------------------------------------------------

    def _reset ( self ):
        """ Resets the internal state of the model (i.e. flushes all cached
            data).
        """
        self.model_updated = True

    #---------------------------------------------------------------------------
    #  Handles items being added to the model:
    #---------------------------------------------------------------------------

    def _add_items ( self, items ):
        model = self.model
        for item in items:
            self.add_trait( item.name, Property( self._get_data ) )
            model.on_trait_change( self._reset, item.name )
        self.model_added = items

    #---------------------------------------------------------------------------
    #  Hooks a model into the pipeline (if necessary):
    #---------------------------------------------------------------------------

    def _hook_model ( self, model ):
        """ Hooks a model into the pipeline (if necessary).
        """
        if (model is not None) and (model.model is self.model):
            self.model = model
        return model

    #---------------------------------------------------------------------------
    #  Creates a new model of the specified type (if necessary):
    #---------------------------------------------------------------------------

    def _create_model ( self, mode ):
        """ Creates a new model of the specified type (if necessary).
        """
        if mode != CreateModel:
            return self

        return self.__class__( model = self )

#-------------------------------------------------------------------------------
#  'FilterModel' class:
#-------------------------------------------------------------------------------

class FilterModel ( DerivativeModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask (actually defined in each subclass):
    # model_selection = Property

    # The filter being applied to the model:
    model_filter = Instance( NumericFilter )

    # Current selection mask (private property)
    _mask = Property

    #---------------------------------------------------------------------------
    #  Prints the model structure:
    #---------------------------------------------------------------------------

    def dump ( self, indent = 0 ):
        filter = ''
        mf     = self.model_filter
        if mf is not None:
            filter = ', %s( %08X )' % ( mf.__class__.__name__, id( mf ) )
        print '%s%s( %08X%s )' % (
              ' ' * indent, self.__class__.__name__, id( self ), filter )
        self.model.dump( indent + 3 )

    #---------------------------------------------------------------------------
    #  Implementation of the '_mask' property:
    #---------------------------------------------------------------------------

    def _get__mask ( self ):
        if (self._cur_mask is None) and (self.model_filter is not None):
            self._cur_mask = self.model_filter( self.model )
        return self._cur_mask

    #---------------------------------------------------------------------------
    #  Handles the model filter being changed:
    #---------------------------------------------------------------------------

    def _model_filter_changed ( self, old, new ):
        """ Handles the model filter being changed.
        """
        if old is not None:
            old.on_trait_change( self._reset, 'updated', remove = True )

        if new is not None:
            new.on_trait_change( self._reset, 'updated' )

        self._reset()

    #---------------------------------------------------------------------------
    #  Resets the internal state of the model (i.e. flushes all cached data):
    #---------------------------------------------------------------------------

    def _reset ( self ):
        """ Resets the internal state of the model (i.e. flushes all cached
            data).
        """
        self._cur_mask = None
        super( FilterModel, self )._reset()

    #---------------------------------------------------------------------------
    #  The generic implementation of the item data property
    #  (must be overridden in a subclass):
    #---------------------------------------------------------------------------

    def _get_data ( self, ignore, name ):
        """ The generic implementation of the item data property.
        """
        raise NotImplementedError

#-------------------------------------------------------------------------------
#  'ReductionModel' class:
#-------------------------------------------------------------------------------

class ReductionModel ( FilterModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    model_selection = Property

    # Should filtered out values be set to a specified value, rather than
    # discarded?
    use_value = false

    #---------------------------------------------------------------------------
    #  Gets a ReductionModel associated with the model:
    #---------------------------------------------------------------------------

    def get_reduction_model ( self, mode = CreateModel ):
        """ Gets a ReductionModel associated with the model.
        """
        return self._create_model( mode )

    #---------------------------------------------------------------------------
    #  Implementation of the 'model_selection' property:
    #---------------------------------------------------------------------------

    def _get_model_selection ( self ):
        model_mask = self.model.model_selection
        self_mask  = self._mask
        if (self_mask is None) or (model_mask is None):
            return model_mask

        return compress( self_mask, model_mask, axis = 0 )

    #---------------------------------------------------------------------------
    #  The generic implementation of the item data property:
    #---------------------------------------------------------------------------

    def _get_data ( self, ignore, name ):
        """ The generic implementation of the item data property.
        """
        return self._reduce_data( getattr( self.model, name ), name )

    #---------------------------------------------------------------------------
    #  Reduces the specified data by the current mask:
    #---------------------------------------------------------------------------

    def _reduce_data ( self, data, name = None ):
        """ Reduces the specified data by the current mask.
        """
        mask = self._mask
        if mask is None:
            return data

        if self.use_value:
            if name is None:
                return data
            temp = data.copy()
            putmask( temp, mask == 0, self._model_value_for( name ) )
            return temp

        return compress( mask, data, axis = 0 )

#-------------------------------------------------------------------------------
#  'MappingModel' class:
#-------------------------------------------------------------------------------

class MappingModel ( FilterModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    model_selection = Property

    #---------------------------------------------------------------------------
    #  Gets a ReductionModel associated with the model:
    #---------------------------------------------------------------------------

    def get_reduction_model ( self, mode = CreateModel ):
        """ Gets a ReductionModel associated with the model.
        """
        return self._hook_model( self.model.get_reduction_model( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a MappingModel associated with the model:
    #---------------------------------------------------------------------------

    def get_mapping_model ( self, mode = CreateModel ):
        """ Gets a MappingModel associated with the model.
        """
        return self._create_model( mode )

    #---------------------------------------------------------------------------
    #  Implementation of the 'model_selection' property:
    #---------------------------------------------------------------------------

    def _get_model_selection ( self ):
        model_mask = self.model.model_selection
        mask       = self._mask
        if (mask is None) or (model_mask is None):
            return model_mask

        return take( model_mask, mask, axis = 0 )

    #---------------------------------------------------------------------------
    #  The generic implementation of the item data property:
    #---------------------------------------------------------------------------

    def _get_data ( self, ignore, name ):
        """ The generic implementation of the item data property.
        """
        data = getattr( self.model, name )
        mask = self._mask
        if mask is None:
            return data

        return take( data, mask, axis = 0 )

#-------------------------------------------------------------------------------
#  'SelectionModel' class:
#-------------------------------------------------------------------------------

class SelectionModel ( FilterModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    model_selection = Property

    #---------------------------------------------------------------------------
    #  Gets a ReductionModel associated with the model:
    #---------------------------------------------------------------------------

    def get_reduction_model ( self, mode = CreateModel ):
        """ Gets a ReductionModel associated with the model.
        """
        return self._hook_model( self.model.get_reduction_model( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a MappingModel associated with the model:
    #---------------------------------------------------------------------------

    def get_mapping_model ( self, mode = CreateModel ):
        """ Gets a MappingModel associated with the model.
        """
        return self._hook_model( self.model.get_mapping_model( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a SelectionModel associated with the model:
    #---------------------------------------------------------------------------

    def get_selection_model ( self, mode = CreateModel ):
        """ Gets a SelectionModel associated with the model.
        """
        return self._create_model( mode )

    #---------------------------------------------------------------------------
    #  Implementation of the 'model_selection' property:
    #---------------------------------------------------------------------------

    def _get_model_selection ( self ):
        model_mask = self.model.model_selection
        self_mask  = self._mask
        if self_mask is None:
            return model_mask

        if model_mask is None:
            return self_mask

        if sum( model_mask & self_mask ) == 0:
            return model_mask | self_mask

        return maximum( model_mask, self_mask )

    #---------------------------------------------------------------------------
    #  The generic implementation of the item data property:
    #---------------------------------------------------------------------------

    def _get_data ( self, ignore, name ):
        """ The generic implementation of the item data property.
        """
        return getattr( self.model, name )

#-------------------------------------------------------------------------------
#  'TerminationModel' class:
#-------------------------------------------------------------------------------

class TerminationModel ( DerivativeModel ):

    #---------------------------------------------------------------------------
    #  Gets a ReductionModel associated with the model:
    #---------------------------------------------------------------------------

    def get_reduction_model ( self, mode = CreateModel ):
        """ Gets a ReductionModel associated with the model.
        """
        return self._hook_model( self.model.get_reduction_model( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a MappingModel associated with the model:
    #---------------------------------------------------------------------------

    def get_mapping_model ( self, mode = CreateModel ):
        """ Gets a MappingModel associated with the model.
        """
        return self._hook_model( self.model.get_mapping_model( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a SelectionModel associated with the model:
    #---------------------------------------------------------------------------

    def get_selection_model ( self, mode = CreateModel ):
        """ Gets a SelectionModel associated with the model.
        """
        return self._hook_model( self.model.get_selection_model( mode ) )

#-------------------------------------------------------------------------------
#  'SelectionReductionModel' class:
#-------------------------------------------------------------------------------

class SelectionReductionModel ( TerminationModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    model_selection = Constant( None )

    #---------------------------------------------------------------------------
    #  The generic implementation of the item data property:
    #---------------------------------------------------------------------------

    def _get_data ( self, ignore, name ):
        """ The generic implementation of the item data property.
        """
        data = getattr( self.model, name )
        mask = self.model.model_selection

        if mask is None:
            return []

        return compress( mask, data, axis = 0 )

#-------------------------------------------------------------------------------
#  'CachedModel' class:
#-------------------------------------------------------------------------------

class CachedModel ( TerminationModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    model_selection = Property

    #---------------------------------------------------------------------------
    #  Implementation of the 'model_selection' property:
    #---------------------------------------------------------------------------

    def _get_model_selection ( self ):
        return self._get_data( None, 'model_selection' )

    #---------------------------------------------------------------------------
    #  The generic implementation of the item data property:
    #---------------------------------------------------------------------------

    def _get_data ( self, ignore, name ):
        """ The generic implementation of the item data property.
        """
        cache = self._cache
        if cache is None:
            self._cache = cache = {}
        result = cache.get( name, '' )
        if isinstance(result, basestring):
            cache[ name ] = result = getattr( self.model, name )
        return result

    #---------------------------------------------------------------------------
    #  Resets the internal state of the model (i.e. flushes all cached data):
    #---------------------------------------------------------------------------

    def _reset ( self ):
        """ Resets the internal state of the model (i.e. flushes all cached
            data).
        """
        self._cache = {}
        super( CachedModel, self )._reset()

#-------------------------------------------------------------------------------
#  'PassThruModel' class:
#-------------------------------------------------------------------------------

class PassThruModel ( TerminationModel ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    model_selection = Delegate( 'model' )

    #---------------------------------------------------------------------------
    #  The generic implementation of the item data property:
    #---------------------------------------------------------------------------

    def _get_data ( self, ignore, name ):
        """ The generic implementation of the item data property.
        """
        return getattr( self.model, name )

