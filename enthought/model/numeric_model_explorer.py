#-------------------------------------------------------------------------------
#
#  Data Explorer: A tool for displaying, manipulating and visualizing sets of
#                 numbers
#
#  Written by: David C. Morrill
#
#  Date: 12/03/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from numpy import arange, array, compress, cos, sin, transpose

from enthought.enable.traits.api import RGBAColor

from enthought.traits.api \
    import HasPrivateTraits, Array, Instance, List, Str, Enum, \
           Tuple, Button, Event, Property

from enthought.traits.ui.api \
    import View, Item, HSplit, VSplit, HGroup, VGroup, Tabbed, SetEditor, \
           ListEditor, InstanceEditor, TableEditor, CustomEditor, Handler

from enthought.traits.ui.menu \
    import NoButtons

from enthought.traits.ui.table_column \
    import NumericColumn, ObjectColumn

from enthought.model.traits.ui.wx.numeric_editor \
    import ToolkitEditorFactory as NumericEditor

from enthought.model.api \
    import ANumericModel, NumericArrayModel, ReductionModel, SelectionModel, \
           SelectionReductionModel, NumericItem, ExpressionFilter, \
           IndexFilter, PolygonFilter

from enthought.pyface.timer.api \
    import do_later

from enthought.chaco.plot_canvas \
    import PlotCanvas

from enthought.chaco.plot_value \
    import PlotValue

from enthought.chaco.plot_group \
    import PlotGroup

from enthought.chaco.plot_overlay \
    import PlotOverlay

from enthought.chaco.plot_axis \
    import PlotAxis

from enthought.chaco.plot_component \
    import PlotComponent

from enthought.chaco.plot_data \
    import PlotData

from enthought.chaco.plot_interaction \
    import PlotInteraction

from enthought.enable.wx \
    import Window

from enthought.kiva \
    import STROKE



#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Transparent color:
transparent = ( 0.0, 0.0, 0.0, 0.0 )

#-------------------------------------------------------------------------------
#  'NumericModelExplorerInteraction' class:
#-------------------------------------------------------------------------------

