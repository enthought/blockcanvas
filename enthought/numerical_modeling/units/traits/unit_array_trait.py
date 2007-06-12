
# Standard library imports

# Major library imports

# Enthought library imports
from enthought.numerical_modeling.units.api import UnitArray as UA
from enthought.numerical_modeling.units.traits.ui.unit_editor \
    import UnitEditor
from enthought.traits.api import Instance, TraitFactory

# Local Imports

def UnitArrayTrait(value=None, units=None, **kwargs):
    args = ()
    kw = {}
    if value and units:
        args = (value,)
        kwargs['args'] = args
        kw = {'units':units}
        kwargs['kw'] = kw
    return Instance(UA, editor=UnitEditor, **kwargs)

UnitArrayTrait = TraitFactory(UnitArrayTrait)
