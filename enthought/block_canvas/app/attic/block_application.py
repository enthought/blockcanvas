""" The "Model" object for an application that ties together an execution
    block and a data context within which the block executes.  It also provides
    a function search window
"""

# Standard library imports:
import logging, os, shutil

# Enthought library imports:
from enthought.etsconfig.api \
    import ETSConfig
    
from enthought.naming.unique_name \
    import make_unique_name
    
from enthought.traits.api \
    import HasTraits, Property, Instance, Str, File, Any, on_trait_change
    
from enthought.traits.ui.api \
    import View, VGroup, Item, HSplit, VSplit, InstanceEditor, ValueEditor
    
from enthought.pyface.api \
    import DirectoryDialog

from enthought.blocks.api \
    import Block, unparse
        
from enthought.block_canvas.block_display.block_unit \
    import BlockUnit
    
from enthought.block_canvas.context.data_context \
    import DataContext
    
from enthought.block_canvas.context.editors.context_shell_editor \
    import ContextShellEditor
    
from enthought.block_canvas.function_tools.handled_function_search \
    import HandledFunctionSearch
    
from enthought.block_canvas.function_tools.function_library \
    import FunctionLibrary
    
from enthought.block_canvas.function_tools.utils \
    import USER_MODULE_NAME

from enthought.block_canvas.interactor.configurable_interactor \
     import INTERACTOR_LIST

# Local imports:
from block_application_view_handler \
    import BlockApplicationMenuBar, BlockApplicationViewHandler
    
from ui.project_folder_ui \
    import ProjectFolderUI
    
from utils \
    import create_unique_project_name
    
# Global logger:
logger = logging.getLogger(__name__)
saved_context_prefix = 'saved_contexts_'

##########################################################################
# The main application class
##########################################################################

