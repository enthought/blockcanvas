# Copyright (c) 2008-2011 by Enthought, Inc.
# All rights reserved.

from setuptools import setup, Extension, find_packages

# This works around a setuptools bug which gets setup_data.py metadata
# from incorrect packages.
setup_data = dict(__name__='', __file__='setup_data.py')
execfile('setup_data.py', setup_data)
INFO = setup_data['INFO']


# Build Python extensions
cobyla = Extension(
    'blockcanvas.cobyla2c.moduleCobyla',
    sources=[
        'blockcanvas/cobyla2c/cobyla.c',
        'blockcanvas/cobyla2c/moduleCobyla.c'
        ],
    )

greenlet = Extension(
    'blockcanvas.greenlet.greenlet',
    sources = [
        'blockcanvas/greenlet/greenlet.c',
        ],
    include_dirs = [
        'blockcanvas/greenlet',
        ],
    depends=[
        'blockcanvas/greenlet/greenlet.h',
        'blockcanvas/greenlet/slp_platformselect.h',
        'blockcanvas/greenlet/switch_amd64_unix.h',
        'blockcanvas/greenlet/switch_ppc_macosx.h',
        'blockcanvas/greenlet/switch_ppc_unix.h',
        'blockcanvas/greenlet/switch_s390_unix.h',
        'blockcanvas/greenlet/switch_sparc_sun_gcc.h',
        'blockcanvas/greenlet/switch_x86_msvc.h',
        'blockcanvas/greenlet/switch_x86_unix.h',
        ],
    )


# The actual setup call.
setup(
    author = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    download_url = (
        'http://www.enthought.com/repo/ets/blockcanvas-%s.tar.gz' %
        INFO['version']),
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
    description = 'visual environment for creating simulation experiments',
    long_description = open('README.rst').read(),
    # Note: The greenlet package is very old and has not been ported to
    #       Windows amd64.  Since it is very deprecated, we keep the code
    #       around, but exclude it form being build as an extension module.
    ext_modules = [cobyla], # greenlet],
    include_package_data = True,
    install_requires = INFO['install_requires'],
    license = 'BSD',
    maintainer = 'ETS Developers',
    maintainer_email = 'enthought-dev@enthought.com',
    name = 'BlockCanvas',
    packages = find_packages(exclude=[
        'integrationtests',
        'integrationtests.*',
        ]),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    test_suite = 'nose.collector',
    url = 'http://code.enthought.com/projects/block_canvas.php',
    version = INFO['version'],
    zip_safe = False,
)
