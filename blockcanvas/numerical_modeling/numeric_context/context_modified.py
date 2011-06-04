#-------------------------------------------------------------------------------
#
#  An event object which describes what changes have occurred to a numeric
#  context.
#
#  Written by: David C. Morrill
#
#  Date: 03/07/2007
#
#  (c) Copyright 2007 by Enthought, Inc.
#
#-------------------------------------------------------------------------------

""" An event object which describes what changes have occurred to a numeric
    context.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traits.api \
    import HasStrictTraits, Bool, List, Str, Property

#-------------------------------------------------------------------------------
#  'ContextModified' class:
#-------------------------------------------------------------------------------

class ContextModified ( HasStrictTraits ):
    """ An event object which describes what changes have occurred to a
        numeric context.
    """

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Has the context has been reset?
    reset = Bool( False )

    # The list of modified array context item names:
    modified = List( Str )

    # The list of added array context item names:
    added = List( Str )

    # The list of removed array context item names:
    removed = List( Str )

    # The list of all non-array changed context item names:
    changed = List( Str )

    # The list of all modified context item names
    # (modified + added + removed + changed):
    all_modified = Property

    # Is there any content in the event:
    not_empty = Property

    #-- Property Implementations -----------------------------------------------

    def _get_all_modified ( self ):
        return dict.fromkeys( self.modified + self.added + self.removed +
                              self.changed ).keys()

    def _get_not_empty ( self ):
        return (self.reset or
                self.modified != [] or
                self.added    != [] or
                self.removed  != [] or
                self.changed  != [])

