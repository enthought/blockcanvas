# Tests for mapping (i.e. dict-like) objects.
#
# A small, maintainable extension of python/Lib/test/mapping_tests.py. It
# should be easy to use diff to keep this file up-to-date.
#
# Changelog:
# 2007-01-26 danb: Copied from python/Lib/test/mapping_tests.py
# 2007-03-08 danb: Moved from internal/eric repo to enthought repo
# 2007-03-08 danb: Added 'adapt_keys'
# 2007-03-29 danb: Employed new-style classes and 'super'
# 2007-03-29 danb: Renamed TestFoo to FooTest to hide from nose
# 2007-03-29 danb: Converted from unittest to nose
# 2007-04-24 danb: Added KeyAdapter.copy
#
# Licensed under Python Software Foundation License, v2

import unittest
from nose.tools import assert_equal, assert_raises
import UserDict


def adapt_keys(mapping):
    ''' Wrap a mapping object so that it accepts all key types used by
        BasicMappingProtocolTest.
    '''

    # We need from_str(to_str(x)) == x, and 'help(repr)' says "For most object
    # types, eval(repr(object)) == object". It seems to hold for built-ins, but
    # it fails for many user-defined objects. Since it holds for all of the key
    # types used by BasicMappingProtocolTest, it's good enough.
    to_str = repr
    from_str = eval

    class KeyAdapter(UserDict.DictMixin):
        ''' A mapping object that converts keys into strings and otherwise
            delegates to another mapping object.
        '''
        def __init__(self, mapping_object):
            self._m = mapping_object

        def __getitem__(self, x):
            return self._m[to_str(x)]
        def __setitem__(self, x, value):
            self._m[to_str(x)] = value
        def __delitem__(self, x):
            del self._m[to_str(x)]
        def keys(self):
            return map(from_str, self._m.keys())

        def copy(self):
            return KeyAdapter(self._m.copy())

        # Whoops, can't define this one
        #@staticmethod
        #def fromkeys(keys, value=None):
        #    return ...

    return KeyAdapter(mapping)


