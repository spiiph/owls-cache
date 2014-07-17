"""Provides the base persistent cache class.
"""


# System imports
from collections import OrderedDict


class PersistentCache(object):
    """The base caching backend.  This backend should be subclasses by concrete
    implementations.
    """

    def key(self, name, args, kwargs):
        """Return a suitable string for caching a function with the given name
        and specified arguments.

        Implementations need not override this method, as the given key should
        be suitable in most cases.  Implementations may however wish to
        override this method to provide more human-readable keys.

        Args:
            name: The name of the callable being cached
            args: The positional arguments to the callable
            kwargs: The keyword arguments to the callable

        Returns:
            A (string) key suitable to use as the cache key.
        """
        return '{0}_{1}'.format(name, hash(repr(args) + repr(kwargs)))

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
