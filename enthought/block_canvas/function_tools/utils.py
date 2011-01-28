""" Utility functions for functions
"""

# Standard imports
import os, sys

# Enthought library imports
from enthought.etsconfig.api import ETSConfig
from enthought.blocks.analysis import walk

# Global assignment
USER_MODULE_NAME = 'user_functions'

#-------------------------------------------------------------------------------
# AST operations
#-------------------------------------------------------------------------------

class FunctionArgWalker:
    def __init__(self):
        self.num_args = 0
    def visitCallFunc(self, node):
        self.num_args += len(node.args)

def count_function_args(ast):
    """ Given an ast node, finds the total number of arguments in FunctionCalls.
        This is probably only useful if you know the node to have only one
        function call.
    """

    return walk(ast, FunctionArgWalker()).num_args


#-------------------------------------------------------------------------------
# File operations
#-------------------------------------------------------------------------------

def get_code_from_file( filepath, mode = 'r' ):
    """ Return code from file

        Parameters:
        -----------
        filepath : Str

    """

    if not os.path.exists(filepath):
        return ''

    file_object = open(filepath, mode)
    code = file_object.read()
    file_object.close()

    return code

def get_user_package_directory():
    usr_dir = ETSConfig.user_data
    usr_data = os.path.join(usr_dir, USER_MODULE_NAME)

    return usr_data


def initialize_user_data_dir():
    """ Initialize user data folders

        ETSConfig gives platform dependent user-directory:
            C:\\Documents and Settings\\John Doe\\My Documents\\Enthought
            or
            ~/Enthought

        In order to save functions defined by users, or edited by users, we use
        the following directory <user-directory>/<USER_MODULE_NAME>.

        We add an empty __init__.py to make it a package for future imports.

    """

    usr_data = get_user_package_directory()

    usr_dir = os.path.dirname(usr_data)
    if not usr_dir in sys.path:
        sys.path.append(usr_dir)

    if not os.path.exists(usr_data):
        os.makedirs(usr_data)
    if not os.path.isfile(os.path.join(usr_data, '__init__.py')):
        open(os.path.join(usr_data, '__init__.py'), 'w').close()

    return usr_data


# Test
if __name__ == '__main__':
    usr_data = initialize_user_data_dir()
    print usr_data

    # Save a function in the user directory
    code = '\n'.join(('def my_add(a,b):',
                      '   return (a*a+b*b)**0.5'))
    new_file_path = os.path.join(usr_data, 'my_func.py')
    new_file = open(new_file_path, 'w')
    new_file.write(code)
    new_file.close()

    # Retrieve the function and test it
    importline = 'from ' + USER_MODULE_NAME + '.my_func import my_add'
    exec importline
    print 'Check: 5=', my_add(3,4)

    # Remove the files.
    os.remove(new_file_path)
    os.remove(new_file_path+'c')


### EOF ------------------------------------------------------------------------
