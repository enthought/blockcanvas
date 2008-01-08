from wx import SearchCtrl, EVT_TEXT

from enthought.traits.api import Str
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.basic_editor_factory import BasicEditorFactory

class _SearchEditor(Editor):

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """

        self.control = SearchCtrl(parent, -1, value=self.value)
        self.control.SetDescriptiveText(self.factory.text)
        self.control.ShowSearchButton(True)
        self.control.ShowCancelButton(False)
        EVT_TEXT(parent, self.control.GetId(), self.update_object)

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user entering input data in the edit control.
        """

        if not self._no_update:
            self.value = self.control.GetValue()

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """

        if self.control.GetValue() != self.value:
            self._no_update = True
            self.control.SetValue(self.str_value)
            self._no_update = False


class SearchEditor(BasicEditorFactory):
    """ wxPython editor factory for Search Editor.
    """

    # The editor class to be created:
    klass = _SearchEditor

    # The descriptive text for the widget
    text = Str("Search")