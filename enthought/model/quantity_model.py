#-------------------------------------------------------------------------------
#  
#  Extends the core NumericModel classes to support Quantity based values  
#  (i.e. values having units)
#  
#  Written by: David C. Morrill
#  
#  Date: 10/11/2005
#  
#  (c) Copyright 2005 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:  
#-------------------------------------------------------------------------------
    
from NumericModel \
    import NumericItem, NumericModelBase, NumericModel, DerivationModel

from enthought.traits.api \
    import Category

from enthought.units \
    import unit_manager
    
from enthought.units.quantity \
    import Quantity
    
from enthought.units.SI \
    import dimensionless
    
#-------------------------------------------------------------------------------
#  'QuantityNumericItem' category:  
#-------------------------------------------------------------------------------
        
class QuantityNumericItem ( Category, NumericItem ):

    #---------------------------------------------------------------------------
    #  Trait definitions: 
    #---------------------------------------------------------------------------

    # Is the referenced value an array or a Quantity (i.e. has units)?
    is_quantity = false
    
    # The current value of the associated numeric array (override):
    data = Property
    
    #---------------------------------------------------------------------------
    #  Implementation of the 'data' property:  
    #---------------------------------------------------------------------------
        
    def _get_data ( self ):
        data = self.object
        if self.id != '':
            data = getattr( data, self.id )
            
        if self.is_quantity:
            return data.data
            
        return data
        
#-------------------------------------------------------------------------------
#  'QuantityNumericModelBase' category:  
#-------------------------------------------------------------------------------
                
class QuantityNumericModelBase ( Category, NumericModelBase ):
    
    #---------------------------------------------------------------------------
    #  Returns the units associated with a specified trait:  
    #---------------------------------------------------------------------------
        
    def get_units_for ( self, name ):
        """ Returns the units associated with a specified trait.
        """
        if self.is_quantity( name ):
            return unit_manager.default_units_for( 
                       self._get_quantity_for( name ).family_name )
        
        return None
    
    #---------------------------------------------------------------------------
    #  Returns the data associated with a specified trait, optionally in a
    #  specified set of units:
    #---------------------------------------------------------------------------
        
    def get_data_for ( self, name, units = None ):
        """ Returns the data associated with a specified trait, optionally in  a
            specified set of units.
        """
        if (units is None) or (not self.is_quantity( name )):
            return getattr( self, name )
            
        return Quantity( Quantity( getattr( self, name ), 
                                   self.get_units_for( name ) ), units )
    
    #---------------------------------------------------------------------------
    #  Returns a Quantity object associated with a specified trait, optionally
    #  in a specified set of units:
    #---------------------------------------------------------------------------
        
    def get_quantity_for ( self, name, units = None ):
        """ Returns a Quantity object associated with a specified trait, 
            optionally in a specified set of units.
        """
        if self.is_quantity( name ):
            quantity = Quantity( getattr( self, name ), 
                                 self.get_units_for( name ) )
            if units is not None:
                return Quantity( quantity, units )
            return quantity
            
        if units is None:
            units = dimensionless
        return Quantity( getattr( self, name ), units ) 
        
    #---------------------------------------------------------------------------
    #  Returns whether or not a specified item is a quantity (i.e. has units):  
    #---------------------------------------------------------------------------
                
    def is_quantity ( self, name ):
        """ Returns whether or not a specified item is a quantity (i.e. has units).
        """
        raise NotImplementedError
    
    #---------------------------------------------------------------------------
    #  Returns the underlying Quantity object associated with a specified item:  
    #---------------------------------------------------------------------------
                
    def _get_quantity_for ( self, name ):
        """ Returns the underlying Quantity object associated with a specified item.
        """
        raise NotImplementedError
        
#-------------------------------------------------------------------------------
#  'QuantityNumericModel' class:  
#-------------------------------------------------------------------------------
        
class QuantityNumericModel ( Category, NumericModel ):
        
    #---------------------------------------------------------------------------
    #  Returns whether or not a specified item is a quantity (i.e. has units):  
    #---------------------------------------------------------------------------
                
    def is_quantity ( self, name ):
        """ Returns whether or not a specified item is a quantity (i.e. has 
            units).
        """
        return self._model_items[ name ].is_quantity
    
    #---------------------------------------------------------------------------
    #  Returns the underlying Quantity object associated with a specified item:  
    #---------------------------------------------------------------------------
                
    def _get_quantity_for ( self, name ):
        """ Returns the underlying Quantity object associated with a specified 
            item.
        """
        self._model_items[ name ].quantity
        
#-------------------------------------------------------------------------------
#  'QuantityDerivationModel' class:  
#-------------------------------------------------------------------------------
        
class QuantityDerivationModel ( Category, DerivationModel ):
    
    #---------------------------------------------------------------------------
    #  Returns whether or not a specified item is a quantity (i.e. has units):  
    #---------------------------------------------------------------------------
                
    def is_quantity ( self, name ):
        """ Returns whether or not a specified item is a quantity (i.e. has units).
        """
        return self.model.is_quantity( name )
    
    #---------------------------------------------------------------------------
    #  Returns the underlying Quantity object associated with a specified item:  
    #---------------------------------------------------------------------------
                
    def _get_quantity_for ( self, name ):
        """ Returns the underlying Quantity object associated with a specified 
            item.
        """
        return self.model._get_quantity_for( name )
        
