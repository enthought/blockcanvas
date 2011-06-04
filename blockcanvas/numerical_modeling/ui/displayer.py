import enthought.traits.ui.menu as menu

from enthought.numerical_modeling.numeric_context.api \
    import ANumericContext

from enthought.numerical_modeling.workflow.api \
    import Block

from enthought.traits.api \
    import *

from enthought.traits.ui.api \
    import *

#-------------------------------------------------------------------------------
#  'DisplayerEditor' class:
#-------------------------------------------------------------------------------

class DisplayerEditor ( HasTraits ):

    # The label for the trait:
    label = Str

    # Should a range editor be used (or a text editor)?
    is_range = Bool

    # Low bound of range:
    low = Float

    # High bound of range:
    high = Float

    view = View(
        Item( 'label' ),
        Item( 'is_range' ),
        '_',
        Item( 'low',  enabled_when = 'is_range' ),
        Item( 'high', enabled_when = 'is_range' ),
        buttons = [ 'OK', 'Cancel' ],
        kind    = 'livemodal'
    )

#-------------------------------------------------------------------------------
#  'DisplayerHandler' class:
#-------------------------------------------------------------------------------

class DisplayerHandler( ViewHandler ):

#-- Event Handlers -------------------------------------------------------------

    def object_block_changed ( self, info ):
        if info.initialized and (not self._no_update):
            self._no_update = True
            view = info.ui.view
            view.set_content( *info.object.view_items() )
            view.updated    = True
            self._no_update = False

    def object_id_changed ( self, info ):
        if info.object.id != '':
            self._load_view( info )

    def on_right_up ( self, info, item, event ):
        return
        if (item is not None) and (item._is_range is not None):
            low, high = 0.0, 1.0
            if item._is_range:
                low, high = item.editor.low, item.editor.high
            re = InteractorEditor( label    = item.label or item.name[4:],
                                   is_range = item._is_range,
                                   low      = low,
                                   high     = high )
            if re.edit_traits().result:
                item.label     = re.label
                item._is_range = re.is_range
                if re.is_range:
                    if re.low == re.high:
                        re.high = re.low + 1.0
                    item.editor = RangeEditor( low  = min( re.low, re.high ),
                                               high = max( re.low, re.high ) )
                else:
                    item.editor = TextEditor( evaluate = float )
                self._no_update      = True
                info.ui.view.updated = True
                self._no_update      = False
                if info.object.id != '':
                    self._save_view( info )

#-- Private Methods ------------------------------------------------------------

    def _save_view ( self, info ):
        """ Tries to persist the contents of the view.
        """
        fh = None
        try:
            fh = open ( self._view_file( info ), 'w' )
            dump( info.view.content, fh, -1 )
        except:
            pass
        if fh is not None:
            fh.close()

    def _load_view ( self, info ):
        """ Tries to reload a persisted version of the view.
        """
        fh = None
        try:
            fh = open( self._view_file( info ), 'rb' )
            info.view.set_content( load( fh ) )
            info.view.updated = True
        except:
            pass
        if fh is not None:
            fh.close()

    def _view_file ( self, info ):
        """ Returns the persisted file name associated with the view.
        """
        return info.object.id + '.view'

#-------------------------------------------------------------------------------
#  'Displayer' class:
#-------------------------------------------------------------------------------

class Displayer ( HasTraits ):
    """ Displays the results of a computational model.
    """

    #---------------------------------------------------------------------------
    #  Displayer interface:
    #---------------------------------------------------------------------------

    # The persistence id associated with this displayer (empty string means no
    # persistence):
    id = Str

    # The whole block:
    block = Any( Block( '' ) )

    # The namespace in which the block executes:
    context = Instance( ANumericContext )

    # Subset of the block's outputs to display
    display_outputs = List(Str)

    # Event fired when the block or context changes:
    _updated = Event

    #---------------------------------------------------------------------------
    #  Displayer interface:
    #---------------------------------------------------------------------------

    def view_items ( self ):
        """ Returns the contents of the view based upon the current block.
        """
        return [ Item( name   = 'var_' + output,
                       label  = output,
                       style  = 'readonly',
                       editor = TextEditor() )
                 for output in self.block.outputs
                 if output in self.display_outputs or
                    self.display_outputs == [] ]

    #-- Trait Event Handlers ---------------------------------------------------

    def _block_changed ( self, old, new ):
        # Remove the old outputs:
        if old is not None:
            [ self.remove_trait( 'var_' + output ) for output in old.outputs ]

        # Add the new inputs:
        if new is not None:
            [ self.add_trait( 'var_' + output, Any ) for output in new.outputs ]

        self._updated = True

    def _context_changed ( self, old, new ):
        self._updated = True

    def _context_modified_changed_for_context ( self, event ):
        if len( event.removed ) > 0:
            block = self.block
            if block is not None:
                context = self.context
                outputs = block.outputs
                for name in event.removed:
                    if name in outputs:
                        self._set_var( name, context[ name ] )

    #-- Event Interface --------------------------------------------------------

    def __updated_fired ( self ):
        """ Handles the 'block' or 'context' being changed.
        """

        # The block or context changed, so put them back in sync:
        #  - Run the whole block once to initialize the intermediate variables
        #    within the context.

        # Be robust when block and context disagree:
        block, context = self.block, self.context
        if (block is not None) and (context is not None):
            for output in block.outputs:
                try:
                    value = context[ output ]
                except:
                    context[ output ] = value = 0.0
                self._set_var( output, value )

    #-- Private Methods --------------------------------------------------------

    def _set_var ( self, name, value ):
        """ Set a 'legal' value for the specified output variable.
        """
        try:
            n = len( value )
        except:
            n = 0

        max_len = 10
        if isinstance( value, basestring ):
            max_len = 80

        if n > max_len:
            value = '%s[%d]' % ( value.__class__.__name__, n )

        setattr( self, 'var_' + name, value )

    #---------------------------------------------------------------------------
    #  HasTraits interface:
    #---------------------------------------------------------------------------

    def trait_view ( self, name = None, view_element = None ):
        return View(
            Group( *self.view_items() ),
            id        = 'enthought.numerical_modeling.ui.displayer.Displayer',
            width     = 250,
            buttons   = menu.NoButtons,
            resizable = True,
            handler   = DisplayerHandler
        )

