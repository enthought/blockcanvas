# System library imports
import wx

# ETS imports
from enthought.traits.api import Str, Bool
from enthought.traits.ui.wx.editor import Editor
from enthought.traits.ui.wx.basic_editor_factory import BasicEditorFactory


class _SearchEditor(Editor):

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """

        style = 0
        if self.factory.enter_set:
            style = wx.TE_PROCESS_ENTER
        self.control = wx.SearchCtrl(parent, -1, value=self.value, style=style)
        
        self.control.SetDescriptiveText(self.factory.text)
        self.control.ShowSearchButton(self.factory.search_button)
        self.control.ShowCancelButton(self.factory.cancel_button)
        
        if self.factory.auto_set:
            wx.EVT_TEXT(parent, self.control.GetId(), self.update_object)
            
        if self.factory.enter_set:
            wx.EVT_TEXT_ENTER(parent, self.control.GetId(), self.update_object)

        wx.EVT_SEARCHCTRL_SEARCH_BTN(parent, self.control.GetId(),
                                     self.update_object)
        wx.EVT_SEARCHCTRL_CANCEL_BTN(parent, self.control.GetId(),
                                     self.clear_text)

    #---------------------------------------------------------------------------
    #  Handles the user entering input data in the edit control:
    #---------------------------------------------------------------------------

    def update_object(self, event):
        """ Handles the user entering input data in the edit control.
        """

        if not self._no_update:
            self.value = self.control.GetValue()
            if self.factory.search_event_trait != '':
                setattr(self.object, self.factory.search_event_trait, True)

    def clear_text(self, event):
        """ Handles the user pressing the cancel search button.
        """
        
        if not self._no_update:
            self.control.SetValue("")
            self.value = ""
            if self.factory.search_event_trait != '':
                setattr(self.object, self.factory.search_event_trait, True)

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

    # Is user input set on every keystroke?
    auto_set = Bool(True)

    # Is user input set when the Enter key is pressed?
    enter_set = Bool(False)

    # Whether to show a search button on the widget
    search_button = Bool(True)

    # Whether to show a cancel button on the widget
    cancel_button = Bool(False)

    # Fire this event on the object whenever a search should be triggered,
    # regardless of whether the search term changed
    search_event_trait = Str
