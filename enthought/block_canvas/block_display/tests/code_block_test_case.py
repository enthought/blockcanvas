import nose

raise nose.SkipTest("CodeBlock is deprecated")

import unittest

from enthought.block_canvas.block_display.code_block import CodeBlock
from enthought.blocks.api import Block, unparse

class CodeBlockTestCase(unittest.TestCase):
    
    def test_insert_into_empty(self):
        
        code = ""
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "x = 1"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 0)
        self.assertEqual(last_line, 0)
        self.assertEqual(lines, 1)

    def test_insert_before_line(self):
        
        code = "y = 2"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "x = 1\ny = 2"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 0)
        self.assertEqual(last_line, 0)
        self.assertEqual(lines, 1)
        
    def test_insert_after_line(self):
        
        code = "y=2"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "y=2\nx=1"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 1)
        

    def test_insert_in_middle(self):
        
        code = "y=2\nz=4"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "y=2\nx=1\nz=4"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 1)
        

    def test_insert_in_middle_multiline(self):
        
        code = "y=2\nz=4"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "y=2\na=1\nb=2\nc=3\nz=4"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 3)
        

    def test_insert_before_after_and_middle(self):
        
        code = "y=2\nz=4"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "a=1\ny=2\nx=1\nz=4\nb=99"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 0)
        self.assertEqual(last_line, 0)
        self.assertEqual(lines, 3)

    def test_delete_all(self):
        
        code = "x=1"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = ""
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 0)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 0)
        
    def test_delete_before_line(self):
        code = "x=1\ny=2"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "y=2"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 0)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 0)
                
    def test_delete_after_line(self):
        code = "x=1\ny=2"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "x=1"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 2)
        self.assertEqual(lines, 0)
                
    def test_delete_in_middle(self):
        code = "x=1\na=9\ny=2"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "x=1\ny=2"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 2)
        self.assertEqual(lines, 0)        
        
    def test_line_change(self):
        code = "x=1\ny=2"
        block = Block(code)
        code_block = CodeBlock(code=code, block=block)
        
        new_code = "x=12\ny=2"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 0)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 1)        
        
    def test_multi_line_delete(self):
        code = "x=1\ny=2\nz=3"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        new_code="x=1"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 3)
        self.assertEqual(lines, 0)        
        
    def test_multi_line_partial_delete(self):
        code = "x=1\ny=2+x\nz=3"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        new_code="x=1\ny=2"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 3)
        self.assertEqual(lines, 1)        
        
    def test_newline(self):
        code = "x=1\ny=2"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        new_code="x=1\n\ny=2"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 1)        
        
    def test_modified(self):
        code = "from foo import bar"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        new_code="from baz import nothing"

        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 0)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 1)        
        
    def test_modified_newline(self):
        code = "x=1\nz=3"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        new_code="x=1\ny=2\nz=3"
        
        first_line, last_line, lines = code_block.get_changes(code_block.code, new_code)
        
        self.assertEqual(first_line, 1)
        self.assertEqual(last_line, 1)
        self.assertEqual(lines, 1)        
        
    def test_multi_line_partial_delete_block_update(self):
        code = "x=1\ny=2+x\nz=3"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        new_code="x=1\ny=2"
        
        code_block.code = new_code

        self.assertEqual(len(code_block.block.ast.nodes), 2)
        self.assertEqual(unparse(code_block.block.ast.nodes[0]).strip(), "x = 1")
        self.assertEqual(unparse(code_block.block.ast.nodes[1]).strip(), "y = 2")        

    def test_block_static(self):
        """ Tests if a block changes if a line does not change """
        code = "x=1\ny=2\nz=3"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        new_code="x=1\ny=2"
        
        old_block = code_block.block.sub_blocks[0]
        code_block.code = new_code
        new_block = code_block.block.sub_blocks[0]
        
        self.assertEqual(unparse(old_block.ast), unparse(new_block.ast))
        self.assertEqual(old_block.uuid, new_block.uuid)

    def test_block_decomposition(self):
        """ Tests if a block changes if its the only line left """

        code = "x=1\ny=2"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        old_ast = code_block.block.ast
        old_block = code_block.block.sub_blocks[0]
        
        new_code="x=1"
        code_block.code = new_code
        new_block = code_block.block.sub_blocks[0]
        
        self.assertNotEqual(unparse(old_ast), unparse(code_block.block.ast))
        self.assertEqual(unparse(old_block.ast), unparse(new_block.ast))
        self.assertEqual(old_block.uuid, new_block.uuid)

    def test_block_static_special_case(self):
        """ Tests if a block changes if a line does not change when its the only line unchanged """
        code = "x=1\ny=2+x\nz=3"

        block = Block(code)
        code_block = CodeBlock(code=code)
        
        old_ast = code_block.block.ast
        old_block = code_block.block.sub_blocks[0]

        new_code="x=1\ny=2"
        code_block.code = new_code
        new_block = code_block.block.sub_blocks[0]
        
        self.assertNotEqual(unparse(old_ast), unparse(code_block.block.ast))
        self.assertEqual(unparse(old_block.ast), unparse(new_block.ast))
        self.assertEqual(old_block.uuid, new_block.uuid)
        
if __name__ == '__main__':
    unittest.main()
        
