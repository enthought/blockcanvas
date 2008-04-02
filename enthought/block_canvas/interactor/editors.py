""" editors which are used by the interactor classes
"""

# Sytem library imports
from numpy import delete, typeDict

# ETS imports
from enthought.traits.api import TraitError, Any
from enthought.traits.ui.api import TextEditor, TabularAdapter, TabularEditor


#-------------------------------------------------------------------------------
#  Returns an integer which is the result of evaluating a specified string:
#-------------------------------------------------------------------------------

def int_eval ( str ):
    try:
        return int( eval( str ) )
    except:
        raise TraitError()

int_eval_editor = TextEditor( evaluate  = int_eval,
                              auto_set  = False,
                              enter_set = True )

#-------------------------------------------------------------------------------
#  Returns an float which is the result of evaluating a specified string:
#-------------------------------------------------------------------------------

def float_eval ( str ):
    try:
        return float( eval( str ) )
    except:
        raise TraitError()

float_eval_editor = TextEditor( evaluate  = float_eval,
                              auto_set  = False,
                              enter_set = True )

#-------------------------------------------------------------------------------
#  Adapter for editing an array in a TabularEditor
#-------------------------------------------------------------------------------

class ArrayAdapter(TabularAdapter):
    # fixme: TabularEditor won't work for editing arrays that are
    #        multidimensional because it only supports editing in first column

    dtype = Any
    columns = [ ('Data', 0) ]

    def _name_changed(self):
        self.dtype = getattr(self.object, self.name).dtype

    def delete(self, object, trait, row):
        array = getattr(object, trait)
        setattr(object, trait, delete(array, row))

    def get_text(self, object, trait, row, column):
        return str(getattr(object, trait)[row])

    def set_text(self, object, trait, row, text):
        getattr(object, trait)[row] = typeDict[str(self.dtype)](text)
        return

array_eval_editor = TabularEditor(adapter=ArrayAdapter(),
                                  show_titles=False,
                                  editable=True)