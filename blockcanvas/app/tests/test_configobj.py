""" Verifies that ConfigObj does what we expect with our project and
context configspecs file.  This is primarily a parsing test, and even
though it strives to use the same format as our actual saved project
files, it does not test actual object persistence or loading.
"""

# Standard library imports
import os
import unittest
from configobj import ConfigObj

CONFIG_SPEC = "project_config_spec.txt"

TEST_LINES = """
[Project]
    active_experiment = "exp1"

[Experiments]
    [[E1]]
        name = "exp1"
        save_dir = "exp1"
        layout_file = "test_layout.txt"
        code_file = "test_code.txt"
        local_context = ""
        shared_context = "c2"

    [[E2]]
        name = "exp2"
        save_dir = "exp2"
        layout_file = "layout2.txt"
        code_file = "code2.txt"


[Contexts]
    [[C1]]
        name = "c1"
        file = "test_c1_data.txt"

    [[C2]]
        name = "c2"
        file = "test_c2_data.txt"

    [[C3]]
        name = "c3"
        file = "test_c3_data.txt"
""".splitlines()

# This is a dict that corresponds to the TEST_LINES above.  It can be used as a
# test target for correct parsing of the above.
TEST_DICT = {"Project": {
                    "active_experiment": "exp1",
                    },
             "Experiments": {
                 "E1": {
                    "name": "exp1",
                    "save_dir": "exp1",
                    "layout_file": "test_layout.txt",
                    "code_file": "test_code.txt",
                    "local_context": "",
                    "shared_context": "c2"
                    },
                 "E2": {
                     "name": "exp2",
                     "save_dir": "exp2",
                     "layout_file": "layout2.txt",
                     "code_file": "code2.txt"
                     }
                 },
             "Contexts": {
                 "C1": {
                     "name": "c1",
                     "file": "test_c1_data.txt"
                     },
                 "C2": {
                     "name": "c2",
                     "file": "test_c2_data.txt"
                     },
                 "C3": {
                     "name": "c3",
                     "file": "test_c3_data.txt"
                     }
                 }
             }

GENERATED_OUTPUT = ['[Project]',
                    '    active_experiment = exp1',
                    '[Contexts]',
                    '    [[C3]]',
                    '        name = c3',
                    '        file = test_c3_data.txt',
                    '    [[C2]]',
                    '        name = c2',
                    '        file = test_c2_data.txt',
                    '    [[C1]]',
                    '        name = c1',
                    '        file = test_c1_data.txt',
                    '[Experiments]',
                    '    [[E1]]',
                    '        code_file = test_code.txt',
                    '        name = exp1',
                    '        shared_context = c2',
                    '        save_dir = exp1',
                    '        local_context = ""',
                    '        layout_file = test_layout.txt',
                    '    [[E2]]',
                    '        code_file = code2.txt',
                    '        layout_file = layout2.txt',
                    '        name = exp2',
                    '        save_dir = exp2']

class ConfigObjTestCase(unittest.TestCase):

    def _get_spec_filename(self):
        """ Returns the path to the "most relevant" configspec file to this
        test by playing games with __file__
        """
        path, curfile = os.path.split(os.path.abspath(__file__))
        parent_dir, curdir = os.path.split(path)
        return os.path.join(parent_dir, CONFIG_SPEC)

    def test_configspec(self):
        configspec = ConfigObj(self._get_spec_filename(), list_values=False)
        config = ConfigObj(TEST_LINES, configspec=configspec)
        target = ConfigObj(TEST_DICT)
        self.assert_(config == target)

    def test_project_save(self):
        config = ConfigObj(TEST_DICT)
        self.assert_(config.write() == GENERATED_OUTPUT)


if __name__ == "__main__":
    unittest.main()

