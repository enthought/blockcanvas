#-------------------------------------------------------------------------------
#
#  Helper functions for constructing various types of common numeric context
#  pipelines.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Helper functions for constructing various types of common numeric context
    pipelines.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numeric_context \
    import NumericContext

from termination_context \
    import PassThruContext

from trait_item \
    import TraitItem

#-------------------------------------------------------------------------------
#  Helper function for creating a properly terminated NumericContext:
#-------------------------------------------------------------------------------

def NumericPipe ( **traits ):
    return PassThruContext( context = NumericContext( **traits ) )

#-------------------------------------------------------------------------------
#  Helper function for creating a NumericContext pipe based on an object with
#  traits which contain Numeric arrays:
#-------------------------------------------------------------------------------

def NumericObjectContext ( object, **traits ):
    return NumericPipe( context_items = [ TraitItem( object = object,
                                                     id     = name )
                                        for name in object.trait_names()
                                        if object.base_trait( name ).array ],
                        **traits )

#-------------------------------------------------------------------------------
#  Helper function for creating a NumericContext pipe from a list of named
#  arrays:
#-------------------------------------------------------------------------------

def NumericArrayContext ( **arrays ):
    context = NumericContext()
    context.update( arrays )
    return PassThruContext( context = context )

#-------------------------------------------------------------------------------
#  Creates a Data Explorer view from a list of named arrays:
#-------------------------------------------------------------------------------

def ArrayExplorer ( format = '%.3f', **arrays ):
    """ Creates a Data Explorer view from a list of named arrays.
    """
    raise NotImplementedError
# fixme: This still needs to be converted from numeric_model to numeric_context.
#    from numeric_context_explorer import NumericContextExplorer
#
#    NumericContextExplorer( context = NumericArrayContext( **arrays ),
#                            format  = format,
#                            title   = 'Array Explorer' ).configure_traits()

