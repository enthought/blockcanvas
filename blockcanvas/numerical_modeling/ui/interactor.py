#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import traitsui.menu as menu

from cPickle \
    import load, dump

from numpy \
    import arange, ndarray

from blockcanvas.numerical_modeling.workflow.api \
    import Block

from blockcanvas.numerical_modeling.numeric_context.api \
    import NumericContext

from traits.api \
    import HasTraits, HasPrivateTraits, Float, Int, Any, Str, Enum, Dict, \
        List, Event, Bool

from traitsui.api \
    import TextEditor, View, HGroup, Item, ViewHandler

from traitsui.menu \
    import Action

from traitsui.instance_choice \
    import InstanceFactoryChoice

from pyface.api import GUI

from enthought.util.distribution.api \
    import Distribution, Constant, Gaussian, Triangular, Uniform

from types \
    import IntType, FloatType

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Valid block input types:
ValidTypes = ( ndarray, IntType, FloatType, Distribution )

#-------------------------------------------------------------------------------
#  Returns a float which is the result of evaluating a specified string:
#-------------------------------------------------------------------------------

def float_eval ( str ):
    try:
        return float( eval( str ) )
    except:
        return 0.0

float_eval_editor = TextEditor( evaluate  = float_eval,
                                auto_set  = False,
                                enter_set = True )

#-------------------------------------------------------------------------------
#  Returns an integer which is the result of evaluating a specified string:
#-------------------------------------------------------------------------------

def int_eval ( str ):
    try:
        return int( eval( str ) )
    except:
        return 0

int_eval_editor = TextEditor( evaluate  = int_eval,
                              auto_set  = False,
                              enter_set = True )

#-------------------------------------------------------------------------------
#  'ArangeGenerator' class:
#-------------------------------------------------------------------------------

