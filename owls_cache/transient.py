"""Provides transient caching facilities via the @cached decorator.
"""


# System imports
from collections import defaultdict, OrderedDict
from functools import wraps


# Global size limits for caches
_cache_limits = defaultdict(lambda: 5)


def set_cache_limit(name, limit):
    """Sets a cache size limit for the specified cache.

    If no limit is set for a cache, the default limit is 5.  If the limit is
    set to None, then no limits are placed on the cache.

    Args:
        name: The name of the cache
        limit: The maximum allowed size of the cache (None for unlimited)
    """
    _cache_limits[name] = limit


# Global caches
_caches = defaultdict(OrderedDict)


def cached(f):
    """Creates a transiently-cached version of a function.

    The function can have an unlimited number of caches associated with it -
    one of which is the default cache and others of which can be named with the
    added 'cache' keyword argument.  This allows users to associate caches with
    call-sites rather than functions, and allows users of code with transient
    caching embedded to more effectively control caching on a per-call-site
    basis.

    The resulting function will take an additional keyword argument:

        cache: The name of the cache in which to store objects (defaults to the
            function name).  This value must be a string.  If None is provided,
            then caching is disabled for that call.

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
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Extract keyword argument if specified
        cache_name = kwargs.get('cache', f.__name__)

        # Mask this argument from the underlying function
        if 'cache' in kwargs:
            del kwargs['cache']

        # Check if caching is disabled
        if cache_name is None:
            return f(*args, **kwargs)

        # Grab the cache
        cache = _caches[cache_name]

        # Grab the maximum cache size
        cache_limit = _cache_limits[cache_name]

        # Compute the cache key
        key = hash(repr(args) + repr(kwargs))

        # Check if we have a cache hit
        result = cache.get(key)
        if result is not None:
            return result

        # If not, do the hard work
        result = f(*args, **kwargs)

        # Shrink the cache to accomodate
        if cache_limit is not None:
            while len(cache) >= cache_limit:
                cache.popitem(last = False)

        # Cache the value
        cache[key] = result

        # All done
        return result

    # Return the wrapper function
    return wrapper


def clear_transient_caches():
    """Clears all transient caches.
    """
    _caches.clear()
