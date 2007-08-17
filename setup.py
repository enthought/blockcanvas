from setuptools import setup, find_packages


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
ENABLE2_WX = etsdep('enthought.enable2[wx]', '2.0b1')
PYFACE = etsdep('enthought.pyface', '2.0b1')
TESTING = etsdep('enthought.testing', '2.0b1')
TRAITS_UI = etsdep('enthought.traits[ui]', '2.0b1')
TRAITSUIWX = etsdep('enthought.traits.ui.wx', '2.0b1')
UNITS = etsdep('enthought.units', '2.0b1')
UTIL_DISTRIBUTION = etsdep('enthought.util[distribution]', '2.0b1')


# Configure our setup.
setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        'http://code.enthought.com/enstaller/eggs/source/unstable',
        ],
    description = 'Numerical Modeling',
    extras_require = {
        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            "docutils",
            "geo",    # we use geo.cow (a different enthought repo) in /ui/interactor.py
            "nose",
            "numpy >=1.0.2",
            ],
        },
    include_package_data = True,
    install_requires = [
        ENABLE2_WX,
        PYFACE,
        TRAITS_UI,
        TRAITSUIWX,
        UNITS,
        UTIL_DISTRIBUTION
        ],
    license = 'BSD',
    name = 'enthought.numerical_modeling',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(exclude=['integrationtests']),
    tests_require = [
        'nose >= 0.9',
        TESTING,
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = '3.0.0a1',
    zip_safe = False,
    )
