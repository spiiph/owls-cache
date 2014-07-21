"""Provides a redis-based persistent caching backend.
"""


# HACK: Use absolute_import behavior to get around module having the same name
# as the global redis module
from __future__ import absolute_import

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
        # Check for a prefix arguments
        prefix = kwargs.get('prefix', None)
        if prefix is None:
            self._prefix = ''
        else:
            self._prefix = '{0}-'.format(prefix)

        # Mask the prefix argument from StrictRedis
        if 'prefix' in kwargs:
            kwargs.pop('prefix')

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

    def key(self, name, args, kwargs):
        """Return a suitable string for caching a function with the given name
        and specified arguments.

        Since redis is less restrictive in its key space, the following format
        is used:

            function_name(arg1, ..., argN, kwarg1 = val1, ..., kwargM = valM)

        Args:
            name: The name of the callable being cached
            args: The positional arguments to the callable
            kwargs: The keyword arguments to the callable

        Returns:
            A (string) key suitable to use as the cache key.
        """
        # Create a human-readable key based on function name and arguments
        key_args = ', '.join((repr(a) for a in args))
        key_kwargs = ', '.join(('{0}={1}'.format(k, repr(v))
                                for k, v
                                in iteritems(kwargs)))
        if key_args != '' and key_kwargs != '':
            key_args += ', '
        return '{0}{1}({2}{3})'.format(self._prefix,
                                       name,
                                       key_args,
                                       key_kwargs)

    def set(self, key, value):
        """Sets the cache value for a given key, overwriting any previous
        value set for that key.

        Args:
            key: The key to update
            value: The value to set
        """
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
            return None

        # Deserialize it
        return loads(cache_value)
