
# Enthought Library imports
from enthought.traits.api import HasTraits, Instance, Property, Any
from enthought.traits.ui.api import View, Item, InstanceEditor
from enthought.pyface.workbench.api import View as WorkbenchView

# Block Canvas imports
from enthought.block_canvas.app.project import Project
from enthought.block_canvas.context.ui.context_variable import ContextVariableList

# Local imports
from traits_ui_view import TraitsUIView

# fixme: Convert to a handler.
class ExperimentContextModelView(HasTraits):
    """ Simple Model View that translates the context into a
        ContextVariableList.
    """

    # fixme: This isn't working because of relative import issues.
    model = Any # Instance(Experiment)

    # A ContextVariableList wrapper around the experiment's data context.
    context = Property(depends_on='model.context')

    def __init__(self, model):
        self.model = model

    def _get_context(self):
        context_viewer = ContextVariableList(context=self.model.context)
        return context_viewer

#    @on_trait_change('context:execute_for_names')
#    def execute_for_names(self, names):
#        """ When the user clicks the "Execute" menu item on the context UI,
#        actually execute the code.
#        """
#        # XXX: undo/redo
#        exec_context = self.model.exec_context
#        if len(names) == 0:
#            # Don't actually pass this in. Use None instead. Counter-intuitive
#            # in code, but from the UI, it makes sense.
#            names = None
#        exec_context.execute_for_names(names)
#
#    @on_trait_change('context:delete_names')
#    def delete_names(self, object, name, old, new):
#        """ When the user clicks the "Delete" menu item on the context UI,
#        actually perform the deletion.
#        """
#        # XXX: undo/redo
#        exec_context = self.model.exec_context
#        exec_context.defer_events = True
#        for name in new:
#            del exec_context[name]
#        exec_context.defer_events = False

class ExperimentContextView(TraitsUIView):
    """ Create a view of the active project's context.

        fixme: Need to hook up listeners to the active project context.
    """


    ###########################################################################
    # 'TraitsUIView' interface.
    ###########################################################################

    def _view_default(self):
        """ This view uses a ModelView to translate the view into
            ContextVariableList
        """
        view = View(
                    Item('context',
                         label = 'Context',
                         id = 'context_table',
                         editor = InstanceEditor(),
                         style = 'custom',
                         dock = 'horizontal',
                         show_label = False,
                    ),
                    model_view=ExperimentContextModelView,
               )
        return view
