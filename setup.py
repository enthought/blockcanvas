#!/usr/bin/env python
#
# Copyright (c) 2008-2009 by Enthought, Inc.
# All rights reserved.


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

Prerequisites
-------------
If you want to build BlockCanvas from source, you must first install
`setuptools <http://pypi.python.org/pypi/setuptools/0.6c8>`_.

"""

import traceback
import sys

from distutils import log
from distutils.command.build import build as distbuild
from setuptools import setup, Extension, find_packages
from setuptools.command.develop import develop


# FIXME: This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages. Ticket #1592
#from setup_data import INFO
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']
# FIXME: Same thing as above. Uncomment import on line 32 when fixed.
ETSDEVTOOLS = setup_data['ETSDEVTOOLS']


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


# The actual setup call.
setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    download_url = (
        'http://www.enthought.com/repo/ETS/BlockCanvas-%s.tar.gz' %
        INFO['version']),
    classifiers = [c.strip() for c in """\
        Development Status :: 5 - Production/Stable
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
    description = DOCLINES[1],
    extras_require = INFO['extras_require'],
    # Note: The greenlet package is very old and has not been ported to
    #       Windows amd64.  Since it is very deprecated, we keep the code
    #       around, but exclude it form being build as an extension module.
    ext_modules = [cobyla], # greenlet],
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

