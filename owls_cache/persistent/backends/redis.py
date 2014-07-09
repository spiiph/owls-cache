"""Provides a redis-based persistent caching backend.
"""


# System imports
import logging

# Six imports
from six.moves.cPickle import dumps, loads

# redis imports
import redis

# owls-cache imports
from owls_cache.persistent.backends import PersistentCachingBackend


class RedisPersistentCachingBackend(PersistentCachingBackend):
    """Implements a persistent cache in a redis key-value store.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of the RedisPersistentCachingBackend.

        This method will raise an exception if redis support is unavailable.

        Args: The same as the redis.StrictRedis class
        """
        # Create the client
        self._client = redis.StrictRedis(*args, **kwargs)

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
        # NOTE: I don't normally like catch-alls, but there is a big stack here
        # and a lot of things could go wrong
        try:
            return loads(cache_value)
        except:
            return None
