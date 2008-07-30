# Function to convert simple ETS project names and versions to a requirements
# spec that works for both development builds and stable builds.  Allows
# a caller to specify a max version, which is intended to work along with
# Enthought's standard versioning scheme -- see the following write up:
#    https://svn.enthought.com/enthought/wiki/EnthoughtVersionNumbers
def etsdep(p, min, max=None, literal=False):
    require = '%s >=%s.dev' % (p, min)
    if max is not None:
        if literal is False:
            require = '%s, <%s.a' % (require, max)
        else:
            require = '%s, <%s' % (require, max)
    return require


# Declare our ETS project dependencies.
APPTOOLS = etsdep('AppTools', '3.0.0b1')  # -- all from enthought.block_canvas' use of enthought.undo
CHACO = etsdep('Chaco', '3.0.0b1')
DEVTOOLS = etsdep('DevTools', '3.0.0b1')  # -- all from enthought.block_canvas' use of enthought.testing.api
ENABLE_TRAITS = etsdep('Enable[traits]', '3.0.0b1')  # -- all from enthought.block_canvas' use of enthought.kiva.traits
ENTHOUGHTBASE_DISTRIBUTION_UI = etsdep('EnthoughtBase[distribution,ui]', '3.0.0b1')
SCIMATH_TRAITS = etsdep('SciMath[traits]', '3.0.0b1')
TRAITS_UI = etsdep('Traits[ui]', '3.0.0b1')
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.0.0b1')
TRAITSGUI = etsdep('TraitsGUI', '3.0.0b1')


# A dictionary of the setup data information.
INFO = {
    'extras_require' : {
        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            "docutils",
            "Geo",    # we use geo.cow (a different enthought repo) in /ui/interactor.py
            'PIL',
            "numpy >=1.0.2",
            ],
        },
    'install_requires' : [
        APPTOOLS,
        CHACO,
        DEVTOOLS,
        ENABLE_TRAITS,
        ENTHOUGHTBASE_DISTRIBUTION_UI,
        SCIMATH_TRAITS,
        TRAITSBACKENDWX,
        TRAITSGUI,
        TRAITS_UI,
        ],
    'name': 'BlockCanvs',
    'version': '3.0.0b1',
    }
