""" Test saving and loading of projects """

# Standard imports
import os, shutil, unittest, tempfile
from os.path import abspath, join

# ETS library imports

# Local imports
from blockcanvas.app.project import Project
from blockcanvas.app.tests.experiment_utils import (create_simple_experiment,
    create_simple_project, create_multi_experiment_proj, compare_contexts,
    compare_experiments, compare_projects)



#-------------------------------------------------------------------------------
#   ProjectTestCase
#-------------------------------------------------------------------------------

class ProjectPersistenceTestCase(unittest.TestCase):

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
        if isinstance(first, Project) and isinstance(second, Project):
            self.assert_(compare_projects(first, second), **kw)
        else:
            super(ProjectPersistenceTestCase, self).assertEqual(first, second, **kw)

    #---------------------------------------------------------------------------
    # ProjectPersistenceTestCase interface
    #---------------------------------------------------------------------------


    def test_empty_project(self):
        dirname = abspath(join(self.root_dir, "empty_project"))
        self.directories.append(dirname)

        p = Project(project_save_path=dirname)
        p.save()
        p2 = Project.from_dir(dirname)
        self.assert_(compare_projects(p, p2))

    def test_simple_project(self):
        dirname = abspath(join(self.root_dir, "simple_project"))
        self.directories.append(dirname)

        p1 = create_simple_project()
        p1.save(dirname)
        p2 = Project.from_dir(dirname)
        self.assert_(compare_projects(p1, p2))

    def test_multi_experiment_project(self):
        dirname = abspath(join(self.root_dir, "project3"))
        self.directories.append(dirname)

        p1 = create_multi_experiment_proj()
        p1.save(dirname)
        p2 = Project.from_dir(dirname)
        self.assert_(compare_projects(p1, p2))



if __name__ == '__main__':
    unittest.main()
