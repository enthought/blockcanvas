""" Testing importing a block unit from a project-file and exporting it to a
    project-file.
"""

import nose
raise nose.SkipTest("BlockApplication is deprecated")

# Standard imports
import os, unittest, tempfile

# ETS library imports
from enthought.blocks.api import Block

# Local imports
from enthought.block_canvas.app.utils import create_unique_project_name
from enthought.block_canvas.app.block_application import BlockApplication
from enthought.block_canvas.block_display.block_unit import BlockUnit
from enthought.contexts.api import DataContext

#-------------------------------------------------------------------------------
#   ProjectTestCase
#-------------------------------------------------------------------------------

class ProjectTestCase(unittest.TestCase):

    #---------------------------------------------------------------------------
    # TestCase interface
    #---------------------------------------------------------------------------

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.code = 'from enthought.block_canvas.debug.my_operator import add\n' \
                    'c = add(a,b)\n'
        self.dir_name = tempfile.gettempdir()
        self.app = BlockApplication(block_unit=BlockUnit())

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    #---------------------------------------------------------------------------
    # ProjectTestCase interface
    #---------------------------------------------------------------------------

    def test_load_block_from_file(self):
        """ Does loading script from file work correctly ?
        """

        # Preparing the test case
        file_path = os.path.join(self.dir_name, 'test_load_block.py')

        file_object = open(file_path, 'w')
        file_object.write(self.code)
        file_object.close()

        # Load the script from the file.
        self.app.block_unit = BlockUnit()
        self.app.load_block_from_file(file_path)
        # Cleanup after loading the file
        os.remove(file_path)

        # Test the block unit
        context = DataContext(name = 'dummy_context',
                              _bindings = {'a':1, 'b':2})
        self.app.block_unit.codeblock.execute(context)

        self.assertTrue(context.has_key('c'))
        self.assertEqual(context['c'], 3)


    def test_save_block_to_file(self):
        """ Does saving script to file work correctly ?
        """

        # Preparing the test case
        self.app.block_unit = BlockUnit(code=self.code)
        file_path = os.path.join(self.dir_name,'test_save_block.py')

        check_exists = [os.path.exists(file_path)]
        self.app.save_block_to_file(file_path)

        # Check if the file exists after saving and retrieve the code saved in
        # the file.
        check_exists.append(os.path.exists(file_path))
        file_object = open(file_path, 'r')
        check_code = file_object.read()
        file_object.close()

        # Cleanup after retrieving important information.
        os.remove(file_path)

        # Test
        self.assertTrue(check_exists == [False, True])
        a, b = 1,2
        exec check_code
        self.assertEqual(c, 3)


    def test_load_project_from_file(self):
        """ Does loading a project from file work correctly ?
        """
        # Preparing the test case
        # Make project.py, project.pickle, project.prj
        project_name = create_unique_project_name(self.dir_name,
                                                  'test_load_project')
        project_dir = os.path.join(self.dir_name, project_name+'_files')
        project_file = os.path.join(self.dir_name, project_name+'.prj')

        script_path = os.path.join(project_dir, project_name+'.py')
        context_path = os.path.join(project_dir, project_name+'.pickle')
        script = '\n'.join(('SCRIPT_PATH = '+script_path,
                            'CONTEXT_PATH = '+context_path))

        os.makedirs(project_dir)

        file_object = open(project_file, 'wb')
        file_object.write(script)
        file_object.close()
        file_object = open(script_path, 'w')
        file_object.write(self.code)
        file_object.close()
        d = DataContext(name = 'dummy_context',
                        _bindings = {'a': 1, 'b':2, 'd': 0.01})
        d.save_context_to_file(context_path)


        # Check if the setup is correct
        self.assertTrue([os.path.exists(project_file),
                         os.path.exists(project_dir),
                         os.path.exists(script_path),
                         os.path.exists(context_path)])

        # Load the project from the file.
        self.app.block_unit = BlockUnit()
        self.app.load_project_from_file(project_file)

        # Clean up after loading
        os.remove(project_file)
        os.remove(script_path)
        os.remove(context_path)
        os.rmdir(project_dir)

        expected_keys = set(['a', 'b', 'c', 'd', 'context'])
        self.assertEqual(set(self.app.block_unit.data_context.keys()),
                         expected_keys)
        self.assertTrue(self.app.block_unit.data_context.has_key('c'))
        self.assertEqual(self.app.block_unit.data_context['c'], 3)


    def test_save_new_project(self):
        """ Does saving a new project to file work correctly ?
        """
        context = DataContext(name = 'dummy_context',
                              _bindings = {'a':1, 'b':2})
        self.app.block_unit = BlockUnit(code=self.code, data_context = context)

        project_name = create_unique_project_name(self.dir_name,
                                                  'test_save_project')
        project_file = os.path.join(self.dir_name,project_name+'.prj')
        self.app.save_project_to_file(project_file)

        # Check if the new files exist
        project_dir = os.path.join(self.dir_name,project_name+'_files')
        context_file = os.path.join(project_dir, project_name+'.pickle')
        script_file = os.path.join(project_dir, project_name+'.py')
        layout_file = os.path.join(project_dir, 'layout.pickle')

