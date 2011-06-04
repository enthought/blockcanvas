import unittest

from traits.api import Any, HasTraits, Enum, implements

from enthought.block_canvas.canvas.selection_manager import SelectionManager
from enthought.block_canvas.canvas.i_selectable import ISelectable

class Event(HasTraits):
    """
    """
    control_down = False
    alt_down = False
    shift_down = False

class SelectableItem(HasTraits):
    """ Dummy class used as a selectable item in tests.
    """
    implements(ISelectable)

    # Is this item currently selected?  coselected means the item is selected,
    # but it isn't the "primary" selected item.
    selection_state = Enum('unselected', 'selected', 'coselected')

    # The graph node.
    graph_node = Any()


class SelectionManagerTestCase(unittest.TestCase):

    ###########################################################################
    # TestCase Interface
    ###########################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.selection_manager = SelectionManager()

    def tearDown(self):
        unittest.TestCase.tearDown(self)


    ###########################################################################
    # Test for selection list.
    ###########################################################################

    def test_single_selection_assigment(self):
        """ Is 1st item in selection list marked 'selected'?
        """
        selection = [SelectableItem()]
        self.selection_manager.selection = selection

        self.assertEqual(selection[0].selection_state, 'selected')

    def test_multi_selection_assignment(self):
        """ Is 2nd item in selection list marked 'coselected'?
        """
        selection = [SelectableItem(), SelectableItem()]
        self.selection_manager.selection = selection

        self.assertEqual(selection[0].selection_state, 'selected')
        self.assertEqual(selection[1].selection_state, 'coselected')

    def test_single_selection_replacement(self):
        """ Are items replaced during selection assignment marked 'unselected'?
        """
        old_selection = [SelectableItem(), SelectableItem()]
        self.selection_manager.selection = old_selection

        selection = [SelectableItem()]
        self.selection_manager.selection = selection

        for item in old_selection:
            self.assertEqual(item.selection_state, 'unselected')

        self.assertEqual(selection[0].selection_state, 'selected')

    def test_remove_first_item(self):
        """ Try removing the first item in the selection list?
        """
        items = [SelectableItem(), SelectableItem()]
        self.selection_manager.selection = items

        del self.selection_manager.selection[0]

        desired = ['unselected', 'selected']
        for item, state in zip(items, desired):
            self.assertEqual(item.selection_state, state)

    def test_remove_only_item(self):
        """ Try removing the only item in the selection list?
        """
        items = [SelectableItem()]
        self.selection_manager.selection = items

        del self.selection_manager.selection[0]

        desired = ['unselected']
        for item, state in zip(items, desired):
            self.assertEqual(item.selection_state, state)

    def test_remove_middle_item(self):
        """ Try removing the first item in the selection list?
        """
        items = [SelectableItem(), SelectableItem(), SelectableItem(),
                 SelectableItem()]
        self.selection_manager.selection = items

        desired = ['selected', 'coselected', 'coselected', 'coselected']
        for item, state in zip(items, desired):
            self.assertEqual(item.selection_state, state)

        del self.selection_manager.selection[1:3]

        desired = ['selected', 'unselected', 'unselected', 'coselected']
        for item, state in zip(items, desired):
            self.assertEqual(item.selection_state, state)

    def test_replace_middle_item(self):
        """ Try removing the first item in the selection list?
        """
        items = [SelectableItem(), SelectableItem(), SelectableItem(),
                 SelectableItem()]
        self.selection_manager.selection = items

        desired = ['selected', 'coselected', 'coselected', 'coselected']
        for item, state in zip(items, desired):
            self.assertEqual(item.selection_state, state)

        new_items = [SelectableItem(), SelectableItem()]
        self.selection_manager.selection[1:3] = new_items

        desired = ['selected', 'unselected', 'unselected', 'coselected']
        for item, state in zip(items, desired):
            self.assertEqual(item.selection_state, state)

        desired = ['coselected', 'coselected']
        for item, state in zip(new_items, desired):
            self.assertEqual(item.selection_state, state)

    def test_insert_first_item(self):
        """ Insert item at beginning?
        """
        items = [SelectableItem(), SelectableItem()]
        self.selection_manager.selection = items

        desired = ['selected', 'coselected']
        for item, state in zip(items, desired):
            self.assertEqual(item.selection_state, state)

        new_item = SelectableItem()
        self.selection_manager.selection.insert(0, new_item)
        self.assertEqual(new_item.selection_state, 'selected')

        desired = ['coselected', 'coselected']
        for item, state in zip(items, desired):
            self.assertEqual(item.selection_state, state)

    ###########################################################################
    # Test select_item
    ###########################################################################

    def test_select_item_normal(self):
        """ Select item works when selection empty?
        """

        item = SelectableItem()
        self.selection_manager.select_item(item)

        self.assertEqual(item.selection_state, 'selected')
        self.assertEqual(len(self.selection_manager.selection), 1)

        # Test toggle unselected.
        self.selection_manager.select_item(item)
        self.assertEqual(item.selection_state, 'unselected')
        self.assertEqual(len(self.selection_manager.selection), 0)

    def select_item_add_when_empty_helper(self, event):
        """ Select item with add mode and selection emtpy
        """

        self.selection_manager.add_subtract_mode = True

        item = SelectableItem()
        self.selection_manager.select_item(item)
        self.assertEqual(item.selection_state, 'selected')
        self.assertEqual(len(self.selection_manager.selection), 1)

        self.selection_manager.add_subtract_mode = False

        # Test toggle unselected.
        self.selection_manager.select_item(item)
        self.assertEqual(item.selection_state, 'unselected')
        self.assertEqual(len(self.selection_manager.selection), 0)


    def select_item_add_when_full_helper(self, event):
        """ Select item work when selection is full
        """

        self.selection_manager.add_subtract_mode = True

        self.selection_manager.selection = [SelectableItem()]
        item = SelectableItem()
        self.selection_manager.select_item(item)
        self.assertEqual(item.selection_state, 'selected')
        self.assertEqual(len(self.selection_manager.selection), 2)

        self.selection_manager.add_subtract_mode = False

        # Test toggle unselected.
        self.selection_manager.select_item(item)
        self.assertEqual(item.selection_state, 'unselected')
        self.assertEqual(len(self.selection_manager.selection), 1)


if __name__ == '__main__':
    unittest.main()
