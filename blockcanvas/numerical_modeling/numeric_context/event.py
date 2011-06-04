from traits.util.sequence import disjoint

# The two 'merge_*_events' methods below have a very similar structure...
# Should 'ContextModified' subtype 'TraitDictEvent'? (As of now they are
# slightly incongruous because 'ContextModified' keeps lists instead of
# dictionaries.)

def merge_trait_dict_events(a, b, dict_):
    ''' Merge TraitDictEvent 'b' into TraitDictEvent 'a'.

        ``dict_`` should be a mapping object that gives the current value of
        'changed' items in the events.

        Assumes that 'b' is an event generated immediately after event 'a'.
        This entails, for example, that 'a.added.keys()' and
        'b.added.keys()' are disjoint, since it doesn't make sense for the
        same name to be added twice in succession.
    '''
    assert disjoint(set(a.added), set(a.changed), set(a.removed))
    assert disjoint(set(b.added), set(b.changed), set(b.removed))

    for k,v in b.added.iteritems():
        if k in a.added:
            assert False
        elif k in a.changed:
            assert False
        elif k in a.removed:
            if v is a.removed[k]:
                del a.removed[k]
            else:
                a.changed[k] = a.removed.pop(k)
        else:
            a.added[k] = v

    for k,v in b.changed.iteritems():
        if k in a.added:
            a.added[k] = dict_[k]
        elif k in a.changed:
            pass # 'a.added[k]' is already the correct value
        elif k in a.removed:
            assert False
        else:
            a.changed[k] = v

    for k,v in b.removed.iteritems():
        if k in a.added:
            del a.added[k]
        elif k in a.changed:
            a.removed[k] = a.changed[k]
            del a.changed[k]
        elif k in a.removed:
            assert False
        else:
            a.removed[k] = v

    assert disjoint(set(a.added), set(a.changed), set(a.removed))

def merge_context_modified_events(a, b):
    ''' Merge ContextModified event 'b' into ContextModified event 'a'.

        Assumes that 'b' is an event generated immediately after event 'a'.
        This entails, for example, that 'a.added' and 'b.added' are disjoint,
        since it doesn't make sense for the same name to be added twice in
        succession.
    '''
    assert disjoint(set(a.added), set(a.modified), set(a.removed))
    assert disjoint(set(b.added), set(b.modified), set(b.removed))

    for x in b.added:
        if x in a.added:
            assert False
        elif x in a.modified:
            assert False
        elif x in a.removed:
            a.removed.remove(x)
            a.added.append(x)
        else:
            a.added.append(x)

    for x in b.modified:
        if x in a.added:
            pass # 'a.added' is already correct
        elif x in a.modified:
            pass # 'a.modified' is already correct
        elif x in a.removed:
            assert False
        else:
            a.modified.append(x)

    for x in b.removed:
        if x in a.added:
            a.added.remove(x)
        elif x in a.modified:
            a.modified.remove(x)
            a.removed.append(x)
        elif x in a.removed:
            assert False
        else:
            a.removed.append(x)

    # 'changed' gives us little information, so this is the best we can do
    a.changed = list(set(a.changed + b.changed))

    a.reset |= b.reset

    assert disjoint(set(a.added), set(a.modified), set(a.removed))

def single_event(f):
    ''' Method decorator that merges all of a method's events into one.

        Useful for methods like 'dict.update' that are easily implemented in
        terms of smaller methods (like 'dict.__setitem__'), each call to which
        will fire an event.

        Requires an object that defers its events with a 'defer_events' flag.
    '''
    def g(self, *args, **kw):

        # Allow re-entrance
        old = self.defer_events

        self.defer_events = True
        try:
            return f(self, *args, **kw)
        finally:
            self.defer_events = old
    return g
