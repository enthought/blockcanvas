# Enthought library imports
from traits.api import Interface


class ICanvasNodeFactory(Interface):
    """ A factory which transforms arbitrary objects into Enable components
        for use on the canvas.
    """

    #########################################################################
    # ICanvasNodeFactory interface
    #########################################################################

    def make_component(self, node, old=None, old_position=[]):
        """ Given an object 'node', return an Enable Component which represents
            it. If old is supplied, apply settings to the new component from the
            old component (except position). Position is supplied with the
            old_position keyword (safer because Components have their positions
            set to 0 when removed from a container).
        """
