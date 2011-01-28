# Local Imports
from callable_info import CallableInfo
from python_function_info import PythonFunctionInfo


class ExtensionFunctionInfo(PythonFunctionInfo):
    """ExtensionFunctionInfo represents a Python Extension function, i.e.  one
    without python source code available.
    """

    def __init__(self, **traits):
        # Avoid the PythonFunctionInfo.__init__ since it assumes that it is
        # actually a defined-in-Python function.
        CallableInfo.__init__(self, **traits)

    # FIXME: Actually flesh this out