#        print project_file, project_dir, context_file, script_file
        self.assertTrue([os.path.exists(project_file),
                         os.path.exists(project_dir),
                         os.path.exists(context_file),
                         os.path.exists(script_file)])

        # Check if the code was saved out correctly
        file_object = open(script_file, 'r')
        check_code = file_object.read()
        file_object.close()
        a, b = 1,2
        exec check_code
        self.assertTrue(c, 3)

        # Check if the project file was written out correctly
        file_object = open(project_file, 'rb')
        check_code = file_object.read()
        file_object.close()
        actual_result = [line[line.find('=')+1:].strip() for line in
                         check_code.split('\n')]

        self.assertTrue(actual_result==[script_file, context_file, layout_file])

        # Check if the context is correct
        retrieved_context = DataContext.load_context_from_file(context_file)
        expected_keys = set(['a', 'b', 'c'])
        self.assertEqual(retrieved_context.name, 'dummy_context')
        self.assertEqual(set(retrieved_context.keys()), expected_keys)
        self.assertEqual(retrieved_context['c'], 3)

        # Cleanup
        os.remove(project_file)
        os.remove(script_file)
        os.remove(context_file)
        os.remove(layout_file)
        os.rmdir(project_dir)


    def test_load_and_resave_project(self):
        """ Does load and resaving a project work correctly ?
        """
        project_name = create_unique_project_name(self.dir_name,
                                                  'test_load_save_project')
        project_dir = os.path.join(self.dir_name, project_name+'_files')
        project_file = os.path.join(self.dir_name, project_name+'.prj')

        script_path = os.path.join(project_dir, project_name+'.py')
        context_path = os.path.join(project_dir, project_name+'.pickle')
        layout_path = os.path.join(project_dir, 'layout.pickle')
        script = '\n'.join(('SCRIPT_PATH = '+script_path,
                            'CONTEXT_PATH = '+context_path,
                            'LAYOUT_PATH = '+layout_path))

        os.makedirs(project_dir)

        file_object = open(project_file, 'wb')
        file_object.write(script)
        file_object.close()
        file_object = open(script_path, 'w')
        file_object.write(self.code)
        file_object.close()
        d = DataContext(name = 'dummy_context',
                        _bindings = {'a': 1, 'b':2, 'e': 0.01})
        d.save_context_to_file(context_path)


        # Check if the setup is correct
        self.assertTrue([os.path.exists(project_file),
                         os.path.exists(project_dir),
                         os.path.exists(script_path),
                         os.path.exists(context_path)])

        # Load the project from the file.
        self.app.block_unit = BlockUnit()
        self.app.load_project_from_file(project_file)
        self.app.block_unit.codeblock.code = self.app.block_unit.codeblock.code + '\nd = add(a,c)'
        self.app.save_loaded_project()

        # The key 'context' should get removed while saving the project.
        expected_keys = set(['a', 'b', 'c', 'd', 'e'])
        self.assertEqual(set(self.app.block_unit.data_context.keys()),
                         expected_keys)
        self.assertEqual(self.app.block_unit.data_context['d'], 4)

        # Check if the new code contains the new line
        file_object = open(script_path, 'r')
        code = file_object.read()
        a,b = 1,2
        exec code
        file_object.close()
        self.assertEqual(d, 4)

        # Clean up after loading
        os.remove(project_file)
        os.remove(script_path)
        os.remove(context_path)
        os.remove(layout_path)
        os.rmdir(project_dir)


if __name__ == '__main__':
    unittest.main()
