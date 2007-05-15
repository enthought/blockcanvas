#-------------------------------------------------------------------------------
#
#  Unit Scalar Editor
#
#  Date: 05/08/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

import wx

from enthought.traits.api \
    import CFloat, false, HasPrivateTraits, Instance, Str
    
from enthought.traits.ui.api \
    import View, HGroup, Item, Label
    
from enthought.traits.ui.wx.ui_editor \
    import UIEditor
    
from enthought.traits.ui.wx.basic_editor_factory \
    import EditorFactory
    
from enthought.units.convert \
    import convert
    
from enthought.units.unit \
    import unit
    
from enthought.numerical_modeling.units.unit_scalar \
    import UnitArray
    
class UnitView ( HasPrivateTraits ):
    pass    
    
class UnitScalarView ( UnitView ):

    #-- Trait Definitions ------------------------------------------------------    
    
    # The current value of the Unit Scalar:
    magnitude = CFloat
    
    # The units of the Units Scalar:
    units = Instance( unit )

    #-- Traits Views -----------------------------------------------------------
    
    view = View( 
        HGroup(
            Item( 'magnitude' ),
            Item( 'units', style = 'readonly' ),
            show_labels=False
        )
    )
    
class ReadonlyUnitScalarView ( UnitScalarView ):

    #-- Traits Views -----------------------------------------------------------
    
    view = View( 
        HGroup(
            Item( 'magnitude', style = 'readonly'),
            Item( 'units', style = 'readonly' ),
            show_labels=False
        )
    )
    
class UnitArrayView ( UnitView ):
    
    #-- Trait Definitions ------------------------------------------------------    
    
    # The units of the Units Scalar:
    units = Instance( unit )
    
    #-- Trait Views ------------------------------------------------------------
    
    view = View( 
        HGroup(
            Label( '[Array]' ),
            Item( 'units', style = 'readonly' ),
            show_labels=False
        )
    )
    
class SimpleEditor ( UIEditor ):
    
    #-- Trait Definitions ------------------------------------------------------
    
    # The current unit view object:
    unit_view = Instance( UnitView )

    # should this editor be readonly?
    readonly = false
    
    #-- Trait Views ------------------------------------------------------------
    
    view = View(
        Item( 'unit_view', style = 'custom', show_label = False )
    )
        
    #---------------------------------------------------------------------------
    #  Creates the traits UI for the editor (must be overridden by a subclass): 
    #---------------------------------------------------------------------------
                
    def init_ui ( self, parent ):
        """ Creates the traits UI for the editor.
        """
        self.update_editor()
        return self.edit_traits( parent = parent, kind = 'subpanel' )
        
    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------
        
    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the 
            editor.
        """
        
        try:
            if len(self.value) > 1: 
                self.unit_view = UnitArrayView( units = self.value.units )
        except:
            if self.readonly:
                self.unit_view = \
                    ReadonlyUnitScalarView( units = self.value.units,
                                            magnitude = self.value) 
            else:
                self.unit_view = \
                    UnitScalarView( units = self.value.units,
                                    magnitude = self.value) 
                self.unit_view.on_trait_change(self._update, "magnitude")

    def _update(self):
        self.value = UnitArray(self.unit_view.magnitude, units=self.value.units)

                    
#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

class UnitEditor( EditorFactory ):

    def simple_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             readonly    = False )
  
    def readonly_editor ( self, ui, object, name, description, parent ):
        return SimpleEditor( parent,
                             factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             readonly    = True )
