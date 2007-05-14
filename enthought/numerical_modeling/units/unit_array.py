# Numeric Library Imports
import numpy

# Enthought library imports
import enthought.units as units

def __newobj__ ( cls, *args ):
    """ Unpickles new-style objects.
    """
    return cls.__new__( cls, *args )


class UnitArray(numpy.ndarray):
    """ Define a UnitArray that subclasses from a Numpy array

        This class simply adds a "units" object to a numpy array.  Is *does
        not* try to do any automatic unit conversion or calculation during
        binary operations.  It is simply there as information for other
        application objects to use and manipulate.

        This code is shamelessly copied from the numpy matrix class.  It is
        of course modified to suite our purposes.
    """

    ############################################################################
    # numpy.ndarray attributes
    ############################################################################

    # priority->0.0 results in binary array ops returning UnitArray objects.
    __array_priority__ = 10.0

    ############################################################################
    # UnitArray attributes
    #
    # Note: These are commented out because we are not using traits.  However,
    #       They are left here for documentation.
    ############################################################################

    # Units specification.  it is a enthought.units.unit object, not a string.
    # units = Instance(units.unit)

    # 'type' specifies the type of UnitArray.
    # This could be useful for specifying that this is a 'tops' UnitArray or of
    # 'flag' or other such types.  I am not sure if this is useful, but I
    # think it might be.
    # fixme: Not Implemented
    # type = Str

    ############################################################################
    # object interface
    ############################################################################
    def __reduce_ex__(self, protocol):
        """
        pickling function for classes which inherit from tuple.
        
        __reduce_ex__ must be overloaded for pickling to work. Refer to the docs
        in the pickle source code for details as to why.
        
        """
        
        state = (self.units, super(UnitArray, self).__reduce_ex__(protocol))
        return ( __newobj__, ( self.__class__, ()), state )

    def __setstate__(self, state):
        """
        unpickling function
        """
        
        super(UnitArray, self).__setstate__(state[1][2])
        self.units = state[0]

    ############################################################################
    # numpy.ndarray interface
    ############################################################################

    def __new__(cls, data, dtype=None, copy=True, units=None):
        """ Called when a new object is created (before __init__).

            The default behavior of ndarray is overridden to add units and
            family_name to the class.

            For more details, see:
                http://docs.python.org/ref/customization.html

        """


        ### Array Setup ########################################################

        if isinstance(data, numpy.ndarray):
            # Handle the case where we are passed in a numpy array.
            if dtype is None:
                intype = data.dtype
            else:
                intype = numpy.dtype(dtype)

            new = data.view(cls)

            if intype != data.dtype:
                res = new.astype(intype)
            elif copy:
                res = new.copy()
            else:
                res = new

        else:
            # Handle other input types (lists, etc.)
            arr = numpy.array(data, dtype=dtype, copy=copy)

            res = numpy.ndarray.__new__(cls, arr.shape, arr.dtype,
                                        buffer=arr)

        ### Configure Other Attributes #########################################
        res.units = units

        return res

    def __array_finalize__(self, obj):

        # Copy any values that were on the original UnitArray into the output
        # UnitArray.
        try:
            self.units = obj.units
        except AttributeError:
            pass


    ############################################################################
    # UnitArray interface
    ############################################################################

    ### Unit Conversion ########################################################

    def as_units(self, new_units):
        """ Convert UnitArray from its current units to a new set of units.

        """
        result = units.convert(self, self.units, new_units)
        result.units = new_units

        return result
    
    ############################################################################
    # static methods which wrap numpy builtin functions
    ############################################################################
    
    @staticmethod
    def concatenate(sequences, axis=0):
        result = numpy.concatenate(sequences, axis)
        result.units = sequences[0].units
        return result
    
