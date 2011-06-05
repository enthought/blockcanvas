# Standard library imports
import sys
import traceback
import compiler

# Enthought library imports
from codetools.blocks.api import unparse
from traits.api import Str


# Local imports
from callable_info import CallableInfo, InputArgument, OutputArgument
from parse_tools import find_local_defs, function_arguments_from_ast, \
                        function_returns_from_ast


class LocalFunctionInfo(CallableInfo):
    """ A LocalFunctionInfo is an editable function defined inside a block.

        The code for a python function is editable, and its argument list
        should update if the underlying code changes.  The argument list
        is read-only because the code is not updated on any changes to the
        argument list.

        Note: Users should check the is_valid flag for the function before
        trusting any of its other trait values.
    """

    ##########################################################################
    # LocalFunctionInfo traits
    ##########################################################################

    # Error string indicating why function failed to load.
    load_error = Str

    # Is the code for this definition editable?  Defaults to True for
    # LocalFunctionInfo.
    editable = True

    ##########################################################################
    # LocalFunctionInfo interface
    ##########################################################################

    @classmethod
    def from_function_ast(cls, function_ast):
        code = unparse(function_ast)
        return cls(code=code)



    ### Private methods ######################################################

    def _initialize_from_ast(self, function_ast):
        """ Given a function_ast, pull out all the important parts.
        """
        res = function_arguments_from_ast(function_ast)
        args, var_args, kw_args = res

        self.inputs = [InputArgument(name=arg, default=default)
                           for arg, default in args]

        # Now the output variables.
        output_vars = function_returns_from_ast(function_ast)
        self.outputs = [OutputArgument(name=name) for name in output_vars]

        # Grab the name out of the function.
        self.name = function_ast.name

        # Set the doc string.  If it is None, make it an empty string.
        self.doc_string = function_ast.doc or ""

        # If we mad it to here, then this python function is valid.
        self.is_valid = True

    def _initialize_as_invalid(self):
        """ If the code we are pointing at is invalid, set all our variables
            to empty states.

            fixme: Is this really a good idea?  This results in a lot of
                   flashing in a UI as we type.  Perhaps we just set
                   ourselves to invalid and require the user to check this
                   before they trust our values.
        """
        self.inputs = []
        self.outputs = []
        self.name = ""
        self.doc_string = ""
        self.is_valid = False


    ### Trait change Handlers ################################################

    def _code_changed(self):
        """ Whenever the code changes, try and update the input and output
            arguments.

            fixme: We only handle one function definition in the code.
                   Fix this to where we allow local functions, and we
                   are defined by the first function in the file.
        """

        # If we fail to parse the ast, our current behavior is to reset
        # all our values to empty and set our invalid flag.
        try:
            ast = compiler.parse(self.code)
        except:
            # If the code failed to load, invalidate all traits,
            # set the load error based on the exception that happened,
            # and set ast to None so that we don't do any further
            # processing.
            ast = None

        if ast is not None:
            functions = find_local_defs(ast)
            if functions.items():
                # Use the first function we find as the one used for this
                # local function.
                # fixme: Should we raise an error if we find more?
                # fixme: find_local_defs will loose a function def if there are
                #        two versions with same name.
                name, function_ast = functions.items()[0]
                self._initialize_from_ast(function_ast)
                self.load_error = ""
            else:
                # There weren't any functions found to initialize from.
                self._initialize_as_invalid()
                self.load_error = "No function definition found."
        else:
            self._initialize_as_invalid()
            # fixme: For now we just report the type of error.  This
            #        should be improved.
            self.load_error = "%s" % exception_info()[0]


##############################################################################
# Utility Function
##############################################################################

def exception_info(traceback_level=1):
    """ Return a formatted tuple of strings for the last traceback.

        The tuple is of the form:
            (exception_name, exception_args, traceback)
    """
    cla, exc, trbk = sys.exc_info()
    exc_name = cla.__name__
    try:
        exc_args = exc.__dict__["args"]
    except KeyError:
        exc_args = ""
    exc_tb = traceback.format_tb(trbk, traceback_level)
    return (exc_name, exc_args, exc_tb)
