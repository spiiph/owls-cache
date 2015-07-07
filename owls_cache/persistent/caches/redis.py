"""Provides a redis-based persistent caching backend.
"""


# HACK: Use absolute_import behavior to get around module having the same name
# as the global redis module
from __future__ import absolute_import
from __future__ import print_function

# System imports
import logging

# Six imports
from six import iteritems
from six.moves.cPickle import dumps, loads

# redis imports
import redis

# owls-cache imports
from owls_cache.persistent.caches import PersistentCache


class RedisPersistentCache(PersistentCache):
    """Implements a persistent cache in a redis key-value store.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of the RedisPersistentCache.

        Args: The same as the redis.StrictRedis class, with an additional
            keyword argument:
            prefix: A prefix to append to all keys in the persistent cache.  If
                provided, it will have a dash appended to it, so keys will be
                of the form:

                    prefix-...

                If None (the default), no prefix is used.
        """
        # Check for a prefix argument
        prefix = kwargs.pop('prefix', None)
        if prefix is None:
            self._prefix = ''
        else:
            self._prefix = '{0}-'.format(prefix)

        # Check for a debug argument
        self._debug = kwargs.pop('debug', False)
        if self._debug:
            print('Redis: Debug messages on')

        # Store creation arguments for pickling
        self._args = args
        self._kwargs = kwargs

        # Create the client
        self._client = redis.StrictRedis(*args, **kwargs)

    def __getstate__(self):
        """Returns a reconstructable state for pickling.
        """
        return (self._args, self._kwargs, self._prefix)

    def __setstate__(self, state):
        """Sets the object state from pickling information.

        Args:
            state: The object state
        """
        # Recreate the client
        self._args, self._kwargs, self._prefix = state
        self._client = redis.StrictRedis(*self._args, **self._kwargs)

    def set(self, key, value):
        """Sets the cache value for a given key, overwriting any previous
        value set for that key.

        Args:
            key: The key to update
            value: The value to set
        """
        if self._debug:
            print('Redis: Cacheing {0}'.format(key))
        self._client.set(key, dumps(value))

    def get(self, key):
        """Gets the cache value for a given key, if any.

        Args:
            key: The key to locate

        Returns:
            The associated value, or None if the key is not found.
        """
        # Get the value, if any
        cache_value = self._client.get(key)
        if not cache_value:
            if self._debug:
                print('Redis: Cache miss for {0}'.format(key))
            return None
        if self._debug:
            print('Redis: Cache hit for {0}'.format(key))

        # Deserialize it
        return loads(cache_value)
