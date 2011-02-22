# System library imports
import time 
import compiler
from compiler.ast import (AssTuple, CallFunc, From)
import re
import traceback
from copy import deepcopy
from uuid import UUID

# ETS imports
from enthought.execution.interfaces import IExecutable
from enthought.block_canvas.function_tools.function_info import find_functions
from enthought.block_canvas.function_tools.python_function_info import PythonFunctionInfo
from enthought.block_canvas.function_tools.local_function_info import LocalFunctionInfo
from enthought.block_canvas.function_tools.function_call import FunctionCall
from enthought.block_canvas.function_tools.function_call_group import FunctionCallGroup
from enthought.block_canvas.function_tools.general_expression import GeneralExpression
from enthought.block_canvas.function_tools.group_spec import GroupSpec
from enthought.block_canvas.function_tools.parse_code import retrieve_inputs_and_outputs
from enthought.blocks.analysis import walk, is_const
from enthought.blocks.api import (Block, unparse)
from enthought.traits.api import \
    (Any, cached_property, HasTraits, List, Property, implements, Instance, Bool, List)
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

        FIXME:  Currently, this will only find function calls, constant
        expressions, for and while loops.
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

    def visitFor(self,node):
        """  Explore for loops
        """
        
        gfunc_def = (node.assign, node.list)
        sub_statement_info = walk(node.body, StatementWalker())
        
        group_struct = {'type':'for',
                        'stmts':sub_statement_info,
                        'gfunc':gfunc_def}
        
        self.groups.append(group_struct)

    def visitWhile(self,node):
        """  Explore while loops
        """
        
        gfunc_def = node.test
        sub_statement_info = walk(node.body, StatementWalker())
        
        group_struct = {'type':'while',
                        'stmts':sub_statement_info,
                        'gfunc':gfunc_def}
        
        self.groups.append(group_struct)
        
#-------------------------------------------------------------------------
# Helping functions
#
# They are needed to recursively analyze the structure created by 
# StatementsWalker.
#-------------------------------------------------------------------------

def parse_stmts_info(statement_info,info):
    # Functions
    functions = collect_func_call(statement_info,info)

    # TO DO
    groups = []
    for group_struct in statement_info.groups:
        groups.append(handle_group(group_struct,info))

    # Expressions
    expressions = collect_gen_expr(statement_info)
    
    return functions + groups + expressions

def handle_group(group_struct,info):
        
    gfunc = GroupSpec.from_ast(group_struct['type'],group_struct['gfunc'],None)
    statements = parse_stmts_info(group_struct['stmts'],info)
    
    return FunctionCallGroup(gfunc,statements=statements)
      
def collect_func_call(statement_info,info):
    functions = []
    for names, node in statement_info.call_funcs:
        function = FunctionCall.from_ast(node, info)
        # update the output bindings if we can, else just leave empty
        if len(function.outputs) == len(names):
            for output, name in zip(function.outputs, names):
                output.binding = name
        functions.append(function)
    return functions

def collect_gen_expr(statement_info):        
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
    return expressions




