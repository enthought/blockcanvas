# Standard library imports
import os, unittest

# Local library imports
from blockcanvas.function_tools.utils import initialize_user_data_dir


class UtilsTestCase(unittest.TestCase):

    #---------------------------------------------------------------------------
    # TestCase interface
    #---------------------------------------------------------------------------

    def setUp(self):
        unittest.TestCase.setUp(self)


    def tearDown(self):
        unittest.TestCase.tearDown(self)


    #---------------------------------------------------------------------------
    # UtilsTestCase interface
    #---------------------------------------------------------------------------

    def test_initialize_user_data_dir(self):
        """ Is the initialization of the user data dir done correctly ?
        """

        usr_dir = initialize_user_data_dir()

        # Check if the path exists
        self.assertEqual(os.path.exists(usr_dir), True)
        self.assertEqual(os.path.isdir(usr_dir), True)

        init_file = os.path.join(usr_dir, '__init__.py')
        self.assertEqual(os.path.exists(init_file), True)
        self.assertEqual(os.path.isfile(init_file), True)


### EOF ------------------------------------------------------------------------
