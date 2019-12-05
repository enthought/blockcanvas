#-------------------------------------------------------------------------------
#
#  Unit Scalar Editor
#
#  Date: 05/08/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

from traits.api \
    import Bool, CFloat, HasPrivateTraits, Instance, Str

from traitsui.api \
    import View, HGroup, Item, Label

from traitsui.ui_editor \
    import UIEditor

from traitsui.api \
    import EditorFactory

from scimath.units.convert \
    import convert

from scimath.units.unit \
    import unit

from scimath.units.unit_scalar \
    import UnitArray

class UnitView ( HasPrivateTraits ):
    pass

class UnitScalarView ( UnitView ):

    #-- Trait Definitions ------------------------------------------------------

    # The current value of the Unit Scalar:
    magnitude = CFloat

    # The units of the Units Scalar:
    units = Str

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
    units =Str

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
    readonly = Bool(False)

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

        if hasattr(self.value.units, 'label'):
            units_str = self.value.units.label
        else:
            units_str = repr(self.value.units)

        try:
            if len(self.value) > 1:
                self.unit_view = UnitArrayView( units = units_str )
        except:
            if self.readonly:
                self.unit_view = \
                    ReadonlyUnitScalarView( units = units_str,
                                            magnitude = self.value)
            else:
                self.unit_view = \
                    UnitScalarView( units = units_str,
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
