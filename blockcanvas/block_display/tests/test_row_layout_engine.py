# Standard imports
import unittest, os
from random import randint

# Enthought library imports
from traits.api import push_exception_handler, pop_exception_handler

# Application imports
from enthought.block_canvas.block_display.execution_model import ExecutionModel
from enthought.block_canvas.block_display.block_graph_controller import BlockGraphController


# Module-level setup and teardown.
def setup():
    push_exception_handler(handler=lambda *args, **kwds: None, reraise_exceptions=True)

def teardown():
    pop_exception_handler


class RowLayoutEngineTestCase(unittest.TestCase):

    #---------------------------------------------------------------------------
    # TestCase interface
    #---------------------------------------------------------------------------

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.code = 'from enthought.block_canvas.debug.my_operator import mul, add\n' \
                    'a = mul(1,2)\n' \
                    'b = mul(5,6)\n' \
                    'c = add(a,b)'
        self.model = ExecutionModel.from_code(self.code)
        self.controller = BlockGraphController(execution_model=self.model)
        self.file_path = 'temp.pickle'

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        if os.path.isfile(self.file_path):
            os.remove(self.file_path)

    #---------------------------------------------------------------------------
    # RowLayoutEngineTestCase interface
    #---------------------------------------------------------------------------

    #def test_layout_persistence(self):
    #    """ Is the layout saved and loaded properly?
    #    """

    #    # Layout the nodes and set some test positions
    #    self.controller.layout_engine.clear_history()
    #    self.controller.update_canvas()
    #    desired = {}
    #    for block, node in self.controller.layout_engine._nodes.items():
    #        pos = [ randint(0, 100), randint(0, 100) ]
    #        desired[block] = pos
    #        node.position = pos

    #    # Save the positions
    #    self.controller.layout_engine.save_layout(self.file_path)

    #    # Load the positions and make sure that nodes are put in the correct
    #    # place when update_canvas (and thus update_nodes) is called
    #    self.controller.layout_engine.load_layout(self.file_path)
    #    self.controller.update_canvas()
    #    for block, node in self.controller.layout_engine._nodes.items():
    #        self.assertEqual(node.position, desired[block])

    def test_rows(self):
        """ Is the correct hierarchy produced? """

        rows = self.controller.layout_engine.organize_rows(self.model.dep_graph)

        # There should be two rows, the first two statements in the first row
        # the last statement in the last row
        assert self.model.statements[0] in rows[0]
        assert self.model.statements[1] in rows[0]
        assert self.model.statements[-1] in rows[-1]

    def test_empty(self):
        """ Do we handle incorrect input correctly? """

        rows = self.controller.layout_engine.organize_rows({})
        assert rows == []

if __name__ == '__main__':
    #import nose
    #nose.main()
    unittest.main()