class BasicMappingProtocolTest(unittest.TestCase):
    # This base class can be used to check that an object conforms to the
    # mapping protocol

    # Functions that can be useful to override to adapt to dictionary
    # semantics
    type2test = None # which class is being tested (overwrite in subclasses)

    def _reference(self):
        """Return a dictionary of values which are invariant by storage
        in the object under test."""
        return {1:2, "key1":"value1", "key2":(1,2,3)}
    def _empty_mapping(self):
        """Return an empty mapping object"""
        return self.type2test()
    def _full_mapping(self, data):
        """Return a mapping object with the value contained in data
        dictionary"""
        x = self._empty_mapping()
        for key, value in data.items():
            x[key] = value
        return x

    def __init__(self, *args, **kw):
        super(BasicMappingProtocolTest, self).__init__(*args, **kw)
        self.reference = self._reference().copy()

        # A (key, value) pair not in the mapping
        key, value = self.reference.popitem()
        self.other = {key:value}

        # A (key, value) pair in the mapping
        key, value = self.reference.popitem()
        self.inmapping = {key:value}
        self.reference[key] = value

    def test_read(self):
        # Test for read only operations on mapping
        p = self._empty_mapping()
        p1 = dict(p) #workaround for singleton objects
        d = self._full_mapping(self.reference)
        if d is p:
            p = p1
        #Indexing
        for key, value in self.reference.items():
            assert_equal(d[key], value)
        knownkey = self.other.keys()[0]
        assert_raises(KeyError, lambda:d[knownkey])
        #len
        assert_equal(len(p), 0)
        assert_equal(len(d), len(self.reference))
        #has_key
        for k in self.reference:
            assert d.has_key(k)
            assert k in d
        for k in self.other:
            assert not (d.has_key(k))
            assert not (k in d)
        #cmp
        assert_equal(cmp(p,p), 0)
        assert_equal(cmp(d,d), 0)
        assert_equal(cmp(p,d), -1)
        assert_equal(cmp(d,p), 1)
        #__non__zero__
        if p: assert False, ("Empty mapping must compare to False")
        if not d: assert False, ("Full mapping must compare to True")
        # keys(), items(), iterkeys() ...
        def check_iterandlist(iter, lst, ref):
            assert hasattr(iter, 'next')
            assert hasattr(iter, '__iter__')
            x = list(iter)
            assert set(x)==set(lst)==set(ref)
        check_iterandlist(d.iterkeys(), d.keys(), self.reference.keys())
        check_iterandlist(iter(d), d.keys(), self.reference.keys())
        check_iterandlist(d.itervalues(), d.values(), self.reference.values())
        check_iterandlist(d.iteritems(), d.items(), self.reference.items())
        #get
        key, value = d.iteritems().next()
        knownkey, knownvalue = self.other.iteritems().next()
        assert_equal(d.get(key, knownvalue), value)
        assert_equal(d.get(knownkey, knownvalue), knownvalue)
        assert not (knownkey in d)

    def test_write(self):
        # Test for write operations on mapping
        p = self._empty_mapping()
        #Indexing
        for key, value in self.reference.items():
            p[key] = value
            assert_equal(p[key], value)
        for key in self.reference.keys():
            del p[key]
            assert_raises(KeyError, lambda:p[key])
        p = self._empty_mapping()
        #update
        p.update(self.reference)
        assert_equal(dict(p), self.reference)
        items = p.items()
        p = self._empty_mapping()
        p.update(items)
        assert_equal(dict(p), self.reference)
        d = self._full_mapping(self.reference)
        #setdefault
        key, value = d.iteritems().next()
        knownkey, knownvalue = self.other.iteritems().next()
        assert_equal(d.setdefault(key, knownvalue), value)
        assert_equal(d[key], value)
        assert_equal(d.setdefault(knownkey, knownvalue), knownvalue)
        assert_equal(d[knownkey], knownvalue)
        #pop
        assert_equal(d.pop(knownkey), knownvalue)
        assert not (knownkey in d)
        assert_raises(KeyError, d.pop, knownkey)
        default = 909
        d[knownkey] = knownvalue
        assert_equal(d.pop(knownkey, default), knownvalue)
        assert not (knownkey in d)
        assert_equal(d.pop(knownkey, default), default)
        #popitem
        key, value = d.popitem()
        assert not (key in d)
        assert_equal(value, self.reference[key])
        p=self._empty_mapping()
        assert_raises(KeyError, p.popitem)

    def test_constructor(self):
        assert_equal(self._empty_mapping(), self._empty_mapping())

    def test_bool(self):
        assert not self._empty_mapping()
        assert self.reference
        assert bool(self._empty_mapping()) is False
        assert bool(self.reference) is True

    def test_keys(self):
        d = self._empty_mapping()
        assert_equal(d.keys(), [])
        d = self.reference
        assert self.inmapping.keys()[0] in d.keys()
        assert self.other.keys()[0] not in d.keys()
        assert_raises(TypeError, d.keys, None)

    def test_values(self):
        d = self._empty_mapping()
        assert_equal(d.values(), [])

        assert_raises(TypeError, d.values, None)

    def test_items(self):
        d = self._empty_mapping()
        assert_equal(d.items(), [])

        assert_raises(TypeError, d.items, None)

    def test_len(self):
        d = self._empty_mapping()
        assert_equal(len(d), 0)

    def test_getitem(self):
        d = self.reference
        assert_equal(d[self.inmapping.keys()[0]], self.inmapping.values()[0])

        assert_raises(TypeError, d.__getitem__)

    def test_update(self):
        # mapping argument
        d = self._empty_mapping()
        d.update(self.other)
        assert_equal(d.items(), self.other.items())

        # No argument
        d = self._empty_mapping()
        d.update()
        assert_equal(d, self._empty_mapping())

        # item sequence
        d = self._empty_mapping()
        d.update(self.other.items())
        assert_equal(d.items(), self.other.items())

        # Iterator
        d = self._empty_mapping()
        d.update(self.other.iteritems())
        assert_equal(d.items(), self.other.items())

        # FIXME: Doesn't work with UserDict
        # assert_raises((TypeError, AttributeError), d.update, None)
        assert_raises((TypeError, AttributeError), d.update, 42)

        outerself = self
        class SimpleUserDict:
            def __init__(self):
                self.d = outerself.reference
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        i1 = d.items()
        i2 = self.reference.items()
        i1.sort()
        i2.sort()
        assert_equal(i1, i2)

        class Exc(Exception): pass

        d = self._empty_mapping()
        class FailingUserDict:
            def keys(self):
                raise Exc
        assert_raises(Exc, d.update, FailingUserDict())

        d.clear()

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = 1
                    def __iter__(self):
                        return self
                    def next(self):
                        if self.i:
                            self.i = 0
                            return 'a'
                        raise Exc
                return BogonIter()
            def __getitem__(self, key):
                return key
        assert_raises(Exc, d.update, FailingUserDict())

        class FailingUserDict:
            def keys(self):
                class BogonIter:
                    def __init__(self):
                        self.i = ord('a')
                    def __iter__(self):
                        return self
                    def next(self):
                        if self.i <= ord('z'):
                            rtn = chr(self.i)
                            self.i += 1
                            return rtn
                        raise StopIteration
                return BogonIter()
            def __getitem__(self, key):
                raise Exc
        assert_raises(Exc, d.update, FailingUserDict())

        d = self._empty_mapping()
        class badseq(object):
            def __iter__(self):
                return self
            def next(self):
                raise Exc()

        assert_raises(Exc, d.update, badseq())

        assert_raises(ValueError, d.update, [(1, 2, 3)])

    # no test_fromkeys or test_copy as both os.environ and selves don't support it

    def test_get(self):
        d = self._empty_mapping()
        assert d.get(self.other.keys()[0]) is None
        assert_equal(d.get(self.other.keys()[0], 3), 3)
        d = self.reference
        assert d.get(self.other.keys()[0]) is None
        assert_equal(d.get(self.other.keys()[0], 3), 3)
        assert_equal(d.get(self.inmapping.keys()[0]), self.inmapping.values()[0])
        assert_equal(d.get(self.inmapping.keys()[0], 3), self.inmapping.values()[0])
        assert_raises(TypeError, d.get)
        assert_raises(TypeError, d.get, None, None, None)

    def test_setdefault(self):
        d = self._empty_mapping()
        assert_raises(TypeError, d.setdefault)

    def test_popitem(self):
        d = self._empty_mapping()
        assert_raises(KeyError, d.popitem)
        assert_raises(TypeError, d.popitem, 42)

    def test_pop(self):
        d = self._empty_mapping()
        k, v = self.inmapping.items()[0]
        d[k] = v
        assert_raises(KeyError, d.pop, self.other.keys()[0])

        assert_equal(d.pop(k), v)
        assert_equal(len(d), 0)

        assert_raises(KeyError, d.pop, k)


