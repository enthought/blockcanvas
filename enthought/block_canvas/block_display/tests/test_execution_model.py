# System library imports
import unittest

# ETS imports
from enthought.block_canvas.block_display.execution_model import ExecutionModel
from enthought.blocks.api import Block, unparse
from enthought.block_canvas.function_tools.function_call import FunctionCall
from enthought.block_canvas.function_tools.function_info import find_functions


class ExecutionModelTestCase(unittest.TestCase):

    def setUp(self):
        self.exec_code = (
            "from enthought.block_canvas.debug.my_operator import add, mul\n"
            "c = mul(a,b)\n"
            "d = add(c,b)\n"
            "f = mul(d,e)\n"
        )
        self.exec_model = ExecutionModel.from_code(self.exec_code)
        self.inputs = {}
        for stmt in self.exec_model.statements:
            for iv in stmt.inputs:
                self.inputs[iv.binding] = iv
        self.simple_context = dict(a=2, b=4, e=5)

    def test_import_func_with_const(self):

        code = "from enthought.block_canvas.debug.my_operator import mul\n" \
               "a = mul(1.0, 2.0)\n" \

        desired = "from enthought.block_canvas.debug.my_operator import mul\n\na = mul(1.0, 2.0)"
        model = ExecutionModel.from_code(code)
        self.assertEqual(model.code, desired)

    def test_imported_func_code(self):
        code = "from enthought.block_canvas.debug.my_operator import mul\n" \
               "c = mul(a, b)\n" \

        desired = "from enthought.block_canvas.debug.my_operator import mul\n\nc = mul(a, b)"
        model = ExecutionModel.from_code(code)
        self.assertEqual(model.code, desired)

    def test_imported_func_multi_line(self):
        """ Right now, we can't ensure the order of the import statements nor
            can we consolidate imports from the same locations. """

        code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
               "a = add(1.0,2.0)\n" \
               "b = add(a,3.0)\n" \
               "c = mul(b,b)\n" \

        desired = ["a = add(1.0, 2.0)",
                   "b = add(a, 3.0)",
                   "c = mul(b, b)"]
        model = ExecutionModel.from_code(code)
        codelines = model.code.split('\n')
        for line in desired:
            assert line in codelines

        import_line = codelines[0]
        assert import_line.find('add') and import_line.find('mul')

    def test_add_function(self):

        code = "def foo(a, b):\n" \
                "    x, y = a, b\n" \
                "    return x, y\n" \
                "c, d = foo(1, 2)"


        block = Block(code)
        info = find_functions(block.ast)
        func = FunctionCall.from_ast(block.sub_blocks[-1].ast, info)
        model = ExecutionModel()
        model.add_function(func)

        assert len(model.sorted_statements) == 1

        desired = '\ndef foo(a, b): \n    x, y = (a, b)\n    return x, y\n\nx, y = foo(1, 2)'
        self.assertEqual(desired, model.code)

    def test_remove_function(self):

        code = "def foo(a, b):\n" \
                "    x, y = a, b\n" \
                "    return x, y\n" \
                "c, d = foo(1, 2)\n" \
                "e, f = foo(3, 4)"


        block = Block(code)
        info = find_functions(block.ast)
        foo1_func = FunctionCall.from_ast(block.sub_blocks[-1].ast, info)
        foo2_func = FunctionCall.from_ast(block.sub_blocks[-2].ast, info)
        assert foo1_func != foo2_func

        model = ExecutionModel()
        model.add_function(foo1_func)
        model.add_function(foo2_func)

        model.remove_function(foo2_func)

        assert not( foo2_func in model.statements)
        assert foo1_func in model.statements

    def test_change_binding(self):
        """ Does a change in the binding update the code from the ExecutionModel
            correctly?
        """

        code = "from enthought.block_canvas.debug.my_operator import add\n" \
               "a = add(1, 2)\n"

        model = ExecutionModel.from_code(code)
        func_call = model.statements[0]
        func_call.inputs[0].binding = '2'

        desired = "from enthought.block_canvas.debug.my_operator import add\n\n" \
                  "a = add(2, 2)"
        self.assertEqual(desired, model.code)

    def test_code_from_local_def(self):

        code = "def foo(a, b):\n" \
               "\treturn b, a\n" \
               "x,y = foo(1,2)\n"

        desired = '\ndef foo(a, b): \n    return b, a\n\nx, y = foo(1, 2)'
        model = ExecutionModel.from_code(code)
        self.assertEqual(desired, model.code)


    def test_import_code(self):

        code = "from enthought.block_canvas.debug.my_operator import mul\n" \
               "def foo(a):\n" \
               "\tb = a\n" \
               "\treturn b\n" \
               "a = mul(1.0, 2.0)\n" \
               "b = foo(a)\n"

        desired = 'from enthought.block_canvas.debug.my_operator import mul\n'
        model = ExecutionModel.from_code(code)
        assert model.code.find(desired) == 0

    def test_local_def_code(self):

        code = "from enthought.block_canvas.debug.my_operator import mul\n" \
               "def foo(a):\n" \
               "\tb = a\n" \
               "\treturn b\n" \
               "a = mul(1.0, 2.0)\n" \
               "b = foo(a)\n"

        desired = 'def foo(a): \n    b = a\n    return b\n'
        model = ExecutionModel.from_code(code)
        assert model.code.find(desired) > 0


    def test_merge_statements(self):

        code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
               "a = mul(1.0,2.0)\n" \
               "b = add(1.0,3.0)\n" \

        model = ExecutionModel.from_code(code)
        model.merge_statements([model.statements[0].uuid, model.statements[1].uuid])

    def test_unmerge_statements(self):

        code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
               "a = mul(1.0,2.0)\n" \
               "b = add(1.0,3.0)\n" \

        model = ExecutionModel.from_code(code)
        model.merge_statements([model.statements[0].uuid, model.statements[1].uuid])
        model.unmerge_statements(model.statements[0].uuid)

    def test_restricted(self):
        code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
               "c = mul(a,b)\n" \
               "d = add(c,b)\n" \
               "f = mul(d,e)\n"

        model = ExecutionModel.from_code(code)

        not_really_restricted = model.restricted()
        self.assertEqual(not_really_restricted.sorted_statements,
            model.sorted_statements)

        cstmt, dstmt, fstmt = model.statements
        self.assertEqual(model.restricted(inputs=['e']).sorted_statements,
            [fstmt])
        self.assertEqual(model.restricted(outputs=['d']).sorted_statements,
            [cstmt, dstmt])
        self.assertEqual(model.restricted(inputs=['b'], outputs=['c']).sorted_statements,
            [cstmt])

    def test_execution(self):
        # These imports need to be inside these test functions in order to
        # preserve identity for some weird reason I haven't had time to
        # investigate.
        from enthought.block_canvas.debug.my_operator import add, mul
        context = self.simple_context
        self.exec_model.execute(context)
        self.assertEqual(context, dict(a=2, b=4, e=5, c=8, d=12, f=60, add=add, mul=mul))

    def test_reexecution(self):
        from enthought.block_canvas.debug.my_operator import add, mul
        context = self.simple_context
        self.exec_model.execute(context)
        context['b'] = 3
        self.exec_model.execute(context)
        self.assertEqual(context, dict(a=2, b=3, e=5, c=6, d=9, f=45, add=add, mul=mul))

    def test_execution_restrict_inputs(self):
        from enthought.block_canvas.debug.my_operator import add, mul
        context = self.simple_context
        self.exec_model.execute(context)
        # We'll change `a` and `e` but lie to .execute() and only tell it about `e`.
        context['a'] = 3
        context['e'] = 4
        self.exec_model.execute(context, inputs=['e'])
        self.assertEqual(context, dict(a=3, b=4, e=4, c=8, d=12, f=48, add=add, mul=mul))

    def test_execution_restrict_outputs(self):
        from enthought.block_canvas.debug.my_operator import add, mul
        context = self.simple_context
        self.exec_model.execute(context)
        context['b'] = 3
        context['e'] = 10
        self.exec_model.execute(context, outputs=['d'])
        self.assertEqual(context, dict(a=2, b=3, e=10, c=6, d=9, f=60, add=add, mul=mul))

    def test_execution_restrict_inputs_and_outputs(self):
        from enthought.block_canvas.debug.my_operator import add, mul
        context = self.simple_context
        self.exec_model.execute(context)
        context['b'] = 3
        context['e'] = 10
        self.exec_model.execute(context, inputs=['b'], outputs=['c'])
        self.assertEqual(context, dict(a=2, b=3, e=10, c=6, d=12, f=60, add=add, mul=mul))

    def test_mark_unsatisfied_inputs(self):
        inout = [
            (['a', 'b', 'e'], []),
            (['a', 'b'], ['e']),
            (['a', 'e'], ['b']),
            (['b', 'e'], ['a']),
            (['a'], ['b', 'e']),
            (['b'], ['a', 'e']),
            (['e'], ['a', 'b']),
            ([], ['a', 'b', 'e']),
        ]
        for input, desired in inout:
            desired = set(desired)
            required, satisfied = self.exec_model.mark_unsatisfied_inputs(input)
            self.assertEqual(required, desired)
            self.assertEqual(satisfied, set(input) | set(['c', 'd']))
            for binding, iv in self.inputs.items():
                if binding in desired:
                    self.assertFalse(iv.satisfied)
                else:
                    self.assertTrue(iv.satisfied)




if __name__ == '__main__':
    unittest.main()