class ExecutionModel(HasTraits):

    """ TO DO:
            - Generate Block from self.statements
    """

    implements(IExecutable)

    # List of function calls, groups, and expressions
    # These must all have inputs, outputs, uuid
    statements = List(Any)

    # List of Groups present in the exec model identified by their UUID
    groups = Property(depends_on=['statements'])
    _groups = List(Instance(UUID))
    
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

    # Flag to impose if the code can be executed or not. 
    # It is needed to speed up the use of the canvas when we are adding new 
    # blocks instead of executing the code. 
    allow_execute = Bool(True)
        
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
        
        statement_info = walk(ast, StatementWalker())

        statements = parse_stmts_info(statement_info,info)

        return cls(statements=statements)
    
    def generate_unique_function_name(self,base_name=""):
        """ Returns a unique name for a new function based on the names of
        existing functions and imports in the code.
        """
        statements = self.statements
        functions = funcs_name_retrieve(statements)
        
        # Basic name generation method: template + counter
        if base_name == "":
            base_name = "new_function"
        if base_name not in functions:
            return base_name
        i = 1
        while base_name + str(i) in functions:
            i += 1
        return base_name + str(i)

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
        
        if not self.allow_execute:
            return
         
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
        required_names, _ = restricted.mark_unsatisfied_inputs(
            available_names)
        if required_names:
            bad = restricted.restricted(inputs=required_names)
            good_statements = [stmt for stmt in restricted.statements if stmt not in bad.statements]
            restricted = self.__class__(statements=good_statements)

        # Big optimization with small effort! The exec command works 
        # really bad when the passed context contains "big" object like
        # that produced by our computations. We remove all of them there are 
        # going to be overwritten. 
        restricted._clean_old_results_from_context(context)

        try:
            t_in = time.time()
            # This is likely the most important line in block canvas
            exec restricted.code in globals, context
            t_out = time.time()
            print '%f seconds: Execution time' % (t_out-t_in)
            
        except Exception, _:
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

    def merge_statements(self, gfunc=None, ids=None):
        """ Merge statements specified by ids into a Group 
        
        They can be specified by ids otherwise all the statements in the 
        current execution model are merged. 
        After creating the group, the model is cleaned (removing 
        merged statements by themselves) and the group is added to the 
        model statements list.
        """
        
        if ids is not None:
            # Just the statements specified by ids vector are merged
            new_group = FunctionCallGroup.from_ids(self, gfunc, ids)
        else:
            # All the current statements in the execution model are 
            # merged
            func_name = self.generate_unique_function_name(base_name='group')
            new_group = FunctionCallGroup(gfunc=gfunc, \
                                          statements=self.sorted_statements, \
                                          gname=func_name)
            
        # Remove merged statements from the current exec model
        self._clear_merged(ids)
        
        # Add the group
        self.statements.append(new_group)

    def unmerge_all_groups(self):
        """ Separate all groups present in the execution model. """
                
        for id in self.groups:
            self.unmerge_statements(id)

    def unmerge_statements(self, id):
        """ Separate Group specified by id into statements. """
        
        # TODO: It will be useful just in the future 
        
        for stmt in self.statements:
            if stmt.uuid == id and isinstance(stmt,FunctionCallGroup):
                for gstmt in stmt.group_statements:
                    self.statements.append(gstmt)
                self.statements.remove(stmt)
                break

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
            if isinstance(stmt,FunctionCallGroup):
                for celem in stmt.gfunc.curr_elemts:
                    available_names.add(celem.outputs[0].binding)

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


    # Private methods ########################################################
    
    def _clear_merged(self,ids):
        """ Cleans merged statements.
        
        They are no more needed because already store in the group object added to
        execution model. 
        If ids is None all non-group statements are removed. 
        """
        
        to_remove = []
        if ids is not None:
            cids = deepcopy(ids)
            for stmt in self.statements:
                if stmt.uuid in cids and not isinstance(stmt,FunctionCallGroup):
                    to_remove.append(stmt)
        else:
            to_remove = []
            for stmt in self.statements:
                if not isinstance(stmt,FunctionCallGroup):
                    to_remove.append(stmt)            
          
        for stmt in to_remove:
            self.statements.remove(stmt)
            if ids is not None:    
                cids.remove(stmt.uuid)
        
        if ids is not None:
            assert(cids==[])
            

    def _clean_old_results_from_context(self,context):
        """ Cleans old results in the context.
        
        It is useful to speed up the re-execution of the code.  
        """
               
        _, outputs_name = \
           retrieve_inputs_and_outputs(self.body)
        
        for key in context.keys():
            if key in outputs_name:
                del context[key]

    #---------------------------------------------------------------------------
    #  ExecutionModel protected interface:
    #---------------------------------------------------------------------------

    #-- Trait Event Handlers --------------------------------------------------

    def _get_sorted_statements(self):
        """ self.statements in topologically sorted order. """
        succ_graph = graph.reverse(self.dep_graph)
        sorted = graph.topological_sort(succ_graph)
        return sorted

    def _get_groups(self):
        """ Generate and return the list of groups (i.e. uuids). """
        for stmt in self.statements:
            if isinstance(stmt,FunctionCallGroup):
                self._groups.append(stmt.uuid)        
        return self._groups

    def _get_imports_and_locals(self):
        """ Generate the import statements and local definitions  
            Should we worry about the order of the imports?
        """

        local_funcs = []
        imports = {}
        function_calls = [statement for statement in self.statements \
                               if isinstance(statement, FunctionCall) ]
        
        # Function calls merged into a group 
        for stmt in self.statements:
            if isinstance(stmt, FunctionCallGroup):
                for statement in stmt.group_statements:
                    function_calls.append(statement)
                
                
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

#-------------------------------------------------------------------------
# Helping functions
#-------------------------------------------------------------------------

def funcs_name_retrieve(stmt):
    """ Recursively explore statements to retrieve functions name. """
    functions = set([s.label_name for s in stmt 
              if hasattr(s, 'function') and (
                  isinstance(s.function, PythonFunctionInfo) or 
                  isinstance(s.function, LocalFunctionInfo))])
    for s in stmt:
        if isinstance(s,FunctionCallGroup):
            functions.add(s.label_name)
            functions.update(funcs_name_retrieve(s.group_statements))

    return functions

# EOF
