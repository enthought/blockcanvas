# Enthought Library imports
from enthought.traits.ui.api import View, Item, InstanceEditor
from enthought.block_canvas.ui.source_editor import MarkableSourceEditor

# Local imports
from traits_ui_view import TraitsUIView

                
class ExperimentCodeView(TraitsUIView):
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
                    Item( 'object.exec_model.code',
                          label      = 'Code',
                          id         = 'code',
                          editor     = MarkableSourceEditor( dim_lines = 'dim_lines',
                                                dim_color = 'dim_color',
                                                squiggle_lines = 'squiggle_lines',
                                                             ),
                          dock       = 'horizontal',
                          show_label = False
                    ),
               )
        return view
