#-------------------------------------------------------------------------------
#  
#  Defines the abstract base class for all numeric contexts which connect to
#  another numeric context and behave as if they are the context base for the
#  pipeline.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines the abstract base class for all numeric contexts which connect to
    another numeric context and behave as if they are the context base for the
    pipeline.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from derivative_context \
    import DerivativeContext
    
#-------------------------------------------------------------------------------
#  'ExtensionContext' class:
#-------------------------------------------------------------------------------

class ExtensionContext ( DerivativeContext ):
    """ Defines the abstract base class for all numeric contexts which connect
        to another numeric context and behave as if they are the context base
        for the pipeline.
    """

    #---------------------------------------------------------------------------
    #  Returns the context base any upstream contexts should use:
    #---------------------------------------------------------------------------

    def get_context_base ( self ):
        """ Returns the context base any upstream contexts should use.
        """
        return self

