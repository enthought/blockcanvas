""" Classes to represent function input and output variables along with
    "bindings" (variable names or values) to them.  There are also classes
    that store information about the units of a variable.

    Note: The Variable class could "grow" another trait called "unique_name"
          or something like that to handle re-writing of variables to enforce
          uniqueness during execution.
"""
import re

# enthought library imports
from traits.api import HasTraits, Any, Bool, Str, Property, TraitError


python_name = re.compile('^[a-zA-Z_][a-zA-Z0-9_]*$')

class _Undefined(object):
    """ Simple marker that specifies Undefined default values.

        We don't use None because that may be a valid input value.

        NOTE: DEPRECATED! For use only to allow FunctionDefinition to work,
        which is also deprecated and will be gone once the new FunctionCall
        based system is working.
    """

    ##########################################################################
    # object interface
    ##########################################################################

    def __repr__(self):
        return "Undefined"



# Singleton version of Undefined (like None)
Undefined = _Undefined()


class Variable(HasTraits):
    """ Represent function variables (inputs and outputs).

        fixme: We should probably only allow floats, a quoted string, None, or
               a valid python variable name for a binding.  If we choose to
               make this restriction, see OutputVariable (below) for ideas
               on how to implement it.

        Note: Sub-classes perhaps can add things like units. [do we need it?]
    """

    ##########################################################################
    # Variable traits
    ##########################################################################

    # Name of the input variable.
    name = Str

    # Variable (or value) bound to this name.
    binding = Property(depends_on=['_binding'])

    # Keep track of binding name that user may set.  This is a string or
    # None if there isn't a binding.
    _binding = Any(None)

    # Whether this binding has been satisfied. Mostly, this is for graphical
    # elements representing this Variable to listen to and controllers to set.
    satisfied = Bool(True)

    ##########################################################################
    # Variable interface
    ##########################################################################


    ### private property get/set methods #####################################

    def _get_binding(self):
        if self._binding is not None:
            result = self._binding
        else:
            result = self.name

        return result

    def _set_binding(self, value):
        self._binding = value

    def __binding_changed(self, old, new):
        # Checking for old and new values to avoid executing
        # when a binding is first being set on start up.
        if old and new:
            from enthought.block_canvas.app.scripting import app
            app.execute_for_binding(self, old, new)


    ##########################################################################
    # object interface
    ##########################################################################

    def __repr__(self):
        return "Variable(%s=%s)" % (self.name, self.binding)



class InputVariable(Variable):
    """ InputVariables have a name, default value, and a binding.
    """

    ##########################################################################
    # InputVariable traits
    ##########################################################################

    # Default value of a keyword input variable.  It defaults to None.
    default = Any(None)

    # String that represents how this variable appears in a call signature.
    # For the standard case, this is just the binding.  If it is a keyword
    # argument (denoted by having a default), then it will name=binding.
    call_signature = Property


    # True if this is a keyword argument.  False otherwise
    keyword_argument = Property


    ##########################################################################
    # Variable interface
    ##########################################################################



    ### private property get/set methods #####################################

    def _get_binding(self):
        """ If the user has set the binding, use that value.  If a default
            value is available, use that value.  Otherwise, just use the name.
        """
        if self._binding is not None:
            result = self._binding
        elif self.default is not None:
            result = self.default
        else:
            result = self.name

        return result

    def _get_keyword_argument(self):
        """ Simply check if we have a default value.  If we do, we are a
            keyword argument.
        """
        return self.default is not None

    def _get_call_signature(self):
        """ Return a string for how this variable looks in a function call.

            For non-keyword arguments, this is simply the binding.  For
            keyword arguments, we have name=binding if a binding has been
            explicitly set for the variable.  Otherwise, nothing is returned
            and the default value is used automatically in by Python.
        """
        if not self.keyword_argument:
            signature = self.binding
        else:
            if self._binding is None:
                signature = ""
            else:
                signature = "%s=%s" %(self.name, self.binding)

        return signature

    ##########################################################################
    # object interface
    ##########################################################################

    def __repr__(self):
        return "InputVariable(%s, %s, %s)" % (self.name, self.binding,
                                              self.default)

def is_python_variable(value):
    """ Property validator function that tests whether a value is a
        valid python variable name.
    """
    if not python_name.match(value):
        msg = "'%s' isn't a valid variable name."
        raise TraitError, msg

    return value


class OutputVariable(Variable):
    """ Represent an function output along with a name binding that the the
        output variable is assigned to.

        This binding for an output variable must be a valid python variable.
    """

    ##########################################################################
    # Variable traits
    ##########################################################################

    binding = Property(fvalidate=is_python_variable, depends_on=['_binding'])


    ##########################################################################
    # Variable interface
    ##########################################################################

    ### private property get/set methods #####################################

    def _get_binding(self):
        return super(OutputVariable, self)._get_binding()

    def _set_binding(self, value):
        super(OutputVariable, self)._set_binding(value)

    ######################################################################
    # object interface
    ######################################################################

    def __repr__(self):
        return "OutputVariable(%s, %s)" % (self.name, self.binding)


###############################################################################
# Variables carrying units
###############################################################################

class UnittedInputVariable(InputVariable):
    """ Enables units for input-variables
    """

    units = Str('')

    ##########################################################################
    # object interface
    ##########################################################################

    def __repr__(self):
        return "UnittedInputVariable(%s, %s, %s, %s)" % (self.name,
                                                         self.binding,
                                                         self.default,
                                                         self.units)


class UnittedOutputVariable(OutputVariable):
    """ Enables units for output-variable
    """

    units = Str('')

    ##########################################################################
    # object interface
    ##########################################################################

    def __repr__(self):
        return "UnittedOutputVariable(%s=%s, %s)" % (self.name, self.binding,
                                                      self.units)

### EOF ------------------------------------------------------------------------
