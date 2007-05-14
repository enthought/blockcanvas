#-------------------------------------------------------------------------------
#  
#  Defines an abstract base class for numeric contexts which can act as
#  'termination' points of numeric context pipelines. Note that the first
#  termination context encountered does not have to be the endpoint of the
#  pipeline, but the last context in the pipeline should derive from
#  TerminationContext.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Defines an abstract base class for numeric contexts which can act as
    'termination' points of numeric context pipelines. Note that the first
    termination context encountered does not have to be the endpoint of the
    pipeline, but the last context in the pipeline should derive from
    TerminationContext.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import Property
    
from constants \
    import CreateContext
    
from derivative_context \
    import DerivativeContext

#-------------------------------------------------------------------------------
#  'TerminationContext' class:
#-------------------------------------------------------------------------------

class TerminationContext ( DerivativeContext ):
    """ Defines an abstract base class for numeric contexts which can act as
        'termination' points of numeric context pipelines. Note that the first
        termination context encountered does not have to be the endpoint of the
        pipeline, but the last context in the pipeline should derive from
        TerminationContext.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Current selection mask:
    context_selection = Property

    #-- 'ANumericContext Class Method Overrides --------------------------------

    #---------------------------------------------------------------------------
    #  Gets a ReductionContext associated with the context:
    #---------------------------------------------------------------------------

    def get_reduction_context ( self, mode = CreateContext ):
        """ Gets a ReductionContext associated with the context.
        """
        return self.hook_context( self.context.get_reduction_context( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a MappingContext associated with the context:
    #---------------------------------------------------------------------------

    def get_mapping_context ( self, mode = CreateContext ):
        """ Gets a MappingContext associated with the context.
        """
        return self.hook_context( self.context.get_mapping_context( mode ) )

    #---------------------------------------------------------------------------
    #  Gets a SelectionContext associated with the context:
    #---------------------------------------------------------------------------

    def get_selection_context ( self, mode = CreateContext ):
        """ Gets a SelectionContext associated with the context.
        """
        return self.hook_context( self.context.get_selection_context( mode ) )

    #-- Property Implementaions ------------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'context_selection' property:
    #---------------------------------------------------------------------------

    def _get_context_selection ( self ):
        return self.context.context_selection

# Define 'PassThruContext' as an alias for 'TerminationContext':
PassThruContext = TerminationContext
