#-------------------------------------------------------------------------------
#
#  Experimental support for simplifying Traits UI building for objects
#  containing Numeric arrays.
#
#  Written by: David C. Morrill
#
#  Date: 01/17/2006
#
#  (c) Copyright 2006 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from numpy import \
    arange

from traits.api \
    import List, Str, Instance, Enum

from traitsui.api \
    import View, Item, HSplit

from traitsui.table_column \
    import NumericColumn

from traitsui.api \
    import Editor

from traitsui.api \
    import BasicEditorFactory

from enthought.model.traits.ui.wx.numeric_editor \
    import ToolkitEditorFactory as NumericEditor

from enthought.model.api \
    import NumericObjectModel, ANumericModel, NumericItem, IndexFilter, \
           PolygonFilter

from enthought.model.numeric_model_explorer \
    import ModelData, SelectionData, NumericModelExplorerInteraction

from chaco.plot_canvas \
    import PlotCanvas

from chaco.plot_value \
    import PlotValue

from chaco.plot_axis \
    import PlotAxis

from chaco.plot_component \
    import PlotComponent

from enable.api \
    import Window


#-------------------------------------------------------------------------------
#  Returns a Kiva (R, G, B, A) tuple for a specified wxPython system colour:
#-------------------------------------------------------------------------------

def color_tuple_for ( id ):
    """ Returns an (R, G, B) tuple for a specified wxPython system colour.
    """
    color = wx.SystemSettings_GetColour( id )
    return ( color.Red()   / 255.,
             color.Green() / 255.,
             color.Blue()  / 255.,
             1.0 )

# Standard systems colors:
BGColor = color_tuple_for( wx.SYS_COLOUR_BTNFACE )

#-------------------------------------------------------------------------------
#  'Table' class:
#-------------------------------------------------------------------------------

class Table ( Item ):

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, *names, **traits ):
        self.name       = '_hidden_model'
        self.label      = 'Table'
        self.show_label = False
        self.editor     = _TableEditorFactory( names = list( names ) )
        super( Table, self ).__init__( **traits )
        if (self.name == '_hidden_model') and (self.id == ''):
            self.id = 'Table_%s' % ('_'.join( names ))

#-------------------------------------------------------------------------------
#  '_TableEditor' class:
#-------------------------------------------------------------------------------

