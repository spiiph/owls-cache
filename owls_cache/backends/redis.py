"""Provides a redis-based persistent caching backend.
"""


# System imports
import logging

# Six imports
from six.moves.cPickle import dumps, loads

# owls-cache imports
from owls_cache.backends import PersistentCachingBackend


# Create a logger
logger = logging.getLogger(__name__)


# Check whether or not redis support is available
try:
    import redis
    _redis_available = True
except ImportError:
    _redis_available = False
    logger.warn('redis module not available, redis persistent caching '
                'unavailable')


class RedisPersistentCachingBackend(PersistentCachingBackend):
    """Implements a persistent cache in a redis key-value store.
    """

    def __init__(self, *args, **kwargs):
        """Initializes a new instance of the RedisPersistentCachingBackend.

        This method will raise an exception if redis support is unavailable.

        Args: The same as the redis.StrictRedis class
        """
        # Check that redis is available
        global _redis_available
        if not _redis_available:
            raise RuntimeError('redis support not available')

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
