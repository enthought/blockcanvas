#!/usr/bin/env python
#
# Copyright (c) 2008 by Enthought, Inc.
# All rights reserved.
#

"""
Numerical Modeling

The BlockCanvas project provides a visual environment for creating simulation
experiments, where function and data are separated. Thus, you can define your
simulation algorithm by visually connecting function blocks into a data flow
network, and then run it with various data sets (known as "contexts");
likewise, you can use the same context in a different functional simulation.

The project provides support for plotting, function searching and inspection,
and optimization. It includes a stand-alone application that demonstrates the
block-canvas environment, but the same functionality can be incorporated into
other applications.

The BlockCanvas project relies on included libraries that allow multiple data
sets using Numeric arrays to be incorporated in a Traits-based model in a
way that is simple, fast, efficient, and consistent.
"""


from distutils import log
from distutils.command.build import build as distbuild
from make_docs import HtmlBuild
from pkg_resources import DistributionNotFound, parse_version, require, \
    VersionConflict
from setup_data import ETSDEVTOOLS
from setuptools import setup, Extension, find_packages
from setuptools.command.develop import develop
import os
import zipfile

# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']

# Pull the description values for the setup keywords from our file docstring.
DOCLINES = __doc__.split("\n")


# Build Python extensions
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


# Functions to generate docs from sources during builds
def generate_docs():
    """ If sphinx is installed, generate docs.
    """
    doc_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'docs')
    source_dir = os.path.join(doc_dir, 'source')
    html_zip = os.path.join(doc_dir,  'html.zip')
    dest_dir = doc_dir

    required_sphinx_version = "0.4.1"
    sphinx_installed = False
    try:
        require("Sphinx>=%s" % required_sphinx_version)
        sphinx_installed = True
    except (DistributionNotFound, VersionConflict):
        log.warn('Sphinx install of version %s could not be verified.'
            ' Trying simple import...' % required_sphinx_version)
        try:
            import sphinx
            if parse_version(sphinx.__version__) < parse_version(
                required_sphinx_version):
                log.error("Sphinx version must be >=" + \
                    "%s." % required_sphinx_version)
            else:
                sphinx_installed = True
        except ImportError:
            log.error("Sphnix install not found.")

    if sphinx_installed:
        log.info("Generating %s documentation..." % INFO['name'])
        docsrc = source_dir
        target = dest_dir

        try:
            build = HtmlBuild()
            build.start({
                'commit_message': None,
                'doc_source': docsrc,
                'preserve_temp': True,
                'subversion': False,
                'target': target,
                'verbose': True,
                'versioned': False
                }, [])
            del build

        except:
            log.error("The documentation generation failed.  Falling back to "
                "the zip file.")

            # Unzip the docs into the 'html' folder.
            unzip_html_docs(html_zip, doc_dir)
    else:
        # Unzip the docs into the 'html' folder.
        log.info("Installing %s documentaion from zip file.\n" % INFO['name'])
        unzip_html_docs(html_zip, doc_dir)

def unzip_html_docs(src_path, dest_dir):
    """ Given a path to a zipfile, extract its contents to a given 'dest_dir'.
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
        generate_docs()

class my_build(distbuild):
    def run(self):
        distbuild.run(self)
        generate_docs()


# The actual setup call.
setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    classifiers = [c.strip() for c in """\
        Development Status :: 4 - Beta
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: C
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0],
    cmdclass = {
        'develop': my_develop,
        'build': my_build
    },
    dependency_links = [
        'http://code.enthought.com/enstaller/eggs/source',
        ],
    description = DOCLINES[1],
    extras_require = INFO['extras_require'],
    ext_modules = [cobyla, greenlet],
    include_package_data = True,
    install_requires = INFO['install_requires'],
    license = 'BSD',
    long_description = '\n'.join(DOCLINES[3:]),
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'BlockCanvas',
    namespace_packages = [
        "enthought",
        ],
    packages = find_packages(exclude=[
        'integrationtests',
        'integrationtests.*',
        ]),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    tests_require = [
        ETSDEVTOOLS,
        'nose >= 0.10.3',
        ],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/block_canvas.php',
    version = INFO['version'],
    zip_safe = False,
    )

