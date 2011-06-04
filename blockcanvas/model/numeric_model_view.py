#-------------------------------------------------------------------------------
#
#  NumericModel view support
#
#  Written by: David C. Morrill
#
#  Date: 12/01/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Instance

from traitsui.api \
    import View, Item, VSplit, VGroup

from traitsui.menu \
    import NoButtons

from traitsui.table_column \
    import NumericColumn

from enthought.model.traits.ui.wx.numeric_editor \
    import ToolkitEditorFactory as NumericEditor

from enthought.model.api \
    import ANumericModel, NumericArrayModel, ExpressionFilter, IndexFilter

#-------------------------------------------------------------------------------
#  'NumericModelObject' class:
#-------------------------------------------------------------------------------

class NumericModelObject ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    model     = Instance( ANumericModel )
    reduction = Instance( ExpressionFilter )
    selection = Instance( ExpressionFilter )

    #---------------------------------------------------------------------------
    #  Views the object:
    #---------------------------------------------------------------------------

    def view ( self ):
        """ Views the object.
        """
        model = self.model
        model.get_reduction_model().model_filter = self.reduction = \
            ExpressionFilter()
        model.get_selection_model().model_filter = self.selection = \
            ExpressionFilter()
        number_editor = NumericEditor(
            extendable              = False,
            columns                 = [ NumericColumn( name  = 'model_indices',
                                                       label = 'i' ) ] +
                                      [ NumericColumn( name  = item.id,
                                                       label = item.id )
                                        for item in model.model_items ],
            choose_selection_filter = False,
            edit_selection_filter   = False,
            edit_selection_colors   = False,
            user_selection_filter   = IndexFilter(),
            choose_reduction_filter = False,
            edit_reduction_filter   = False,
            deletable               = False,
            sortable                = True,
            editable                = False )
        self.edit_traits( view = View(
            VSplit( VGroup( 'reduction@', 'selection@',
                            export      = 'DockWindowShell',
                            show_labels = False ),
                    Item( 'model',
                          export = 'DockWindowShell',
                          editor = number_editor ),
                    show_labels = False,
                    id          = 'splitter' ),
            id        = 'enthought.model.numeric_model_view',
            title     = 'Array Viewer',
            dock      = 'horizontal',
            width     = 0.5,
            height    = 0.5,
            resizable = True,
            buttons   = NoButtons ) )

#-------------------------------------------------------------------------------
#  Create a generic NumericEditor view of a NumericModel or a list of arrays:
#-------------------------------------------------------------------------------

def numeric_model_view ( *amodel, **arrays ):
    if len( amodel ) == 1:
        model = amodel[0]
    else:
        model = NumericArrayModel( **arrays )
    NumericModelObject( model = model ).view()

