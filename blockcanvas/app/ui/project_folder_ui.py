""" UI for choosing folder and project name to save a project
"""

# Standard imports
import logging

# ETS imports
from enthought.block_canvas.app.utils import create_unique_project_name
from traits.api import HasTraits, Str, Directory
from traitsui.api import View, Item, Handler

# Global logger
logger = logging.getLogger(__name__)


#-------------------------------------------------------------------------------
# ProjectFolderUIHandler class
#-------------------------------------------------------------------------------

class ProjectFolderUIHandler(Handler):
    """ Handler for the UI class for choosing folder and project name for saving
        a project.
    """

    def closed(self, info, is_ok):
        if is_ok:
            pfui = info.object
            project_name = create_unique_project_name(pfui.base_dir,
                                                      pfui.project_name)
            if project_name != pfui.project_name:
                logger.debug('Since %s already exists, the project is '
                             'named as %s' % (pfui.project_name, project_name))
                pfui.project_name = project_name

        return


#-------------------------------------------------------------------------------
#  ProjectFolderUI Class
#-------------------------------------------------------------------------------

class ProjectFolderUI(HasTraits):
    """ UI for choosing folder and project name to save a project
    """

    base_dir = Directory
    project_name = Str('converge_project')

    view = View(Item('base_dir'), Item('project_name'),
                buttons = ['OK', 'Cancel'],
                close_result = False,
                resizable = True,
                handler = ProjectFolderUIHandler,
                width = 550,
                )


if __name__ == '__main__':
    pfui = ProjectFolderUI(base_dir='C:\\',project_name = 'Converge Project')
    ui = pfui.edit_traits(kind = 'livemodal')
    if ui.result:
        print pfui.base_dir, pfui.project_name


### EOF ------------------------------------------------------------------------
