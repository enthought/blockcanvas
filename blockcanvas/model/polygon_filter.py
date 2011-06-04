#-------------------------------------------------------------------------------
#
#  NumericModel filter for determining the set of points within a specified
#  polygon.
#
#  Written by: Brandon DuRette
#
#  Date: 10/01/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from numpy \
    import array, shape

from enable.kiva.agg \
    import points_in_polygon  # FIXME: bad dependency

from traits.api \
    import List, String, Tuple

from numeric_model \
    import NumericFilter

#-------------------------------------------------------------------------------
#  'PolygonFilter' class:
#-------------------------------------------------------------------------------

class PolygonFilter ( NumericFilter ):

    # The points in the polygon:
    points = List

    # The numeric item that provides the x values:
    x_value = String

    # The numeric item that provides the y values:
    y_value = String

    #---------------------------------------------------------------------------
    #  Public 'NumericFilter' interface:
    #---------------------------------------------------------------------------

    def _eval ( self, model ):
        """ Evaluates the result of the filter for the specified model.
        """
        if len( self.points ) == 0:
            return None

        points = array( zip( getattr( model, self.x_value ),
                             getattr( model, self.y_value ) ) )

        result = None
        for items in self.points:
            pip = points_in_polygon( points, array( items ) )
            if result is None:
                result = pip
            else:
                result = result | pip

        return result

    #---------------------------------------------------------------------------
    #  Trait handlers:
    #---------------------------------------------------------------------------

    def _points_changed (  self ):
        """ Handles the points trait being changed.
        """
        self.updated = True

    def _points_items_changed (  self ):
        """ Handles points being added or removed from points.
        """
        self.updated = True

