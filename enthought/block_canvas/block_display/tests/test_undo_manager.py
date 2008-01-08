# Standard library imports
import unittest

# Enthought library imports
from enthought.traits.api import TraitError

# Local imports
from enthought.block_canvas.block_display.undo_manager import UndoManager

class UndoManagerTestCase(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.man = UndoManager(type=str)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # UndoManagerTestCase interface
    ##########################################################################

    def test_helper(self):
        self.man.clear()
        self.man.push("t")
        self.man.push("tz")
        self.man.push("foo")

    def test_push(self):
        """ Does pushing objects work?
        """
        self.test_helper()
        self.assertEqual(self.man._stack, ["t", "tz", "foo"])

    def test_pop(self):
        """ Does popping work?
        """
        self.test_helper()
        self.man.pop()
        self.man.pop()
        self.assertEqual(self.man._stack, ["t"])

    def test_push_type_check(self):
        """ Does type checking for pushing work?
        """
        self.man.clear()
        self.failUnlessRaises(TraitError, self.man.push, 1)

    def test_undo(self):
        """ Does undo work?
        """
        self.test_helper()
        s = self.man.undo()
        self.assertEqual(s, "foo")
        s = self.man.undo()
        self.assertEqual(s, "tz")
        s = self.man.undo()
        self.assertEqual(s, "t")

    def test_undo_empty_stack(self):
        """ Does undo work if stack is empty?
        """
        self.man.clear()
        s = self.man.undo()
        self.assertEqual(s, None)

    def test_redo(self):
        """ Does redo work?
        """
        self.test_helper()
        self.man.undo()
        self.man.undo()
        self.man.undo()
        self.man.redo()
        self.man.redo()
        s = self.man.redo()
        self.assertEqual(s, "foo")

    def test_redo_emtpy_stack(self):
        """ Does redo work if the stack is empty?
        """
        self.man.clear()
        s = self.man.redo()
        self.assertEqual(s, None)

if __name__ == '__main__':
    unittest.main()