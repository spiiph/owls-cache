"""Provides the base persistent cache class.
"""


# System imports
from collections import OrderedDict


class PersistentCache(object):
    """The base caching backend.  This backend should be subclassed by concrete
    implementations.
    """

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
