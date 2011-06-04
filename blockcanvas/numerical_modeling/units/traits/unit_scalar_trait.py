
# Standard library imports

# Major library imports

# Enthought library imports
from scimath.units.api import UnitScalar as US
from scimath.units.traits.ui.unit_editor \
    import UnitEditor
from traits.api import Instance, TraitFactory

# Local Imports

def UnitScalarTrait(value=None, units=None, **kwargs):
    args = ()
    kw = {}
    if value is not None and units is not None:
        args = (value,)
        kwargs['args'] = args
        kw = {'units':units}
        kwargs['kw'] = kw
    return Instance(US, editor=UnitEditor, **kwargs)

UnitScalarTrait = TraitFactory(UnitScalarTrait)

