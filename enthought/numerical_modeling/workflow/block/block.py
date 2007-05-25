'Simple blocks of python code with dependency analysis.'

import compiler
from compiler.ast import Module, Node, Pass, Stmt
from compiler.visitor import ASTVisitor
from copy import copy
from cStringIO import StringIO

from enthought.traits.api import (Any, Bool, Default, Dict, Either, HasTraits,
                                  Instance, List, Property, Str, Trait)
from enthought.util.dict import map_keys, map_values
import enthought.util.graph as graph
from enthought.util.sequence import is_sequence

from enthought.numerical_modeling.workflow.block.analysis import NameFinder
from enthought.numerical_modeling.workflow.block.compiler_.api \
    import compile_ast, parse
from enthought.numerical_modeling.workflow.block.parser_ import BlockTransformer
from enthought.numerical_modeling.util.uuid import UUID, uuid4

###############################################################################
# TODO:
#  - Blocks should listen to changes in each sub-block
#  - Unify 'Block' and 'Expression'
#  - Should we be copying AST objects...?
#  - Decompose more than just Stmt's
#  - Expose functions that blocks use? (e.g. simply by name)
###############################################################################

class Block(HasTraits):
    'A block of code that can be inspected, manipulated, and executed.'

    __this = Instance('Block') # (traits.This scopes dynamically (#986))

    ###########################################################################
    # Block traits
    ###########################################################################

    ### Public traits ########################################################

    # Input and output parameters
    inputs = Instance(set)
    outputs = Instance(set)
    conditional_outputs = Instance(set)
    all_outputs = Property(Instance(set))
    _get_all_outputs = lambda self: self.outputs | self.conditional_outputs

    # The sequence of sub-blocks that make up this block, if any. If we don't
    # decompose into sub-blocks, 'sub_blocks' is None.
    #sub_blocks = Either(List(__this), None) # FIXME
    sub_blocks = Either(List(Any), None)

    # The AST that represents our behavior
    ast = Instance(Node)

    # The name of the file this block represents, if any. For blocks that
    # aren't files, the default value just shows repr(self). Annotates
    # tracebacks.
    filename = Instance(str) # (Default 'None', allow 'None')

    # A unique identifier
    uuid = Instance(UUID)
    _uuid_default = lambda self: uuid4()

    # Enabling this makes tracebacks less useful but speeds up Block.execute.
    # The problem is that a code object has a unique filename ('co_filename'),
    # so we can compile all of our sub-blocks' ASTs into a single code object
    # only if we ignore the fact that they might each come from different
    # files.
    no_filenames_in_tracebacks = Bool(False)

    ### Protected traits #####################################################

    # The dependency graph for 'sub_blocks', if they exist. If we don't
    # decompose into sub-blocks, '_dep_graph' is None. The '_dep_graph'
    # property uses '__dep_graph' as a cache, and '__dep_graph_is_valid =
    # False' invalidates the cache. ('__dep_graph = None' is valid, so we need
    # to track validity with another variable.)
    _dep_graph = Property(Either(Dict, None))
    __dep_graph = Either(Dict, None)
    __dep_graph_is_valid = Bool(False)

    # Compiled code for our AST. The '_code' property uses '__code' as a cache,
    # and '__code = None' invalidates the cache.
    _code = Property
    __code = Any

    # Flag to break call cycles when we update 'ast' and 'sub_blocks'
    _updating_structure = Bool(False)

    # A cache for block restrictions. Invalidates when structure changes.
    __restrictions = Dict

    ###########################################################################
    # object interface
    ###########################################################################

    def __init__(self, x=(), file=None, **kw):
        super(Block, self).__init__(**kw)

        # fixme: Why not use static handlers for this?
        self.on_trait_change(self._structure_changed, 'sub_blocks')
        self.on_trait_change(self._structure_changed, 'sub_blocks_items')
        self.on_trait_change(self._structure_changed, 'ast')

        # Interpret arguments:

        is_file_object = lambda o: hasattr(o, 'read') and hasattr(o, 'name')

        # 'file' -> 'x'
        if file is not None:
            # Turn 'file' into a file object and move to 'x'
            if isinstance(file, basestring):
                file = open(file)
            elif not is_file_object(file):
                raise ValueError("Expected 'file' to be a file or string, "
                                 "got %r" % f)
            x = file

        # 'x': file object -> string
        saved_filename = None
        if is_file_object(x):
            self.filename = x.name
            saved_filename = self.filename
            x = x.read()

        # 'x' -> 'self.ast' or 'self.sub_blocks'
        if isinstance(x, basestring):
            # (BlockTransformer handles things like 'import *')
            self.ast = parse(x, mode='exec', transformer=BlockTransformer())
            print self.ast
        elif isinstance(x, Node):
            self.ast = x
        elif is_sequence(x):
            self.sub_blocks = map(to_block, x)
        else:
            raise ValueError('Expecting string, Node, or sequence. Got %r' % x)

        # We really want to keep the filename for "pristine" blocks, and 
        # _structure_changed nukes it most times
        self.filename = saved_filename

    def __eq__(self, other):
        return type(self) == type(other) and self.uuid == other.uuid

    def __hash__(self):
        return hash((type(self), self.uuid))

    def __getstate__(self):

        # Evaluate attributes with non-deterministic default values to force
        # their initialization (see #1023)
        self.uuid

        return super(Block, self).__getstate__()

    def __repr__(self):
        return '%s(uuid=%s)' % (self.__class__.__name__, self.uuid)

    def __str__(self):
        return repr(self) # TODO Unparse ast (2.5) (cf. #1167)

    ###########################################################################
    # Block public interface
    ###########################################################################

    def execute(self, context):
        # To get tracebacks to show the right filename for any line in any
        # sub-block, we need each sub-block to compile its own '_code' since a
        # code object only keeps one filename. This is slow, so we give the
        # user the option 'no_filenames_in_tracebacks' to gain speed but lose
        # readability of tracebacks.
        if self.sub_blocks is None or self.no_filenames_in_tracebacks:
            if self.filename:
                context['__file__'] = self.filename
            exec self._code in {}, context
        else:
            for b in self.sub_blocks:
                b.execute(context)

    def restrict(self, inputs=(), outputs=()):
        ''' The minimal sub-block that computes 'outputs' from 'inputs'.

            Consider the block:

                x = expensive()
                x = 2
                y = f(x, a)
                z = g(x, a)
                w = h(a)

            This block has inputs 'a' (and 'f', 'g', 'h', and 'expensive'), and
            outputs 'x', 'y', 'z', and 'w'. If one is only interested in
            computing 'z', then lines 1, 3, and 5 can be omitted. Similarly, if
            one is only interested in propagating the effects of changing 'a',
            then lines 1 and 2 can be omitted. And if one only wants to
            recompute 'z' after changing 'a', then all but line 4 can be
            omitted.

            In this fashion, 'restrict' computes the minimal sub-block that
            computes 'outputs' from 'inputs'. See the tests in
            'block_test_case.BlockRestrictionTestCase' for concrete examples.

            Assumes 'inputs' and 'outputs' are subsets of 'self.inputs' and
            'self.outputs', respectively.
        '''

        inputs = set(inputs)
        outputs = set(outputs)

        # Look for results in the cache
        cache_key = (frozenset(inputs), frozenset(outputs))
        if cache_key in self.__restrictions:
            return self.__restrictions[cache_key]

        if not (inputs or outputs):
            raise ValueError('Must provide inputs or outputs')
        if not inputs.issubset(self.inputs):
            raise ValueError('Unknown inputs: %s' % (inputs - self.inputs))
        if not outputs.issubset(self.all_outputs):
            raise ValueError('Unknown outputs: %s' %(outputs-self.all_outputs))

        # If we don't decompose, then we are already as restricted as possible
        if self.sub_blocks is None:
            return self

        # We use the mock constructors `In` and `Out` to separate input and
        # output names in the dep graph in order to avoid cyclic graphs (in
        # case input and output names overlap)
        in_, out = object(), object() # (singletons)
        In = lambda x: (x, in_)
        Out = lambda x: (x, out)

        def wrap_names(wrap):
            "Wrap names and leave everything else alone"
            def g(x):
                if isinstance(x, basestring):
                    return wrap(x)
                else:
                    return x
            return g

        # Decorate input names with `In` and output names with `Out` so that
        # `g` isn't cyclic
        g = map_keys(wrap_names(Out),
                map_values(lambda l: map(wrap_names(In), l), self._dep_graph))

        # TODO Restrict recursively (cf. '_decompose' and #1165)

        # Find the subgraph reachable from inputs, and then find its subgraph
        # reachable from outputs. (We could also flip the order.)
        if inputs:
            inputs = map(In, inputs)
            g = graph.reverse(graph.reachable_graph(graph.reverse(g), inputs))
        if outputs:
            outputs = map(Out, outputs)
            g = graph.reachable_graph(g, set(outputs).intersection(g.keys()))

        # Create a new block from the remaining sub-blocks (ordered input to
        # output, ignoring the variables at the ends) and give it our filename
        b = Block(node for node in reversed(graph.topological_sort(g))
                       if isinstance(node, Block))
        b.filename = self.filename

        # Cache result
        self.__restrictions[cache_key] = b

        return b

    ###########################################################################
    # Block protected interface
    ###########################################################################

    # 'ast' determines 'sub_blocks' and 'sub_blocks' determines 'ast', so when
    # one changes we update the other. Both together represent the main
    # structure of the Block object and determine 'inputs', 'outputs',
    # 'conditional_outputs', '_dep_graph', and '_code'.
    #
    # We compute '_dep_graph' and '_code' only when necessary and avoid
    # redundant computation.

    def _structure_changed(self, name, new):
        if not self._updating_structure:
            try:
                self._updating_structure = True

                if name == 'ast':
                    print 'here'
                    # Policy: Keep our AST composable and tidy
                    if isinstance(self.ast, Module):
                        self.ast = self.ast.node
                    if isinstance(self.ast, Stmt) and len(self.ast.nodes) == 1:
                        [self.ast] = self.ast.nodes

                    # Compute our new sub-blocks and give them our filename
                    self.sub_blocks = Block._decompose(self.ast)
                    if self.sub_blocks is not None:
                        for b in self.sub_blocks:
                            b.filename = self.filename
                        # Policy: Only atomic blocks have filenames
                        self.filename = None

                elif name in ('sub_blocks', 'sub_blocks_items'):

                    if len(self.sub_blocks) > 1:
                        self.ast = Stmt([ b.ast for b in self.sub_blocks ])
                    # If our sub-blocks became too few, then we no longer
                    # have sub-blocks because we are too simple to decompose
                    elif len(self.sub_blocks) == 1:
                        self.ast = self.sub_blocks[0].ast
                        self.filename = self.sub_blocks[0].filename
                        self.sub_blocks = None
                    else:
                        self.ast = Stmt([])
                        self.filename = None
                        self.sub_blocks = None

                else:
                    assert False

                # Invalidate caches
                self.__dep_graph_is_valid = False
                self.__code = None
                self.__restrictions.clear()

                # Find inputs and outputs
                v = compiler.walk(self.ast, NameFinder())
                self.inputs = set(v.free)
                self.outputs = set(v.locals)
                self.conditional_outputs = set(v.conditional_locals)

            finally:
                self._updating_structure = False

    def _get__code(self):

        # Cache code objects
        if self.__code is None:

            # Policy: our AST is either a Module or something that fits in a
            # Stmt. (Note that a Stmt fits into a Stmt.)
            ast = self.ast
            if not isinstance(ast, Module):
                ast = Module(None, Stmt([ast]))

            # Make a useful filename to display in tracebacks
            if not self.no_filenames_in_tracebacks:
                if self.filename is not None:
                    filename = self.filename
                else:
                    filename = '<%r>' % self
            else:
                filename = '(Block with filename suppressed)'

            self.__code = compile_ast(ast, filename, 'exec')

        return self.__code

    def _get__dep_graph(self):

        # Cache dep graphs
        if not self.__dep_graph_is_valid:

            if self.sub_blocks is None:
                # fixme: This is questionable.  Shouldn't it make a
                #        graph with empty dependencies?
                self.__dep_graph = None
            else:
                inputs, outputs, conditional_outputs, self.__dep_graph = \
                    Block._compute_dependencies(self.sub_blocks)
                assert inputs == self.inputs
                assert outputs == self.outputs
                assert conditional_outputs == self.conditional_outputs

            self.__dep_graph_is_valid = True

        return self.__dep_graph

    ###########################################################################
    # Block class interface
    ###########################################################################

    @classmethod
    def from_file(cls, f): # (XXX Deprecated)
        'Create a Block from a source file.'
        import warnings
        warnings.warn(DeprecationWarning("Use Block.__init__(file=...)"))
        return cls(file=f)

    @classmethod
    def from_string(cls, s): # (XXX Deprecated)
        'Create a Block from a code string.'
        import warnings
        warnings.warn(DeprecationWarning("Use Block.__init__"))
        return cls(s)

    ###########################################################################
    # Block class protected interface
    ###########################################################################

    @classmethod
    def _decompose(cls, ast):
        ''' Decompose an AST into a sequence of blocks, if possible.

            Returns 'None' on failure.
        '''
        assert isinstance(ast, Node)

        # TODO Look within 'for', 'if', 'try', etc. (#1165)
        if isinstance(ast, Module):
            return cls._decompose(ast.node)
        elif isinstance(ast, Stmt):
            if len(ast.nodes) != 1:
                return map(Block, ast.nodes)
            else:
                # Treat 'Stmt([node])' the same as 'node'
                return cls._decompose(ast.nodes[0])
        else:
            return None

    ###########################################################################
    # Block static protected interface
    ###########################################################################

    @staticmethod
    def _compute_dependencies(blocks):
        ''' Given a sequence of blocks, compute the aggregate inputs, outputs,
            and dependency graph.

            Parameters
            ----------
            blocks : List(Block)
              A list of blocks in order of execution to "tie-up" into a larger,
              single block.

            Returns
            -------
            inputs : Set(Str)
              The input parameters to the new block.

            outputs : Set(Str)
              The output parameters to the new block.

            conditional_outputs : Set(Str)
              The conditional output parameters to the new block, i.e. names
              that might or might not be defined by an arbitrary execution of
              the block.

            dep_graph : Dict(Either(Block, Str), List(Either(Block,Str)))
              The dependency graph (directed, acyclic) relating the blocks from
              the given sequence: block A depends on block B iff an output from
              B is used as an input to A.
              Additionally, the names of the inputs and outputs for the new
              block are included in the graph to capture their dependency
              relations to the contained blocks: name X depends on block A iff
              X is an output of A, and block A depends on name X iff X is an
              input to A.

            (Alternative: make each Block track its own dependencies)
        '''

        # An ad-hoc graph interface
        class Graph(dict):
            def link(self, k, v):
                return self.setdefault(k, set()).add(v)
            def unlink_from(self, k):
                if k in self:
                    del self[k]

        # Deferred computations
        deferred = set()

        # Build dep_graph: a not transitively closed dependency graph that
        # relates blocks to the blocks and inputs they depend on, and outputs
        # to the last block that modifies or creates them
        inputs, outputs, conditional_outputs = set(), set(), set()
        dep_graph, env = Graph(), {}
        for b in blocks:

            # 'b' depends on the provider for each of its inputs or, if none
            # exists, it depends on the inputs themselves (as inputs to the
            # aggregate block). If a name is provided only conditionally, then
            # 'b' depends on both the provider and the input.
            for i in b.inputs:
                if i in env:
                    dep_graph.link(b, env[i])
                if i not in env or i in conditional_outputs:
                    inputs.add(i)
                    dep_graph.link(b, i)

            for c in b.conditional_outputs:

                # 'b's outputs depend only on 'b'
                dep_graph.unlink_from(c)
                dep_graph.link(c, b)

                # 'b' depends on the provider for each of its conditional
                # outputs or, if none exists and the end result has an input of
                # the same name, 'b' depends on that input. (We defer the
                # latter test to check against the final set of inputs rather
                # than just the inputs we've found so far.)
                if c in env:
                    dep_graph.link(b, env[c])
                else:
                    def f(b=b, c=c):
                        if c in inputs:
                            dep_graph.link(b, c)
                    deferred.add(f)

                # 'b' contributes conditional outputs to the aggregate block
                # unless they are already unconditional
                if c not in outputs:
                    conditional_outputs.add(c)

                # 'b' becomes the provider for its conditional outputs
                env[c] = b

            for o in b.outputs:

                # 'b's outputs depend only on 'b'
                dep_graph.unlink_from(o)
                dep_graph.link(o, b)

                # 'b' contributes its outputs to the aggregate block -- as
                # unconditional outputs
                outputs.add(o)
                conditional_outputs.discard(o)

                # 'b' becomes the provider for its outputs
                env[o] = b

        # Run deferred computations
        for f in deferred:
            f()

        return inputs, outputs, conditional_outputs, dep_graph

