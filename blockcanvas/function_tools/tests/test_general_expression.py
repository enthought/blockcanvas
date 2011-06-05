from nose.tools import assert_raises

from codetools.blocks.analysis import walk
from codetools.blocks.api import parse, unparse
from traits.api import push_exception_handler, pop_exception_handler

# Module-level setup and teardown.
def setup_module():
    push_exception_handler(handler=lambda *args, **kwds: None, reraise_exceptions=True)

def teardown_module():
    pop_exception_handler


from blockcanvas.function_tools.function_variables import OutputVariable
from blockcanvas.function_tools.general_expression import StatementWalker, GeneralExpression


def test_simple_statement_walker():
    const_code = "a = 10"
    walker = walk(parse(const_code), StatementWalker())
    assert len(walker.names) == 0
    assert len(walker.imported_names) == 0
    assert len(walker.expressions) == 1

    const_code = "a, b = 10"
    walker = walk(parse(const_code), StatementWalker())
    assert len(walker.names) == 0
    assert len(walker.imported_names) == 0
    assert len(walker.expressions) == 1

    const_code = "a = 10; b = 20"
    walker = walk(parse(const_code), StatementWalker())
    assert len(walker.names) == 0
    assert len(walker.imported_names) == 0
    assert len(walker.expressions) == 2

    const_code = "a = 10 + 20"
    walker = walk(parse(const_code), StatementWalker())
    assert len(walker.names) == 0
    assert len(walker.imported_names) == 0
    assert len(walker.expressions) == 1

def test_complex_statement_walker():
    code = "\n".join([
        "from math import sin",
        "x = 10",
        "y = 10 + x",
        "z = sin(y) + b",
    ])
    walker = walk(parse(code), StatementWalker())
    assert len(walker.names) == 4
    assert set(walker.names) == set(['x', 'y', 'b', 'sin'])
    assert len(walker.imported_names) == 1
    assert set(walker.imported_names) == set(['sin'])
    assert len(walker.expressions) == 3

def test_init():
    ge = GeneralExpression(code='a = 10')
    assert hasattr(ge, 'inputs')
    assert ge.inputs == []
    assert len(ge.outputs) == 1
    assert ge.outputs[0].binding == 'a'
    assert hasattr(ge, 'uuid')
    assert hasattr(ge, 'call_signature')
    assert ge.call_signature == "a = 10"
    assert ge.code == "a = 10"

def test_update_code_error():
    ge = GeneralExpression()
    assert_raises(SyntaxError, ge.set, code="not even valid Python")


# XXX: needs more testing of the correctness of assigning to
# GeneralExpression.code
