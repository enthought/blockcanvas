from setuptools import setup, Extension, find_packages


greenlet = Extension(
    'enthought.greenlet.greenlet',
    sources = [
        'enthought/greenlet/greenlet.c',
        ],
    include_dirs = [
        'enthought/greenlet',
        ],
    depends=[
        'enthought/greenlet/greenlet.h',
        'enthought/greenlet/slp_platformselect.h',
        'enthought/greenlet/switch_amd64_unix.h',
        'enthought/greenlet/switch_ppc_macosx.h',
        'enthought/greenlet/switch_ppc_unix.h',
        'enthought/greenlet/switch_s390_unix.h',
        'enthought/greenlet/switch_sparc_sun_gcc.h',
        'enthought/greenlet/switch_x86_msvc.h',
        'enthought/greenlet/switch_x86_unix.h',
        ]
    )


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
DEVTOOLS = etsdep('DevTools', '3.0.0b1')
ENABLE_WX = etsdep('Enable[wx]', '3.0.0b1')
ENTHOUGHTBASE = etsdep('EnthoughtBase', '3.0.0b1')
SCIMATH = etsdep('SciMath', '3.0.0b1')
TRAITSBACKENDQT = etsdep('TraitsBackendQt', '3.0.0b1')
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.0.0b1')
TRAITSGUI = etsdep('TraitsGUI', '3.0.0b1')
TRAITS_UI = etsdep('Traits[ui]', '3.0.0b1')


# Configure our setup.
setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = 'Numerical Modeling',
    extras_require = {
        'qt': [
            TRAITSBACKENDQT,
            ],
        'wx': [
            TRAITSBACKENDWX,
            ],
        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            "docutils",
            "geo",    # we use geo.cow (a different enthought repo) in /ui/interactor.py
            "numpy >=1.0.2",
            ],
        },
    ext_modules = [greenlet],
    include_package_data = True,
    install_requires = [
        ENABLE_WX,
        ENTHOUGHTBASE,
        SCIMATH,
        TRAITSGUI,
        TRAITS_UI,
        ],
    license = 'BSD',
    name = 'BlockCanvas',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(exclude=['integrationtests']),
    tests_require = [
        DEVTOOLS,
        'nose >= 0.9',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = '3.0.0b1',
    zip_safe = False,
    )

