""" Class that holds information about assignments from general expressions.

It can be used in many of the places FunctionCall is used.
"""

from compiler.ast import AssTuple

from codetools.blocks.analysis import walk
from codetools.blocks.api import parse, unparse
from uuid import UUID, uuid4
from traits.api import List, HasTraits, Instance, Property, Str, on_trait_change
from traitsui import api as tui

from function_variables import InputVariable, OutputVariable


builtin_names = set(__builtins__)


class StatementWalker(object):
    """ Extract the expressions.
    """
    def __init__(self):
        self.imported_names = []
        self.expressions = []
        self.names = set()

    def visitImport(self, node):
        for name, alias in node.names:
            self.imported_names.append(alias or name)

    def visitFrom(self, node):
        if node.names[0][0] == '*':
            raise ValueError('cannot deal * imports: %s' % unparse(node))
        for name, alias in node.names:
            self.imported_names.append(alias or name)

    def visitAssign(self, node):
        assign_nodes = node.nodes
        if isinstance(assign_nodes[0], AssTuple):
            assigns = assign_nodes[0].nodes
        else:
            assigns = assign_nodes
        assign_names = [n.name for n in assigns]

        expression = node.expr
        # Collect names.
        nf = NameFinder()
        walk(expression, nf)
        self.names.update(nf.names)
        self.expressions.append((assign_names, expression))


class NameFinder(object):
    """ Extract Name nodes.
    """

    def __init__(self):
        self.names = set()

    def visitName(self, node):
        self.names.add(node.name)


class GeneralExpression(HasTraits):
    """ Class that holds information about assignments from general expressions.
    """

    # Name displayed for the function in a UI as well as in the call signature.
    # If it is not specified, then we use the function's library name.
    name = Property(Str, depends_on=['code'])

    label_name = Property(lambda obj: getattr(obj, 'name'),
                          lambda obj, val: setattr(obj, 'name', val),
                          depends_on=['code'])

    # List of the function's input variable names, bindings, and default values.
    # This should always be empty by definition.
    inputs = List(InputVariable, transient=True)

    # List of the function's output variables names and bindings
    outputs = List(OutputVariable, transient=True)

    # The list of external import statements that are required for this code.
    # Each should have its trailing newline; unparse() will do this for you.
    import_statements = List(Str)

    # The code itself.
    code = Str()

    # Read-only string of python code that executes this assignment.
    call_signature = Property(Str, depends_on=['code'])

    # A unique identifier
    uuid = Instance(UUID, factory=uuid4)


    def trait_view(self, name=None, view_elements=None):
        view = tui.View(
            tui.Item('code', editor=tui.CodeEditor(),
                show_label=False,
            ),

            height=600,
            width=600,
            resizable=True,
            title = 'Edit Expressions',
            buttons=['OK', 'Cancel'],
        )
        return view

    def copyable_trait_names(self, **metadata):
        """ Only copy certain traits.

        The rest we be computed.
        """
        return 'code uuid'.split()

    @on_trait_change('code')
    def _update_code(self, code):
        """ Update the expression code.
        """
        ast = parse(code)
        walker = walk(ast, StatementWalker())
        self.imported_names = walker.imported_names
        outputs = []
        notinputs = set()
        for assigns, expr in walker.expressions:
            for name in assigns:
                outputs.append(OutputVariable(name=name, binding=name))
                notinputs.add(name)
        notinputs.update(self.imported_names)
        # Add the builtins, too.
        notinputs.update(builtin_names)
        inputs = []
        for name in walker.names:
            if name not in notinputs:
                # Icky. We don't know that the user gave code in the correct
                # order.
                inputs.append(InputVariable(name=name, binding=name))
        self.inputs = inputs
        self.outputs = outputs


    def __repr__(self):
        template = 'GeneralExpression(\n  name=%r,\n  code=%r,\n  inputs=%r,\n  outputs=%r,\n  uuid=%r,\n)  <%x>'
        return template % (self.name, self.code, self.inputs, self.outputs, self.uuid, id(self))

    #### Property get/set methods  #############################################

    def _get_name(self):
        out_args = ', '.join(output.binding for output in self.outputs)
        return out_args

    def _get_call_signature(self):
        return self.code.strip()
