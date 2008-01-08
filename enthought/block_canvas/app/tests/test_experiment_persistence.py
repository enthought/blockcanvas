
import os
from os.path import abspath, join
import shutil
import tempfile
import unittest


from enthought.block_canvas.app.experiment import Experiment
from enthought.block_canvas.app.tests.experiment_utils import (create_simple_experiment,
    compare_experiments)


class ExperimentPersistenceTestCase(unittest.TestCase):

    #---------------------------------------------------------------------------
    # TestCase interface
    #---------------------------------------------------------------------------

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.root_dir = tempfile.gettempdir()
        
        # The list of files and directories used by a test; these get cleaned
        # up in tearDown().
        self.files = []
        self.directories = []

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        for f in self.files:
            os.unlink(f)
        for d in self.directories:
            shutil.rmtree(d)

    def assertEqual(self, first, second, **kw):
        if isinstance(first, Experiment) and isinstance(second, Experiment):
            self.assert_(compare_experiments(first, second))
        else:
            super(ExperimentPersistenceTestCase, self).assertEqual(first, second, **kw)


    #---------------------------------------------------------------------------
    # ExperimentPersistenceTestCase interface
    #---------------------------------------------------------------------------

    def test_empty_save(self):
        """ Tests saving an empty experiment """
        root_dir = abspath(self.root_dir)
        exp = Experiment(name="first experiment")
        dirname = "first_experiment"
        self.directories.append(join(root_dir, dirname))
        config = exp.save(self.root_dir, dirname)
        
        e2 = Experiment()
        e2.load_from_config(config, join(root_dir,dirname))
        self.assertEqual(exp, e2)

    def test_simple_save(self):
        root_dir = abspath(self.root_dir)
        e = create_simple_experiment()
        e.name = "simple_save_test"
        dirname = e.name
        self.directories.append(join(root_dir, dirname))
        config = e.save(root_dir, dirname)

        e2 = Experiment()
        e2.load_from_config(config, join(root_dir,dirname))
        self.assertEqual(e, e2)


if __name__ == "__main__":
    unittest.main()
