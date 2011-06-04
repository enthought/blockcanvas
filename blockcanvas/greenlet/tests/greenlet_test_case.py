
# This was orginally named test_greenlet.py.  I converted that file to
# a unittest.TestCase to conform to our process.
import unittest

from enthought.greenlet import greenlet
import sys, thread, threading

class SomeError(Exception):
    pass

def fmain(seen):
    try:
        greenlet.getcurrent().parent.switch()
    except:
        seen.append(sys.exc_info()[0])
        raise
    raise SomeError


class GreenletTestCase( unittest.TestCase ):

    def test_simple(self):
        lst = []
        def f():
            lst.append(1)
            greenlet.getcurrent().parent.switch()
            lst.append(3)
        g = greenlet(f)
        lst.append(0)
        g.switch()
        lst.append(2)
        g.switch()
        lst.append(4)
        assert lst == range(5)

    def test_threads(self):
        success = []
        def f():
            self.test_simple()
            success.append(True)
        ths = [threading.Thread(target=f) for i in range(10)]
        for th in ths:
            th.start()
        for th in ths:
            th.join()
        assert len(success) == len(ths)


    def test_exception(self):
        seen = []
        g1 = greenlet(fmain)
        g2 = greenlet(fmain)
        g1.switch(seen)
        g2.switch(seen)
        g2.parent = g1
        assert seen == []
        self.failUnlessRaises(SomeError, g2.switch)
        assert seen == [SomeError]
        g2.switch()
        assert seen == [SomeError]

    def send_exception(self, g, exc):
        def crasher(exc):
            raise exc
        g1 = greenlet(crasher, parent=g)
        g1.switch(exc)

    def test_send_exception(self):
        seen = []
        g1 = greenlet(fmain)
        g1.switch(seen)
        self.failUnlessRaises(KeyError, self.send_exception, g1, KeyError)
        assert seen == [KeyError]

    def test_dealloc(self):
        seen = []
        g1 = greenlet(fmain)
        g2 = greenlet(fmain)
        g1.switch(seen)
        g2.switch(seen)
        assert seen == []
        del g1
        assert seen == [greenlet.GreenletExit]
        del g2
        assert seen == [greenlet.GreenletExit, greenlet.GreenletExit]

    def test_dealloc_other_thread(self):
        seen = []
        someref = []
        lock = thread.allocate_lock()
        lock.acquire()
        lock2 = thread.allocate_lock()
        lock2.acquire()
        def f():
            g1 = greenlet(fmain)
            g1.switch(seen)
            someref.append(g1)
            del g1
            lock.release()
            lock2.acquire()
            greenlet()   # trigger release
            lock.release()
            lock2.acquire()
        t = threading.Thread(target=f)
        t.start()
        lock.acquire()
        assert seen == []
        assert len(someref) == 1
        del someref[:]
        # g1 is not released immediately because it's from another thread
        assert seen == []
        lock2.release()
        lock.acquire()
        assert seen == [greenlet.GreenletExit]
        lock2.release()
        t.join()

    def test_frame(self):
        def f1():
            f = sys._getframe(0)
            assert f.f_back is None
            greenlet.getcurrent().parent.switch(f)
            return "meaning of life"
        g = greenlet(f1)
        frame = g.switch()
        assert frame is g.gr_frame
        assert g
        next = g.switch()
        assert not g
        assert next == "meaning of life"
        assert g.gr_frame is None

if __name__ == '__main__':
    unittest.main(argv=sys.argv)

### EOF #######################################################################
