from setuptools import setup, find_packages

setup(
    name = 'enthought.numerical_modeling',
    version = '3.0a1',
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
    ],
    extras_require = {
        # All non-ets dependencies should be in this extra to ensure users can
        # decide whether to require them or not.
        'nonets': [
            "docutils",
            ],
        },
    namespace_packages = [
        "enthought",
    ],
)
