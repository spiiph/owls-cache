"""Provides the base persistent cache backend class.
"""


# System imports
from collections import OrderedDict


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
