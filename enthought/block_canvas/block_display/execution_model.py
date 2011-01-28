# System library imports
import compiler
from compiler.ast import (AssTuple, CallFunc, From)
import re
import traceback

# ETS imports
from enthought.execution.interfaces import IExecutable
from enthought.block_canvas.function_tools.function_info import find_functions
from enthought.block_canvas.function_tools.python_function_info import PythonFunctionInfo
from enthought.block_canvas.function_tools.local_function_info import LocalFunctionInfo
from enthought.block_canvas.function_tools.function_call import FunctionCall
from enthought.block_canvas.function_tools.general_expression import GeneralExpression
from enthought.blocks.analysis import walk, is_const
from enthought.blocks.api import (Block, unparse)
from enthought.traits.api import (Any, cached_property, HasTraits, List, Property, implements)
from enthought.util import graph


python_name = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')
import __builtin__
builtin_names = set(dir(__builtin__))


class StatementWalker(object):
    """ Walks code ast to find all nodes that will be used to create statements
        for the ExecutionModel object.
        There is a method for visitAssign in order to capture output binding
        information for the function calls returned from FunctionCall.from_ast
        which cannot return this information.
        For functions with no output binding information, the visitCallFunc
        method will capture the ast.

        FIXME:  Currently, this will only find function calls and constant
        expressions.  Need to add code to visit general expressions, groups,
        etc.
    """
    def __init__(self):
        self.call_funcs = []
        self.groups = []
        self.constant_expressions = []
        self.general_assignments = []
        self.import_statements = {}

    def visitImport(self, node):
        for name, alias in node.names:
            self.import_statements[(alias or name)] = node

    def visitFrom(self, node):
        if node.names[0][0] == '*':
            raise ValueError('cannot deal * imports: %s' % unparse(node))
        for name, alias in node.names:
            self.import_statements[(alias or name)] = node

    def visitCallFunc(self, node):
        self.call_funcs.append(([], node))

    def visitAssign(self, node):
        assign_nodes = node.nodes
        if isinstance(assign_nodes[0], AssTuple):
            assigns = assign_nodes[0].nodes
        else:
            assigns = assign_nodes
        assign_names = [n.name for n in assigns]

        expression = node.expr
        if isinstance(expression, CallFunc):
            self.call_funcs.append((assign_names, expression))
        elif is_const(expression):
            self.constant_expressions.append((assign_names, node))
        else:
            self.general_assignments.append(node)

    def visitFunction(self, node):
        """ Prevent descending into function definitions.
        """
        pass

