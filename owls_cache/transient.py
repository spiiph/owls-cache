"""Provides transient caching facilities via the @cached decorator.
"""


# System imports
from collections import defaultdict, OrderedDict
from functools import wraps
import logging

# Six imports
from six import iteritems


# Global transient caching logger (with debug disabled by default)
_cache_log = logging.getLogger(__name__)
_cache_log.setLevel(logging.INFO)


def set_cache_debug(debug = True):
    """Sets whether or not to print debugging information for transient cache
    hits/misses.

    Args:
        debug: Whether or not to print debugging information
    """
    _cache_log.setLevel(logging.DEBUG if debug else logging.INFO)


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


def cached(name, mapper):
    """Decorator to create a transiently-cached version of a function.

    The function can have an unlimited number of caches associated with it -
    one of which is the default cache and others of which can be named with the
    added `cache` keyword argument.  This allows users to associate caches with
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
        name: A unique name to use for the transient cache (note that this may
            be overridden by the `cache` keyword argument)
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
            cache_name = kwargs.get('cache', name)

            # Mask this argument from the underlying function
            if 'cache' in kwargs:
                del kwargs['cache']

            # Compute the cache key
            key = mapper(*args, **kwargs)

            # Compute a nice representation of the key assuming all key
            # elements are `repr` results
            key_repr = '({0})'.format(', '.join((str(x) for x in key)))

            # Check if caching is disabled
            if cache_name is None:
                _cache_log.debug(
                    'transient caching disabled in {0} for {1}'.format(
                        name,
                        key_repr
                    )
                )
                return f(*args, **kwargs)

            # Grab the cache
            cache = _caches[cache_name]

            # Grab the maximum cache size
            cache_limit = _cache_limits[cache_name]

            # Check if we have a cache hit
            result = cache.get(key)
            if result is not None:
                # If we have a cache hit then set the result as the most recent
                cache[key] = cache.pop(key)

                # Log the cache it
                _cache_log.debug('transient cache hit in {0} for {1}'.format(
                    cache_name,
                    key_repr
                ))

                # All done
                return result

            # Log the cache miss
            _cache_log.debug('transient cache miss in {0} for {1}'.format(
                cache_name,
                key_repr
            ))

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

    # Return the decorator
    return decorator


def clear_transient_caches():
    """Clears all transient caches.
    """
    _caches.clear()
