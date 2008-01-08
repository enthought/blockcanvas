""" Create menus that operate on TableEditors. Useful for making a right-click
    context menu.
"""

# Enthought library imports.
from enthought.traits.api import List, Int
from enthought.traits.ui.api import Handler
from enthought.traits.ui.menu import Action, Menu
from enthought.traits.ui.wx.table_editor import TableEditor as _TableEditor


new_delete_menu = Menu(Action(name="New", action="new_in_table"),
                       Action(name="Delete", action="delete_from_table"))

class TableMenuHandler(Handler):
    """ A Handler that provides for menu options to operate on the selected rows
    """

    # The list of table editors in the View
    table_editors = List(_TableEditor)

    #########################################################################
    # Handler interface
    #########################################################################

    def init(self, info):
        """ Find table editors in the ui object that is passed.
        """

        self.table_editors = [ editor for editor in info.ui._editors
                               if editor.__class__ == _TableEditor ]


    #########################################################################
    # TableMenuHandler interface
    #########################################################################

    def get_focused_editor(self, selection):
        """ If a subclass is handling a view with multiple table editors, it
            must define thise method to determine which table editor to operate
            on. This is due to the limitations of Traits. Should return an index
            into the list of editors.
        """

        return 0

    def new_in_table(self, info, selection):
        """ Adds a new item to the table
        """

        editor = self.table_editors[self.get_focused_editor(selection)]
        if editor is not None:
            editor.add_row(object=editor.create_new_row(),
                           index=editor.selected_index - 1)

    def delete_from_table(self, info, selection):
        """ Removes an item from the table
        """

        editor = self.table_editors[self.get_focused_editor(selection)]
        if editor is not None and not self.is_row_auto_add(selection):
                editor.on_delete()

    def is_row_auto_add(self, selection):
        """ Is the row currently selected the row created by auto_add?
            If auto_add is disabled, return False.
        """

        editor = self.table_editors[self.get_focused_editor(selection)]
        if editor is not None:
            return (editor.model.get_row_count()-1 == editor.selected_index and
                    editor.auto_add)
        else:
            return False