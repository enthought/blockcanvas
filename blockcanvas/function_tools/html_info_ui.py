""" HTML Window UI for displaying text, html and function doc-strings.

    fixme: This module may be better located somewhere else.
"""

# Standard Library imports
import platform

# Enthought library imports.
from traits.api import HasTraits, Str
from traitsui.api import View, Item
from traitsui.menu import NoButtons

# Try using the fancy new IE widget if on windows.
# Note: The IE widget takes about about 25 MB of memory on its own, so it
#       is a pretty hefty overhead to add to the application's memory usage.
#       At some point, we may want to switch to the RichTextCtrl.
# fixme: Need to check traits.ui backend.
#        How do you ask a traits.ui toolkit() what it's backend is?
if platform.system() == 'Windows':
    from traitsui.wx.extra.windows.ie_html_editor import \
        IEHTMLEditor as HTMLEditor
    html_editor = HTMLEditor()
else:
    from traitsui.api import HTMLEditor
    html_editor = HTMLEditor(format_text=False)


# Local imports
import rest_html
from python_function_info import PythonFunctionInfo

html_view = View(
                 Item('_html',
                      show_label=False,
                      editor=html_editor,
                      springy= True,
                      resizable=True,
                 ),
                 id='help_view',
                 resizable=True,
                 buttons=NoButtons,
            )

class HtmlInfoUI(HasTraits):
    """ Model for the a window to display Html in an application.

        This widget has the following APIs:
            set_text(text):
                display raw text.
            set_html(text):
                display html formatted text.
            set_function_help(function_name, module_name):
                display an htmlified version of the doc-string for the
                given function.
    """

    ##########################################################################
    # HtmlInfoWindow traits
    ##########################################################################

    # The html that is displayed in the lower panel of the search window.
    # fixme: This needs to be split out into another application level object.
    _html = Str("<html>\n<body>\n<em>Select a function</em>\n</body>\n</html>")

    view = html_view

    def set_function_help(self, function_name, module_name):
        """ Display Beautified version of a function doc-string.

            The function is specified as the name of the function and the
            module name for the function.
        """
        func = PythonFunctionInfo(name=function_name, module=module_name)

        if func.doc_string == "":
            self.set_text("No information about this function.")
        else:
            self._html = rest_html.convert_function_info(func.name,
                                                         func.doc_string)

    def set_text(self, text):
        """ Display a message in the help window.

            The text message is wrapped in html tags so that it displays
            correctly in the html window.
        """
        self._html = self._htmlify(text)

    def set_html(self, html):
        """ Display html text without modification into the window.
        """
        self._html = html


    ### private methods ######################################################


    def _htmlify(self, text):
        """ Add <html> and <body> tags around text so that it is valid html.
        """
        return "<html>\n<body>\n%s\n</body>\n</html>" % text


if __name__ == "__main__":
    widget = HtmlInfoDisplay()
    html_view.height = .3
    html_view.width = .3
    widget.edit_traits(view=html_view)
