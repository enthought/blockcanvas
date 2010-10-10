= Don't make test directory a package = 

There is a bug in pkgutil that will not find local modules in a directory if 
there is also an __init__.py in that directory. This causes the PythonFunction 
and FunctionCall (and perhaps other) tests to fail if we put an __init__.py in 
this tests directory.  While we should fix pkgutil, the short term fix is to 
just not make this directory a package.
