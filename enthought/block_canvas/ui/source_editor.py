# System library imports
import wx.stc as stc

# Enthought library imports
from enthought.traits.api import Int, Str, List, TraitError, Event, \
    on_trait_change
from enthought.traits.ui.wx.code_editor import ToolkitEditorFactory, \
    SourceEditor, OKColor
from enthought.pyface.util.python_stc import faces


class MarkableSourceEditor(ToolkitEditorFactory):

    #---------------------------------------------------------------------------
    # Trait definitions
    #---------------------------------------------------------------------------

    # The lexer to use. Default is 'python'; 'null' indicates no lexing.
    lexer = Str('python')

    # Object trait containing the list of line numbers to dim
    dim_lines = Str

    # Object trait to dim lines to. Can be of form #rrggbb or a color spec. If
    # not specified, dark grey is used.
    dim_color = Str

    # Object trait containing the list of line numbers to put squiggles under
    squiggle_lines = Str

    # Object trait for the color of squiggles. If not specified, red is used.
    squiggle_color = Str
    
    #---------------------------------------------------------------------------
    #  'Editor' factory methods:
    #---------------------------------------------------------------------------

    def simple_editor ( self, ui, object, name, description, parent ):
        return _MarkableSourceEditor( parent,
                             factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             readonly    = False )

    def readonly_editor ( self, ui, object, name, description, parent ):
        return _MarkableSourceEditor( parent,
                             factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             readonly    = True )

    #---------------------------------------------------------------------------
    #  Allow an instance to be called:
    #---------------------------------------------------------------------------

    def __call__ ( self, *args, **traits ):
        return self.set( **traits )


class _MarkableSourceEditor(SourceEditor):

    lexer = Int

    dim_lines = List(Int)
    dim_color = Str
    _dim_style_number = Int(16) # 0-15 are reserved for the python lexer
    
    squiggle_lines = List(Int)
    squiggle_color = Str
     
    #---------------------------------------------------------------------------
    # Editor interface
    #---------------------------------------------------------------------------

    def init(self, parent):
        """ Initialize and sync values.
        """
        super(_MarkableSourceEditor, self).init(parent)
        
        # Clear out the goofy hotkeys for zooming text
        self.control.CmdKeyClear(ord('B'), stc.STC_SCMOD_CTRL)
        self.control.CmdKeyClear(ord('N'), stc.STC_SCMOD_CTRL)

        self.control.SetLexer(stc.STC_LEX_CONTAINER)
        self.control.Bind(stc.EVT_STC_STYLENEEDED, self._style_needed)

        try:
            self.lexer = getattr(stc, 'STC_LEX_' + self.factory.lexer.upper())
        except AttributeError:
            self.lexer = stc.STC_LEX_NULL

        self.sync_value(self.factory.dim_lines, 'dim_lines', 'from',
                        is_list=True)
        if self.factory.dim_color == '':
            self.dim_color = 'dark grey'
        else:
            self.sync_value(self.factory.dim_color, 'dim_color', 'from')

        self.sync_value(self.factory.squiggle_lines, 'squiggle_lines', 'from',
                        is_list=True)
        if self.factory.squiggle_color == '':
            self.squiggle_color = 'red'
        else:
            self.sync_value(self.factory.squiggle_color, 'squiggle_color', 
                            'from')

    def update_editor(self):
        """ Updates the editor when the object trait changes externally to the 
            editor.
        """
        super(_MarkableSourceEditor, self).update_editor()
        self.control.Colourise(0, -1)
        self.control.Refresh()

    #---------------------------------------------------------------------------
    # MarkableSourceEditor interface
    #-------------------------------------------------------------------------

    def _dim_color_changed(self):
        self.control.StyleSetForeground(self._dim_style_number, self.dim_color)
        self.control.StyleSetFaceName(self._dim_style_number, "courier new")
        self.control.StyleSetSize(self._dim_style_number, faces['size'])
        self.control.Refresh()

    def _squiggle_color_changed(self):
        self.control.IndicatorSetStyle(2, stc.STC_INDIC_SQUIGGLE)
        self.control.IndicatorSetForeground(2, self.squiggle_color)
        self.control.Refresh()

    @on_trait_change('dim_lines, squiggle_lines')
    def _style_document(self):
        """ Force the STC to fire an STC_STYLENEEDED event for the entire 
            document.
        """
        self.control.ClearDocumentStyle()
        self.control.Refresh()

    def _style_needed(self, event):
        position = self.control.GetEndStyled()
        start_line = self.control.LineFromPosition(position)
        end = event.GetPosition()
        end_line = self.control.LineFromPosition(end)

        # Fixes a strange a bug with the STC widget where creating a new line
        # after a dimmed line causes it to mysteriously lose its styling
        if start_line in self.dim_lines:
            start_line -= 1
        
        # Trying to Colourise only the lines that we want does not seem to work
        # so we do the whole area and then override the styling on certain lines
        if self.lexer != stc.STC_LEX_NULL:
            self.control.SetLexer(self.lexer)
            self.control.Colourise(position, end)
            self.control.SetLexer(stc.STC_LEX_CONTAINER)

        for line in xrange(start_line, end_line+1):
            # We don't use LineLength here because it includes newline 
            # characters. Styling these leads to strange behavior.
            position = self.control.PositionFromLine(line)
            style_length = self.control.GetLineEndPosition(line) - position

            if line+1 in self.dim_lines:
                # Set styling mask to only style text bits, not indicator bits
                self.control.StartStyling(position, 0x1f)
                self.control.SetStyling(style_length, self._dim_style_number)
            elif self.lexer == stc.STC_LEX_NULL:
                self.control.StartStyling(position, 0x1f)
                self.control.SetStyling(style_length, stc.STC_STYLE_DEFAULT)
                
            if line+1 in self.squiggle_lines:
                self.control.StartStyling(position, stc.STC_INDIC2_MASK)
                self.control.SetStyling(style_length, stc.STC_INDIC2_MASK)
            else:
                self.control.StartStyling(position, stc.STC_INDIC2_MASK)
                self.control.SetStyling(style_length, stc.STC_STYLE_DEFAULT)

         
# Test
if __name__ == '__main__':
    from enthought.traits.api import HasTraits
    from enthought.traits.ui.api import View, Group, Item

    class Foo(HasTraits):
        code = Str
        dim_lines = List
        dim_color = Str("dark grey")
        squiggle_lines = List

    foo = Foo()
    foo.code = "from enthought.block_canvas.debug.my_operator import add, mul\n" \
               "from numpy import arange\n" \
               "x = arange(0,10,.1)\n" \
               "c1 = mul(a,a)\n" \
               "x1 = mul(x,x)\n" \
               "t1 = mul(c1,x1)\n" \
               "t2 = mul(b, x)\n" \
               "t3 = add(t1,t2)\n" \
               "y = add(t3,c)\n"
    foo.dim_lines = [3, 8, 9]
    foo.squiggle_lines = [1, 3, 5]

    editor = MarkableSourceEditor(dim_lines='dim_lines',
                                  dim_color='dim_color',
                                  squiggle_lines='squiggle_lines')
    view = View(Group(Item('dim_lines'),
                      Item('dim_color'),
                      Item('squiggle_lines'),
                      Item('code', editor=editor, show_label=False)),
                width=800, height=600, resizable=True)
    foo.configure_traits(view=view)
