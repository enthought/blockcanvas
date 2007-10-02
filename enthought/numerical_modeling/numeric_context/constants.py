#-------------------------------------------------------------------------------
#  
#  Constants defined and used by the numeric context package.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Constants defined and used by the numeric context package.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import ufunc

from types \
    import FunctionType, MethodType, ModuleType

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# get_xxx_context 'mode' values:
QueryContext  = 0    # Query existence of a context
OpenContext   = 1    # Return current context if any; otherwise create one
CreateContext = 2    # Always create a new context

# Contents of an empty context group:
empty_group = ( ( 0, ), [] )

# The set of unpickleable objects we filter from a NumericContext when
# persisting it:
NonPickleable = ( FunctionType, MethodType, ModuleType, ufunc )

