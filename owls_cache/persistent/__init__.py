# System imports
from os import environ
from os.path import join
from functools import wraps
import logging


# Global persistent caching logger (with debug disabled by default)
_cache_log = logging.getLogger(__name__)
_cache_log.setLevel(logging.INFO)


def set_cache_debug(debug = True):
    """Sets whether or not to print debugging information for persistent cache
    hits/misses.

    Args:
        debug: Whether or not to print debugging information
    """
    _cache_log.setLevel(logging.DEBUG if debug else logging.INFO)


# Global persistent cache
_persistent_cache = None


def set_persistent_cache(cache):
    """Sets the global persistent cache.

    The global cache is used by persistently-cached methods which do not have a
    persistent cache passed in via the 'cache' argument.  If the global cache
    is unset (the default) and no 'cache' argument is provided, then no
    persistent caching is performed.

    Args:
        cache: An instance of a subclass of
            owls_cache.persistent.caches.PersistentCache
    """
    # Switch to the global variable
    global _persistent_cache

    # Set the cache
    _persistent_cache = cache


def get_persistent_cache():
    """Gets the global persistent cache.

    Returns:
        The global persistent cache, or None if the global cache is not set.
    """
    return _persistent_cache


def cached(name, mapper):
    """Creates a persistently-cached version of a function.

    The persistent cache to use for the function can be passed via the 'cache'
    keyword argument.  If no cache is passed in this manner, then the global
    persistent cache is used (if set), and if neither is available, no
    persistent caching takes place.

    The resulting function will take an additional keyword argument:

        cache: An instance of a subclass of
            owls_cache.persistent.caches.PersistentCache

    For caching to succeed, you must call the function with the same arg/kwarg
    structure (i.e. you will get a cache miss if you use an argument as a
    positional argument and then later as a keyword argument - this is
    impossible to solve in the general case).

    Args:
        name: A unique name by which to refer to the callable in the persistent
            cache
        mapper: A function which accepts the same arguments as the underlying
            function and maps them to a tuple of representations (i.e. the
            results of `repr`) or hashable values which should be used as the
            cache key (usually calling repr on each argument is sufficient)

    Returns:
        A cached version of the callable.
    """
    # Create the decorator
    def decorator(f):
        # Create the wrapper function
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Extract keyword argument if specified
            cache = kwargs.get('cache', get_persistent_cache())

            # Mask this argument from the underlying function
            if 'cache' in kwargs:
                del kwargs['cache']

            # Compute the argument key
            argument_key = mapper(*args, **kwargs)

            # Compute a nice representation of the key assuming all key
            # elements are `repr` results
            argument_key_repr = '({0})'.format(
                ', '.join((str(x) for x in argument_key))
            )

            # Check if caching is disabled
            if cache is None:
                _cache_log.debug(
                    'persistent caching disabled in {0} for {1}'.format(
                        name,
                        argument_key_repr
                    )
                )
                return f(*args, **kwargs)

            # Compute the cache key
            key = cache.key(name, argument_key)

            # Check if we have a cache hit
            result = cache.get(key)
            if result is not None:
                _cache_log.debug(
                    'persistent cache hit in {0} for {1}'.format(
                        name,
                        argument_key_repr
                    )
                )
                return result

            # Log the cache miss
            _cache_log.debug('persistent cache miss in {0} for {1}'.format(
                name,
                argument_key_repr
            ))

            # If not, do the hard work
            result = f(*args, **kwargs)

            # Cache the value
            cache.set(key, result)

            # All done
            return result

        # Return the wrapper function
        return wrapper

    # Return the decorator
    return decorator
