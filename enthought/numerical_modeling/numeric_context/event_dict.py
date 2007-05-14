from UserDict import DictMixin

from enthought.traits.api import \
    Bool, Dict, Event, HasTraits, Instance, Property, TraitDictEvent
from enthought.util.dict import sub_dict

from enthought.numerical_modeling.numeric_context.event import (
    merge_trait_dict_events, single_event
)

class EventDict(HasTraits, DictMixin):
    ''' A dictionary with notification and an attribute interface

        Essentially a wrapper around traits' Dict.

        (Is this totally backwards? Is there a real need for a self-standing
        dictionary with notification rather than just a Dict trait on some
        other object?)
    '''

    # Our dictionary
    _dict = Dict

    # Fires when our dictionary is modified
    dict_modified = Event(TraitDictEvent)

    # Whether to buffer 'dict_modified' events. When true, no events are fired,
    # and when reverted to false, one event fires that represents the net
    # change since 'defer_events' was set.
    defer_events = Bool(False)

    # Our event buffer
    _deferred_event = Instance(TraitDictEvent)

    ###########################################################################
    # object interface
    ###########################################################################

    def __new__(cls, *args, **kw):
        # Our ctor arguments aren't for HasTraits, they're for dict
        return HasTraits.__new__(cls)

    def __init__(self, *args, **kw):
        self._dict = dict(*args, **kw)

    def __repr__(self):
        return self._dict.__repr__()

    ###########################################################################
    # Events
    ###########################################################################

    def __dict_items_changed(self, ev):

        # Only notify when values actually change (shouldn't TraitDict do
        # this for us?)
        for k, old_v in ev.changed.items():
            if self[k] is old_v:
                del ev.changed[k]

        # Don't fire empty events as a result of stripping ev.changed
        if ev.added != {} or ev.changed != {} or ev.removed != {}:
            self._post_event(ev)

    def __dict_changed(self, old, new):

        old_keys = set(old)
        new_keys = set(new)
        added   = sub_dict(new, new_keys - old_keys)
        removed = sub_dict(old, old_keys - new_keys)
        changed = sub_dict(old, new_keys & old_keys)

        self._post_event(
            TraitDictEvent(added=added, changed=changed, removed=removed)
        )

    def _post_event(self, ev):
        "Fire an event immediately if we aren't deferring or later if we are."
        if ev.added != {} or ev.changed != {} or ev.removed != {}:
            if not self.defer_events:
                self.dict_modified = ev
            else:
                merge_trait_dict_events(self._deferred_event, ev, self._dict)

    def _defer_events_changed(self, old, new):
        if old != new:
            if self.defer_events:
                self._deferred_event = TraitDictEvent()
            else:
                self._post_event(self._deferred_event)
                self._deferred_event = None

    ###########################################################################
    # dict interface
    ###########################################################################

    # Pass through to self._dict:

    # Minimum requirements to extend DictMixin
    def keys(self, *a, **kw):        return self._dict.keys(*a, **kw)
    def __getitem__(self, *a, **kw): return self._dict.__getitem__(*a, **kw)
    def __setitem__(self, *a, **kw): return self._dict.__setitem__(*a, **kw)
    def __delitem__(self, *a, **kw): return self._dict.__delitem__(*a, **kw)

    # For more efficiency
    def __contains__(self, *a, **kw): return self._dict.__contains__(*a, **kw)
    def __iter__(self, *a, **kw):     return self._dict.__iter__(*a, **kw)
    def iteritems(self, *a, **kw):    return self._dict.iteritems(*a, **kw)

    # No method should generate multiple events
    update = single_event(DictMixin.update)
    clear  = single_event(DictMixin.clear)

    # Use DictMixin.get instead of HasTraits.get
    get = DictMixin.get

    # We have to define these ourself:

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, *args, **kw):
        d = cls()
        d.update(dict.fromkeys(*args, **kw))
        return d

        # This breaks a case in MappingProtocolTest.test_fromkeys where they
        # construct a subclass ('mydict') whose '__new__' method returns an
        # object that isn't an instance of 'cls', thus precluding the expected
        # call to '__init__'.
        #return cls(dict.fromkeys(*args, **kw))

    ###########################################################################
    # attr interface
    ###########################################################################

    # Defining __getattr__/__setattr__/__delattr__ interferes with HasTraits.
    # Instead, make the magic undefined trait '_' a property that passes
    # through to the dict interface, and simply forego __delattr__. (In fact,
    # using delattr causes a segfault; see #1156 on enthought.)
    _ = Property(lambda self, name: self.__getitem__(name),
                 lambda self, name, value: self.__setitem__(name, value))
