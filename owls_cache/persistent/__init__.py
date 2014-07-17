# System imports
from os import environ
from os.path import join


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
            owls_cache.persistent.backends.PersistentCachingBackend
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


def cached(f):
    """Creates a persistently-cached version of a function.

    The persistent cache to use for the function can be passed via the 'cache'
    keyword argument.  If no cache is passed in this manner, then the global
    persistent cache is used (if set), and if neither is available, no
    persistent caching takes place.

    The resulting function will take an additional keyword argument:

        cache: An instance of a subclass of
            owls_cache.persistent.backends.PersistentCachingBackend

    For caching to succeed, you must call the function with the same arg/kwarg
    structure (i.e. you will get a cache miss if you use an argument as a
    positional argument and then later as a keyword argument - this is
    impossible to solve in the general case).

    Args:
        f: The callable to cache

    Returns:
        A cached version of the callable.
    """
    # Create the wrapper function
    def wrapper(*args, **kwargs):
        # Extract keyword argument if specified
        cache = kwargs.get('cache', _persistent_cache)

        # Mask this argument from the underlying function
        if 'cache' in kwargs:
            del kwargs['cache']

        # Check if caching is disabled
        if cache is None:
            return f(*args, **kwargs)

        # Compute the cache key
        key = cache.key(f.__name__, args, kwargs)

        # Check if we have a cache hit
        result = cache.get(key)
        if result is not None:
            return result

        # If not, do the hard work
        result = f(*args, **kwargs)

        # Cache the value
        cache.set(key, result)

        return result

    # Return the wrapper function
    return wrapper