class NumericModelExplorerInteraction ( PlotInteraction ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # PlotValue to use for screen to data mapping:
    value = Instance( PlotValue )

    # The final polygon points in data space:
    points = List

    # Current set of polygon points:
    polygon = List

    #---------------------------------------------------------------------------
    #  Converts the current polygon into a data-space selection:
    #---------------------------------------------------------------------------

    def set_selection ( self, polygon = None ):
        """ Converts the current polygon into a data-space selection.
        """
        if polygon is not None:
            self.polygon = polygon
        map_xy      = self.value.map_xy
        self.points = [ [ map_xy( x, y )[0:2] for x, y in items ]
                        for items in self.polygon ]

    #---------------------------------------------------------------------------
    #  'Component' interface:
    #---------------------------------------------------------------------------

    def normal_left_down ( self, event ):
        if event.control_down:
            self.polygon.append( [ ( event.x, event.y ) ] )
        else:
            self.polygon = [ [ ( event.x, event.y ) ] ]
        self.event_state        = 'drawing'
        self.window.mouse_owner = self
        self.redraw()

    def drawing_mouse_move ( self, event ):
        self.polygon[-1].append( ( event.x, event.y ) )
        self.redraw()

    def drawing_left_up ( self, event ):
        self.window.mouse_owner = None
        self.event_state        = 'normal'
        self.polygon[-1].append( self.polygon[-1][0] )
        self.set_selection()
        self.redraw()

    #---------------------------------------------------------------------------
    #  Handle the bounds of the component being changed:
    #---------------------------------------------------------------------------

    def _bounds_changed ( self, old, new ):
        """ Handle the bounds of the component being changed.
        """
        super( NumericModelExplorerInteraction, self )._bounds_changed( old,
                                                                        new )

        if len( self.polygon ) > 0:
            ox, oy, odx, ody = old
            nx, ny, ndx, ndy = new
            sx = float( ndx ) / float( odx )
            sy = float( ndy ) / float( ody )
            self.polygon = [ [ ( nx + ((x - ox) * sx), ny + ((y - oy) * sy) )
                             for x, y in items ] for items in self.polygon ]

    #---------------------------------------------------------------------------
    #  Draws the interactor:
    #---------------------------------------------------------------------------

    def _old_draw ( self, gc ):
        """ Draws the interactor.
        """
        gc.save_state()
        gc.set_stroke_color( self.value.fill_color_ )
        gc.set_line_width( 2.0 )
        for items in self.polygon:
            if len( items ) > 1:
                gc.begin_path()
                gc.lines( items )
                gc.draw_path( STROKE )
        gc.restore_state()

    def _draw(self, gc):
        if self.event_state != "normal":
            self._old_draw(gc)
        elif self.points:
            gc.save_state()
            gc.set_stroke_color( self.value.fill_color_ )
            gc.set_line_width( 2.0 )
            if self.value._plot_bounds:
                gc.clip_to_rect(*self.value._plot_bounds)
            for items in self.points:
                if len( items ) > 1:
                    # Map the points from data space
                    items = transpose(array(items))
                    screenpts = self.value.map_screen(items[0], items[1], xy=True)
                    gc.begin_path()
                    gc.lines( screenpts )
                    gc.draw_path( STROKE )
            gc.restore_state()


#-------------------------------------------------------------------------------
#  Creates a data explorer plot:
#-------------------------------------------------------------------------------

def create_plot ( parent, editor ):
    """ Creates a data explorer plot.
    """
    try:
        nmep  = editor.object
        model = nmep.model
        items = nmep.plot_items
        if len( items ) == 0:
            return wx.Panel( parent, -1 )
        index = nmep.plot_index
        if index is None:
            plot_index = PlotValue( arange( 0.0, len( model.model_indices ) ) )
            selection_index = None
        else:
            plot_index      = PlotValue( ModelData( model = model,
                                                    name  = index.name ) )
            selection_index = PlotValue( SelectionData( model = model,
                                                        name  = index.name ) )
        canvas = PlotCanvas( plot_type     = items[0].plot_type,
                             plot_bg_color = items[0].canvas_color )
        canvas.axis_index = PlotAxis()
        if index is not None:
            canvas.axis_index.title = index.label
        if len( items ) == 1:
            canvas.axis = PlotAxis( title = items[0].label )
        else:
            canvas.add( PlotGroup(
                            overlay  = True,
                            position = 'top right',
                            *[ PlotOverlay( legend_color = item.line_color,
                                            text         = item.label,
                                            border_size  = 0,
                                            bg_color     = transparent,
                                            margin       = 0,
                                            padding      = 2 )
                               for item in items ] ) )
        for item in items:
            canvas.add( PlotValue( ModelData( model = model ).set(
                                              name  = item.name ),
                                   index         = plot_index,
                                   plot_type     = item.plot_type,
                                   line_weight   = item.line_weight,
                                   line_color    = item.line_color,
                                   fill_color    = item.fill_color,
                                   outline_color = item.outline_color,
                                   size          = 'small' ) )
            if selection_index is not None:
                plot_value = PlotValue( SelectionData( model = model ).set(
                                                       name  = item.name ),
                                        index      = selection_index,
                                        plot_type  = 'scatter',
                                        size       = item.selection_size,
                                        fill_color = item.selection_color )
                canvas.add( plot_value )

        # Set up the interactive data filters:
        if selection_index is not None:
            canvas.interaction = nmep._interaction = ia = \
                NumericModelExplorerInteraction( value = plot_value )
            nmep._selection_models = sms = []
            ia._filters = filters = []
            for item in items:
                sm = model.get_selection_model()
                sms.append( sm )
                sm.model_filter = PolygonFilter( x_value = index.name,
                                                 y_value = item.name )
                filters.append( sm.model_filter )

            ia.on_trait_change( editor.ui.handler.interaction_complete,
                                'points' )
            if len( nmep.polygon ) > 0:
                do_later( ia.set_selection, nmep.polygon )

        return Window( parent,
                       component = PlotComponent( component = canvas ) ).control
    except:
        import traceback
        traceback.print_exc()
        raise

#-------------------------------------------------------------------------------
#  'ModelData' class:
#-------------------------------------------------------------------------------

class ModelData ( PlotData ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The model data is being obtained from:
    model = Instance( ANumericModel )

    # The model item the data is being obtained from:
    name = Str

    # Event fired when the data is modified:
    modified = Event( event = 'update' )

    #---------------------------------------------------------------------------
    #  Returns the model data to be plotted:
    #---------------------------------------------------------------------------

    def data ( self, source_name ):
        return getattr( self.model, self.name )

    #---------------------------------------------------------------------------
    #  Handles the 'name' trait being changed:
    #---------------------------------------------------------------------------

    def _name_changed ( self ):
        self.model.on_trait_change( self._data_updated, 'model_updated' )

    #---------------------------------------------------------------------------
    #  Handles the model data being changed:
    #---------------------------------------------------------------------------

    def _data_updated ( self ):
        self.modified = True

#-------------------------------------------------------------------------------
#  'SelectionData' class:
#-------------------------------------------------------------------------------

class SelectionData ( ModelData ):

    #---------------------------------------------------------------------------
    #  Returns the model selection data to be plotted:
    #---------------------------------------------------------------------------

    def data ( self, source_name ):
        """ Returns the model selection data to be plotted.
        """
        mask = self.model.model_selection
        if mask is None:
            return array( [] )

        return compress( mask, getattr( self.model, self.name ), axis = 0 )

#-------------------------------------------------------------------------------
#  'DataItem' class:
#-------------------------------------------------------------------------------

class DataItem ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The name of the model trait supplying the data:
    name = Str

    # The label of the data item:
    label = Property

    # The type of plot to be created:
    plot_type = Enum( 'line', 'scatter', 'stackedline', 'stackedbar' )

    # The weight of the plot:
    line_weight = Enum( 2, ( 1, 2, 3, 4, 5, 6, 7, 8, 9 ) )

    # The color of the plot:
    line_color = RGBAColor( 'blue' )

    # The fill color of the plot:
    fill_color = RGBAColor( 'yellow' )

    # The outline color of the plot:
    outline_color = RGBAColor( 'black' )

    # The color of the selection:
    selection_color = RGBAColor( 'red' )

    # The size of the selection markers:
    selection_size = Enum( 'small', ( 'tiny', 'small', 'medium' ,'large' ) )

    # The color of the plot canvas:
    canvas_color = RGBAColor( 'white' )

    #---------------------------------------------------------------------------
    #  Implementation of the 'label' property:
    #---------------------------------------------------------------------------

    def _get_label ( self ):
        if self._label:
            return self._label
        return self.name

    def _set_label ( self, label ):
        self._label = label

    #---------------------------------------------------------------------------
    #  Returns the string value of the object:
    #---------------------------------------------------------------------------

    def __str__ ( self ):
        """ Returns the string value of the object.
        """
        return self.name

#-------------------------------------------------------------------------------
#  'NumericModelExplorerPlotHandler' class:
#-------------------------------------------------------------------------------

class NumericModelExplorerPlotHandler ( Handler ):

    #---------------------------------------------------------------------------
    #  Handles a dialog-based user interface being closed by the user:
    #---------------------------------------------------------------------------

    def closed ( self, info, is_ok ):
        """ Handles a dialog-based user interface being closed by the user.
        """
        nmep  = info.object
        model = nmep.model
        nmep.polygon = nmep._interaction.polygon[:]
        for selection_model in nmep._selection_models:
            model.remove_model( selection_model )

    #---------------------------------------------------------------------------
    #  Updates the selection filter when the canvas interaction is updated:
    #---------------------------------------------------------------------------

    def interaction_complete ( self, object, name, old, new ):
        """ Updates the selection filter when the canvas interaction is updated.
        """
        for filter in object._filters:
            filter.points = object.points

#-------------------------------------------------------------------------------
#  'NumericModelExplorerPlot' class:
#-------------------------------------------------------------------------------

class NumericModelExplorerPlot ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The model containing the data to be plotted:
    model = Instance( ANumericModel )

    # The list of items to plot:
    plot_items = List( DataItem )

    # The model item to use as the plot index:
    plot_index = Instance( DataItem, allow_none = True )

    # The name of the plot:
    plot_name = Str

    # The page name of the plot:
    page_name = Property

    # The current points in the selection:
    polygon = List

    #---------------------------------------------------------------------------
    #  Traits view definition:
    #---------------------------------------------------------------------------

    view = View( [ Item( 'plot_name',
                         resizable = True,
                         editor    = CustomEditor( create_plot ) ),
                   '|<>' ],
                 handler = NumericModelExplorerPlotHandler() )

    #---------------------------------------------------------------------------
    #  Implementation of the 'page_name' property:
    #---------------------------------------------------------------------------

    def _get_page_name ( self ):
        page_name = self.plot_name.strip()
        if page_name == '':
            index = self.plot_index
            if index is not None:
                page_name = index.label + ': '
            page_name += ', '.join( [ item.label for item in self.plot_items ] )
            if page_name == '':
                page_name = 'Plot'
        return page_name

#-------------------------------------------------------------------------------
#  'ColorColumn' class:
#-------------------------------------------------------------------------------

class ColorColumn ( ObjectColumn ):

    #---------------------------------------------------------------------------
    #  Gets the value of the column for a specified object:
    #---------------------------------------------------------------------------

    def get_value ( self, object ):
        """ Gets the value of the column for a specified object.
        """
        return ''

    #---------------------------------------------------------------------------
    #  Returns the cell background color for the column for a specified object:
    #---------------------------------------------------------------------------

    def get_cell_color ( self, object ):
        """ Returns the cell background color for the column for a specified
            object.
        """
        r, g, b, a = getattr( object, self.name + '_' )
        return wx.Colour( int( 255 * r ), int( 255 * g ), int( 255 * b ) )

#-------------------------------------------------------------------------------
#  'CustomColumn' class:
#-------------------------------------------------------------------------------

class CustomColumn ( ObjectColumn ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Override default column horizontal alignment:
    horizontal_alignment = 'center'

#-------------------------------------------------------------------------------
#  NumericModelExplorer 'plot_items' table editor:
#-------------------------------------------------------------------------------

plot_items_table_editor = TableEditor(
    editable = True,
    columns  = [ CustomColumn( name     = 'name',
                               editable = False ),
                 CustomColumn( name     = 'label' ),
                 CustomColumn( name     = 'plot_type' ),
                 CustomColumn( name     = 'line_weight' ),
                 ColorColumn(  name     = 'line_color' ),
                 ColorColumn(  name     = 'fill_color' ),
                 ColorColumn(  name     = 'outline_color' ),
                 ColorColumn(  name     = 'canvas_color' ),
                 ColorColumn(  name     = 'selection_color' ),
                 CustomColumn( name     = 'selection_size' ),
               ]
)

#-------------------------------------------------------------------------------
#  'NumericModelExplorer' class:
#-------------------------------------------------------------------------------

class NumericModelExplorer ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Title of the view:
    title = Str( 'Numeric Model Explorer' )

    # Default format for columns:
    format = Str( '%.3f' )

    # The model containing the data being explored:
    model = Instance( ANumericModel )

    # The model containing only the currently selected items:
    selection_model = Instance( ANumericModel )

    # The list of model items available for plotting:
    values = List( DataItem )

    # The list of model items to be plotted:
    plot_items = List( DataItem )

    # The model item to use as the plot index:
    plot_index = Instance( DataItem )

    # The name of the plot to be create when the 'Plot' button is pressed:
    plot_name = Str

    # The button used to create new plots:
    plot = Button( 'Plot' )

    # The list of plots that have been created:
    plots = List( NumericModelExplorerPlot )

    #---------------------------------------------------------------------------
    #  Handles  the 'model' trait being changed:
    #---------------------------------------------------------------------------

    def _model_changed ( self, old, new ):
        """ Handles  the 'model' trait being changed.
        """
        if old is not None:
            old.on_trait_change( self._update_values, 'model_added',
                                 remove = True )

        if new is not None:
            new.on_trait_change( self._update_values, 'model_added' )
            self._update_values()
            self.selection_model = SelectionReductionModel( new )

    #---------------------------------------------------------------------------
    #  Handles the 'plot' button being clicked:
    #---------------------------------------------------------------------------

    def _plot_changed ( self ):
        """ Handles the 'plot' button being clicked.
        """
        if len( self.plot_items ) > 0:
            self.plots.append(
                NumericModelExplorerPlot( model      = self.model,
                                          plot_items = self.plot_items[:],
                                          plot_index = self.plot_index,
                                          plot_name  = self.plot_name ) )

    #---------------------------------------------------------------------------
    #  Updates the list of available items to be plotted:
    #---------------------------------------------------------------------------

    def _update_values ( self ):
        """ Updates the list of available items to be plotted.
        """
        values = self.values
        new    = []
        for item in self.model.model_items:
            name = item.name
            for value in values:
                if name == value.name:
                    break
            else:
                new.append( DataItem( name = name ) )
        values.extend( new )

    #---------------------------------------------------------------------------
    #  Creates the view of the data explorer:
    #---------------------------------------------------------------------------

    def trait_view ( self, name = None, view_element = None ):
        """ Creates the view of the data explorer.
        """
        columns = ([ NumericColumn( name  = 'model_indices',
                                    label = 'i' ) ] +
                   [ NumericColumn( name = item.name, format = self.format )
                     for item in self.model.model_items ])

        number_editor = NumericEditor(
            columns               = columns,
            edit_selection_colors = False,
            user_selection_filter = IndexFilter(),
            deletable             = True,
            sortable              = True,
            auto_size             = False
        )

        selection_editor = NumericEditor(
            columns                 = columns,
            extendable              = False,
            choose_selection_filter = False,
            edit_selection_filter   = False,
            #user_selection_filter   = IndexFilter(),
            choose_reduction_filter = False,
            edit_reduction_filter   = False,
            deletable               = False,
            sortable                = False,
            auto_size               = False
        )

        return View(
            VSplit(
                HSplit(
                    Tabbed(
                        Item( 'model',
                              editor = number_editor ),
                        Item( 'selection_model{Selection}',
                              editor = selection_editor ),
                        label       = 'Model',
                        export      = 'DockShellWindow',
                        show_labels = False
                    ),
                    Item( 'plots@',
                          width  = 300,
                          height = 300,
                          editor = ListEditor(
                              use_notebook = True,
                              deletable    = True,
                              dock_style   = 'tab',
                              export       = 'DockShellWindow',
                              view         = 'view',
                              page_name    = '.page_name' ),
                          label      = 'Plots',
                          show_label = False,
                          export     = 'DockShellWindow'
                    ),
                ),
                HSplit(
                    VGroup(
                        VGroup(
                            Item( 'plot_items{}',
                                  editor = SetEditor(
                                     name               = 'values',
                                     can_move_all       = False,
                                     left_column_title  = 'Available values:',
                                     right_column_title = 'Values to plot:' ) ),
                            '_',
                            VGroup(
                                Item( 'plot_index',
                                   editor = InstanceEditor(
                                                name     = 'values',
                                                editable = False ) ),
                                HGroup( 'plot_name<134>', 'plot{}' )
                            )
                        ),
                        label  = 'Plot items',
                        export = 'DockShellWindow'
                    ),
                    Item( 'plot_items',
                          width      = 300,
                          height     = 150,
                          editor     = plot_items_table_editor,
                          label      = 'Plot properties',
                          show_label = False,
                          export     = 'DockShellWindow'
                    )
                ),
                id = 'splitter'
            ),
            title     = self.title,
            id        = 'enthought.model.numeric_model_explorer',
            dock      = 'horizontal',
            width     = 0.4,
            height    = 0.5,
            resizable = True,
            buttons   = NoButtons
        )

#-------------------------------------------------------------------------------
#  Run the test:
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    x     = arange( -20.0, 20.005, 0.1 )
    model = NumericArrayModel( x = x, sinx = sin( x ), cosx = cos( x ),
                               xsinx = x * sin( x ), xcosx = x * cos( x ) )
    NumericModelExplorer( model = model ).configure_traits()

