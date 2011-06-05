#-------------------------------------------------------------------------------
#
#  Defines an array value whose value is determined by an expression
#  evaluated on a context.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" Defines an array value whose value is determined by an expression
    evaluated on a context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import Property, Expression

from codetools.blocks.api \
    import Expression as ExpressionBlock

from a_numeric_item \
    import ANumericItem

from context_modified \
    import ContextModified

from error \
    import NumericItemError

#-------------------------------------------------------------------------------
#  'EvaluatedItem' class:
#-------------------------------------------------------------------------------

class EvaluatedItem ( ANumericItem ):
    """ Defines an array value whose value is determined by an expression
        evaluated on a context.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the context trait for this item:
    name = Property

    # Expression used to compute the numeric value:
    evaluate = Expression

    # The current value of the associated numeric array:
    data = Property

    #-- Property Implementations -----------------------------------------------

    #---------------------------------------------------------------------------
    #  Implementation of the 'data' property:
    #---------------------------------------------------------------------------

    def _get_data ( self ):
        if self._data is None:
            try:
                if self._busy:
                    raise NumericItemError( "Recursive definition involving "
                                            "the value of '%s'" % self.name )
                self._busy = True
                self._data = self._block.evaluate( self.context )
            finally:
                self._busy = False

        return self._data

    #---------------------------------------------------------------------------
    #  Implementation of the 'name' property:
    #---------------------------------------------------------------------------

    def _get_name ( self ):
        return self._name or self.evaluate

    def _set_name ( self, name ):
        old = self.name
        if name != old:
            self._name = name
            self._data = None
            if self.context is not None:
                self.context.post_context_modified(
                    ContextModified( removed = [ old ], added   = [ name ] )
                )

    #-- Event Handlers ---------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the 'evaluate' trait being changed:
    #---------------------------------------------------------------------------

    def _evaluate_changed ( self, evaluate ):
        """ Handles the 'evaluate' trait being changed.
        """
        self._block  = ExpressionBlock.from_string( evaluate )
        self._inputs = dict.fromkeys( self._block.inputs )
        self._data   = None
        if self.context is not None:
            self.context.post_context_modified(
                ContextModified( modified = [ self.name ] )
            )

    #-- Private Methods --------------------------------------------------------

    #---------------------------------------------------------------------------
    #  Handles the data associated with this item being changed:
    #---------------------------------------------------------------------------

    def _context_modified_changed_for_context ( self, event ):
        """ Handles the data associated with this item being changed.
        """
        inputs = self._inputs
        if inputs is not None:
            for name in event.all_modified:
                if name in inputs:
                    self._data = None
                    self.context.post_context_modified(
                        ContextModified( modified = [ self.name ] )
                    )
                    break

