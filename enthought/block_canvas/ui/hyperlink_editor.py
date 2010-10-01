from wx import HL_ALIGN_CENTRE
from wx.lib.hyperlink import (HyperLinkCtrl, EVT_HYPERLINK_LEFT,
                              EVT_HYPERLINK_MIDDLE, EVT_HYPERLINK_RIGHT)

from enthought.traits.api import Str
from enthought.traits.ui.api import BasicEditorFactory
from enthought.traits.ui.wx.editor import Editor

class _HyperlinkEditor(Editor):

    def init(self, parent):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """

        self.control = HyperLinkCtrl(parent, -1, self.factory.label,
                                     style=HL_ALIGN_CENTRE)
        self.control.AutoBrowse(False)
        self.control.SetColours("BLUE", "BLUE", "BLUE")
        self.control.SetUnderlines(True, True, True)
        self.control.SetBold(False)
        self.set_tooltip()

        EVT_HYPERLINK_LEFT(parent, self.control.GetId(),
                           self.update_object)
        EVT_HYPERLINK_MIDDLE(parent, self.control.GetId(),
                             self.update_object)
        EVT_HYPERLINK_RIGHT(parent, self.control.GetId(),
                            self.update_object)

        self.control.UpdateLink()

    #---------------------------------------------------------------------------
    #  Handles the user clicking the button by setting the value on the object:
    #---------------------------------------------------------------------------

    def update_object (self, event):
        """ Handles the user clicking the button
        """

        self.value = 1

    #---------------------------------------------------------------------------
    #  Updates the editor when the object trait changes external to the editor:
    #---------------------------------------------------------------------------

    def update_editor ( self ):
        """ Updates the editor when the object trait changes externally to the
            editor.
        """

        pass

class HyperlinkEditor(BasicEditorFactory):
    """ wxPython editor factory for Hyperlink Editor.
    """

    # The editor class to be created:
    klass = _HyperlinkEditor

    # Button text
    label = Str("Link")
