""" Defines the Project class """


# Standard library imports
import logging
import os
from os.path import abspath, join

# Enthought library imports
from traits.api import (Directory, HasTraits, Instance, Int, List,
        on_trait_change, Property, Trait)

# Block canvas imports
from codetools.contexts.api import IListenableContext
from blockcanvas.app import scripting
from codetools.contexts.api import DataContext

# Local relative imports
from experiment import Experiment

logger = logging.getLogger(__name__)

class Project(HasTraits):
    """
    Ties together the contexts, execution model, and layouts that comprise a
    single project.  Also stores various view-related state.
    """

    # A list of contexts that are associated with the project
    contexts = List(Instance(IListenableContext, adapt='yes', rich_compare=False))

    # A list of the experiments in this project
    experiments = List(Instance(Experiment))

    # The active experiment for this project.  This can be used by scripting
    # methods on the project.
    active_experiment = Property(Instance(Experiment),
        depends_on=['_active_exp_ndx', 'experiments', 'experiments_items'])

    # Name of directory where the project is saved out.  Projects are
    # always saved to their own directories.
    project_save_path = Directory()

    #---------------------------------------------------------------------
    # Private traits
    #---------------------------------------------------------------------

    # Index of the currently active experiment.  If None, then there is no
    # active experiment.
    _active_exp_ndx = Trait(None, None, Int)

    #---------------------------------------------------------------------
    # Class attributes
    #---------------------------------------------------------------------

    # This is the name of the ConfigObj specification file that defines
    # the format and structure of saved project files.
    CONFIG_SPEC = "project_config_spec.txt"

    # Since projects are represented/encapsulated by a directory (see
    # **project_save_path** instance attribute), the actual ini-format
    # save file inside that directory has to be given a name.  Since
    # there is no mechanism for a priori informing a project what that
    # file is named, we settle on a convention to always name the
    # project file the same.
    PROJECT_FILE_NAME = "project.txt"

    #---------------------------------------------------------------------
    # Classmethods
    #---------------------------------------------------------------------

    @classmethod
    def from_dir(cls, dirname):
        """ Constructs a new project instance from the given **dirname**.
        If no directory name is provided, returns None.
        """
        if dirname == "":
            return None
        proj = cls()
        proj.load(dirname)
        return proj

    #---------------------------------------------------------------------
    # Public methods / scripting API
    #---------------------------------------------------------------------

    def add_context(self, context):
        """ Makes another context available to the project.  (The active context
            must be one of the available contexts.)
        """
        self.contexts.append(context)

    def remove_context(self, context):
        """ Removes the particular context from the list of available contexts
        """
        # Not only do we need to remove the context from our list, but we
        # also need to each of our experiments and disconnect them from
        # the context.
        for exp in self.experiments:
            if exp.shared_context == context:
                exp.shared_context = None
        self.contexts.remove(context)

    def add_experiment(self, experiment):
        """ Adds a new experiment to the project.
        """
        self.experiments.append(experiment)

    def remove_experiment(self, experiment):
        """ Removes an experiment from the project.  If this is the active
            experiment, then the active experiment is set to None.
        """
        self.experiments.remove(experiment)

    def find_context(self, name):
        """ Returns the named context from the project's list of contexts.
            If it cannot be found, returns None.
        """
        for c in self.contexts:
            if c.name == name:
                return c
        return None

    def find_experiment(self, name):
        """ Returns the name experiment from the project's list of experiments.
        If it cannot be found, returns None.
        """
        for e in self.experiments:
            if e.name == name:
                return e
        return None

    #---------------------------------------------------------------------
    # Persistence
    #---------------------------------------------------------------------

    def load(self, dirname):
        """ Loads the project from the given directory.  The existing state
        of the project is completely modified.
        """
        # TODO: We should formalize this dependency at some point and move
        # this import to the top level
        from configobj import ConfigObj

        if dirname == "":
            raise IOError("Cannot load project from empty path.")
        elif not os.path.isdir(dirname):
            raise IOError("Cannot find directory: " + dirname)

        filename = abspath(join(dirname, self.PROJECT_FILE_NAME))
        if not os.path.isfile(filename):
            raise IOError('Cannot load %s from project directory "%s".' % \
                        (self.PROJECT_FILE_NAME, dirname))

        # Every project is saved as a text ConfigObj file that describes
        # the name and location of the real data files.
        configspec = ConfigObj(self.CONFIG_SPEC, list_values=False)
        config = ConfigObj(filename, configspec=configspec)

        contexts = []
        for context_config in config["Contexts"].values():
            ctx = DataContext.load(join(dirname, context_config["file"]))
            ctx.name = context_config["name"]
            contexts.append(ctx)
        self.contexts = contexts

        experiments = []
        if hasattr(scripting, "app"):
            app = scripting.app
        else:
            app = None
        for exp_config in config["Experiments"].values():
            experiment = Experiment()
            exp_dir = join(dirname, exp_config["save_dir"])
            experiment.load_from_config(exp_config, exp_dir, project=self)
            experiments.append(experiment)
        self.experiments = experiments

        proj_config = config["Project"]
        if proj_config.has_key("active_experiment"):
            self.active_experiment = self.find_experiment(proj_config["active_experiment"])
            
        # Update Project Save Path 
        self.project_save_path = dirname
        
        return

    def save(self, dirname=""):
        """ Saves the project as a directory named **dirname**.

        If **dirname** is not provided, the **project_save_path** attribute
        should already be set.

        If **project_save_path** is not set, then it will be set to **dirname**.
        """
        if dirname == "":
            dirname = self.project_save_path
        elif self.project_save_path == "":
            self.project_save_path = dirname

        # Do some error checking
        if dirname == "":
            raise IOError("Cannot save project to empty path.")
        elif os.path.isfile(dirname):
            raise IOError('Cannot save project to directory "%s"; '
                          'file exists.' % dirname)

        logger.info('Starting save of project to "%s"' % dirname)
        if not os.path.isdir(dirname):
            logger.info('    Creating directory "%s"' % dirname)
            os.mkdir(dirname)

        # TODO: We should formalize this dependency at some point and move
        # this import to the top level
        from configobj import ConfigObj
        config = ConfigObj()

        config["Project"] = {}

        exp = {}
        for i, experiment in enumerate(self.experiments):
            if experiment.name is not None and experiment.name != "":
                safename = self._encode_name(experiment.name)
            else:
                safename = "Experiment_%d" % i
            exp[safename] = experiment.save(basename=dirname, dirname=safename)
            logger.info('    Saved experiment "%s" to subdir "%s"' % \
                            (experiment.name, safename))
        config["Experiments"] = exp

        if self.active_experiment is not None:
            config["Project"]["active_experiment"] = self.active_experiment.name

        contexts = {}
        for i, ctx in enumerate(self.contexts):
            if ctx.name is not None and ctx.name != "":
                safename = self._encode_name(ctx.name)
            else:
                safename = "Context_%d" % i
            filename = safename + ".pickle"
            contexts[safename] = dict(name=ctx.name, file=filename)
            ctx.save(join(dirname, filename))
            logger.info('    Saved context "%s" to file "%s"' % \
                          (ctx.name, filename))
        config["Contexts"] = contexts

        config.filename = join(dirname, self.PROJECT_FILE_NAME)
        logger.info('    Writing project to "%s"' % config.filename)
        config.write()
        logger.info('Finished saving project to "%s"' % dirname)
        return

    def _encode_name(self, name):
        """ Given the name of a context or experiment, returns an encoding of
        it that is compliant with the filesystem.
        """
        # TODO: For now, just return the given name
        return name

    #---------------------------------------------------------------------------
    # Event handlers, property getters and setters
    #---------------------------------------------------------------------------

    def _get_active_experiment(self):
        if self._active_exp_ndx is not None:
            return self.experiments[self._active_exp_ndx]
        else:
            return None

    def _set_active_experiment(self, experiment):
        if experiment not in self.experiments:
            self.experiments.append(experiment)
        self._active_exp_ndx = self.experiments.index(experiment)

    @on_trait_change("experiments[]")
    def _experiments_changed(self):
        if len(self.experiments) == 0:
            self._active_exp_ndx = None
        elif self._active_exp_ndx is None:
            self._active_exp_ndx = 0
        elif self._active_exp_ndx > len(self.experiments) - 1:
            self._active_exp_ndx = len(self.experiments) - 1

