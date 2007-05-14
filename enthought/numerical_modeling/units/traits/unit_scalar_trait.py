
# Standard library imports

# Major library imports

# Enthought library imports
from enthought.numerical_modeling.units.api import UnitScalar as US
from enthought.numerical_modeling.units.traits.ui.unit_editor \
    import UnitEditor
from enthought.traits.api import Instance
from enthought.units.unit import dimensionless 

# Local Imports

UnitScalarTrait = Instance(US, editor=UnitEditor)
