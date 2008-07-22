import os, zipfile
from setuptools import setup, Extension, find_packages
from setuptools.command.develop import develop
from distutils.command.build import build as distbuild
from distutils import log
from pkg_resources import require, DistributionNotFound

from setup_data import INFO
from make_docs import HtmlBuild 

cobyla = Extension(
    'enthought.block_canvas.cobyla2c.moduleCobyla',
    sources=[
        'enthought/block_canvas/cobyla2c/cobyla.c',
        'enthought/block_canvas/cobyla2c/moduleCobyla.c'
        ],
    )

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
        ],
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
APPTOOLS = etsdep('AppTools', '3.0.0b1')  # -- all from enthought.block_canvas' use of enthought.undo
CHACO = etsdep('Chaco', '3.0.0b1')
DEVTOOLS = etsdep('DevTools', '3.0.0b1')  # -- all from enthought.block_canvas' use of enthought.testing.api
ENABLE_TRAITS = etsdep('Enable[traits]', '3.0.0b1')  # -- all from enthought.block_canvas' use of enthought.kiva.traits
ENTHOUGHTBASE_DISTRIBUTION_UI = etsdep('EnthoughtBase[distribution,ui]', '3.0.0b1')
SCIMATH_TRAITS = etsdep('SciMath[traits]', '3.0.0b1')
TRAITS_UI = etsdep('Traits[ui]', '3.0.0b1')
TRAITSBACKENDWX = etsdep('TraitsBackendWX', '3.0.0b1')
TRAITSGUI = etsdep('TraitsGUI', '3.0.0b1')

def generate_docs():
    """If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),'docs',
                           'source')
    html_zip = os.path.join(os.path.abspath(os.path.dirname(__file__)),'docs',
                            'html.zip')
    dest_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            'docs')
    
    try:
        require("Sphinx>=0.4.1")
            
        log.info("Auto-generating documentation in %s/html" % dest_dir)
        doc_src = doc_dir
        target = dest_dir
        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': doc_src,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False,
                }, [])
            del build
        except:
            log.error("The documentation generation failed."
                      " Installing from zip file.")
            
            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, dest_dir)
            
    except DistributionNotFound:
        log.error("Sphinx is not installed, so the documentation could not be "
                  "generated.  Installing from zip file...")
        
        # Unzip the docs into the 'html' folder.
        unzip_html_docs(html_zip, dest_dir)

def unzip_html_docs(src_path, dest_dir):
    """Given a path to a zipfile, extract
    its contents to a given 'dest_dir'.
    """
    file = zipfile.ZipFile(src_path)
    for name in file.namelist():
        cur_name = os.path.join(dest_dir, name)
        if not name.endswith('/'):
            out = open(cur_name, 'wb')
            out.write(file.read(name))
            out.flush()
            out.close()
        else:
            if not os.path.exists(cur_name):
                os.mkdir(cur_name)
    file.close()

class my_develop(develop):
    def run(self):
        develop.run(self)
        # Generate the documentation.
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        # Generate the documentation.
        generate_docs()

# Configure our setup.
setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    cmdclass = {
        'develop': my_develop,
        'build': my_build
    },
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = 'Numerical Modeling',
    extras_require = {
        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            "docutils",
            "Geo",    # we use geo.cow (a different enthought repo) in /ui/interactor.py
            'PIL',
            "numpy >=1.0.2",
            ],
        },
    ext_modules = [cobyla, greenlet],
    include_package_data = True,
    install_requires = [
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
    license = 'BSD',
    name = 'BlockCanvas',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(exclude=[
        'integrationtests',
        'integrationtests.*',
        ]),
    tests_require = [
        DEVTOOLS,
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/ets',
    version = INFO['version'],
    zip_safe = False,
    )

