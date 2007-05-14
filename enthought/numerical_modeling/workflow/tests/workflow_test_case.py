import unittest

from enthought.testing.doctest_tools import doctest_for_module

import enthought.numerical_modeling.workflow.dataflow as dataflow
from enthought.numerical_modeling.workflow.block.api import Block
from enthought.numerical_modeling.workflow.dataflow import Dataflow

class DataflowDocTestCase(doctest_for_module(dataflow)):
    pass

#class DataflowTestCase(unittest.TestCase): # TODO

if __name__ == '__main__':
    import sys
    unittest.main(argv=sys.argv)
