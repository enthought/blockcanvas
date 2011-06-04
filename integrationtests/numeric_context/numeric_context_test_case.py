''' Tests for numeric_context, context_data, and various derivative contexts.

    Each module should ideally have its own test file, but it's convenient to
    test these alongside each other and I haven't tried to split it out into
    multiple files yet.
'''

# Standard imports
from cPickle import dumps, loads
from nose.tools import assert_not_equal, assert_equal, assert_raises
from numpy import arange, array
from test import test_support
import unittest

# ETS imports
from enthought.numerical_modeling.numeric_context.tests.mapping_object_test_case import \
    BasicMappingProtocolTest, adapt_keys
from enthought.numerical_modeling.numeric_context.api import \
     NumericContext, DerivativeContext, PassThruContext, TraitsContext, CachedContext
from scimath.units.api import UnitArray
from traits.api import Int
from traits.util.functional import compose
from traits.util.sequence import union

# Local imports
from utils import DictModifiedEventMonitor, ContextModifiedEventMonitor, \
     assert_similar_contexts


# Coverage (2007-04-24):
#
#   event_dict          95% (with event_dict_test_case.py)
#
#   a_numeric_context   63%
#   numeric_context     82%
#   derivative_context  80%
#
#   a_numeric_item     100%
#   context_item        91%
#   sub_context_item    93%

# Features to test:
#
# (* Well-covered)
# (+ Partially covered)
# (- Not covered)
#
# * Storage (cf. event_dict_test_case.py)
#   * 'dict' interface
#   * Attribute access
# * Nesting
# * Events
#   * 'dict_modified' (cf. event_dict_test_case.py)
#   * 'context_modified'
# + Pickling
# - Pipelining
#   - Reduction
#   - Selection
#   - Mapping
#   - Cached, Deferred
#   - Traits
#   - (Extension)
# - (Grouping)

###############################################################################
# Test cases: abstract base classes
###############################################################################

# Subtype BasicMappingProtocolTest for free mapping object test cases:
# MappingProtocolTest assumes 'fromkeys' and 'copy', which we don't implement
# (yet?), and HashMappingProtocolTest is hopeless because the key adapter
# doesn't preserve key hashes.
#
# Override BasicMappingProtocolTest.type2test and return a constructor for the
# type that should be tested.
#
# NumericContexts are almost mapping objects, except they expect keys to be
# strings. Because we really want to reuse python's mapping object test case,
# we wrap NumericContexts with the 'adapt_keys' mapping adapter that injects
# keys into strings.
class MappingObjectTest(BasicMappingProtocolTest, object):
    __test__ = False
    def type2test(self, *args, **kw):
        return adapt_keys(self.factory(*args, **kw))

