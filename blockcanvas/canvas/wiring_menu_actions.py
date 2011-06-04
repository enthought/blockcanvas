#Enthought Library Imports
from enthought.traits.api import HasTraits, List, Str
from enthought.traits.ui.api import View, Item
from enthought.pyface.action.api import Action


class SuffixDialog(HasTraits):
    """ Dialog for getting the suffix to be added to selected variables """
    suffix = Str()

    view = View(Item("suffix", label="Suffix"),
                title = "Suffix Dialog",
                buttons = ["OK", "Cancel"])


class AddSuffixAction(Action):
    """ Adds a Suffix to a selected variable """
    name = "Add Suffix"

    # For adding suffix to variable names
    view = View( Item('suffix'), buttons=['OK', 'Cancel'] )

    selected_fields = List()

    def perform(self, event):
        dlg = SuffixDialog()
        if dlg.edit_traits(kind="livemodal"):
            suffix = dlg.suffix
            if suffix:
                for field in self.selected_fields:
                    old_text = field.variable.binding
                    if not old_text.isdigit():
                        from enthought.block_canvas.app.scripting import app
                        new_text = old_text + '_' + suffix
                        app.update_function_variable_binding(field.box.graph_node,
                                                             field.variable, new_text)
            self.container.wiring_tool.clear_selection()
        return

class ChangeSuffixAction(Action):
    """ Changes a Suffix on selected variables """
    name = "Change Suffix"

    # For adding suffix to variable names
    view = View( Item('suffix'), buttons=['OK', 'Cancel'] )

    selected_fields = List()

    def perform(self, event):
        dlg = SuffixDialog()
        if dlg.edit_traits(kind="livemodal"):
            suffix = dlg.suffix
            if suffix:
                for field in self.selected_fields:
                    old_text = field.variable.binding
                    if not old_text.isdigit():
                        i = old_text.rfind('_')
                        if i > 0:
                            base = old_text[:i]
                            from enthought.block_canvas.app.scripting import app
                            new_text = base + '_' + suffix
                            app.update_function_variable_binding(field.box.graph_node,
                                                                 field.variable, new_text)
            self.container.wiring_tool.clear_selection()
        return

#EOF
