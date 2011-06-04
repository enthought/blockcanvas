# Global imports
from random import shuffle
import wx
from wx.stc import STC_CMD_DELETEBACK
from random import Random, random

# Enthought Library Imports
from traits.api import HasTraits, Instance, Code, Int, Bool, Any
from traitsui.api import View, Item


class CodeEditingTest(HasTraits):
    block_code_editor = Instance(wx.Control, allow_none=False)
    code = Code("""from enthought.block_canvas.debug.my_operator import add, mul
from numpy import arange
x = arange(0,10,.1)
c1 = mul(a,a)
x1 = mul(x,x)
t1 = mul(c1,x1)
t2 = mul(b, x)
t3 = add(t1,t2)
y = add(t3,c)
""")

    text_index = Int(0)
    random_seed = Int(0)
    random_generator = Instance(Random)
    permute_lines = Bool(True)
    random_backspace = Bool(True)
    clear_first = Bool(False)
    num_runs = Int(1)
    finish_callback = Any

    traits_view = View(Item('code'),
                       Item('random_seed'),
                       Item('num_runs'),
                       Item('random_backspace'),
                       Item('num_runs'),
                       Item('permute_lines'),
                       Item('clear_first'),
                       buttons=['OK'],
                       resizable=True,
                       )



    def interactive_test(self):
        self.configure_test()
        self.run_test()
        return

    def run_test(self):
        self.random_generator = Random()
        self.random_generator.seed(self.random_seed)
        if self.permute_lines:
            codelines = self.code.split('\n')
            shuffle(codelines)
            self.code = '\n'.join(codelines)
        # Should have a more realistic markov process here
        if self.clear_first:
            self.clear_editor()
        timerid = wx.NewId()
        self.timer = wx.Timer(self.block_code_editor, timerid)
        self.block_code_editor.Bind(wx.EVT_TIMER, self.test_step, id=timerid)
        self.text_index = 0
        self.test_step(None)

    def test_step(self, event):
        if self.text_index < len(self.code):
            if random()>0.8 or not self.random_backspace:
                self.text_index -= 1
                self.block_code_editor.CmdKeyExecute(STC_CMD_DELETEBACK)
            else:
                self.block_code_editor.AddText(self.code[self.text_index])
                self.text_index += 1
            self.timer.Start(50.0, wx.TIMER_ONE_SHOT)
        else:
            if self.finish_callback is not None:
                self.finish_callback()


    def configure_test(self):
        self.edit_traits(kind='modal')
        return

    def __init__(self, **kwtraits):
        super(CodeEditingTest, self).__init__(**kwtraits)
        from enthought.block_canvas.block_display.code_block_ui import editor_control
        self.block_code_editor = editor_control()
        self.random_seed = int(random()*1000000)
        return

    def insert_text(self, text, at_once=False):
        """Insert text into the code editor.  This can be done character
        by charager, or all at once if at_once is True"""
        if at_once:
            self.block_code_editor.AddText(text)
        else:
            for char in text:
                self.block_code_editor.AddText(char)
        return


    def clear_editor(self):
        """Removes all of the text all at once from the editor.
        this is equivalent for almost all purposes to the user
        selecting all and hitting backspace"""
        self.block_code_editor.ClearAll()

    def goto_line(self, linenum):
        self.block_code_editor.GotoLine(linenum)
        return

    def enter_basic_code(self):
        self.insert_text(self.basic_code)