class NumericContextTest(MappingObjectTest, unittest.TestCase):
    __test__ = True

    def test_equality(self):
        nc1 = NumericContext()
        nc2 = NumericContext()
        assert_not_equal(nc1, nc2)

        nc1['a'] = 1
        assert_not_equal(nc1, nc2)

        nc2['a'] = 1
        assert_not_equal(nc1, nc2)

        return


    def test_events_single_name(self):
        'Events: single name'

        c = self.factory()
        dm = DictModifiedEventMonitor(c)
        cm = ContextModifiedEventMonitor(c)

        c['x'] = 1
        dm.assert_event(added={'x':1})
        cm.assert_event(changed='x')

        c['x'] = 1
        dm.assert_events()
        cm.assert_events()

        c['x'] = 'foo'
        dm.assert_event(changed={'x':1})
        cm.assert_event(changed='x')

        c['x'] = 'foo'
        dm.assert_events()
        cm.assert_events()

        del c['x']
        dm.assert_event(removed={'x':'foo'})
        cm.assert_event(changed='x')

        c['x'] = 'foo'
        dm.flush();
        cm.flush()

        c['x'] = arange(3)
        dm.assert_event(changed={'x':'foo'})
        cm.assert_event(added='x', changed='x')

        c['x'] = arange(3) # This fires because 'arange(3) is not arange(3)'
        dm.assert_event(changed={'x':arange(3)})
        cm.assert_event(modified='x')

        c['x'] = -arange(4)
        dm.assert_event(changed={'x':arange(3)})
        cm.assert_event(modified='x')

        del c['x']
        dm.assert_event(removed={'x':-arange(4)})
        cm.assert_event(removed='x')

        c['x'] = arange(3)
        dm.assert_event(added={'x':arange(3)})
        cm.assert_event(added='x')

        c['x'] = 3
        dm.assert_event(changed={'x':arange(3)})
        cm.assert_event(removed='x', changed='x')

    def test_events_multiple_names(self):
        'Events: multiple names'

        c = self.factory()
        dm = DictModifiedEventMonitor(c)
        cm = ContextModifiedEventMonitor(c)

        c.update(a=1, x=arange(3), t=True)
        dm.assert_event(added={'a':1, 'x':arange(3), 't':True})
        cm.assert_event(changed='at', added='x')

        c.update(a=2, x=-arange(3), y=arange(3))
        dm.assert_event(changed={'a':1, 'x':arange(3)}, added={'y':arange(3)})
        cm.assert_events(dict(changed='a', modified='x', added='y'))

        del c['t']
        dm.assert_event(removed={'t':True})
        cm.assert_event(changed='t')

        del c['x']
        dm.assert_event(removed={'x':-arange(3)})
        cm.assert_event(removed='x')

        c.clear()
        dm.assert_event(removed={'a':2, 'y':arange(3)})
        cm.assert_event(changed='a', removed='y')

    def test_nested_contexts(self):
        'Nested contexts'

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        c3.update(a=1, x=arange(3))
        c2.update(a=2, x=-arange(3), c3=c3)
        c1.update(a=3, x=1+arange(3), c2=c2)

        assert_equal(set(c1.sub_context_names), set(['c2']))
        assert_equal(set(c2.sub_context_names), set(['c3']))

        assert_equal(set(c3.keys()), set(['a', 'x']))
        assert_equal(set(c2.keys()), set(['a', 'x', 'c3']))
        assert_equal(set(c1.keys()), set(['a', 'x', 'c2']))

        assert_equal(set(c3.context_names), set(['x']))
        assert_equal(set(c2.context_names), set(['x', 'c3.x']))
        assert_equal(set(c1.context_names), set(['x', 'c2.x', 'c2.c3.x']))

    def test_events_nested_contexts(self):
        'Events: nested contexts'

        ### setitem (inside-out)

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        c3['a'] = 1
        c3['x'] = arange(3)
        dm.assert_events()
        cm.assert_events()

        c2['a'] = 2
        c2['x'] = arange(3)
        c2['c3'] = c3
        dm.assert_events()
        cm.assert_events()

        c1['a'] = 3
        c1['x'] = 1+arange(3)
        c1['c2'] = c2
        dm.assert_events(dict(added={'a':3}),
                         dict(added={'x':1+arange(3)}),
                         dict(added={'c2':c2}))
        cm.assert_events(dict(changed='a'),
                         dict(added='x'),
                         dict(changed=['c2'], added=['c2.x', 'c2.c3.x']))

        ### setitem (outside-in)

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        c1['a'] = 3
        c1['x'] = 1+arange(3)
        c1['c2'] = c2
        dm.assert_events(dict(added={'a':3}),
                         dict(added={'x':1+arange(3)}),
                         dict(added={'c2':c2}))
        cm.assert_events(dict(changed='a'),
                         dict(added='x'),
                         dict(changed=['c2']))

        c2['a'] = 2
        c2['x'] = arange(3)
        c2['c3'] = c3
        dm.assert_events()
        cm.assert_event(added=['c2.x'])

        c3['a'] = 1
        c3['x'] = arange(3)
        dm.assert_events()
        cm.assert_event(added=['c2.c3.x'])

        ### update (inside-out)

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        c3.update(a=1, x=arange(3))
        dm.assert_events()
        cm.assert_events()

        c2.update(a=2, x=-arange(3), c3=c3)
        dm.assert_events()
        cm.assert_events()

        c1.update(a=3, x=1+arange(3), c2=c2)
        dm.assert_event(added={'a':3, 'x':1+arange(3), 'c2':c2})
        cm.assert_event(added=['x', 'c2.x', 'c2.c3.x'], changed=['a', 'c2'])

        ### update (outside-in)

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        c1.update(a=3, x=1+arange(3), c2=c2)
        dm.assert_event(added={'a':3, 'x':1+arange(3), 'c2':c2})
        cm.assert_event(added='x', changed=['a', 'c2'])

        c2.update(a=2, x=-arange(3), c3=c3)
        dm.assert_events()
        cm.assert_event(added=['c2.x'])

        c3.update(a=1, x=arange(3))
        dm.assert_events()
        cm.assert_event(added=['c2.c3.x'])

        ### Mutate

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        c3.update(a=1, l=[1], x=arange(3))
        c2.update(a=2, l=[2], x=-arange(3), c3=c3)
        c1.update(a=3, l=[3], x=1+arange(3), c2=c2)
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        c1['a'] += 3
        dm.assert_event(changed={'a':3})
        cm.assert_event(changed='a')

        c1['l'].append(0)
        dm.assert_events()
        cm.assert_events()

        c1['x'] += 3
        dm.assert_events()
        cm.assert_events()

        c1['x'] = c1['x'] + 3
        dm.assert_event(changed={'x':4+arange(3)})
        cm.assert_event(modified='x')

        c2['a'] += 3
        dm.assert_events()
        cm.assert_events()

        c2['l'].append(0)
        dm.assert_events()
        cm.assert_events()

        c2['x'] += 3
        dm.assert_events()
        cm.assert_event(modified=['c2.x'])

        c3['a'] += 3
        dm.assert_events()
        cm.assert_events()

        c3['l'].append(0)
        dm.assert_events()
        cm.assert_events()

        c3['x'] += 3
        dm.assert_events()
        cm.assert_event(modified=['c2.c3.x'])

        ### delitem (outside-in)

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        c3.update(a=1, x=arange(3))
        c2.update(a=2, x=-arange(3), c3=c3)
        c1.update(a=3, x=1+arange(3), c2=c2)
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        del c1['a']
        del c1['x']
        del c1['c2']
        dm.assert_events(dict(removed={'a':3}),
                         dict(removed={'x':1+arange(3)}),
                         dict(removed={'c2':c2}))
        cm.assert_events(dict(changed='a'),
                         dict(removed='x'),
                         dict(changed=['c2'], removed=['c2.x', 'c2.c3.x']))

        del c2['a']
        del c2['x']
        del c2['c3']
        dm.assert_events()
        cm.assert_events()

        del c3['a']
        del c3['x']
        dm.assert_events()
        cm.assert_events()

        ### delitem (inside-out)

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        c3.update(a=1, x=arange(3))
        c2.update(a=2, x=-arange(3), c3=c3)
        c1.update(a=3, x=1+arange(3), c2=c2)
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        del c3['a']
        del c3['x']
        dm.assert_events()
        cm.assert_event(removed=['c2.c3.x'])

        del c2['a']
        del c2['x']
        del c2['c3']
        dm.assert_events()
        cm.assert_event(removed=['c2.x'])

        del c1['a']
        del c1['x']
        del c1['c2']
        dm.assert_events(dict(removed={'a':3}),
                         dict(removed={'x':1+arange(3)}),
                         dict(removed={'c2':c2}))
        cm.assert_events(dict(changed='a'),
                         dict(removed='x'),
                         dict(changed=['c2']))

        ### clear (outside-in)

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        c3.update(a=1, x=arange(3))
        c2.update(a=2, x=-arange(3), c3=c3)
        c1.update(a=3, x=1+arange(3), c2=c2)
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        c1.clear()
        dm.assert_event(removed={'a':3, 'x':1+arange(3), 'c2':c2})
        cm.assert_event(changed=['a', 'c2'], removed=['x', 'c2.x', 'c2.c3.x'])

        c2.clear()
        dm.assert_events()
        cm.assert_events()

        c3.clear()
        dm.assert_events()
        cm.assert_events()

        ### clear (inside-out)

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        c3.update(a=1, x=arange(3))
        c2.update(a=2, x=-arange(3), c3=c3)
        c1.update(a=3, x=1+arange(3), c2=c2)
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        c3.clear()
        dm.assert_events()
        cm.assert_event(removed=['c2.c3.x'])

        c2.clear()
        dm.assert_events()
        cm.assert_event(removed=['c2.x'])

        c1.clear()
        dm.assert_event(removed={'a':3, 'x':1+arange(3), 'c2':c2})
        cm.assert_event(changed=['a', 'c2'], removed='x')

    def test_deferred_events_debug(self): # XXX Subsumed by next test
        'Deferred events -- DEBUG'

        c1, c2, c3 = self.factory(), self.factory(), self.factory()
        dm = DictModifiedEventMonitor(c1)
        cm = ContextModifiedEventMonitor(c1)

        #print 'one' # XXX
        #def p(s): print s # XXX
        #c1.on_trait_change(lambda *args: p('A'), 'defer_events') # XXX
        #c1.context_data.on_trait_change(lambda *args:p('B'), 'defer_events')#XXX
        c1.defer_events = True
        #print 'two' # XXX
        c1.update(a=1, x=arange(3), c2=c2)
        c2.update(a=2, x=-arange(3))
        c3.update(a=3, x=1+arange(3))
        c1.update(c3=c3)
        dm.assert_events()
        cm.assert_events()

        c1.defer_events = False
        dm.assert_event(added={'a':1, 'x':arange(3), 'c2':c2, 'c3':c3})
        cm.assert_event(added=['x', 'c2.x', 'c3.x'], changed=['a', 'c2', 'c3'])

        c1.defer_events = True
        c1['x'] = -arange(3)
        c2['x'] = arange(3)
        c1.set_dotted('c3.x', 1-arange(3))
        dm.assert_events()
        cm.assert_events()

        c1.defer_events = False
        dm.assert_event(changed={'x':arange(3)})
        cm.assert_event(modified=['x', 'c2.x', 'c3.x'])

    def test_deferred_events(self):
        'Deferred events'

        # Possible event combinations:
        #    1. none     + added
        #    2. none     + modified
        #    3. none     + removed
        #    4. removed  + added
        #    5. added    + modified
        #    6. modified + modified
        #    7. added    + removed
        #    8. modified + removed
        #    9. none     + changed
        #   10. changed  + changed

        c = self.factory()
        dm = DictModifiedEventMonitor(c)
        cm = ContextModifiedEventMonitor(c)

        c.update(a=1, x=arange(3), t=True)
        dm.assert_event(added={'a':1, 'x':arange(3), 't':True})

        c.defer_events = True
        #  3. none    + removed
        c.clear()
        #  4. removed + added
        c.update(a=1, x=arange(3), t=True)
        dm.assert_events()
        cm.assert_events()

        c.defer_events = False
        dm.assert_event(changed={'x':arange(3)}) # Because `[1,2] is not [1,2]`
        cm.assert_event(modified=['x'])

        c.defer_events = True
        #  1. none     + added
        c['y'] = -arange(3)
        #  5. added    + modified
        c['y'] = 1+arange(3)
        #  2. none     + modified
        c['x'] = 1+arange(3)
        #  6. modified + modified
        c['x'] = -arange(3)
        #  9. none     + changed
        c['foo'] = 'foo'
        # 10. changed  + changed
        c['foo'] = 'bar'
        dm.assert_events()
        cm.assert_events()

        c.defer_events = False
        dm.assert_event(added={'y':1+arange(3), 'foo':'bar'},
                        changed={'x':arange(3)})
        cm.assert_event(added=['y'], modified=['x'],
                        changed=['foo'])

        c.defer_events = True
        #  1. none     + added
        c['z'] = arange(3)
        #  7. added    + removed
        del c['z']
        #  2. none     + modified
        c['y'] = arange(3)
        #  8. modified + removed
        del c['y']
        dm.assert_events()
        cm.assert_events()

        c.defer_events = False
        dm.assert_event(removed={'y':1+arange(3)})
        cm.assert_event(removed=['y'])

        # Something more normal looking
        c.defer_events = True
        c['n'] = array([-1, 0, 1])
        for c['i'] in range(10):
            c['n'] *= 2
        del c['i']
        dm.assert_events()
        cm.assert_events()

        c.defer_events = False
        dm.assert_event(added={'n':array([-1024, 0, 1024])})
        cm.assert_event(added=['n'])

    def test_pickling(self):
        'Pickling'

        def checked_pickle(c):
            p = loads(dumps(c))
            assert_similar_contexts(c, p)
            return p

        c1,c2,c3 = self.factory(), self.factory(), self.factory()
        c3.update(a=1, x=arange(3))
        c2.update(a=2, x=-arange(3), c3=c3)
        c1.update(a=3, x=1+arange(3), c2=c2)
        c1 = checked_pickle(c1)
        c1.c2 = checked_pickle(c1.c2)
        c1.c2.c3 = checked_pickle(c1.c2.c3)
        c1.c2 = checked_pickle(c1.c2)
        c1 = checked_pickle(c1)

        # Pickle a context with numpy.ufunc's: ufuncs don't pickle, so we throw
        # them out of the pickled state
        c = self.factory()
        fs = 'all, arange, array, cos, sin'
        exec 'from numpy import %s' % fs in {}, c
        loads(dumps(c))
        for f in fs.split(', '):
            assert f in c

    def test_magic_name___context__(self):
        "Magic name: '__context__'"
        c = self.factory()
        assert_equal(c['__context__'], c)
        assert_raises(ValueError, lambda: c.__setitem__('__context__', 3))
        assert_raises(ValueError, lambda: c.__delitem__('__context__'))

    def test_dotted_names(self):
        'Dotted names'
        c = self.factory()
        c['d.e'] = de = self.factory()
        c['d.e']['x.y'] = dexy = arange(3)

        assert c.has_dotted('d.e')
        assert c.has_dotted('d.e.x.y')
        assert not c.has_dotted('d')
        assert not c.has_dotted('d.e.x')
        assert not c.has_dotted('d.e.x.y.z')

        assert c.get_dotted('d.e.x.y') is dexy
        assert_equal(c.get_dotted('d.e'), de)
        assert_raises(KeyError, lambda: c.get_dotted('d'))
        assert_raises(KeyError, lambda: c.get_dotted('d.e.x'))
        assert_raises(KeyError, lambda: c.get_dotted('d.e.x.y.z'))
        assert_raises(KeyError, lambda: c['d.e.x.y'])

        dexy = arange(5)
        c.set_dotted('d.e.x.y', dexy)
        assert c.get_dotted('d.e.x.y') is dexy
        dexyz = -arange(3)
        c.set_dotted('d.e.x.y.z', dexyz)
        assert c.get_dotted('d.e.x.y.z') is dexyz

        # Policy: find longest match
        c['d.e.f'] = def_ = self.factory()
        c['d.e.f']['x.y'] = defxy = -arange(5)
        assert c.get_dotted('d.e.f.x.y') is defxy
        defxyz = arange(8)
        c.set_dotted('d.e.f.x.y.z', defxyz)
        assert c.get_dotted('d.e.f.x.y.z') is defxyz
        assert_equal(set(c['d.e'].keys()), set(['x.y', 'x.y.z']))

        # ...But don't give up early!
        de['f.x'] = 3
        assert_equal(c.get_dotted('d.e.f.x'), 3)
        c['x.y'] = 8
        c.set_dotted('x.y.z', 9)
        assert_equal(c.get_dotted('x.y.z'), 9)

    ### Dynamic binding #######################################################

    def test_dynamic_binding(self):
        'Dynamic binding'

        p = self.factory()
        c = self.factory(context_name='c')
        p.bind_dynamic(c, 'context_name')
        assert_equal(p.keys(), ['c'])

        c.context_name = 'bar'
        assert_equal(p.keys(), ['bar'])
        p['foo'] = c
        assert_equal(c.context_name, 'foo')
        assert_equal(p.keys(), ['foo'])

        p['c'] = 3

        # If a dynamic binding tries to indirectly clobber a dictionary
        # mapping, then we drop the dynamic binding entirely
        c.context_name = 'c'
        assert c not in p.values()
        assert_equal(p['c'], 3)
        assert_equal(c.context_name, 'c')

        # But new dictionary mappings are allowed to clobber dynamic bindings
        p.bind_dynamic(c, 'context_name')
        assert_equal(p['c'], c)
        p['c'] = 3
        assert_equal(p['c'], 3)
        assert c not in p.values()

        c.context_name = 'foo'
        p['c'] = c
        p.bind_dynamic(c, 'context_name')
        assert_equal(p.keys(), ['foo'])
        p['c'] = c
        assert_equal(c.context_name, 'c')

        del p['c']
        assert_equal(p.keys(), [])
        c.context_name = 'foo'
        assert_equal(p.keys(), [])

    def test_events_dynamic_binding(self):
        'Events: dynamic binding'

        # TODO Consolidate events

        p = self.factory()
        c = self.factory(context_name='c')
        c['x'] = arange(3)
        c['a'] = 8

        dm = DictModifiedEventMonitor(p)
        cm = ContextModifiedEventMonitor(p)

        p.bind_dynamic(c, 'context_name')
        dm.assert_event(added={'c':c})
        cm.assert_event(changed='c', added=['c.x'])

        c.context_name = 'bar'
        dm.assert_events(dict(removed={'c':c}),
                         dict(added={'bar':c}))
        cm.assert_events(dict(changed='c', removed=['c.x']),
                         dict(changed=['bar'], added=['bar.x']))

        p['foo'] = c
        dm.assert_events(dict(removed={'bar':c}),
                         dict(added={'foo':c}))
        cm.assert_events(dict(changed=['bar'], removed=['bar.x']),
                         dict(changed=['foo'], added=['foo.x']))

        p['c'] = 3
        dm.assert_event(added={'c':3})
        cm.assert_event(changed='c')

        p['c'] = c
        dm.assert_events(dict(removed={'foo':c}),
                         dict(changed={'c':3}))
        cm.assert_events(dict(changed=['foo'], removed=['foo.x']),
                         dict(changed='c', added=['c.x']))

        p['x'] = arange(3)
        dm.assert_event(added={'x':arange(3)})
        cm.assert_event(added='x')

        p['x'] = c
        dm.assert_events(dict(removed={'c':c}),
                         dict(changed={'x':arange(3)}))
        cm.assert_events(dict(changed='c', removed=['c.x']),
                         dict(removed='x', changed='x', added=['x.x']))

        ### 'del' a dynamic binding:

        del p['x']
        dm.assert_event(removed={'x':c})
        cm.assert_event(changed='x', removed=['x.x'])

        c.context_name = 'c'
        assert 'c' not in p
        dm.assert_events()
        cm.assert_events()

        p.update(c=3, x=arange(3), foo='foo')
        dm.assert_event(added={'c':3, 'x':arange(3), 'foo':'foo'})
        cm.assert_event(added='x', changed=['c', 'foo'])

        ### Clobber dynamic bindings

        c.context_name = 'b'
        p.bind_dynamic(c, 'context_name')
        dm.assert_event(added={'b':c})
        cm.assert_event(changed='b', added=['b.x'])

        # If a dynamic binding tries to indirectly clobber a dictionary
        # mapping, then we drop the dynamic binding entirely
        c.context_name = 'c'
        dm.assert_event(removed={'b':c})
        cm.assert_event(changed='b', removed=['b.x'])
        assert_equal(c.context_name, 'c')

        # But new dictionary mappings are allowed to clobber dynamic bindings
        c.context_name = 'b'
        p.bind_dynamic(c, 'context_name')
        dm.assert_event(added={'b':c})
        cm.assert_event(changed='b', added=['b.x'])
        p['b'] = 2
        dm.assert_event(changed={'b':c})
        cm.assert_event(changed='b', removed=['b.x'])

    def test_pickling_dynamic_binding(self):
        'Pickling: dynamic binding'

        p = self.factory()
        c = self.factory(context_name='c')

        p.bind_dynamic(c, 'context_name')

        # Pickle 'p'. Also pickle the new 'p' out to nowhere to ensure that
        # '__getstate__' doesn't have side effects.
        p = loads(dumps(p))
        dumps(p)
        c = p['c']

        dm = DictModifiedEventMonitor(p)
        cm = ContextModifiedEventMonitor(p)

        c.context_name = 'd'
        dm.assert_events(dict(removed={'c':c}),
                         dict(added={'d':c}))
        cm.assert_events(dict(changed='c'),
                         dict(changed='d'))

        p['c'] = c
        dm.assert_events(dict(removed={'d':c}),
                         dict(added={'c':c}))
        cm.assert_events(dict(changed='d'),
                         dict(changed='c'))

        del p['c']
        dm.assert_event(removed={'c':c})
        cm.assert_event(changed='c')

        c.context_name = 'd'
        dm.assert_events()
        cm.assert_events()

    ### Regression tests ######################################################

    def test_arrays_with_dotted_names(self):
        'Regression: arrays with dotted names'
        c = self.factory()
        c['a.b'] = 3
        c['x.y'] = arange(3)
        c['d.e'] = self.factory()
        c['d.e']['x.y'] = arange(3)
        d = c['d.e']
        x = d['x.y']

    def test_regression_context_modified_incomplete_when_array_replaces_none(self):
        "Regression: 'context_modified' incomplete when array replaces None"

        c = self.factory()
        dm = DictModifiedEventMonitor(c)
        cm = ContextModifiedEventMonitor(c)

        c['x'] = None
        dm.assert_event(added={'x':None})
        cm.assert_event(changed='x')

        c['x'] = arange(3)
        dm.assert_event(changed={'x':None})
        cm.assert_event(changed='x', added='x')

    def test_regression_dynamically_bind_values_already_in_context_data(self):
        "Regression: dynamically bind values already in 'context_data'"
        p = self.factory()
        c = self.factory(context_name='c')
        p['d'] = c
        p.bind_dynamic(c, 'context_name')
        assert_equal(p.keys(), ['c'])

    def test_pickled_parent_contexts_lose_new_names_in_children(self):
        "Regression: pickled parent contexts lose new names in children"

        a = self.factory()
        a.b = self.factory()
        a = loads(dumps(a))
        a.b.x = arange(3)
        assert_equal(a.b.context_all_names, ['x'])
        assert_equal(a.context_all_names, ['b.x']) # This one broke

    #@staticmethod # nose doesn't find static methods
    def test_pickling_subtypes_loses_fields(self):
        "Regression: pickling subtypes loses fields"

        c = FooContext()
        assert_equal(c.a, 3)
        assert_equal(c.b, 4)
        c = loads(dumps(c))
        assert_equal(c.a, 3)
        assert_equal(c.b, 4)

    def test_pickling_duplicates_sub_context_names(self):
        "Regression: pickling duplicates 'sub_context_names'"

        c = self.factory()
        c.d = self.factory()
        assert_equal(c.sub_context_names, ['d'])
        c = loads(dumps(c))
        assert_equal(c.sub_context_names, ['d'])

    def test_dict_modified_fires_before_sub_context_names_updates(self):
        "Regression: 'dict_modified' fires before 'sub_context_names' updates"
        c = self.factory()
        x = {'fired': False, 'success': False}
        def f():
            x['fired'] = True
            # Don't assert here -- traits handlers grab exceptions
            x['success'] = 'd' in c.sub_context_names
        c.on_trait_change(f, 'dict_modified')
        c.d = self.factory()
        assert x['fired']
        assert x['success']

    def test_some_problem_with_sub_contexts(self):
        'Regression: (Some problem with sub-contexts)'
        context = self.factory()
        context['foo'] = self.factory()
        context['foo']['bar'] = UnitArray(1)
        assert_equal(context['foo']['bar'], UnitArray(1))

    def test_clearing_nested_contexts_outside_in(self):
        'Regression: Clearing nested contexts outside-in'
        c1,c2 = self.factory(), self.factory()
        c1['c2'] = c2
        c2['x'] = arange(5)
        c1.clear()
        c2.clear()

    def test_unpickle_bottom_up_nested_contexts(self):
        'Regression: Unpickle bottom-up nested contexts'

        # Construct a numeric context from the bottom up, pickle/unpickle it,
        # and look up using dotted notation.

        well = self.factory()
        raw_logs = self.factory()
        log_suite = self.factory()
        log = UnitArray((1))

        log_suite['bar'] = log
        raw_logs['foo'] = log_suite
        well['logs'] = raw_logs

        assert_equal(well.logs.foo.bar, log)

        state = dumps(well)
        unpickled_well = loads(state)

        assert_equal(unpickled_well.logs.foo.bar, log)

    def test_unpickle_top_down_nested_contexts(self):
        'Regression: Unpickle top-down nested contexts'

        # Construct a numeric context from the top down, pickle/unpickle it,
        # and look up using dotted notation.

        well = self.factory()
        raw_logs = self.factory()
        log_suite = self.factory()
        log = UnitArray((1))

        well['logs'] = raw_logs
        raw_logs['foo'] = log_suite
        log_suite['bar'] = log

        assert_equal(well.logs.foo.bar, log)

        state = dumps(well)
        unpickled_well = loads(state)

        assert_equal(unpickled_well.logs.foo.bar, log)

