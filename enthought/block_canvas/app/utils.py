""" Util functions for block application.
"""

# Standard imports
import logging, os, re, string

# ETS imports
from enthought.contexts.geo_context import GeoContext

# Global logger
logger = logging.getLogger(__name__)

# Global translator to ensure that log-context names are python-friendly
trans_table = string.maketrans('/.\\@#$%^&*()-+=<>', '_________________')

#-------------------------------------------------------------------------------
#  Export functions
#-------------------------------------------------------------------------------

def create_unique_project_name( dir_name, project_name ):
    """ Create a unique project name such that dir_name/<project_name>.prj
        and dir_name/<project_name>_files are unique paths.

        Parameters:
        -----------
        dir_name : Str
            complete path for the directory where the project will be saved
        project_name : Str
            Name chosen for the project

    """

    project_file = os.path.join(dir_name, project_name+'.prj')
    project_dir = os.path.join(dir_name, project_name+'_files')
    final_project_name = project_name

    count = 1
    while os.path.exists(project_dir) or os.path.exists(project_file):
        final_project_name = project_name + str(count)
        project_dir = os.path.join(dir_name, final_project_name+'_files')
        project_file = os.path.join(dir_name, final_project_name+'.prj')
        count = count+1

    return final_project_name


#-------------------------------------------------------------------------------
#  Import functions
#-------------------------------------------------------------------------------

def create_geo_context( context, c_name = None ):
    """ Create a data context from the NumericContext

        Parameters
        ----------
        context : NumericContext
            The source for the new context.
        c_name  : Str
            Name to be given to the geo-context.

        Returns:
        --------
        geo_context : GeoContext
            Has the same context items as the context.

    """

    if c_name is None:
        name = context.context_name
    else:
        name = c_name

    name = str(name).translate(trans_table)

    return GeoContext(name = name, subcontext = context.context_data._dict)


#-------------------------------------------------------------------------------
#  Miscellaneous functions
#-------------------------------------------------------------------------------

def regex_from_str(str):
    """ Maps user input to filters that are internally useful.
    """

    f = []
    for filter in str.split(','):
        str = filter.strip().replace("*", ".*")
        # If re barfs, just match everything
        try:
            f.append(re.compile(str, re.IGNORECASE))
        except:
            f.append(re.compile(".*"))
    return f


# Test
if __name__ == '__main__':
#    tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
#    filename = os.path.join(tests_dir, 'example.las')
#    context = import_log_files(filename, 'las')
#    print context.keys()

    context, filename = import_segy_file()
    if context is not None:
        print context.keys()
    else:
        print 'None'

### EOF ------------------------------------------------------------------------
