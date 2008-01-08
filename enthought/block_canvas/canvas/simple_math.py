""" Define a few simple math functions to avoid dependency on numpy.

    The functions provide facilities for clipping a value to a range
    as well as a number of functions for that treat 2 element lists
    as vectors.  The main purpose of this latter set is for testing
    the distance of a point from a line (useful in hit testing).
"""

from math import sqrt

def clip(value, low, high):
    """ Clip value so that it is betwen low and high values.
    
        Example:
            >>> clip(5, 0, 10)
            5
            >>> clip(-5, 0, 10)
            0
            >>> clip(15, 0, 10)
            10
    """    
    result = value
    if value < low:
        result = low                
    elif value > high:
        result = high

    return result

def dot(pt1, pt2):
    """ Calculate the dot product of two 2D vectors.
    
        pt1 and pt2 can be any sort of indexed sequence.
        
        Example:            
            >>> dot([0,1], [1,0]) # orthogonal vectors have zero projection.
            0.0
            >>> dot([1,1], [1,0]) # 45 degree angle has projection of 1.
            1.0
    """
    return float(pt1[0]*pt2[0] + pt1[1]*pt2[1])
    
def mag(pt):
    """ Calculate the magnitude of a vector.
    
        Example:
            >>> mag([3,4])
            5.0
            >>> mag([3,-4]) # ignore 
            5.0
    """    
    return sqrt(pt[0]**2+pt[1]**2)

def subtract(pt1, pt2):
    """ Subtract one 2D vector from another.
    
        Example:
            >>> subtract([2,1],[.5,.1])
            [1.5, 0.90000000000000002]
    """
    return [pt1[0]-pt2[0], pt1[1]-pt2[1]]

def point_in_box(pt1, pt2, mouse, tolerance=0):    
    """ Returns if the point x,y is in the box.
    
        Inclusive on the lower end, excluive on the upper end.
        
        tolerance -- default 0.  It expands the box the given amount.
    
        examples:
            >>> point_in_box([0,0], [1,1], [.5,.5])
            True
            >>> point_in_box([0,0], [1,1], [1.1,.5])
            False
    """
    lower_left = (min(pt1[0], pt2[0]) - tolerance, 
                  min(pt1[1], pt2[1]) - tolerance)
    upper_right = (max(pt1[0], pt2[0]) + tolerance, 
                   max(pt1[1], pt2[1]) + tolerance)    
    b = subtract(upper_right, lower_left)
    dx, dy = subtract(mouse, lower_left)
    
    return (dx >= 0) and (dx < b[0]) and (dy >= 0) and (dy < b[1])

    
def distance_to_line(pt1, pt2, mouse):
    """ Calculate the distance of the mouse from lint pt1->pt2
        All three inputs are 2 element lists of x,y pairs.    

        examples:
            >>> distance_to_line([0,0],[1,1],[.5,.5])
            0.0
            >>> distance_to_line([0,0],[1,1],[0,0])
            0.0
            >>> distance_to_line([0,0],[1,1],[0,1])
            0.70710678118654757
            >>> distance_to_line([10,1],[20,5],[15,14])
            10.213243599737853
            
        Implementation from:
            http://msdn2.microsoft.com/en-us/library/ms969920.aspx        
    """
    a = subtract(mouse, pt1)
    b = subtract(pt2, pt1)
    sc = dot(a,b)/dot(b,b)    
    c = [b[0]*sc, b[1]*sc]
    normal = subtract(a,c)
    
    return mag(normal)

    
if __name__ == "__main__":
    
    import doctest
    doctest.testmod()
    
    

    