""" Utility functions for getting information about and manipulating Blocks.
"""

# Standard imports
from compiler.ast import From, Import, Function, Getattr
from copy import copy
import logging, numpy

# Enthought imports
from codetools.blocks.api import Block
from codetools.blocks.analysis import walk

# Global logger
logger = logging.getLogger(__name__)


class BlockInfoWalker:
    """ AST Visitor class for finding the function names in an AST and whether
        it contains import statements.
    """

    def __init__(self):
        self.has_import = False
        self.function_names = []

    def visitFrom(self, node):
        self.has_import = True

    def visitImport(self, node):
        self.has_import = True

    def visitCallFunc(self, node):
        if isinstance(node.node, Getattr):
            getattr_node = node.node
            decorated_name = ""
            while (isinstance(getattr_node.expr, Getattr)):
                decorated_name = getattr_node.attrname + "." + decorated_name
                getattr_node = getattr_node.expr
            decorated_name = "%s.%s.%s" % (getattr_node.expr.name,
                                           getattr_node.attrname, decorated_name)
            decorated_name = decorated_name[:-1]

            self.function_names.append(decorated_name)
        else:
            self.function_names.append(node.node.name)

        # fixme: The fact that I have to do this means that something is very
        #        wrong somewhere, but where? walk is suppposed to walk the whole
        #        AST tree! Why isn't this happening?
        for arg in node.args:
            self.function_names.extend(walk(arg, BlockInfoWalker()).function_names)


class BlockNameReplacer:
    """ AST Visitor class for renaming a variable in code.
    """

    def __init__(self, old, new):
        self.old = old
        self.new = new

    def visitAssName(self, node):
        if node.name == self.old:
            node.name = self.new

    def visitName(self, node):
        if node.name == self.old:
            node.name = self.new


def add_to_existing_imports(code_block, from_import):
    """ Given a block and an From ast node, search the block for an existing
        From statement that can accomodate the imports in argument. If
        sucessful, augments the existing statement and returns the modified
        sub_block. Otherwise, returns None.
    """

    block = code_block.block
    block._updating_structure = True
    result, modified = None, False

    for sub_block in block.sub_blocks:
        if (isinstance(sub_block.ast, From) and
            sub_block.ast.modname == from_import.modname):
            for name in from_import.names:
                if name not in sub_block.ast.names:
                    sub_block.ast.names.append(name)
                    if not modified:
                        modified = True
            if modified:
                sub_block._set_inputs_and_outputs()
                result = sub_block
                break

    block._updating_structure = False
    if result and modified:
        result.invalidate_cache()
        code_block.replace_sub_blocks([result], [result], True)
        block.invalidate_cache()

    return result


def find_end_imports(block):
    """ Returns the index of the first non-import statement in a block's
        sub blocks. If there are no non-import statements, returns -1.
    """

    current_index = 0
    for sub_block in block.sub_blocks:
        if (not isinstance(sub_block.ast, From) and not
            isinstance(sub_block.ast, Import)):
            return current_index
        current_index += 1

    return -1


def find_begin_code(block):
    """ Returns the index of the first non-import and non-function-def statement
        in a block's sub_blocks. If there are none, returns -1.
    """

    for i, sub_block in enumerate(block.sub_blocks):
        if not (isinstance(sub_block.ast, From) or
                isinstance(sub_block.ast, Import) or
                isinstance(sub_block.ast, Function)):
            return i
    return -1


def function_names(block):
    """ Return all the function names within a block.
    """

    return walk(block.ast, BlockInfoWalker()).function_names


def rename_variable(ast, old, new):
    """ Replace all references to 'old' with 'new'.
    """

    return walk(ast, BlockNameReplacer(old, new))


def set_var_value(value):
    """ Setting values in a BlockVariable to be either int, float, or
        numpy.ndarray. The latter is evaluated depending on the user's input as
        'numpy.arange' or 'arange'; 'numpy.array' or 'array'; or,
        'numpy.ndarray' or 'ndarray'

        Parameters:
        -----------
        value : Str

    """

    str_value = str(value).strip()
    if str_value == '' or str_value == 'None':
        return None
    else :
        new_value = None
        for i, val_type in enumerate([int, float]):
            try:
                new_value = val_type(str_value)
                break
            except ValueError:
                pass

        if new_value is None:
            if str_value.startswith('numpy.'):
                exec 'new_value = %s' % str_value
            else:
                for func in ['arange', 'array', 'ndarray']:
                     if str_value.startswith(func):
                         try:
                             exec ('from numpy import %s\nnew_value = %s ' %
                                   (func, str_value))
                         except TypeError, err:
                             logger.error('TypeError: %s' %err)
                             new_value = None

                         break

            if type(new_value) != numpy.ndarray:
                new_value = None

    return new_value
