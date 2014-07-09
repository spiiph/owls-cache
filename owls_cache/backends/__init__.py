"""Provides the base persistent cache backend class.
"""


# System imports
from collections import OrderedDict


class TransientCachingBackend(object):
    """The transient (in-memory) cacheing backend.
    """

    def __init__(self, size):
        # Store the fixed size of the cache
        self._size = size

        # Create an ordered dictionary to store cached values
        self._cache = OrderedDict()

    def set(self, key, value):
        """Sets the cache value for a given key.  If no entry for the key
        exists, then the oldest key/value pair in the cache is replaced with
        the new key/value pair, and if an old entry for the key exists, it is
        replaced.

        Args:
            key: The key to update
            value: The value to set
        """
        # Make space in the cache
        while len(self._cache) >= self._size:
            self._cache.popitem(last = False)

        # Set the new key/value
        self._cache[key] = value

    def get(self, key):
        """Gets the cache value for a given key, if any.

        Args:
            key: The key to locate

        Returns:
            The associated value, or None if the key is not found.
        """
        return self._cache.get(key, None)


class PersistentCachingBackend(object):
    """The base caching backend.  This backend should be subclasses by concrete
    implementations.
    """

    def set(self, key, value):
        """Sets the cache value for a given key, overwriting any previous
        value set for that key.

        Args:
            key: The (string) key to update
            value: The (object) value to set
        """
        raise RuntimeError('abstract method')

    def get(self, key):
        """Gets the cache value for a given key, if any.

        Args:
            key: The (string) key to locate

        Returns:
            The associated value, or None if the key is not found.
        """
        raise RuntimeError('abstract method')
