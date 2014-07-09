"""Provides transient caching facilities via the @cached decorator.
"""


# System imports
from collections import defaultdict, OrderedDict


def cached(f):
    """Creates a transiently-cached version of a function.

    The function can have multiple caches associated with it, each of a
    different size, which might generally be associated with multiple callers.

    The resulting function will take two additional keyword arguments:

        cache_name: The name of the cache in which to store objects (defaults
            to the function name).  This value must be hashable.  If None is
            provided, then caching is disabled for that call.
        cache_size: The number of elements to store in the corresponding cache
            (defaults to 1).  If the function is called multiple times with
            different values for cache_size with the same value of cache_name,
            the corresponding cache will be shrunk to the size of the value
            passed when called each time.  This value must be greater than or
            equal to 1 if specified.

    For caching to succeed, you must call the function with the same arg/kwarg
    structure (i.e. you will get a cache miss if you use an argument as a
    positional argument and then later as a keyword argument - this is
    impossible to solve in the general case).

    Args:
        f: The callable to cache

    Returns:
        A cached version of the callable.
    """
    # Create the caches for this function
    caches = defaultdict(OrderedDict)

    # Create the wrapper function
    def wrapper(*args, **kwargs):
        # Extract keyword arguments if specified
        cache_name = kwargs.get('cache_name', f.__name__)
        cache_size = kwargs.get('cache_size', 1)

        # Validate the cache size
        if cache_size < 1:
            raise ValueError('invalid cache size specified')

        # Mask these arguments from the underlying function
        if 'cache_name' in kwargs:
            del kwargs['cache_name']
        if 'cache_size' in kwargs:
            del kwargs['cache_size']

        # Check if caching is disabled
        if cache_name is None:
            return f(*args, **kwargs)

        # Grab the cache
        cache = caches[hash(cache_name)]

        # Compute the cache key
        key = hash(repr(args) + repr(kwargs))

        # Check if we have a cache hit
        result = cache.get(key)
        if result is not None:
            return result

        # If not, do the hard work
        result = f(*args, **kwargs)

        # Shrink the cache to accomodate
        while len(cache) >= cache_size:
            cache.popitem(last = False)

        # Cache the value
        cache[key] = result

        return result

    # Return the wrapper function
    return wrapper
