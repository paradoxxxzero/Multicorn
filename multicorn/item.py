# -*- coding: utf-8 -*-
# Copyright © 2008-2011 Kozea
# This file is part of Multicorn, licensed under a 3-clause BSD license.

from collections import MutableMapping


class BaseItem(MutableMapping):
    """
    Base class for items.

    :param corn: The corn this item is coming from
    :param values: A dict of {property name: value}
    :param lazy_values: A dict of {property name: loader} where loader is a
                        callable returning the actual value. This can be used
                        for values that are expensive to compute or get.
    """
    def __init__(self, corn, values=None, lazy_values=None):
        self.corn = corn
        self._values = dict(values or {})
        self._lazy_values = dict(lazy_values or {})
        self.corn.properties

        corn_properties = set(self.corn.properties.keys())
        given_keys = set(self._values) | set(self._lazy_values)
        extra_keys = given_keys - corn_properties
        if extra_keys:
            raise ValueError(
                "Unexpected properties: %r" % (tuple(extra_keys),))
        missing_keys = corn_properties - given_keys
        if missing_keys:
            # log.debug("Creating a %s with missing properties: %r" %
            # (corn, tuple(missing_keys),))
            for key in missing_keys:
                self._values[key] = None

    def __len__(self):
        return len(self.corn.properties)

    def __iter__(self):
        return iter(self.corn.properties.keys())

    def __contains__(self, key):
        # MutableMapping.__contains__ would work but is based on __getitem__
        # which may load a lazy value needlessly.
        return key in self.corn.properties

    def __getitem__(self, key):
        if key not in self._values and key in self._lazy_values:
            return self._lazy_values[key](self)
        return self._values[key]

    def __setitem__(self, key, value):
        if key not in self:  # based on self.corn.properties
            raise KeyError(key, 'Can not add properties to items.')
        self._values[key] = value
        self._lazy_values.pop(key, None)

    def save(self):
        self.corn.save(self)

    def delete(self):
        self.corn.delete(self)

    def __delitem__(self, key):
        raise TypeError('Can not delete properties from an item.')
