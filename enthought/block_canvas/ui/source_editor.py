# System library imports
import wx.stc as stc

# Enthought library imports
from enthought.traits.api import Int, Str, List, TraitError, Event
from enthought.traits.ui.wx.code_editor import ToolkitEditorFactory, SourceEditor
from enthought.pyface.util.python_stc import faces


class MarkableSourceEditor(ToolkitEditorFactory):

    #---------------------------------------------------------------------------
    # Trait definitions
    #---------------------------------------------------------------------------

    # Object trait containing the list of line numbers to dim
    dim_lines = Str

    # Object trait to dim lines to. Can be of form #rrggbb or a color spec. If
    # not specified, dark grey is used.
    dim_color = Str

    squiggle_lines = Str
    
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

    dim_lines = List(Int)
    dim_color = Str
    
    squiggle_lines = List(Int)

    # Styles numbers 0-15 are reserved for the python lexer
    _dim_style_number = Int(16)

     
    #---------------------------------------------------------------------------
    # SourceEditor interace
    #---------------------------------------------------------------------------

    def init(self, parent):
        """ Initialize and sync values.
        """
        super(_MarkableSourceEditor, self).init(parent)
        self.sync_value(self.factory.dim_lines, 'dim_lines', 'from',
                        is_list=True)
        self.sync_value(self.factory.squiggle_lines, 'squiggle_lines', 'from',
                        is_list=True)
        if self.factory.dim_color == '':
            self.dim_color = "dark grey"
        else:
            self.sync_value(self.factory.dim_color, 'dim_color', 'from')

        
        
    def update_object(self):
        """ Handles user entering text in editor
        """
        if not self._locked:
            try:
                self.control.CallTipCancel()
                self.value = self.control.GetText()

                # Set the margin to show markers for error messages.
                self.control.SetFoldFlags(16)
                self.control.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
                self.control.SetMarginMask(2, stc.STC_MASK_FOLDERS)
                self.control.SetMarginSensitive(2, True)
                self.control.Bind(stc.EVT_STC_MARGINCLICK, self.on_margin_click)
                                  
                self.control.SetMarginWidth(2, 16)
                #self.control.MarkerDefine(stc.STC_MARKNUM_FOLDER,
                #                          stc.STC_MARK_CIRCLEPLUS,
                #                          'red', 'black')
                self.control.MarkerDefine(stc.STC_MARKNUM_FOLDEROPEN,
                                          stc.STC_MARK_CIRCLEMINUS,
                                          'red', 'black')

                prev_pos = self.control.GetCurrentPos()
                self._dim_color_changed()
                self._dim_lines_changed()
                self._refresh_squiggle_lines()
                
               # Ensure that the cursor ends up where the user had it before
                # the styling
                self.control.GotoPos(prev_pos)

                self.control.Refresh()
            except TraitError: pass

    #---------------------------------------------------------------------------
    # Static trait listeners
    #---------------------------------------------------------------------------

    def _dim_lines_changed(self):
        self.control.SetLexer(stc.STC_LEX_PYTHON)
        self.control.Colourise(0,-1)

        # Set the lexer to custom mode so our manual style changes
        # won't get nuked.
        self.control.SetLexer(stc.STC_LEX_CONTAINER)
                
        for line in self.dim_lines:
            self.control.GotoLine(line-1)
            current_pos = self.control.GetCurrentPos()
            line_length = self.control.GetLineEndPosition(line-1) - current_pos
            # Set styling mask to only style text bits, not indicator bits
            self.control.StartStyling(current_pos, 0x1f)
            self.control.SetStyling(line_length, self._dim_style_number)
        self.control.Refresh()

    def _dim_color_changed(self):
        self.control.StyleSetForeground(self._dim_style_number, self.dim_color)
        self.control.StyleSetFaceName(self._dim_style_number, "courier new")
        self.control.StyleSetSize(self._dim_style_number, faces['size'])
        self.control.Refresh()

    def _squiggle_lines_changed ( self ):
        """ Set the marker margin and the squiggle lines
        """
        
        marker_num = stc.STC_MARKNUM_FOLDEROPEN
        for i in range(0, self.control.GetLineCount()):
            self.control.MarkerDelete(i, marker_num)
            
        if len(self.squiggle_lines) == 0:
            # reset the style
            self.control.StartStyling(0, stc.STC_INDIC2_MASK)
            self.control.SetStyling(self.control.GetLength(), stc.STC_INDIC0_MASK)
            #self.control.CallTipCancel()
        
        else:
            prev_pos = self.control.GetCurrentPos()
            
            self.control.MarkerAdd(self.squiggle_lines[0]-1, marker_num)            
            self._refresh_squiggle_lines()
            self.control.GotoPos(prev_pos)

        self.control.Refresh()
                       
    def _refresh_squiggle_lines(self):
        """ Refreshing squiggle lines involves showing the tooltip for
            traceback, as well as the squiggle lines for the code being
            added.
            
        """
        
        self.squiggle_lines.sort()
        if len(self.squiggle_lines) and \
               self.squiggle_lines[-1] > self.control.GetLineCount():
            return

        lines = [l.strip() for l in self.object.code.splitlines()]
        final_squiggle_lines = self.squiggle_lines[:]

        for line in self.squiggle_lines:
            opened_paren = 0
            for ll in range(line-1, len(lines)-1):
                opened_paren += lines[ll].count('(')-lines[ll].count(')')
                if lines[ll].endswith('\\') or opened_paren > 0:
                    final_squiggle_lines.append(ll+2)
                else:
                    break

        for line in final_squiggle_lines:
            self.control.GotoLine(line-1)
            start = self.control.GetCurrentPos()
            end = self.control.GetLineEndPosition(line-1)
            
            self.control.StartStyling(start, stc.STC_INDIC2_MASK)
            self.control.SetStyling(end-start, stc.STC_INDIC2_MASK)
            self.control.IndicatorSetStyle(2, stc.STC_INDIC_SQUIGGLE)
            self.control.IndicatorSetForeground(2, 'red')


    def on_margin_click(self, event):
        if self.object.error:
            print event.GetPosition()
            #self.object.error.edit_traits()
            self.control.CallTipShow(self.squiggle_lines[0],
                                     self.object.error.traceback)
            
# Test
if __name__ == '__main__':
    from enthought.traits.api import HasTraits
    from enthought.traits.ui.api import View, VSplit, Item

    class Foo(HasTraits):
        code = Str
        lines = List
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
    foo.lines = [3, 4, 7, 8]

    editor = MarkableSourceEditor(dim_lines='lines')
    view = View(VSplit(Item('lines', show_label=False),
                       Item('code', editor=editor, show_label=False)),
                resizable=True)
    foo.configure_traits(view=view)