class ArangeGenerator ( HasPrivateTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The lower end of the array range:
    lower = Float( -1.0, event = 'generate' )

    # The upper end of the array range:
    upper = Float( 1.0, event = 'generate' )

    # The number of points in the array range:
    points = Int( 201, event = 'generate' )

    # The current array range:
    array = Any( arange( -1.0, 1.005, 0.01 ) )

    # The context value this object is associated with:
    name = Str

    #---------------------------------------------------------------------------
    #  Trait view definitions:
    #---------------------------------------------------------------------------

    view = View(
        HGroup(
            Item( 'lower',  width = -60, editor = float_eval_editor ),
            Item( 'upper',  width = -60, editor = float_eval_editor ),
            Item( 'points', width = -40, editor = int_eval_editor )
        )
    )

    #-- Event Handlers ---------------------------------------------------------

    def _generate_changed ( self ):
        delta = (self.upper - self.lower)
        if (delta > 0) and (2 <= self.points <= 100000):
            delta /= (self.points - 1)
            self.array = arange( self.lower, self.upper + (delta / 2.0), delta )

#-------------------------------------------------------------------------------
#  'InteractorEditor' class:
#-------------------------------------------------------------------------------

class InteractorEditor ( HasTraits ):

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # The label for the trait:
    label = Str

    # Should a range editor be used (or a text editor)?
    type = Enum( 'Range', 'Number', 'Array', 'Distribution')

    # Low bound of range:
    low = Float

    # High bound of range:
    high = Float

    #---------------------------------------------------------------------------
    #  Trait view definitions:
    #---------------------------------------------------------------------------

    view = View(
        Item( 'label' ),
        Item( 'type' ),
        '_',
        Item( 'low',  enabled_when = 'type=="Range"' ),
        Item( 'high', enabled_when = 'type=="Range"' ),
        buttons = [ 'OK', 'Cancel' ],
        kind    = 'livemodal'
    )

#-------------------------------------------------------------------------------
#  'InteractorHandler' class:
#-------------------------------------------------------------------------------

class InteractorHandler ( ViewHandler ):

#-- Event Handlers -------------------------------------------------------------

    def object_block_changed ( self, info ):
        if info.initialized and (not self._no_update):
            self._no_update = True
            view    = info.ui.view
            content = info.object.view_items()
            items   = self._items
            for i, item in enumerate( content ):
                if item.name in items:
                    content[i] = items[ item.name ]
            view.set_content( Group( *content ) )
            self._get_items( info )
            for name, item in self._items.items():
                if item._type == 'Array':
                    setattr( info.object, name, ArangeGenerator( name = name ) )
            view.updated    = True
            self._no_update = False

    def object_id_changed ( self, info ):
        if info.initialized and (not self._no_update):
            self._items = []
            id = info.object.id
            if (id != '') and ((id[:5] != '<new ') or (id[-1] != ']')):
                self._load_view( info )

    def on_right_up ( self, info, item, event ):
        if (item is not None) and (item._type is not None):
            low, high = 0.0, 1.0
            if item._type == 'Range':
                low, high = item.editor.low, item.editor.high
            re = InteractorEditor( label = item.label or item.name[4:],
                                   type  = item._type,
                                   low   = low,
                                   high  = high )
            if re.edit_traits().result:
                cur_value  = getattr( info.object, item.name, 0.0 )
                item.label = re.label
                item._type = re.type
                item.style = 'simple'
                if re.type == 'Range':
                    if re.low == re.high:
                        re.high = re.low + 1.0
                    item.editor = RangeEditor( low  = min( re.low, re.high ),
                                               high = max( re.low, re.high ) )
                    if not isinstance( cur_value, float ):
                        setattr( info.object, item.name, item.editor.low )
                elif re.type == 'Array':
                    item.set( editor = InstanceEditor(), style = 'custom' )
                    if not isinstance( cur_value, ArangeGenerator ):
                        setattr( info.object, item.name,
                                 ArangeGenerator( name = item.name ) )
                else:
                    item.editor = float_eval_editor
                    if not isinstance( cur_value, float ):
                        setattr( info.object, item.name, 0.0 )
                self._no_update      = True
                info.ui.view.updated = True
                self._no_update      = False
                self._get_items( info )
                id = info.object.id
                if (id != '') and ((id[:5] != '<new ') or (id[-1] != ']')):
                    self._save_view( info )

#-- Private Methods ------------------------------------------------------------

    def _save_view ( self, info ):
        """ Tries to persist the contents of the view.
        """
        fh = None
        try:
            fh = open( self._view_file( info ), 'wb' )
            dump( info.ui.view.content.content[0], fh, -1 )
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
            info.ui.view.set_content( load( fh ) )
            self._get_items( info )
        except:
            pass
        if fh is not None:
            fh.close()

    def _view_file ( self, info ):
        """ Returns the persisted file name associated with the view.
        """
        return info.object.id + '.view'

    def _get_items ( self, info ):
        """ Saves the current set of View Items.
        """
        self._items = dict( [ ( item.name, item )
                         for item in info.ui.view.content.content[0].content ] )

#-------------------------------------------------------------------------------
#  'Interactor' class:
#-------------------------------------------------------------------------------

class Interactor ( HasPrivateTraits ):
    'Interacts with a computational model'

    #---------------------------------------------------------------------------
    #  Interactor interface:
    #---------------------------------------------------------------------------

    # The persistence id associated with this interactor (empty string means
    # no persistence):
    id = Str

    # Whole block
    block = Any( Block( '' ) )

    # Namespace in which block executes
    context = Any( {} )

    # A dict to hold high and how bounds.  Should be of the form {'input_var' : (low, high, format)}
    ranges = Dict

    # Subset of the block's inputs to display
    display_inputs = List(Str)

    # When block or context change
    _updated = Event

    # Cached restricted blocks that need to execute when an input is changed
    # (one for each of block.inputs)
    _blocks = Dict

    # List of actual inputs:
    _block_inputs = List

    # Does the interactor need to run any updates?
    _needs_update = Bool(False)

    #---------------------------------------------------------------------------
    #  Interactor interface:
    #---------------------------------------------------------------------------

    def view_items ( self ):
        """ Returns the contents of the view based upon the current block.
        """
        visible_inputs = self._block_inputs
        if visible_inputs is None:
            return []

        # Only display requested inputs (if requested at all)
        if self.display_inputs != []:
            visible_inputs = set( visible_inputs ) & set( self.display_inputs )

        items = []
        for input in visible_inputs:
            if input != 'clear':
                if self.ranges.has_key( input ):
                    low, high, format = self.ranges[ input ]
                    range = RangeEditor(high = high, low = low, format = format)
                else:
                    range = RangeEditor()
                items.append( Item( name   = 'var_' + input,
                                    label  = input,
                                    _type  = 'Range',
                                    editor = range ) )
        return items

    #-- Trait Listeners --------------------------------------------------------

    def _block_changed ( self, old, new ):

        # Get the old and new inputs:
        old_inputs = new_inputs = []
        if old is not None:
            old_inputs = old.inputs
        if new is not None:
            new_inputs = new.inputs

        # Filter out inputs already bound to arrays in the current context:
        context = self.context
        if context is not None:
            new_inputs = [ input for input in new_inputs
                           if not isinstance( context.get( input ), ndarray ) ]

        # Save the list of actual inputs:
        self._block_inputs = new_inputs

        # Update the trait definitions as needed:
        [ self.remove_trait( 'var_' + input ) for input in old_inputs
                                              if input not in new_inputs ]
        [ self.add_trait( 'var_' + input, Any ) for input in new_inputs
                                              if input not in old_inputs ]

        # Cache restricted blocks, one for each input:
        self._blocks = dict( [ ( input, new.restrict( inputs = [ input ] ) )
                               for input in new_inputs ] )

        self._updated = True

    def _context_changed ( self, old, new ):
        self._updated = True

    def _anytrait_changed ( self, name, old, new ):
        if name[:4] == 'var_':
            name = name[4:]
            if (not self._no_block_update) and (self.block is not None):
                if isinstance( old, ArangeGenerator ):
                    old.on_trait_change( self._array_changed, 'array',
                                         remove = True )
                if isinstance( new, ArangeGenerator ):
                    new.on_trait_change( self._array_changed, 'array' )
                    new = new.array
                self.context[ name ] = new
                self._needs_update = True
                #print "Adding update func"
                def update_func():
                    if self._needs_update:
                        self._blocks[ name ].execute( self.context )
                        self._needs_update = False
                GUI.invoke_after(10, update_func)
#                try:
#                    self._blocks[ name ].execute( self.context )
#                except:
#                    from traceback import print_exc
#                     print_exc()

    def _array_changed ( self, object, name, old, new ):
        name = object.name[4:]
        self.context[ name ] = new
        try:
            self._blocks[ name ].execute( self.context )
        except:
            pass

    #-- Event Interface --------------------------------------------------------

    def __updated_fired ( self ):
        'When block or context change'

        # The block or context changed, so put them back in sync:
        #  - Run the whole block once to initialize the intermediate variables
        #    within the context

        # Be robust when block and context disagree:
        block, context = self.block, self.context
        if (block is not None) and (context is not None):

            ## Calculate the list of 'real' block inputs:
            #self._block_inputs = [
            #    input for input in block.inputs
            #          if isinstance( context.get( input, 0 ), ValidTypes )
            #]

            self._no_block_update = True
            #for input in block.inputs:
            for input in self._block_inputs:
                var_input = 'var_' + input
                try:
                    value = context[ input ]
                    setattr( self, var_input, value )
                except:
                    context[ input ] = value = 0
                    setattr( self, var_input, value )
            self._no_block_update = False
            try:
                self.block.execute( context )
            except:
                pass

            # Remove unreferenced values from the data portion of the context:
            if 'clear' in block.inputs:
                 try:
                     names = context.keys()
                     all   = block.inputs + block.outputs
                     for name in names:
                         if name not in all:
                             del context[ name ]
                 except:
                     pass

    #-- HasTraits Interface ----------------------------------------------------

    def trait_view ( self, name = None, view_element = None ):
        'Returns the View object for the specified name and view_element.'

        return View(
            Group( *self.view_items() ),
            id        ='blockcanvas.numerical_modeling.ui.interactor.Interactor',
            title     = 'Parametric Controls',
            width     = 400,
            height    = 200,
            buttons   = menu.NoButtons,
            resizable = True,
            handler   = InteractorHandler
        )


#-------------------------------------------------------------------------------
#  'StochasticInteractorHandler' class:
#-------------------------------------------------------------------------------

class StochasticInteractorHandler ( InteractorHandler ):

    def execute_stochastic(self, info):
        interactor = info.ui.context["object"]

        context = interactor.context
        block = interactor.block
        machines = interactor.slaves


        if len(machines) == 0:
            import socket
            host = socket.gethostname()
            machines = [(host, 10001), (host, 10002)]

        from geo.cow import cow # FIXME
        c = cow.machine_cluster(machines)
        c.start()

        inputs = {}
        for input in interactor.desired_inputs.keys():
            inputs[input] = getattr(interactor, 'var_' + input)
            if isinstance(inputs[input], Distribution):
                #resize the distributions to ensure there are enough points
                inputs[input].samples = interactor.realizations_per_host

        from blockcanvas.numerical_modeling.workflow.study.stochastic import \
            run_block
        results = c.loop_apply(run_block.run_stocastic_block,
                               0,
                               (range(len(machines)),
                                    block, NumericContext(),
                                    interactor.realizations_per_host,
                                    inputs,
                                    interactor.desired_outputs))

        c.stop()

        for output in interactor.desired_outputs:
            temp = []
            for result in results:
                temp += result[output]
            interactor.results_context[output] = temp

        # seeds are special outputs always returned. It is a map of the seeds
        # for all inputs which are instances of Distribution
        interactor.results_context['_seeds'] = {}
        for input in interactor.desired_inputs:
            if isinstance(inputs[input], Distribution):
                interactor.results_context['_seeds'][input] = []
                for result in results:
                    interactor.results_context['_seeds'][input].append(result['_seeds'][input])

        self._updated = True

#-------------------------------------------------------------------------------
#  'StochasticInteractor' class:
#-------------------------------------------------------------------------------

distribution_classes = [
    InstanceFactoryChoice(klass = Constant,
                          name  = 'Constant',
                          view  = 'view' ),
    InstanceFactoryChoice(klass = Gaussian,
                          name  = 'Gaussian',
                          view  = 'view' ),
    InstanceFactoryChoice(klass = Triangular,
                          name  = 'Triangular',
                          view  = 'view' ),
    InstanceFactoryChoice(klass = Uniform,
                          name  = 'Uniform',
                          view  = 'view' ),
]

class StochasticInteractor(Interactor):

    results_context = Any( {} )

    desired_inputs = Any( {} )
    desired_outputs = Any( [] )

    realizations_per_host = Int(10)

    slaves = Any( [] )

    def view_items ( self ):
        """ Returns the contents of the view based upon the current block.
        """
        block_inputs = self._block_inputs
        if block_inputs is None:
            return []

        items = []

        for input,value in self.desired_inputs.items():
            item = None
            if isinstance(value, Distribution):
                item = Item(name      = 'var_' + input,
                            label     = input,
                            _type     = 'Distribution',
                            editor    = InstanceEditor(values=distribution_classes),
                            style     = 'custom')
            elif isinstance(value, ndarray):
                item = Item(name      = 'var_' + input,
                            label     = input,
                            _type     = 'Array',
                            editor    = InstanceEditor(),
                            style     = 'custom')
            elif isinstance(value, IntType):
                item = Item(name      = 'var_' + input,
                            label     = input,
                            _type     = 'Range',
                            editor    = int_eval_editor)
            elif isinstance(value, FloatType):
                item = Item(name      = 'var_' + input,
                            label     = input,
                            _type     = 'Range',
                            editor    = float_eval_editor)
            else:
                item = Item(name      = 'var_' + input,
                            label     = input,
                            _type     = 'Range')


            items.append(item)

        return items

    def __updated_fired ( self ):
        'When block or context change'

        # The block or context changed, so put them back in sync:
        #  - Run the whole block once to initialize the intermediate variables
        #    within the context

        # Be robust when block and context disagree:
        block, context = self.block, self.context
        if (block is None) or (context is  None):
            return

        for input in block.inputs:
            if context.has_key(input):
                self.desired_inputs[input] = context[input]

        for output in block.outputs:
            if context.has_key(output):
                self.desired_outputs.append(output)

        # hook up the UI inputs
        self._block_inputs = self.desired_inputs.values()

        self._no_block_update = True
        for input in block.inputs:
            var_input = 'var_' + input
            try:
                value = context[ input ]
                setattr( self, var_input, value )
            except:
                context[ input ] = value = Gaussian()
                setattr( self, var_input, value )
        self._no_block_update = False
        try:
            self.block.execute( context )
        except:
            pass

        # Remove unreferenced values from the data portion of the context:
        if 'clear' in block.inputs:
             try:
                 names = context.keys()
                 all   = block.inputs + block.outputs
                 for name in names:
                     if name not in all:
                         del context[ name ]
             except:
                 pass

    #-- HasTraits Interface ----------------------------------------------------

    def trait_view ( self, name = None, view_element = None ):
        'Returns the View object for the specified name and view_element.'

        return View(
            Group( *self.view_items() ),
            id        ='blockcanvas.numerical_modeling.ui.interactor.StocasticInteractor',
            width     = 250,
            height    = 500,
            buttons   = [Action(name="Execute", action="execute_stochastic")],
            resizable = True,
            handler   = StochasticInteractorHandler
        )