class Expression(HasTraits):

    # TODO Unify with Block (factor things out of Block)

    ###########################################################################
    # Expression traits
    ###########################################################################

    inputs = Instance(set)
    outputs = Instance(set)

    uuid = Instance(UUID)
    _uuid_default = lambda self: uuid4()

    _code = Property

    ###########################################################################
    # object interface
    ###########################################################################

    def __init__(self, ast, inputs, outputs):
        super(Expression, self).__init__()

        self._ast = ast
        self.inputs, self.outputs = set(inputs), set(outputs)

    ###########################################################################
    # Expression public interface
    ###########################################################################

    def evaluate(self, context):
        return eval(self._code, {}, context)

    ###########################################################################
    # Expression protected interface
    ###########################################################################

    def _get__code(self):
        return compile_ast(self._ast, '<expr>', 'eval')

    ###########################################################################
    # Expression class interface
    ###########################################################################

    @classmethod
    def from_string(cls, s):
        ast = parse(s, mode='eval', transformer=BlockTransformer())
        assert isinstance(ast, compiler.ast.Expression)
        v = compiler.walk(ast, NameFinder())
        return Expression(ast, v.free, v.locals)

################################################################################
# Util
################################################################################

def to_block(x):
    "Coerce 'x' to a Block without creating a copy if it's one already"
    if isinstance(x, Block):
        return x
    else:
        return Block(x)
