from setuptools import setup

setup(name             = "block_canvas_deps",
      version          = "0.1.0",
      description      = 'Enthought Block Canvas Application dependents',
      author           = 'Enthought, Inc',
      author_email     = 'info@enthought.com',
      url              = 'http://code.enthought.com',
      license          = 'BSD',
      zip_safe         = True,
      install_requires = [
        "blockcanvas",
        "chaco>=3.0a1",
        "etsdevtools.debug",
        "enable>=3.0a1",
        "traits.etsconfig",
        "blockcanvas.greenlet",
        "apptools.io",
        "kiva",
        "apptools.logger",
        "apptools.naming",
        "blockcanvas.numerical_modeling",
        "pyface>=3.0a1",
        "pyface.ui.wx>=3.0a1",
        "pyface.resource",
        "apptools.sweet_pickle",
        "traits.testing",
        "traits>=3.0.0b1",
        "traitsui.wx>=3.0.0b1",
        "apptools.type_manager",
        "scimath.units",
        "traits.util",
        "geo",
        "PIL",
        "wxPython>2.6",
        "docutils",
      ],
)