class MappingProtocolTest(BasicMappingProtocolTest):

    def test_constructor(self):
        super(MappingProtocolTest, self).test_constructor()
        assert self._empty_mapping() is not self._empty_mapping()
        assert_equal(self.type2test(x=1, y=2), {"x": 1, "y": 2})

    def test_bool(self):
        super(MappingProtocolTest, self).test_bool()
        assert not self._empty_mapping()
        assert self._full_mapping({"x": "y"})
        assert bool(self._empty_mapping()) is False
        assert bool(self._full_mapping({"x": "y"})) is True

    def test_keys(self):
        super(MappingProtocolTest, self).test_keys()
        d = self._empty_mapping()
        assert_equal(d.keys(), [])
        d = self._full_mapping({'a': 1, 'b': 2})
        k = d.keys()
        assert 'a' in k
        assert 'b' in k
        assert 'c' not in k

    def test_values(self):
        super(MappingProtocolTest, self).test_values()
        d = self._full_mapping({1:2})
        assert_equal(d.values(), [2])

    def test_items(self):
        super(MappingProtocolTest, self).test_items()

        d = self._full_mapping({1:2})
        assert_equal(d.items(), [(1, 2)])

    def test_has_key(self):
        d = self._empty_mapping()
        assert not d.has_key('a')
        d = self._full_mapping({'a': 1, 'b': 2})
        k = d.keys()
        k.sort()
        assert_equal(k, ['a', 'b'])

        assert_raises(TypeError, d.has_key)

    def test_contains(self):
        d = self._empty_mapping()
        assert not ('a' in d)
        assert 'a' not in d
        d = self._full_mapping({'a': 1, 'b': 2})
        assert 'a' in d
        assert 'b' in d
        assert 'c' not in d

        assert_raises(TypeError, d.__contains__)

    def test_len(self):
        super(MappingProtocolTest, self).test_len()
        d = self._full_mapping({'a': 1, 'b': 2})
        assert_equal(len(d), 2)

    def test_getitem(self):
        super(MappingProtocolTest, self).test_getitem()
        d = self._full_mapping({'a': 1, 'b': 2})
        assert_equal(d['a'], 1)
        assert_equal(d['b'], 2)
        d['c'] = 3
        d['a'] = 4
        assert_equal(d['c'], 3)
        assert_equal(d['a'], 4)
        del d['b']
        assert_equal(d, {'a': 4, 'c': 3})

        assert_raises(TypeError, d.__getitem__)

    def test_clear(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        d.clear()
        assert_equal(d, {})

        assert_raises(TypeError, d.clear, None)

    def test_update(self):
        super(MappingProtocolTest, self).test_update()
        # mapping argument
        d = self._empty_mapping()
        d.update({1:100})
        d.update({2:20})
        d.update({1:1, 2:2, 3:3})
        assert_equal(d, {1:1, 2:2, 3:3})

        # no argument
        d.update()
        assert_equal(d, {1:1, 2:2, 3:3})

        # keyword arguments
        d = self._empty_mapping()
        d.update(x=100)
        d.update(y=20)
        d.update(x=1, y=2, z=3)
        assert_equal(d, {"x":1, "y":2, "z":3})

        # item sequence
        d = self._empty_mapping()
        d.update([("x", 100), ("y", 20)])
        assert_equal(d, {"x":100, "y":20})

        # Both item sequence and keyword arguments
        d = self._empty_mapping()
        d.update([("x", 100), ("y", 20)], x=1, y=2)
        assert_equal(d, {"x":1, "y":2})

        # iterator
        d = self._full_mapping({1:3, 2:4})
        d.update(self._full_mapping({1:2, 3:4, 5:6}).iteritems())
        assert_equal(d, {1:2, 2:4, 3:4, 5:6})

        class SimpleUserDict:
            def __init__(self):
                self.d = {1:1, 2:2, 3:3}
            def keys(self):
                return self.d.keys()
            def __getitem__(self, i):
                return self.d[i]
        d.clear()
        d.update(SimpleUserDict())
        assert_equal(d, {1:1, 2:2, 3:3})

    def test_fromkeys(self):
        assert_equal(self.type2test.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        d = self._empty_mapping()
        assert not(d.fromkeys('abc') is d)
        assert_equal(d.fromkeys('abc'), {'a':None, 'b':None, 'c':None})
        assert_equal(d.fromkeys((4,5),0), {4:0, 5:0})
        assert_equal(d.fromkeys([]), {})
        def g():
            yield 1
        assert_equal(d.fromkeys(g()), {1:None})
        assert_raises(TypeError, {}.fromkeys, 3)
        class dictlike(self.type2test): pass
        assert_equal(dictlike.fromkeys('a'), {'a':None})
        assert_equal(dictlike().fromkeys('a'), {'a':None})
        assert dictlike.fromkeys('a').__class__ is dictlike
        assert dictlike().fromkeys('a').__class__ is dictlike
        # FIXME: the following won't work with UserDict, because it's an old style class
        # assert type(dictlike.fromkeys('a')) is dictlike
        class mydict(self.type2test):
            def __new__(cls):
                return UserDict.UserDict()
        ud = mydict.fromkeys('ab')
        assert_equal(ud, {'a':None, 'b':None})
        # FIXME: the following won't work with UserDict, because it's an old style class
        # assert isinstance(ud, UserDict.UserDict)
        assert_raises(TypeError, dict.fromkeys)

        class Exc(Exception): pass

        class baddict1(self.type2test):
            def __init__(self):
                raise Exc()

        assert_raises(Exc, baddict1.fromkeys, [1])

        class BadSeq(object):
            def __iter__(self):
                return self
            def next(self):
                raise Exc()

        assert_raises(Exc, self.type2test.fromkeys, BadSeq())

        class baddict2(self.type2test):
            def __setitem__(self, key, value):
                raise Exc()

        assert_raises(Exc, baddict2.fromkeys, [1])

    def test_copy(self):
        d = self._full_mapping({1:1, 2:2, 3:3})
        assert_equal(d.copy(), {1:1, 2:2, 3:3})
        d = self._empty_mapping()
        assert_equal(d.copy(), d)
        assert (isinstance(d.copy(), d.__class__))
        assert_raises(TypeError, d.copy, None)

    def test_get(self):
        super(MappingProtocolTest, self).test_get()
        d = self._empty_mapping()
        assert (d.get('c') is None)
        assert_equal(d.get('c', 3), 3)
        d = self._full_mapping({'a' : 1, 'b' : 2})
        assert (d.get('c') is None)
        assert_equal(d.get('c', 3), 3)
        assert_equal(d.get('a'), 1)
        assert_equal(d.get('a', 3), 1)

    def test_setdefault(self):
        super(MappingProtocolTest, self).test_setdefault()
        d = self._empty_mapping()
        assert (d.setdefault('key0') is None)
        d.setdefault('key0', [])
        assert (d.setdefault('key0') is None)
        d.setdefault('key', []).append(3)
        assert_equal(d['key'][0], 3)
        d.setdefault('key', []).append(4)
        assert_equal(len(d['key']), 2)

    def test_popitem(self):
        super(MappingProtocolTest, self).test_popitem()
        for copymode in -1, +1:
            # -1: b has same structure as a
            # +1: b is a.copy()
            for log2size in range(12):
                size = 2**log2size
                a = self._empty_mapping()
                b = self._empty_mapping()
                for i in range(size):
                    a[repr(i)] = i
                    if copymode < 0:
                        b[repr(i)] = i
                if copymode > 0:
                    b = a.copy()
                for i in range(size):
                    ka, va = ta = a.popitem()
                    assert_equal(va, int(ka))
                    kb, vb = tb = b.popitem()
                    assert_equal(vb, int(kb))
                    assert (not(copymode < 0 and ta != tb))
                assert (not a)
                assert (not b)

    def test_pop(self):
        super(MappingProtocolTest, self).test_pop()

        # Tests for pop with specified key
        d = self._empty_mapping()
        k, v = 'abc', 'def'

        # verify longs/ints get same value when key > 32 bits (for 64-bit archs)
        # see SF bug #689659
        x = 4503599627370496L
        y = 4503599627370496
        h = self._full_mapping({x: 'anything', y: 'something else'})
        assert_equal(h[x], h[y])

        assert_equal(d.pop(k, v), v)
        d[k] = v
        assert_equal(d.pop(k, 1), v)


class HashMappingProtocolTest(MappingProtocolTest):

    def test_getitem(self):
        super(HashMappingProtocolTest, self).test_getitem()
        class Exc(Exception): pass

        class BadEq(object):
            def __eq__(self, other):
                raise Exc()

        d = self._empty_mapping()
        d[BadEq()] = 42
        assert_raises(KeyError, d.__getitem__, 23)

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        assert_raises(Exc, d.__getitem__, x)

    def test_fromkeys(self):
        super(HashMappingProtocolTest, self).test_fromkeys()
        class mydict(self.type2test):
            def __new__(cls):
                return UserDict.UserDict()
        ud = mydict.fromkeys('ab')
        assert_equal(ud, {'a':None, 'b':None})
        assert (isinstance(ud, UserDict.UserDict))

    def test_pop(self):
        super(HashMappingProtocolTest, self).test_pop()

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        assert_raises(Exc, d.pop, x)

    def test_mutatingiteration(self):
        d = self._empty_mapping()
        d[1] = 1
        try:
            for i in d:
                d[i+1] = 1
        except RuntimeError:
            pass
        else:
            assert False, ("changing dict size during iteration doesn't raise Error")

    def test_repr(self):
        d = self._empty_mapping()
        assert_equal(repr(d), '{}')
        d[1] = 2
        assert_equal(repr(d), '{1: 2}')
        d = self._empty_mapping()
        d[1] = d
        assert_equal(repr(d), '{1: {...}}')

        class Exc(Exception): pass

        class BadRepr(object):
            def __repr__(self):
                raise Exc()

        d = self._full_mapping({1: BadRepr()})
        assert_raises(Exc, repr, d)

    def test_le(self):
        assert (not (self._empty_mapping() < self._empty_mapping()))
        assert (not (self._full_mapping({1: 2}) < self._full_mapping({1L: 2L})))

        class Exc(Exception): pass

        class BadCmp(object):
            def __eq__(self, other):
                raise Exc()

        d1 = self._full_mapping({BadCmp(): 1})
        d2 = self._full_mapping({1: 1})
        try:
            d1 < d2
        except Exc:
            pass
        else:
            assert False, ("< didn't raise Exc")

    def test_setdefault(self):
        super(HashMappingProtocolTest, self).test_setdefault()

        class Exc(Exception): pass

        class BadHash(object):
            fail = False
            def __hash__(self):
                if self.fail:
                    raise Exc()
                else:
                    return 42

        d = self._empty_mapping()
        x = BadHash()
        d[x] = 42
        x.fail = True
        assert_raises(Exc, d.setdefault, x, [])

class TestTheTests(HashMappingProtocolTest):
    "Test the test suites above with a built-in 'dict'."
    type2test = dict