# TODO Tests specific to subtypes of NumericContext:

class DerivativeContextTest(NumericContextTest):
    pass

class ReductionContextTest(DerivativeContextTest):
    pass

class MappingContextTest(DerivativeContextTest):
    pass

class SelectionContextTest(DerivativeContextTest):
    pass

###############################################################################
# Test cases: concrete classes
###############################################################################

class TestPerformance:
    def test_performance(self): # TODO (current)
        'Performance'
        pass

# Generate test case classes from the abstract hierarchy above:

# TODO Build and test various pipelines

def numeric_context_cases():
    yield ('Basic', NumericContext)

    # TODO Bigger cross-section: push everything through compose(loads, dumps)
    yield ('BasicPickled', compose(loads, dumps, NumericContext))

def derivative_context_cases():
    yield ('Derivative', compose(DerivativeContext, NumericContext))
    yield ('PassThru', compose(PassThruContext, NumericContext))
    yield ('Traits', compose(TraitsContext, NumericContext))
    yield ('Cached', compose(CachedContext, NumericContext))
    yield ('LongPipe', compose(* [DerivativeContext]*10 + [NumericContext] ))

def reduction_context_cases():

    def masked(mask):
        return lambda *args, **kw: \
            ReductionContext(NumericContext(*args, **kw),
                             context_filter=MaskFilter(mask=mask))

    # FIXME These break
    #yield ('Masked', masked([1,1,0,1,0]))
    #yield ('Masked', masked([1,1,0,1,0]))
    #yield ('MaskedEmptyMask', masked([]))
    #yield ('MaskedNullMask', masked([0]*10))
    return () # (XXX)

def mapping_context_cases():
    return ()

def selection_context_cases():
    return ()

# Meta-programming: Generate test case classes specified by *_cases methods.
# (Does nose offer a better solution?)
def test_all():
    for base, cases in [
        (NumericContextTest, numeric_context_cases()),
        (DerivativeContextTest, derivative_context_cases()),
        (ReductionContextTest, reduction_context_cases()),
        (MappingContextTest, mapping_context_cases()),
        (SelectionContextTest, selection_context_cases()),
        ]:
        global ctor
        for class_name, ctor in cases:
            class_name = 'Test' + class_name

            # Flag name collisions that clobber other test cases
            try:
                eval(class_name)
                assert False, 'Test case name collision: ' + class_name
            except NameError:
                pass

            # Create the test case
            exec (
                'class %s(base):\n'
                '    def setUp(self):\n'
                '        self.factory = ctor\n'
                ) % class_name
            test_support.run_unittest(eval(class_name))


###############################################################################
# Support
###############################################################################

class FooContext(NumericContext):
    'A subtype of NumericContext. Used by test_pickling_subtypes_loses_fields.'
    b = Int
    def __init__(self):
        super(FooContext, self).__init__()
        self.a = 3
        self.b = 4


if __name__ == '__main__':
    test_all()
