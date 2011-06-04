# Standard library imports.
import logging

# Enthought library imports.
from traits.api import Instance
from pyface.api import GUI, YES
from pyface.workbench.api import Workbench

from blockcanvas.function_tools.function_library import FunctionLibrary

# Local imports.
from application import Application
from application_window import ApplicationWindow

# Log to stderr.
logging.getLogger().addHandler(logging.StreamHandler())
logging.getLogger().setLevel(logging.DEBUG)

class ApplicationWorkbench(Workbench):
    """ Workbench (ie. Main) class for our application.
    """

    ###########################################################################
    # ApplicationWorkbench traits
    ###########################################################################

    app = Instance(Application)


    ###########################################################################
    # Workbench traits
    ###########################################################################

    # The factory (in this case simply a class) that is used to create
    # workbench windows.
    window_factory = ApplicationWindow

    #### Private interface. ###################################################

    def _exiting_changed(self, event):
        """ Called when the workbench is exiting. """

        #if self.active_window.confirm('Ok to exit?') != YES:
        #    event.veto = True

        return

    def _app_default(self):
        """ Create an application with a minimal library in it...
        """
        function_library = FunctionLibrary(modules=['os'])
        return Application(function_library=function_library)


def main(argv):
    """ A simple example of using the the undo framework in a workbench. """

    # Create the GUI.
    gui = GUI()

    # Create the workbench.
    workbench = ApplicationWorkbench(state_location=gui.state_location)

    window = workbench.create_window(position=(300, 300), size=(400, 300))
    window.open()

    # fixme: This is a little silly...
    window.edit(workbench.app.project.active_experiment)

    # Start the GUI event loop.
    gui.start_event_loop()

    return

if __name__ == '__main__':
    import sys; main(sys.argv)

#### EOF ######################################################################
