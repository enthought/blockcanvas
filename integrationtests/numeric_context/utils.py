# Standard imports
from copy import copy
from nose.tools import assert_equal
from numpy import ndarray, all

# ETS imports
from enthought.numerical_modeling.numeric_context.api import ANumericContext
from traits.util.dict import dict_zip
from traits.util.sequence import union

###############################################################################
# Support
###############################################################################

def assert_similar_contexts(c1, c2):
    ''' Assert that two contexts are structurally equivalent

        This task is hard, and this implementation is incomplete. The goal is
        to just catch as many dissimilarities as possible.
    '''
    assert_equal(type(c1), type(c2))

    # Compare attributes that are easy to compare
    for attr in ['context_names', 'context_all_names', 'sub_context_names',
                 'context_indices']:
        assert_equal(set(getattr(c1, attr)), set(getattr(c2, attr)))
    for attr in ['context_group']:
        assert_equal(getattr(c1, attr), getattr(c2, attr))

    # Compare data, being careful with nested contexts
    assert_equal(set(dict(c1)), set(dict(c2)))
    for k,(a,b) in dict_zip(dict(c1), dict(c2)).items():
        if isinstance(a, ANumericContext) or isinstance(b, ANumericContext):
            assert_similar_contexts(a,b)
        elif isinstance(a, ndarray) and isinstance(b, ndarray):
            assert all(a == b)
        else:
            assert_equal(a,b)

def replace_numpy_arrays(x):
    ''' Replace numpy arrays in a container with lists.

        This is useful when you want to compare two containers for equality,
        but one or the other contains numpy arrays.
    '''
    if isinstance(x, ndarray):
        return list(x)
    elif isinstance(x, basestring):
        return x
    else:
        try:
            return x.__class__([replace_numpy_arrays(a) for a in x.items()])
        except:
            try:
                return x.__class__([replace_numpy_arrays(a) for a in x])
            except:
                return x

def assert_equal_up_to_reordering_with_numpy_arrays(a, b):
    ''' Assert that lists a and b have the same elements in some order.

        Compares numpy arrays as 'all(x == y)'.
    '''
    assert equal_up_to_reordering_with_numpy_arrays(a,b), (
        'Not equal (up to reordering)\n\n'
        '  Expected: %s\n\n'
        '  Got:      %s'
    ) % (a,b)

def equal_up_to_reordering_with_numpy_arrays(a, b):
    ''' Whether lists a and b have the same elements in some order.

        Compares numpy arrays as 'all(x == y)'.

        'set(a) == set(b)' is similar, but we distinguish between sequences
        with repeated elements. For example:

            >>> a, b = [1,2], [2,1,1]
            >>> set(a) == set(b)
            True
            >>> equal_up_to_reordering_with_numpy_arrays(a, b)
            False
    '''
    a = copy(a)
    for y in b:
        for i,x in enumerate(copy(a)):
            if replace_numpy_arrays(x) == replace_numpy_arrays(y):
                del a[i]
    return a == []

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

class ContextModifiedEventMonitor(EventMonitor):

    _event_name = 'context_modified'

    def assert_events(self, *events):
        'Test that a set of events fired (since the last call).'

        attrs = 'modified', 'added', 'removed', 'changed', 'reset'

        # Validate attributes in expected events
        unknown_attrs = union(map(set, events)) - set(attrs)
        if unknown_attrs:
            raise ValueError('Unknown attributes: %s' % list(unknown_attrs))

        # (Make tidy dicts for descriptive errors)
        assert_equal_up_to_reordering_with_numpy_arrays(
            [ dict([ (k, set(e[k])) for k in attrs if k in e ])
              for e in events ],
            [ dict([ (k, set(getattr(e,k))) for k in attrs if getattr(e,k) ])
              for e in self._q ],
        )

        # Validate properties 'all_modified' and 'not_empty'
        for e in self._q:
            assert_equal(set(e.all_modified),
                         set(e.modified + e.added + e.removed + e.changed))
            assert_equal(e.not_empty, bool(e.all_modified))

        self.flush()

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
        assert_equal_up_to_reordering_with_numpy_arrays(
            [ dict([ (k, e[k]) for k in attrs if k in e ])
              for e in events ],
            [ dict([ (k, dict(getattr(e,k))) for k in attrs if getattr(e,k) ])
              for e in self._q ],
        )

        self.flush()
