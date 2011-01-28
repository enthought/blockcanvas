# Standard imports
import logging
from types import FunctionType, BuiltinFunctionType

# Scientific Library imports
from numpy import ufunc

# Enthought library imports
from enthought.traits.api import HasTraits, Str, Bool, List, Property,  \
                                 Trait



logger = logging.getLogger(__name__)


class FunctionArgument(HasTraits):
    """FunctionVariable represents a variable in a function definition,
    either the input of the output of a function."""

    ##########################################################################
    # FunctionArgument Traits
    ##########################################################################

    # The name of the variable
    name = Str

    ##########################################################################
    # FunctionArgument object Interface
    ##########################################################################

    def __repr__(self):
        """Return a more useful string representation of this class"""
        return "%s(name=%s)" % (self.__class__.__name__, repr(self.name))

    def __str__(self):
        return self.__repr__()


class OutputArgument(FunctionArgument):
    """A FunctionVariable that represents an output of a function.
    """
    pass

class InputArgument(FunctionArgument):

    ##########################################################################
    # InputArgument Traits
    ##########################################################################

    # String representation of default argument.  If there isn't a
    # default argument, this is None.
    default = Trait(None, Str, None)

    ##########################################################################
    # InputArgument object Interface
    ##########################################################################

    def __repr__(self):
        """Generate a more useful string representation of InputArgument"""
        return "InputArgument(name=%s, default=%s)" % \
                (repr(self.name), repr(self.default))

    def __str__(self):
        return self.__repr__()




class CallableInfo(HasTraits):
    """ fixme: I think this should be an interface instead of a base class.
    """

    ##########################################################################
    # CallableInfo Traits
    ##########################################################################

    # The package and module that this callable comes from.  The canonical
    # import statementthat would import this object is::
    #
    #     from %(module) import %(name)
    #
    # If the function does not have a module, the string is empty.
    module = Str

    # The name of the callable object.
    name = Str

    # A "pseudonym" for the callable so we can provide multiple signatures
    # for it.  If it isn't explicitly set, then we return name.
    # fixme: I'd like for this to look like:
    # library_name = SelfDelegate('name')
    library_name = Property
    _library_name = Str

    # The full python path module+name for the object.  This is read-only.
    full_name = Property(Str)

    # List of the input arguments to the function
    inputs = List(InputArgument)

    # List of the output arguments of the function
    outputs = List(OutputArgument)

    # Documentation for the function if available
    doc_string = Str

    # The actual code for this callable.  If not
    # available (as in a CompiledPythonFunctionInfo),
    # returns None.
    code = Str

    # Whether we are pointing at a valid callable
    is_valid = Bool

    ##########################################################################
    # CallableInfo interface.
    ##########################################################################

    ### Property get/set methods #############################################

    def _get_full_name(self):
        """ Return module.name
        """
        if self.module:
            full_name = '.'.join((self.module, self.name))
        else:
            full_name = self.name

        return full_name

    def _get_library_name(self):
        """ Return the library name for the function.  If it is empty,
            return the function's name.
        """
        return self._library_name or self.name

    def _set_library_name(self, value):
        """ set the library name to something other than the function's name.
        """
        self._library_name = value



##############################################################################
# Factories
##############################################################################

def python_function_info_from_function(python_func, **traits):
    """ Factory method for returning a CallableInfo given a python function.
    """
    from python_function_info import PythonFunctionInfo
    from extension_function_info import ExtensionFunctionInfo

    if isinstance(python_func, FunctionType):
        return PythonFunctionInfo.from_function(python_func, **traits)
    elif isinstance(python_func, BuiltinFunctionType) or \
         isinstance(python_func, ufunc):
        return ExtensionFunctionInfo.from_function(python_func, **traits)
    else:
        raise ValueError("%r not a function" % python_func)

