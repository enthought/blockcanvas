from setuptools import setup, find_packages

setup(
    name = 'enthought.numerical_modeling',
    version = '1.1.0',
    description  = 'Numerical Modeling',
    author       = 'Enthought, Inc',
    author_email = 'info@enthought.com',
    url          = 'http://code.enthought.com/ets',
    license      = 'BSD',
    zip_safe     = False,
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        "enthought.io", 
        "enthought.type_manager", 
        "enthought.sweet_pickle", 
        "docutils",
    ],
    namespace_packages = [
        "enthought",
    ],
)