class _TableEditor ( Editor ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Indicate that the numeric editor is scrollable (default override):
    scrollable = True

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Make sure the model we'll be editing exists:
        object = self.object
        if getattr( object, '_hidden_model', None ) is None:
            object._hidden_model = NumericObjectModel( object )

        # Get the list of trait names to initially display and the remaining
        # one that will not be initially displayed:
        names       = self.factory.names
        other_names = [ name for name in object.trait_names()
                        if object.base_trait( name ).array and
                           (name not in names) ]
        if len( names ) == 0:
            names, other_names = other_names, names

        # Create the actual table control:
        self.control = object.edit_traits(
            parent = parent,
            view   = View( Item( '_hidden_model',
                         show_label = False,
                         id         = 'numeric_editor',
                         editor     = NumericEditor(
                             columns = [ NumericColumn( name   = name,
                                                        format = '%.3f' )
                                         for name in names ],
                             other_columns = [ NumericColumn( name   = name,
                                                              format = '%.3f' )
                                               for name in other_names ],
                             user_selection_filter = IndexFilter(),
                             sortable = True ) ),
                     kind = 'subpanel',
                     id   = 'enthought.model.numeric_ui._TableEditor' )
        ).control

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  '_TableEditorFactory' class:
#-------------------------------------------------------------------------------

class _TableEditorFactory ( BasicEditorFactory ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Override of the editor class to construct:
    klass = _TableEditor

    # List of trait names to include in the editor:
    names = List( Str )

#-------------------------------------------------------------------------------
#  'Plot' class:
#-------------------------------------------------------------------------------

class Plot ( Item ):

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, *names, **traits ):
        self.name       = '_hidden_model'
        self.show_label = False
        names           = list( names )

        value = traits.get( 'value' )
        if value is not None:
            names.append( value )
            del traits[ 'value' ]

        index = traits.get( 'index' )
        if index is None:
            index, names = names[0], names[1:]
        else:
            del traits[ 'index' ]

        type = traits.get( 'type' )
        if type is None:
            type = 'line'
        else:
            del traits[ 'type' ]

        self.label  = 'Plot: ' + (','.join( [ '%s(%s)' % ( n, index )
                                             for n in names ] ))
        self.editor = _PlotEditorFactory( index = index,
                                          names = names,
                                          type  = type )
        super( Plot, self ).__init__( **traits )
        if (self.name == '_hidden_model') and (self.id == ''):
            self.id = 'Plot_%s' % ('_'.join( [ index ] + names ))

#-------------------------------------------------------------------------------
#  '_PlotEditor' class:
#-------------------------------------------------------------------------------

class _PlotEditor ( Editor ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Indicate that the numeric editor is scrollable (default override):
    scrollable = True

    #---------------------------------------------------------------------------
    #  Finishes initializing the editor by creating the underlying toolkit
    #  widget:
    #---------------------------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Make sure the model we'll be editing exists:
        object = self.object
        model  = getattr( object, '_hidden_model', None )
        if model is None:
            object._hidden_model = model = NumericObjectModel( object )

        # Get the list of traits to plot:
        factory = self.factory
        type    = factory.type
        index   = factory.index
        names   = factory.names
        if len( names ) == 0:
            names = [ name for name in object.trait_names()
                      if object.base_trait( name ).array ]

        idx = getattr( object, index, None )
        if idx is None:
            plot_index = PlotValue( arange( 0.0, len( model.model_indices ) ) )
            selection_index = None
        else:
            plot_index      = PlotValue( ModelData( model = model ).set(
                                                    name  = index ) )
            selection_index = PlotValue( SelectionData( model = model ).set(
                                                        name  = index ) )
        canvas = PlotCanvas( plot_type = factory.type,
                             bg_color  = BGColor )
        canvas.axis_index = PlotAxis()
        if idx is not None:
            canvas.axis_index.title = index
        if len( names ) == 1:
            canvas.axis = PlotAxis( title = names[0] )
        for name in names:
            canvas.add( PlotValue( ModelData( model = model ).set(
                                              name  = name ),
                                   index     = plot_index,
                                   plot_type = type,
                                   size      = 'small' ) )
            if selection_index is not None:
                plot_value = PlotValue( SelectionData( model = model ).set(
                                                       name  = name ),
                                        index      = selection_index,
                                        plot_type  = 'scatter',
                                        fill_color = 'red',
                                        size       = 'small' )
                canvas.add( plot_value )

        # Set up the interactive data filters:
        if selection_index is not None:
            canvas.interaction = ia = \
                NumericModelExplorerInteraction( value = plot_value )
            ia._filters = filters = []
            for name in names:
                sm = model.get_selection_model()
                sm.model_filter = PolygonFilter( x_value = index,
                                                 y_value = name )
                filters.append( sm.model_filter )

            ia.on_trait_change( self.interaction_complete, 'points' )

        self.control = Window( parent, component = PlotComponent(
                                                  component = canvas ) ).control

    #---------------------------------------------------------------------------
    #  Updates the selection filter when the canvas interaction is updated:
    #---------------------------------------------------------------------------

    def interaction_complete ( self, object, name, old, new ):
        """ Updates the selection filter when the canvas interaction is updated.
        """
        for filter in object._filters:
            filter.points = object.points

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes external to the
            editor.
        """
        pass

#-------------------------------------------------------------------------------
#  '_PlotEditorFactory' class:
#-------------------------------------------------------------------------------

class _PlotEditorFactory ( BasicEditorFactory ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Override of the editor class to construct:
    klass = _PlotEditor

    # Name of trait containing the plot index:
    index = Str

    # List of trait names to plot:
    names = List( Str )

    # The type of plot to produce:
    type = Enum( 'line', 'scatter' )

