# System library imports
import os

# Enthought library imports
from enthought.traits.api import (HasTraits, Str, List, Dict,
                                  Callable, implements)

# Local imports
from search_package import find_functions, get_module_path
from i_minimal_function_info import MinimalFunctionInfo

class FunctionLibrary(HasTraits):
    """ Keep track of a list of modules/packages to search for functions.
    
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
            
        fixme: I'm not sure this will handle zip files imports correctly.
        fixme: We do not do anything to try and update a cache if a module
               on disk changes.
        fixme: If we cached module file names, their time stamp, and 
               the functions included in them, startup would be much faster.
    """
    
    ##########################################################################
    # FunctionLibrary traits
    ##########################################################################

    # List of strings such as foo.bar that specifies which modules to search.
    modules = List(Str)
           
    # List of the functions found in the specified modules/pacakges.
    # Each function is represented by an object with 'name' and 'module' 
    # attributes.
    functions = List

    # A factory function for generating items in the function lists.  The
    # only requirements is that it take 'module' and 'name' as keyword args.
    # fixme: If someone assigns a function into this, will pickling break?
    function_factory = Callable(MinimalFunctionInfo)
    
    # Keep function list for modules cached so that we don't have search
    # for them each time there is an update.
    # fixme: Be careful about this so that we don't end up caching things
    #        that the user may be editing.
    _module_cache = Dict
    
        
    ##########################################################################
    # FunctionLibrary interface
    ##########################################################################

    def refresh_module(self, module=None):
        """ Reparse the module,specified as a string , looking for functions.  
        
            If module=None, then all strings in the modules string are 
            re-searched.  If module was not previously in the list of 
            modules, searched, it is added.
            
            FunctionLibrary maintains a cache so that it doesn't have to 
            search modules that it has recently parsed.  This method 
            forces a refresh of this cache.
        """
        # fixme: handle case when module name is bad.
        
        if module is None:
            # Update all modules.  Clear cache, and update the function list.
            self._module_cache[module] = {}
            self._update_function_list()
        else:
            # Find the functions in the module and put them in the cache.    
            funcs = _functions_from_module(self, module)
            self._module_cache[module] = funcs    
            
            if module not in self.modules:
                # This forces an update of the function list, so we don't 
                # do it explicitly in this code path.
                self.modules.append(module)
            else:
                # We'll rebuild the function list from scratch, but it will 
                # be fast because everything is cached.
                self._update_function_list()


    ### private interface ####################################################
    
    def _functions_from_module(self, module):

        # Test whether this module imports from a Pure python file.
        # If it isn't represented as a file, we'll need to 
        # use the import method of searching for functions.
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
            
        mod_and_name = find_functions(module, import_method)    
        funcs = [self.function_factory(module=module,name=name) 
                    for module, name in mod_and_name]
        return funcs
        
    
    def _update_function_list(self):
        functions = []
        for module in self.modules:
            # First, try the cache.
            if self._module_cache.has_key(module):
                funcs = self._module_cache[module]
            else:
                # Otherwise, we need to search the module.
                funcs = self._functions_from_module(module)
                # fixme: We need to filter the cache based on some
                # items we never want to cache.
                self._module_cache[module] = funcs
            functions.extend(funcs)
            
        self.functions = functions

    ### trait listeners ######################################################

    def _modules_changed(self):
        self._update_function_list()
        
    def _modules_items_changed(self):
        self._update_function_list()



if __name__ == "__main__":
    library = FunctionLibrary(modules=['os'])
    print library.modules
    print library.functions
    
    library.modules.append('sys')
    print library.modules
    print library.functions
    
    library.modules.append('_socket')
    print library.modules
    print library.functions
    
    print 'including cp:'
    import time
    t1 = time.clock()
    library.modules.append('xml')
    library.modules.append('cp')
    print library.modules
    print library.functions
    t2 = time.clock()
    print t2-t1
    
    old_functions = library.functions
    t1 = time.clock()
    library.modules = ['cp','xml','_socket','sys','os']
    assert(len(old_functions) == len(library.functions))
    t2 = time.clock()
    print t2-t1
    #library.modules = ['cp']
    #print library.functions
    
    # handling a "bad" module.
    import cPickle
    cPickle.dump(library, open(r'c:\temp\library.pickle','wb'))
    library = cPickle.load(open(r'c:\temp\library.pickle','rb'))
    library.modules = ['cp','xml','_socket','sys','os']
    assert(len(old_functions) == len(library.functions))
    t2 = time.clock()
    print t2-t1
