import unittest

from traits.testing.api import doctest_for_module

import blockcanvas.numerical_modeling.workflow.dataflow as dataflow
from codetools.blocks.api import Block
from blockcanvas.numerical_modeling.workflow.dataflow import Dataflow

class DataflowDocTestCase(doctest_for_module(dataflow)):
    pass

#class DataflowTestCase(unittest.TestCase): # TODO

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
