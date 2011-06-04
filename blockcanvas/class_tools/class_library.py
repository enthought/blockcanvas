# System library imports
import os

# Enthought library imports
from traits.api import (HasTraits, Str, List, Dict,
                                  Callable, implements)

# Local imports
from search_package import find_classes
from blockcanvas.function_tools.search_package import get_module_path
from i_minimal_class_info import MinimalClassInfo

class ClassLibrary(HasTraits):
    """ Keep track of a list of modules/packages to search for classes.

        The typical tree cases for a module are:

        1. The module is a pure python module, and we can search its code.
        2. The module is an extension module, so it has a file, but it is
           not python code we can parse.  We have to import this
           type of module to find its functions.
        3. The module is a builtin module (like sys), and it doesn't have
           a file.  Like an extension module, this must be imported
           and searched.
        4. The module is a package name.  In this case, we search all the
           modules the package contains.
        5. [don't handle currently] The specified value is a file or a
           directory name.
    """

        #fixme: I'm not sure this will handle zip files imports correctly.
        #fixme: We do not do anything to try and update a cache if a module
        #       on disk changes.
        #fixme: If we cached module file names, their time stamp, and
        #       the functions included in them, startup would be much faster.

    ##########################################################################
    # FunctionLibrary traits
    ##########################################################################

    # List of strings such as foo.bar that specifies which modules to search.
    modules = List(Str)

    # List of the classes found in the specified modules/pacakges.
    # Each class is represented by an object with 'name' and 'module'
    # attributes.
    classes = List

    # A factory function for generating items in the function lists.  The
    # only requirements is that it take 'module' and 'name' as keyword args.
    # fixme: If someone assigns a function into this, will pickling break?
    class_factory = Callable(MinimalClassInfo)

    # Keep class list for modules cached so that we don't have search
    # for them each time there is an update.
    # fixme: Be careful about this so that we don't end up caching things
    #        that the user may be editing.
    _module_cache = Dict


    ##########################################################################
    # FunctionLibrary interface
    ##########################################################################

    def refresh_module(self, module=None):
        """ Reparse the module,specified as a string , looking for classes.

            If module=None, then all strings in the modules string are
            re-searched.  If module was not previously in the list of
            modules, searched, it is added.

            ClassLibrary maintains a cache so that it doesn't have to
            search modules that it has recently parsed.  This method
            forces a refresh of this cache.
        """
        # fixme: handle case when module name is bad.

        if module is None:
            # Update all modules.  Clear cache, and update the class list.
            self._module_cache[module] = {}
            self._update_class_list()
        else:
            # Find the classes in the module and put them in the cache.
            clss = self._classes_from_module(self, module)
            self._module_cache[module] = clss

            if module not in self.modules:
                # This forces an update of the class list, so we don't
                # do it explicitly in this code path.
                self.modules.append(module)
            else:
                # We'll rebuild the class list from scratch, but it will
                # be fast because everything is cached.
                self._update_function_list()


    ### private interface ####################################################

    def _classes_from_module(self, module):

        # Test whether this module imports from a Pure python file.
        # If it isn't represented as a file, we'll need to
        # use the import method of searching for classes.
        path = get_module_path(module)

        # fixme: What about zip files.

        if (os.path.exists(path) and
            os.path.splitext(path)[1] == '.py'):
            # If it is a file, then parse the ast.
            import_method = False
        elif (os.path.exists(path) and
            os.path.isdir(path)):
            # If it is a package directory, parse the ast.
            import_method = False
        else:
            # Must be extension module or built-in, or something else...
            # Use import to handle it.
            import_method = True

        mod_and_name = find_classes(module, import_method)
        clss = [self.class_factory(module=module,name=name)
                    for module, name in mod_and_name]
        return clss


    def _update_class_list(self):
        classes = []
        for module in self.modules:
            # First, try the cache.
            if self._module_cache.has_key(module):
                clss = self._module_cache[module]
            else:
                # Otherwise, we need to search the module.
                clss = self._classes_from_module(module)
                # fixme: We need to filter the cache based on some
                # items we never want to cache.
                self._module_cache[module] = clss
            classes.extend(clss)

        self.classes = classes

    ### trait listeners ######################################################

    def _modules_changed(self):
        self._update_class_list()

    def _modules_items_changed(self):
        self._update_class_list()



if __name__ == "__main__":
    library = ClassLibrary(modules=['os'])
    print library.modules
    print library.classes

    library.modules.append('sys')
    print library.modules
    print library.classes

    library.modules.append('_socket')
    print library.modules
    print library.classes

    print 'including cp:'
    import time
    t1 = time.clock()
    library.modules.append('xml')
    library.modules.append('cp')
    print library.modules
    print library.classes
    t2 = time.clock()
    print t2-t1

    old_classes = library.classes
    t1 = time.clock()
    library.modules = ['cp','xml','_socket','sys','os']
    assert(len(old_classes) == len(library.classes))
    t2 = time.clock()
    print t2-t1
