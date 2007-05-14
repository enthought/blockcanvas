#-------------------------------------------------------------------------------
#  
#  Abstract base class for all numeric context filters.
#  
#  Written by: David C. Morrill
#  
#  Date: 03/07/2007
#  
#  (c) Copyright 2007 by Enthought, Inc.
#  
#-------------------------------------------------------------------------------

""" Abstract base class for all numeric context filters.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api \
    import HasPrivateTraits, Event, Bool, Int, RGBAColor

from enthought.util.scipyx \
    import not_equal
    
#-------------------------------------------------------------------------------
#  'ANumericFilter' class (abstract base class):
#-------------------------------------------------------------------------------

class ANumericFilter ( HasPrivateTraits ):
    """ Defines an abstract base class for all NumericContext filters.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Name of the filter (implemented as a Property in each subclass):
    # name = Property

    # Event fired when filter is modified:
    updated = Event

    # Is the filter enabled or disabled?
    enabled = Bool( True, event = 'modified' )

    # Should the value, isbit and color traits be used?
    use_value = Bool( False, event = 'modified' )

    # Value to scale filter results by:
    value = Int( 1, event = 'modified' )

    # Is the value a bit number?
    is_bit = Bool( False, event = 'modified' )

#-- View related ---------------------------------------------------------------

    # Foreground color:
    foreground_color = RGBAColor( 'black', event = 'modified' )

    # Background color:
    background_color = RGBAColor( 'white', event = 'modified' )

    #---------------------------------------------------------------------------
    #  Handles the 'modified' pseudo-event being fired:
    #---------------------------------------------------------------------------

    def _modified_changed ( self ):
        """ Handles the 'modified' pseudo-event being fired.
        """
        self.updated = True

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #---------------------------------------------------------------------------

    def __call__ ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        if self.enabled:
            result = self.evaluate( context )
            if (not self.use_value) or (result is None):
                return result
            result = not_equal( result, 0 )
            scale  = self.value
            if self.is_bit:
                scale = (1 << self.value)
            if scale == 1:
                return result
            return result * scale
        return None

    #---------------------------------------------------------------------------
    #  Sets the 'updated' trait True if the filter is affected by a change
    #  to any of the 'names' values in 'context'. Also returns whether the
    #  'updated' trait was set or not:
    #---------------------------------------------------------------------------

    def context_has_changed ( self, context, names ):
        """ Handles an update to the specified names within a specified context.
        """
        if self.context_changed( context, names ):
            self.updated = True
            return True

        return False

    #-- Overriddable Methods ---------------------------------------------------

    #---------------------------------------------------------------------------
    #  Evaluates the result of the filter for the specified context:
    #
    #  This method should be overridden by subclasses.
    #---------------------------------------------------------------------------

    def evaluate ( self, context ):
        """ Evaluates the result of the filter for the specified context.
        """
        return None

    #---------------------------------------------------------------------------
    #  Returns whether an update to a context affects the filter. It should
    #  return True if a change to any of the 'name' values in the specified
    #  'context' affects the filter, and False otherwise.
    #
    #  This method can be optionally overridden by a subclass if the filter
    #  it defines has dependencies on the contents of a context.
    #---------------------------------------------------------------------------

    def context_changed ( self, context, names ):
        """ Handles an update to the specified names within a specified context.
        """
        return False

    #---------------------------------------------------------------------------
    #  Returns the string representation of the filter:
    #
    #  This method can be optionally overridden by subclasses if they wish to
    #  return a different string representation of the filter.
    #---------------------------------------------------------------------------

    def __str__ ( self ):
        """ Returns the string representation of the filter.
        """
        return self.name

