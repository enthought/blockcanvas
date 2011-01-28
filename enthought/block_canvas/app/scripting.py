""" Module for accessing global objects in the application for scripting.

    Currently, a variable named "app" is set here by the app.Application
    object in its __init__.

    Other code can call:

        scripting.app.add_function_to_execution_model(blah)

    and the like to access functions on the app.

"""
