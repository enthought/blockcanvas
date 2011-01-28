""" A set of simple functions used in testing the FunctionCall, Callable classes.
"""

global_value = 4

def empty():
    pass

def simple(a,b):
    x,y=a,b
    return x,y

# using this in some places...
foo=simple

def with_defaults(a,b=3):
    x,y=a,b
    return x,y

def with_defaults_none(a,b=None):
    x,y=a,b
    return x,y

def with_arg_defaults(a,b=3,c=global_value):
    x,y,z=a,b,c
    return x,y,z

def with_varargs(a,b=3,*args):
    x=a
    y=b
    z=args[:1]
    return x,y,z

def with_kwargs(a,b=3, **kw):
    x=a
    y=b
    z=args[:1]
    return x,y,z

def with_varargs_kwargs(a,b=3,*args, **kw):
    x=a
    y=b
    z=args[:1]
    zz=kw
    return x,y,z,zz

def no_return(a,b):
    pass


def empty_return(a,b):
    x,y = a,b
    return
