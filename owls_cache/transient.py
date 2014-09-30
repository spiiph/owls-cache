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


def cached(mapper = lambda *args, **kwargs: args + tuple(iteritems(kwargs))):
    """Decorator to create a transiently-cached version of a function.

    The function can have an unlimited number of caches associated with it -
    one of which is the default cache and others of which can be named with the
    added `cache` keyword argument.  This allows users to associate caches with
    call-sites rather than just functions, and allows users of code with
    transient caching embedded to more effectively control caching on a
    per-call-site basis.

    Cache purging is on a Least-Recently-Used basis.

    The resulting function will take two additional optional keyword arguments:

        cache: The name of the cache in which to store objects (defaults to the
            function name).  This value must be a string.  If None is provided,
            then caching is disabled for that call.
        cache_size: The maximum allowable size for the cache, in terms of
            number of objects.  Pass None for no size restriction.  Defaults to
            5.

    The resulting function will also have a `caches` attribute, which is a
    special dictionary mapping cache names to the caches themselves.  Names can
    be removed from the dictionary to empty that cache, or the dictionary can
    be cleared to empty all associated caches.

    Args:
        mapper: A function which accepts the same arguments as the underlying
            function and maps them to a tuple of values, which will then be
            hashed to act as the cache key (defaults to a function which
            concatenates args and kwargs)

    Returns:
        A cached version of the callable.
    """
    # Create the decorator
    def decorator(f):
        # Create the caches for the function
        caches = defaultdict(OrderedDict)

        # Create the wrapper function
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Extract keyword arguments if specified
            cache_name = kwargs.get('cache', '')
            cache_size = kwargs.get('cache_size', 5)

            # Mask these arguments from the underlying function
            if 'cache' in kwargs:
                del kwargs['cache']
            if 'cache_size' in kwargs:
                del kwargs['cache_size']

            # Compute the cache key
            key = hash(mapper(*args, **kwargs))

            # Check if caching is disabled
            if cache_name is None:
                _cache_log.debug('caching disabled for {0} with {1}'.format(
                    f.__name__,
                    key
                ))
                return f(*args, **kwargs)

            # Grab the cache
            cache = caches[cache_name]

            # Check if we have a cache hit
            result = cache.get(key)
            if result is not None:
                # If we have a cache hit then set the result as the most recent
                cache[key] = cache.pop(key)

                # Log the cache it
                _cache_log.debug('cache hit for {0} in {1} with {2}'.format(
                    f.__name__,
                    cache_name,
                    key
                ))

                # All done
                return result

            # Log the cache miss
            _cache_log.debug('cache miss for {0} in {1} with {2}'.format(
                f.__name__,
                cache_name,
                key
            ))

            # If not, do the hard work
            result = f(*args, **kwargs)

            # Shrink the cache if a limit is specified
            if cache_size is not None:
                while len(cache) >= cache_size:
                    cache.popitem(last = False)

            # Cache the value
            cache[key] = result

            # All done
            return result

        # Set the caches attribute
        wrapper.caches = caches

        # Return the wrapper function
        return wrapper

    # Return the decorator
    return decorator
