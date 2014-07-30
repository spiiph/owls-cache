"""Provides the base persistent cache class.
"""


# System imports
from collections import OrderedDict


class PersistentCache(object):
    """The base caching backend.  This backend should be subclassed by concrete
    implementations.
    """

    def key(self, name, key):
        """Return a string suitable for use as a cache key, based on the name
        of the callable and the argument key provided by the callable.

        Implementations need not override this method, as the given key should
        be suitable in most cases.  Implementations may however wish to
        override this method to provide more human-readable keys.

        Args:
            name: The name of the callable being cached
            key: The argument key provided by the callable's cache mapper

        Returns:
            A (string) key suitable to use as the cache key.
        """
        return str(hash(name) + hash(key))

    def set(self, key, value):
        """Sets the cache value for a given key, overwriting any previous
        value set for that key.

        Args:
            key: The (string) key to update
            value: The (object) value to set
        """
        raise NotImplementedError('abstract method')

    def get(self, key):
        """Gets the cache value for a given key, if any.

        Args:
            key: The (string) key to locate

        Returns:
            The associated value, or None if the key is not found.
        """
        raise NotImplementedError('abstract method')
