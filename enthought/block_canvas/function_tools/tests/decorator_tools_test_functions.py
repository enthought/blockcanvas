""" Functions for testing decorator_tools methods
"""

# ETS imports
from enthought.units.api import has_units


# The following two functions are the same code, except for the first one being
# decorated.
@has_units
def add(a,b):
    ''' Add two arrays in ft/s and convert them to m/s.

    Parameters
    ----------
    a : array : units=ft/s
        An array
    b : array : units=ft/s
        Another array

    Returns
    -------
    c : array : units=m/s
        c = a + b
    '''
    return (a+b)*0.3048


def non_decorated_add(a,b):
    ''' Add two arrays in ft/s and convert them to m/s.

    Parameters
    ----------
    a : array : units=ft/s
        An array
    b : array : units=ft/s
        Another array

    Returns
    -------
    c : array : units=m/s
        c = a + b
    '''
    return (a+b)*0.3048

