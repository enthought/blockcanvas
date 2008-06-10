from wx import SearchCtrl, EVT_TEXT, EVT_SEARCHCTRL_CANCEL_BTN

from enthought.traits.api import Str, Bool
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.basic_editor_factory import BasicEditorFactory

class _SearchEditor(Editor):

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """

        self.control = SearchCtrl(parent, -1, value=self.value)
        self.control.SetDescriptiveText(self.factory.text)
        self.control.ShowSearchButton(self.factory.searchButton)
        self.control.ShowCancelButton(self.factory.cancelButton)
        EVT_TEXT(parent, self.control.GetId(), self.update_object)
        EVT_SEARCHCTRL_CANCEL_BTN(parent, self.control.GetId(), self.clear_text)

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user entering input data in the edit control.
        """

        if not self._no_update:
            self.value = self.control.GetValue()

    def clear_text(self, event):
        """ Handles the user pressing the cancel search button.
        """
        
        if not self._no_update:
            self.control.SetValue("")
            self.value = ""

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

    # Whether to show a search button on the widget
    searchButton = Bool(True)

    # Whether to show a cancel button on the widget
    cancelButton = Bool(False)
