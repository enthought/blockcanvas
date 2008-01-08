""" Define the IMinimalFunctionInfo interface for the minimum amount of 
    information needed to represent an existing python function.  It doesn't 
    take much -- just a name and a module.
    
    This file also holds a simple implementation of that interface that
    may be useful to applications.
"""
from enthought.traits.api import Interface, Str, HasTraits, implements

class IMinimalFunctionInfo(Interface):
    """ Structure to hold module and name of a function.  
    
        Users can supply their own version of this if they wish by
        assigning FunctionLibrary.function_factory to their own
        class or factory method.  The only requirements are that it
        take module and name as keyword arguments.
    """
    # The name of the function.
    name = Str

    # The name of the module/package where the function lives.
    module = Str
    

    
class MinimalFunctionInfo(HasTraits): 
    """ Structure to hold module and name of a function.  
    
        Users can supply their own version of this if they wish by
        assigning FunctionLibrary.function_factory to their own
        class or factory method.  The only requirements are that it
        take module and name as keyword arguments.
    """

    implements(IMinimalFunctionInfo)
        
    ##########################################################################
    # IBasicFunctionInfo traits
    ##########################################################################
        
    # The name of the function.
    name = Str

    # The name of the module/package where the function lives.
    module = Str


    ##########################################################################
    # object interface
    ##########################################################################

    def __repr__(self):
        return '%s(%s, %s)' % (self.__class__.__name__, self.module, self.name)
        
    def __eq__(self, other):
        """ Objects are considered equal if modules and names are the same.            
        """
        return (self.name == other.name) and (self.module == other.module)    
