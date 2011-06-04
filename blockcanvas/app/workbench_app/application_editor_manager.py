from traits.api import Any

from pyface.workbench.api import EditorManager
from pyface.workbench.traits_ui_editor import TraitsUIEditor


class MyTraitsUIEditor(TraitsUIEditor):
    """ An editor whose content is provided by a traits UI. """

    ##########################################################################
    # TraitsUIEditor traits
    ##########################################################################

    # ??? Wny does this have to be a string?  Can't this be a view.
    # The name of the traits UI view used to create the UI (if not specified,
    # the default traits UI view is used).
    view = Any


class ApplicationEditorManager(EditorManager):
    """ Workbench Editor for an Experiments object.
    """

    ##########################################################################
    # EditorManager traits
    ##########################################################################

    def create_editor(self, window, obj, kind=None):
        """ If kind is a view, we use that as a traits UI view of the object.
            # fixme: Surely there is a more elegant way to arrange this
            #        registry of editors.
        """

        from blockcanvas.app.experiment import Experiment
        from editors.experiment_canvas_editor import  ExperimentCanvasEditor

        # fixme: ?? This fails when it shouldn't because of what appear
        #        to be import path issues.
        #if isinstance(obj,Experiment) and kind in [None,'canvas']:
        if obj.__class__.__name__ == 'Experiment' and kind in [None,'canvas']:
            print 'using the desired editor', obj
            editor = ExperimentCanvasEditor(window=window, obj=obj)
        else:
            print 'using default', obj
            # Default to a traits ui for the object.
            editor = MyTraitsUIEditor(window=window, obj=obj, view=kind)

        print 'editor created', obj
        return editor
