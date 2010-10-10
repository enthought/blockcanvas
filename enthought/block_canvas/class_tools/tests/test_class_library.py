# Standard library imports
import os
import sys
import unittest

# Enthought library imports

from enthought.block_canvas.class_tools.class_library import ClassLibrary

def local_path():
    return os.path.dirname(__file__)

class ClassLibraryTest(unittest.TestCase):

    ##########################################################################
    # TestCase interface
    ##########################################################################

    def setUp(self):
        """ Ensure that the current directory is on the python path.

            We need this to import the test modules.
        """
        sys.path.append(local_path())
        unittest.TestCase.setUp(self)

    def tearDown(self):
        """ Remove the current directory from the python path.
        """
        del sys.path[-1]
        unittest.TestCase.tearDown(self)

    ##########################################################################
    # ClassLibraryTest interface
    ##########################################################################


    def test_xml_timings(self):
        """Test the time it takes to import the xml module, not applicable 
        if xml not present"""
        
        try:
            import xml
        except:
            # Skip this test if cp not available
            import nose
            raise nose.SkipTest()
        
        import time
        t1 = time.clock()
        library = ClassLibrary(modules=[])

        library.modules.append('xml')
        t2 = time.clock()
        self.assertEqual(t2-t1<2., True)
        

        


    def test_pickling(self):
        library = ClassLibrary(modules=[])
        library.modules = ['cp','xml','_socket','sys','os']
        old_classes = library.classes

        import cPickle
        cPickle.dump(library, open(r'test_library.pickle','wb'))
        library = cPickle.load(open(r'test_library.pickle','rb'))
        library.modules = ['cp','xml','_socket','sys','os']
        self.assertEqual(len(old_classes), len(library.classes))
        os.unlink('test_library.pickle')


if __name__ == '__main__':
    unittest.main()