class BlockApplication(HasTraits):
    """ One object to bind them all.

        Hopefully, these won't have to be in one class later on.  They can
        be added removed from an application on the fly.  They will discover
        each other based Envisage services...

        Note (June 19, '07): Refactored the block-application to split into
        block-unit and the rest (PythonShell, Function)
    """

    #########################################################################
    # BlockApplication traits
    #########################################################################

    # Block unit which encapsulates the block, its code, its views, and other
    # attributes.
    block_unit = Instance( BlockUnit )

    # Search boxes for finding functions to place on module.
    function_search = Instance( HandledFunctionSearch, args = () )

    # Data context from the block that is used for the python shell.
    exec_context = Property( depends_on = 'block_unit' )

    # Status bar text
    status = Str

    # File name where block is saved.
    file_path = File

    # Project file it is being loaded from
    project_file_path = Str

    #########################################################################
    # object interface
    #########################################################################

    def __init__(self, code=None, context=None, **traits):
        """ Sync the status message to the status information in the BlockUnit
        """

        super(BlockApplication, self).__init__(**traits)
        if context is None:
            context = DataContext()

        if code is None:
            self.block_unit = BlockUnit(data_context = context)
        else:
            self.block_unit = BlockUnit(code=code, data_context=context)

        # sync the status, but make sure to get the initial status first
        self.status = self.block_unit.status
        self.sync_trait('status', self.block_unit, mutual=True)


    ##########################################################################
    # HasTraits interface
    ##########################################################################

    def trait_view(self, name=None, view_elements=None):
        return View(
          VGroup( 
            HSplit(
                Item( 'function_search',
                      label      = 'Search',
                      id         = 'search',
                      style      = 'custom',
                      dock       = 'horizontal',
                      show_label = False,
                ),
                VSplit(
                    Item( 'object.block_unit.codeblock_ui',
                          label      = 'Canvas',
                          id         = 'canvas',
                          editor     = InstanceEditor( 
                                           view = 'canvas_view' ),
                          style      = 'custom',
                          dock       = 'horizontal',
                          show_label = False
                    ),
                    Item( 'object.block_unit.codeblock_ui',
                          label      = 'Code',
                          id         = 'code',
                          editor     = InstanceEditor( view = 'code_view' ),
                          style      = 'custom',
                          dock       = 'horizontal',
                          show_label = False
                    ),
                    # DEBUG: Comment this 'Item' out to remove debug view...
                    Item( 'object.block_unit.codeblock_ui',
                          label      = 'Debug',
                          id         = 'debug',
                          editor     = ValueEditor(),
                          style      = 'custom',
                          dock       = 'horizontal',
                          show_label = False
                    ),
                    Item( 'exec_context',
                          label      = 'Shell',
                          id         = 'shell',
                          editor     = ContextShellEditor(
                                           block_unit = self.block_unit ),
                          dock       = 'horizontal',
                          show_label = False,
                    ),
                ),
                Item( 'object.block_unit',
                      label      = 'Variables',
                      id         = 'variables',
                      editor     = InstanceEditor(
                                       view = 'variables_view' ),
                      style      = 'custom',
                      dock       ='horizontal',
                      show_label = False,
                ),
                id='panel_split',
            ),
            Item( 'status',
                  style      = 'readonly',
                  show_label = False,
                  resizable  = False 
            ),
            # fixme: This code only works on platforms for which wx.GCDC is
            # defined...
            #group_theme = '@XG1'
          ),
          title     = 'Block Canvas',
          menubar   = BlockApplicationMenuBar,
          width     = 800,
          height    = 600,
          id        = 'enthought.block_canvas.app.block_application',
          resizable = True,
          handler   = BlockApplicationViewHandler,
        )

    ### private methods ######################################################

    def _get_exec_context(self):
        return self.block_unit._exec_context


    ##########################################################################
    # BlockApplication interface
    ##########################################################################

    ### project persistence methods ##########################################

    def load_block_from_file(self, file_path):
        """ Load a file of python code into the block.
        """
        # Load the block from the given path.
        self.block_unit.codeblock.load(str(file_path))

        # And point at the new path name.
        self.file_path = file_path

        return


    def load_project_from_file(self, file_path):
        """ Load a project from .prj files.

            Parameters:
            -----------
            file_path: Str
                Complete file-path where the project is saved.

        """

        logger.debug('BlockUnit: Loading project from %s' %file_path)

        del self.block_unit
        self.block_unit = BlockUnit()

        if not os.path.exists(file_path):
            msg = 'BlockUnit: Loading of project at ' + \
                    file_path + ' failed: Path does not exist.'
            logger.error(msg)
            return

        self.project_file_path = file_path

        # Read the .prj file and retrieve information about where the script
        # and context are separately saved.
        file_object = open(file_path, 'rb')
        lines = file_object.readlines()
        lines_split = [line.split('=') for line in lines]
        lines_dict = {}
        for line in lines_split:
            key = line[0].strip().lower()
            if key != '':
                lines_dict[key] = line[1].strip()
        file_object.close()

        # Read the code and build the block
        s_path = 'script_path'
        if lines_dict.has_key(s_path) and os.path.exists(lines_dict[s_path]):
            self.load_block_from_file(lines_dict[s_path])
        else:
            msg = 'BlockUnit: Loading of script for project at ' + \
                    file_path + ' failed.'
            logger.error(msg)

        # Read the context file
        context, c_path = None, 'context_path'
        if lines_dict.has_key(c_path) and os.path.exists(lines_dict[c_path]):
            context = DataContext.load_context_from_file(lines_dict[c_path])

        # Read the layout file
        l_path = 'layout_path'
        if lines_dict.has_key(l_path) and os.path.exists(lines_dict[l_path]):
            self.block_unit.codeblock_ui.block_controller.layout_engine.load_layout(lines_dict[l_path])

        # Assign the context if any
        if context is not None:
            self.block_unit.data_context = context
        else:
            msg = 'BlockUnit: Loading of context for project at ' + \
                    file_path + ' failed.'
            logger.error(msg)

        # Interactor range files
        for key in INTERACTOR_LIST:
            if lines_dict.has_key(key):
                self.interactor_range_files[key] = lines_dict[key]

        # Loading saved contexts
        self.exec_context.saved_contexts = {}
        saved_context_keys = [key for key in lines_dict.keys() if
                              key.startswith(saved_context_prefix) ]
        if len(saved_context_keys):
            for key in saved_context_keys:
                final_key = key.replace(saved_context_prefix,'')
                self.exec_context.saved_contexts[final_key] = lines_dict[key]

        return


    def save_block_to_file(self, file_path):
        """ Save the block to a file as python code.
        """
        # We convert the block to code directly instead of using the
        # code displayed, because the user may have put it in an unparsable
        # state.
        # fixme: Is this what we should do?

        # Should write it out as .py file
        split_path = os.path.splitext(file_path)
        if split_path[1] != 'py':
            new_path = '.'.join((split_path[0], 'py'))
        else:
            new_path = file_path

        # Save the current code to the file.
        file_obj = open(new_path, 'w')
        block_code = unparse(self.block_unit.codeblock.block.ast)
        file_obj.write(block_code)
        file_obj.close()

        # And point at the new path name.
        self.file_path = new_path
        return


    def save_loaded_project(self):
        """ Save project to where it was loaded from
        """

        if not os.path.exists(self.project_file_path):
            self.save_new_project()

        else:
            path_split = os.path.split(self.project_file_path)
            path_ext = os.path.splitext(path_split[1])
            dir_name = path_split[0]
            project_name = path_ext[0]
            if os.path.exists(dir_name) and \
                isinstance(project_name, basestring) and project_name != '':
                self._save_project(dir_name, project_name)
            else:
                msg = 'Error in saving project at %s'% self.project_file
                logger.error(msg)

        return


    def save_new_project(self):
        """ Save a new project

            Save it in the user-directory.
        """

        # Save afresh in the user directory
        project_dir = ETSConfig.user_data
        project_name = 'converge_project'
        project_name = create_unique_project_name(project_dir,
                                                  project_name)
        pfui = ProjectFolderUI(project_dir = project_dir,
                               project_name = project_name)
        ui = pfui.edit_traits(kind = 'livemodal')
        if ui.result:
            file_path = os.path.join(pfui.project_dir,
                                     pfui.project_name+'.prj')
            if file_path != '':
                self.save_project_to_file(file_path)

        return


    def save_project_to_file(self, file_path):
        """ Save block and context as a project to a file.

            Parameters:
            -----------
            file_path: Str
                Complete file-path where the project file is to be saved.

        """

        # Make a directory to save the pickled context and the script
        pathsplit = os.path.split(file_path)
        path_ext = os.path.splitext(pathsplit[1])
        dir_name = pathsplit[0]
        project_name = create_unique_project_name(dir_name, path_ext[0])

        self._save_project(dir_name, project_name)
        return

    def clear_active_context(self):
        self.block_unit._exec_context.clear()
        self.block_unit.variables.update_variables()
        self.block_unit.data_context['context'] = \
                self.block_unit.data_context._bindings

    ### private methods ######################################################

    def _save_project(self, dir_name, project_name):
        """ Save block and context as a project to a file.

            Parameters:
            -----------
            file_path: Str
                Complete file-path where the project file is to be saved.

        """

        project_file = os.path.join(dir_name, project_name+'.prj')
        project_dir = os.path.join(dir_name, project_name+'_files')
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        # Save saved contexts before pickling the context
        saved_context_script = self._save_saved_contexts_to_project(project_dir)

        # Pickle the context.
        context_path = os.path.join(project_dir, project_name+'.pickle')
        self.block_unit.data_context.pop('context', -1)
        self.block_unit.data_context.save_context_to_file(context_path)

        # Save the script.
        script_path = os.path.join(project_dir, project_name+'.py')
        self.save_block_to_file(script_path)

        # Save the canvas layout
        layout_path = os.path.join(project_dir, 'layout.pickle')
        self.save_canvas_layout_to_file(layout_path)

        # Final script
        script = '\n'.join(('SCRIPT_PATH = %s' % script_path,
                            'CONTEXT_PATH = %s' % context_path,
                            'LAYOUT_PATH = %s' % layout_path))

        # Save interactor-preferences
        for name in INTERACTOR_LIST:
            if self.block_unit.interactor_range_files.has_key(name) and \
                os.path.exists(self.block_unit.interactor_range_files[name]):
                range_file_name = '_'.join((project_name, name,
                                            'interactor_range_file.txt'))
                range_file = os.path.join(project_dir,range_file_name)
                if self.block_unit.interactor_range_files[name] != range_file:
                    shutil.copy(self.block_unit.interactor_range_files[name],
                                range_file)
                    script = '\n'.join((script,
                                        '%s = %s' % (name.upper(), range_file)))

        if saved_context_script != '':
            script = '\n'.join((script, saved_context_script))

        # Write the information of the locations of pickled context and saved
        # script into the .prj file.
        logger.debug('BlockUnit: Saving project at %s' % project_file)
        self.project_file_path = project_file
        file_object = open(project_file, 'wb')
        file_object.write(script)
        file_object.close()

        return


    def _save_saved_contexts_to_project(self, project_dir):
        """ Saving saved_contexts to a project

            Parameters:
            -----------
            project_dir: Str

            Returns:
            --------
            script: Str
                Details of the saved contexts. This script to be added to
                the project file script.

        """

        # Return if there are no saved contexts.
        if not len(self.exec_context.saved_contexts):
            return ''

        # Prepare the directory to save pickled saved contexts.
        saved_contexts_dir = os.path.join(project_dir, 'saved_contexts')
        if not os.path.exists(saved_contexts_dir):
            os.mkdir(saved_contexts_dir)
        elif not os.path.isdir(saved_contexts_dir):
            try:
                os.remove(saved_contexts_dir)
            except OSError, (errno, strerror):
                logger.error('Error removing %s, %s' % (saved_contexts_dir,
                                                        strerror))
                dir_name = make_unique_name('saved_contexts',
                                                     os.listdir(project_dir))
                saved_contexts_dir = os.path.join(project_dir, dir_name)


        # Save out all the files to the new directory.
        count = 0
        script = ''
        for key, value in self.exec_context.saved_contexts.items():
            name_finalized = False
            new_f_name = ''

            # Pick a file name for the saved context.
            while not name_finalized:
                file_name = saved_context_prefix+str(count)+'.pickle'
                new_f_name = os.path.join(saved_contexts_dir, file_name)
                if  value == new_f_name or \
                    not new_f_name in self.exec_context.saved_contexts.values():
                    name_finalized = True
                else:
                    count = count+1

            # Copy the files to the new location and update the context.
            if value != new_f_name and new_f_name != '':
                shutil.copy(value, new_f_name)
                self.exec_context.saved_contexts[key] = new_f_name

                # Add the information to the script that is to be added with
                # the script saving the other information on the project.
                script = script + '%s%s = %s\n' % (saved_context_prefix.upper(),
                                                   key.upper(), new_f_name)
                count = count+1

        return script

    def save_canvas_layout_to_file(self, filename):
        self.block_unit.codeblock_ui.block_controller.layout_engine.save_layout(filename)

    @on_trait_change('function_search.handler.dclicked')
    def _update_from_function_search(self):
        """ Update the block after double-clicking a function from the
            function search.

            The double-click on function search opens a function-call view.
            We need to be able to add the selected function to the block.
            Hence updating the block.

        """

        handler = self.function_search.handler
        func_def = handler.activated_function
        
        if func_def is None:
            return
        
        is_user_function = func_def.fullname.startswith(USER_MODULE_NAME)
        
        if is_user_function \
                and func_def.name in self.block_unit._function_context.keys():
            self.block_unit.codeblock.remove_from_imports(func_def.name, True)
            
        self.block_unit.codeblock.add_function(func_def)

        return


# Test
if __name__ == '__main__':
    b = BlockApplication()
    b.configure_traits()

### EOF ------------------------------------------------------------------------