class ExecutionModel(HasTraits):

    """ TO DO:
            - Generate Block from self.statements
    """

    implements(IExecutable)

    # List of function calls, groups, and expressions
    # These must all have inputs, outputs, uuid
    statements = List(Any)

    # Topologically sorted list of function calls in statements
    sorted_statements = Property(depends_on=['statements', 'statements_items'])

    # Dependency Graph of all the statements in the body
    dep_graph = Property(depends_on=['statements', 'statements_items'])

    # The imports and local definitions
    imports_and_locals = Property(depends_on=['statements', 'statements_items'])

    # The body of the code corresponding to the statements
    body = Property(depends_on=['statements', 'statements_items'])

    # All the code put together = imports + local_defs + body
    code = Property(depends_on=['statements', 'statements_items',
        'statements.call_signature', 'statements.inputs.binding',
        'statements.outputs.binding'])

    # The block corresponding to the source code:
    block = Property(depends_on=['statements'])

    #---------------------------------------------------------------------------
    #  object interface:
    #---------------------------------------------------------------------------

    #--- Class Methods -- constructors -----------------------------------------

    @classmethod
    def from_code(cls, code):
        """ Create an ExecutionModel object from the code.
            Get the ast for the code and pass to from_ast() class method.
        """

        ast = compiler.parse(code)
        return ExecutionModel.from_ast(ast)

    @classmethod
    def from_file(cls, filename):
        ast = compiler.parseFile(filename)
        return ExecutionModel.from_ast(ast)

    @classmethod
    def from_ast(cls, ast):
        """ Create an ExecutionModel object from the ast. """

        # Build dictionaries for import information and local defs
        info = find_functions(ast)

        # Collect all the function calls in the code and add them to
        # self.statements
        statement_info = walk(ast, StatementWalker())
        functions = []
        for names, node in statement_info.call_funcs:
            function = FunctionCall.from_ast(node, info)
            # update the output bindings if we can, else just leave empty
            if len(function.outputs) == len(names):
                for output, name in zip(function.outputs, names):
                    output.binding = name
            functions.append(function)

        # TO DO
        groups = []
        for group in statement_info.groups:
            pass

        expressions = []
        # Join all of the constant expressions into a single GeneralExpression.
        constant_names = []
        lines = []
        for names, node in statement_info.constant_expressions:
            lines.append(unparse(node))
            # Inform the statement of the variables it is writing to.
            constant_names.extend(names)
        if lines:
            ge = GeneralExpression()
            ge.code = ''.join(lines)
            expressions.append(ge)

        for node in statement_info.general_assignments:
            ge = GeneralExpression()
            ge.code = unparse(node)
            # Now check this expression for any inputs that are provided by the
            # import statements we had. If so, add that import statement to the
            # object and remove that input.
            imported_inputs = []
            for iv in ge.inputs:
                node = statement_info.import_statements.get(iv.binding, None)
                if node is not None:
                    ge.import_statements.append(unparse(node))
                    imported_inputs.append(iv)
            for iv in imported_inputs:
                ge.inputs.remove(iv)
            expressions.append(ge)

        statements = functions + groups + expressions
        result = cls(statements=statements)
        return result

    #---------------------------------------------------------------------------
    # IExecutable interface
    #---------------------------------------------------------------------------

    def execute(self, context, globals=None, inputs=None, outputs=None):
        """ Execute the code in the given context.

        Parameters
        ----------
        context : sufficiently dict-like object
            The namespace to execute the code in.
        globals : dict, optional
            The global namespace for the code.
        inputs : list of str, optional
            Names that can be used to restrict the execution to portions of the
            code. Ideally, only code that is affected by these inputs variables
            is executed.
        outputs : list of str, optional
            Names that can be used to restrict the execution to portions of the
            code. Ideally, only code that affects these outputs variables is
            executed.
        """
        if globals is None:
            globals = {}

        if inputs is not None or outputs is not None:
            # Only do this if we have to.
            restricted = self.restricted(inputs=inputs, outputs=outputs)
        else:
            restricted = self

        # Only execute the portions of the code which can be executed given the
        # names in the context.
        available_names = set(context.keys())
        required_names, satisfied_names = restricted.mark_unsatisfied_inputs(
            available_names)
        if required_names:
            bad = restricted.restricted(inputs=required_names)
            good_statements = [stmt for stmt in restricted.statements if stmt not in bad.statements]
            restricted = self.__class__(statements=good_statements)

        try:
            # This is likely the most important line in block canvas
            exec restricted.code in globals, context

        except Exception, e:
            print 'Got exception from code:'
            print restricted.code
            print
            traceback.print_exc()


    #---------------------------------------------------------------------------
    # ExecutionModel interface
    #---------------------------------------------------------------------------

    def add_function(self, func_call):
        """ Add a function call to the block.  Append to the list of statements.
            The code will be generated from the sorted_statements.

            FIXME:  Add imports from func_call being added.
         """
        self.statements.append(func_call)
        return

    def remove_function(self, func_call):
        """ Given a function, remove it from the list of statements. """
        self.statements.remove(func_call)
        return

    def remove_all_function(self, func_call):
        """ Given a function, remove all occurrences of this function from the
            list of statements. """

        py_path = func_call.python_path
        name = func_call.name

        to_remove = []
        for func in self.statements:
            if func.name == name and func.python_path == py_path:
                to_remove.append(func)

        for func in to_remove:
            self.remove_function(func)


    def merge_statements(self, ids):
        """ Merge statements specified by ids into a Group """
        ## FIXME:  TO DO
        pass


    def unmerge_statements(self, id):
        """ Seperate Group specified by id into statements. """
        ## FIXME:  TO DO
        pass

    def restricted(self, inputs=None, outputs=None):
        """ Return an ExecutionModel which has been restricted to the given
        inputs and outputs.

        Parameters
        ----------
        inputs : sequence of str, optional
            The names of the input variables which have changed. If not
            provided, then every possible input will be considered to have
            changed.
        outputs : sequence of str, optional
            The names of the output variables which are desired to recompute.

        Returns
        -------
        model : ExecutionModel
        """
        if inputs is not None:
            inputs = set(inputs)
        if outputs is not None:
            outputs = set(outputs)

        # Convert the names to the nodes which are directly related to them.
        input_nodes = set()
        output_nodes = set()
        for statement in self.statements:
            inbindings = set(iv.binding for iv in statement.inputs)
            if inputs is None or inputs.intersection(inbindings):
                input_nodes.add(statement)
            outbindings = set(ov.binding for ov in statement.outputs)
            if outputs is None or outputs.intersection(outbindings):
                output_nodes.add(statement)

        # Find the reachable subgraphs of both the inputs and outputs.
        dep_graph = self.dep_graph
        inreachable = graph.reverse(graph.reachable_graph(
            graph.reverse(dep_graph), input_nodes))
        outreachable = graph.reachable_graph(dep_graph, output_nodes)

        # Our desired set of statements is the intersection of these two graphs.
        in_nodes = set()
        for node, deps in inreachable.iteritems():
            in_nodes.add(node)
            for d in deps:
                in_nodes.add(d)
        intersection = set()
        for node, deps in outreachable.iteritems():
            if node in in_nodes:
                intersection.add(node)
                for d in deps:
                    if d in in_nodes:
                        intersection.add(d)

        em = self.__class__(
            statements=list(intersection),
        )
        return em

    def mark_unsatisfied_inputs(self, available_names):
        """ Return a list of names of variables which are required to run the
        entire execution.

        Each unsatisfied InputVariable will be marked as unsatisfied.

        Parameters
        ----------
        available_names : sequence/set of str
            The names which are available for execution.

        Returns
        -------
        required_names : set of str
        satisfied_names : set of str
        """
        available_names = set(available_names)
        # Add each output variable name to the set of available names.
        for stmt in self.statements:
            for ov in stmt.outputs:
                available_names.add(ov.binding)

        # Add the builtins, too.
        available_names.update(builtin_names)

        # Now look at each statement's inputs and try to match them up to the
        # available names.
        required_names = set()
        satisfied_names = set()
        for stmt in self.statements:
            for iv in stmt.inputs:
                name = iv.binding
                # Only check bindings which are actual valid Python identifiers.
                if python_name.match(name) and name not in available_names:
                    required_names.add(name)
                    iv.satisfied = False
                else:
                    satisfied_names.add(name)
                    iv.satisfied = True

        return required_names, satisfied_names

    #---------------------------------------------------------------------------
    #  ExecutionModel protected interface:
    #---------------------------------------------------------------------------

    #-- Trait Event Handlers --------------------------------------------------

    def _get_sorted_statements(self):
        """ self.statements in topologically sorted order. """
        succ_graph = graph.reverse(self.dep_graph)
        sorted = graph.topological_sort(succ_graph)
        return sorted

    def _get_imports_and_locals(self):
        """ Generate the import statements and local definitions
            Should we worry about the order of the imports?
        """

        local_funcs = []
        imports = {}
        function_calls = [statement for statement in self.statements \
                               if isinstance(statement, FunctionCall) ]
        info_items = set([(call.label_name, call.function) for call in function_calls])
        for name, func in info_items:
            if isinstance(func, PythonFunctionInfo):
                # This function is imported
                # FIXME - Need to be able to handle 'as' names.
                # If a function has an 'as' name, then it shouldn't be added
                # to the imports dictionary.
                module = func.module
                if imports.has_key(module):
                    imports[module].append(name)
                else:
                    imports[module] = [name]
            elif isinstance(func, LocalFunctionInfo):
                local_funcs.append(func.code + '\n')

        import_lines = []
        for module in imports:
            names = []
            for name in imports[module]:
                names.append((name, None))
            import_lines.append(unparse(From(module, names, 0)))

        # Get the import statements from GeneralExpressions.
        for stmt in self.statements:
            if isinstance(stmt, GeneralExpression):
                import_lines.extend(stmt.import_statements)

        # Uniquify the import list while maintaining order.
        seen = set()
        unique_lines = []
        for line in import_lines:
            if line not in seen:
                unique_lines.append(line)
                seen.add(line)

        return ''.join(unique_lines) + '\n' + ''.join(local_funcs)

    def _get_body(self):
        """ Generate the body of code not including imports and local definitions """
        return '\n'.join(statement.call_signature
                         for statement in self.sorted_statements)

    @cached_property
    def _get_code(self):
        """ Return the code for this execution model """
        return self.imports_and_locals + self.body


    def _get_block(self):
        """ Creates a new Block from the code for this model. """
        return Block(self.code)

    def _get_dep_graph(self):
        """ Returns the function dependency graph for self.statements.
            This just walks the dependencies for each function in self.statements. """

        dep_graph = {}
        outputs = {}
        # First pass to set up outputs
        for s in self.statements:
            for output in s.outputs:
                outputs[output.binding] = s

        # Second pass to set up the dependency graph
        for s in self.statements:
            depends = []
            for input in s.inputs:
                try:
                    depends.append(outputs[input.binding])
                except KeyError:
                    # Not all inputs will depend on the output from a previous function
                    # so this is okay
                    pass
            dep_graph[s] = depends

        return dep_graph

# EOF
