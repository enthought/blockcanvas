from copy import copy
from cPickle import dumps, loads
from nose.tools import assert_equal, assert_not_equal, assert_raises

from enthought.util.sequence import union

from enthought.numerical_modeling.numeric_context.api import EventDict

from mapping_object_test_case import HashMappingProtocolTest

###############################################################################
# Test cases
###############################################################################

# EventDict is a full-featured mapping object; use HashMappingProtocolTest
class TestEventDict(HashMappingProtocolTest):
    type2test = factory = EventDict

    def test_events_single_name(self):
        'Events: single name'

        c = self.factory()
        dm = DictModifiedEventMonitor(c)

        c['x'] = 1
        dm.assert_event(added={'x':1})

        c['x'] = 1
        dm.assert_events()

        c['x'] = 'foo'
        dm.assert_event(changed={'x':1})

        c['x'] = 'foo'
        dm.assert_events()

        del c['x']
        dm.assert_event(removed={'x':'foo'})

        c['x'] = 'foo'
        dm.assert_event(added={'x':'foo'})

        c['x'] = [1,2]
        dm.assert_event(changed={'x':'foo'})

        c['x'] = [1,2]
        dm.assert_event(changed={'x':[1,2]}) # [1,2] is not [1,2] == True

        c['x'] = [2,1]
        dm.assert_event(changed={'x':[1,2]})

        del c['x']
        dm.assert_event(removed={'x':[2,1]})

    def test_events_multiple_names(self):
        'Events: multiple names'

        c = self.factory()
        dm = DictModifiedEventMonitor(c)

        c.update(a=1, x=[1,2], t=True)
        dm.assert_event(added={'a':1, 'x':[1,2], 't':True})

        c.update(a=2, x=[2,1], y=[1,2])
        dm.assert_event(changed={'a':1, 'x':[1,2]}, added={'y':[1,2]})

        del c['t']
        dm.assert_event(removed={'t':True})

        del c['x']
        dm.assert_event(removed={'x':[2,1]})

        c.clear()
        dm.assert_event(removed={'a':2, 'y':[1,2]})

    def test_attribute_interface(self):
        'Attribute interface'
        c = self.factory()
        c.update(a=1, x=[1,2,3], foo='foo')
        assert_equal(c.a, 1)
        assert_equal(c.x, [1,2,3])
        assert_equal(c.foo, 'foo')

    def test_pickling(self):
        'Pickling'
        def checked_pickle(c):
            p = loads(dumps(c))
            assert_equal(c, p)
            return p

        # TODO How should we test pickling?

    def test_methods_dont_generate_multiple_events(self):
        "Methods don't generate multiple events"

        # '__init__', 'update', and 'clear' are the only mapping object methods
        # that have any good reason to generate multiple events, so I don't
        # bother testing the rest.
        #
        # Testing events from '__init__' is a little tricky, and I'm surprised
        # I can actually 'on_trait_change' a '__new__'-ed but not '__init__'-ed
        # HasTraits object! If this stops working at some point, then we don't
        # need the test anyway.

        c = self.factory.__new__(self.factory)
        dm = DictModifiedEventMonitor(c)

        # A very strange case... but there are very strange people
        c.__init__(dict(a=1, b=2), c=3, d=4)
        dm.assert_event(added={'a':1, 'b':2, 'c':3, 'd':4})

        c.clear()
        dm.assert_event(removed={'a':1, 'b':2, 'c':3, 'd':4})

        c.update(dict(a=1, b=2), c=3, d=4)
        dm.assert_event(added={'a':1, 'b':2, 'c':3, 'd':4})

    def test_deferred_events(self):
        'Deferred events'

        # Possible event combinations:
        #   1. none    + added
        #   2. none    + changed
        #   3. none    + removed
        #   4. removed + added
        #   5. added   + changed
        #   6. changed + changed
        #   7. added   + removed
        #   8. changed + removed

        c = self.factory()
        dm = DictModifiedEventMonitor(c)

        c.update(a=1, x=[1,2], t=True)
        dm.assert_event(added={'a':1, 'x':[1,2], 't':True})

        c.defer_events = True
        # 3. none    + removed
        c.clear()
        # 4. removed + added
        c.update(a=1, x=[1,2], t=True)
        dm.assert_events()

        c.defer_events = False
        dm.assert_event(changed={'x':[1,2]}) # Because `[1,2] is not [1,2]`

        c.defer_events = True
        # 1. none    + added
        c['foo'] = 'foo'
        # 5. added   + changed
        c['foo'] = 'bar'
        # 2. none    + changed
        c['x'] = []
        # 6. changed + changed
        c['x'] = [1,2,3]
        dm.assert_events()

        c.defer_events = False
        dm.assert_event(added={'foo':'bar'}, changed={'x':[1,2]})

        c.defer_events = True
        # 1. none    + added
        c['n'] = 1
        # 7. added   + removed
        del c['n']
        # 2. none    + changed
        c['foo'] = 'foo'
        # 8. changed + removed
        del c['foo']
        dm.assert_events()

        c.defer_events = False
        dm.assert_event(removed={'foo':'bar'})

        # Something more normal looking
        c.defer_events = True
        c['n'] = 1
        for c['i'] in range(10):
            c['n'] *= 2
        del c['i']
        dm.assert_events()

        c.defer_events = False
        dm.assert_event(added={'n':1024})

###############################################################################
# Support
###############################################################################

class EventMonitor(object):

    def __init__(self, context, *args, **kw):
        super(EventMonitor, self).__init__(*args, **kw)
        self._q = []
        context.on_trait_change(lambda e: self._q.append(e), self._event_name)

    def assert_event(self, **kw):
        'Test that an event fired (since the last call).'
        self.assert_events(kw)

    def assert_events(self, *events):
        'Test that a set of events fired (since the last call).'
        raise NotImplementedError

    def flush(self):
        'Flush our event queue'
        self._q[:] = []

class DictModifiedEventMonitor(EventMonitor):

    _event_name = 'dict_modified'

    def assert_events(self, *events):
        'Test that a set of events fired (since the last call).'

        attrs = 'added', 'changed', 'removed'

        # Validate attributes in expected events
        unknown_attrs = union(map(set, events)) - set(attrs)
        if unknown_attrs:
            raise ValueError('Unknown attributes: %s' % list(unknown_attrs))

        # (Make tidy dicts for descriptive errors)
        assert_equal_up_to_reordering(
            [ dict([ (k, e[k]) for k in attrs if k in e ])
              for e in events ],
            [ dict([ (k, dict(getattr(e,k))) for k in attrs if getattr(e,k) ])
              for e in self._q ],
        )

        self.flush()

def assert_equal_up_to_reordering(a, b):
    'Assert that lists a and b have the same elements in some order.'
    assert equal_up_to_reordering(a,b), (
        'Not equal (up to reordering)\n\n'
        '  Expected: %s\n\n'
        '  Got:      %s'
    ) % (a,b)

def equal_up_to_reordering(a, b):
    'Whether lists a and b have the same elements in some order.'
    a = copy(a)
    try:
        map(a.remove, b)
    except ValueError:
        return False
    return a == []
