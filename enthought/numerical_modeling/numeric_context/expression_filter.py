#-------------------------------------------------------------------------------
#
#  Defines a filter based on the result of evaluating a specified Python
#  expression in a numeric context.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines a filter based on the result of evaluating a specified Python
    expression in a numeric context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy import issubdtype

from enthought.traits.api \
    import Expression, Property

from enthought.traits.ui.api \
    import View

from enthought.blocks.api \
    import Expression as ExpressionBlock

from a_numeric_filter \
    import ANumericFilter

#-------------------------------------------------------------------------------
#  'ExpressionFilter' class:
#-------------------------------------------------------------------------------

class ExpressionFilter ( ANumericFilter ):
    """ Defines a filter based on the result of evaluating a specified Python
        expression in a numeric context.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Python expression used to filter the data:
    filter = Expression

    # Name of the filter:
    name = Property

    # Should the value, is_bit and color traits be used? (override):
    use_value = True

    #---------------------------------------------------------------------------
    #  Traits view definitions:
    #---------------------------------------------------------------------------

    traits_view = View( 'filter' )

    #-- 'object' Class Overrides -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Initializes the object:
    #---------------------------------------------------------------------------

    def __init__ ( self, filter = 'None', **traits ):
        """ Initializes the object.
        """
        self.filter = filter
        super( ExpressionFilter, self ).__init__( **traits )

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        if self._name:
            return self._name
        if not self.enabled:
            return '[%s]' % self.filter.strip()
        return self.filter.strip()

    def _set_name ( self, value ):
        old = self.name
        if value != old:
            self._name = value
            self.trait_property_changed( 'name', old, value )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the 'filter' expression being changed:
    #---------------------------------------------------------------------------

    def _filter_changed ( self, filter ):
        """ Handles the 'filter' expression being changed.
        """
        self._block  = ExpressionBlock.from_string( filter )
        self._inputs = dict.fromkeys( self._block.inputs )
        self.updated = True
        self._name_updated()

    #---------------------------------------------------------------------------
    #  Handles the 'enabled' state being changed:
    #---------------------------------------------------------------------------

    def _enabled_changed ( self ):
        """ Handles the 'enabled' state being changed.
        """
        self._name_updated()

    #-- 'ANumericFilter' Class Overrides ---------------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #---------------------------------------------------------------------------

    def evaluate ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        try:
            mask = self._block.evaluate( context )
            if ((mask is None) or 
                issubdtype(mask.dtype, bool) or 
                issubdtype(mask.dtype, int)):
                return mask
            return (mask != 0.0)
        except:
            return None

    #---------------------------------------------------------------------------
    #  Returns whether a specified set of context changes affects the filter:
    #---------------------------------------------------------------------------

    def context_changed ( self, context, names ):
        """ Returns whether a specified set of context changes affects the
            filter.
        """
        if self.enabled:
            inputs = self._inputs
            if inputs is not None:
                for name in names:
                    if name in inputs:
                        return True

        return False

    #-- Private Methods --------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the name being potentially changed:
    #---------------------------------------------------------------------------

    def _name_updated ( self ):
        """ Handles the name being potentially changed.
        """
        if not self._name:
            self.trait_property_changed( 'name', self._name, self.name )

