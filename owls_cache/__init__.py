"""Provides transient and persistent caching facilities.
"""


# System imports
from os import environ
from os.path import join

# owls-cache imports
from owls_cache.backends import TransientCachingBackend
from owls_cache.backends.redis import RedisPersistentCachingBackend
from owls_cache.backends.fs import FileSystemPersistentCachingBackend


# Export the owls-cache version
__version__ = '0.0.1'


def transiently_cached(optional = False, keyword = 'cache', default = True,
                       size = 5):
    """Decorator providing transient (in-memory) caching facilities to a
    callable.

    All arguments to this dectorator must be provided as keyword arguments.

    Note that *at least* the `optional` argument needs to be provided to the
    decorator.

    For caching to succeed, you must call the function with the same arg/kwarg
    structure (i.e. you will get a cache miss if you use an argument as a
    positional argument and then later as a keyword argument - this is
    impossible to solve in the general case).

    Args:
        optional: If False, then caching will always occur.  If True, then the
            resultant function will take an extra keyword argument which will
            be masked from the original function and will control (via a
            boolean value) whether or not caching occurs on a per-call basis.
        keyword: The name of the keyword argument which controls optional
            cacheing (defaults to `cache`)
        default: If `optional` is True and no value is specified for the cache
            control keyword argument, this is the value that will be used
        size: The size of the cache, in terms of number of calls
    """
    # Create the decorator
    def decorator(function):
        # Create a transient cache
        cache = TransientCachingBackend(size)

        # Create a wrapper function
        def wrapper(*args, **kwargs):
            # If caching is optional, extract the cache control keyword
            if optional:
                do_cache = kwargs.get(keyword, default)
                if keyword in kwargs:
                    del kwargs[keyword]

            # Compute the caching key
            key = hash(repr(args) + repr(kwargs))

            # Check for a cache hit
            result = cache.get(key)
            if result is not None:
                return result

            # Otherwise, call the function
            result = function(*args, **kwargs)

            # Cache it if necessary
            if not optional or do_cache:
                cache.set(key, result)

            # All done
            return result

        # Return the wrapper
        return wrapper

    # Return the decorator
    return decorator


@transiently_cached(optional = False, size = 1)
def _get_persistent_caching_backend():
    """Factory method which returns the correct persistent caching backend
    based on the user's `OWLS_CACHE_BACKEND` environment variable.

    The `OWLS_CACHE_BACKEND` environment variable can be set to the following
    values:

        - `fs`: This uses the file system backend
        - `redis`: This uses the redis backend

    If `OWLS_CACHE_BACKEND` is set to `fs`, then the following additional
    environment variables will be considered:

        - `OWLS_CACHE_PATH`: The directory path for the cache (defaults to
          $HOME/.owls-cache)

    If `OWLS_CACHE_BACKEND` is set to `redis`, then the following additional
    environment variables will be considered:

        - `OWLS_CACHE_SOCKET`: Sets the path to the UNIX socket on which the
          redis server is listening
        - `OWLS_CACHE_SERVER`: If set, then the value of `OWLS_CACHE_SOCKET` is
          ignored and the redis backend will attempt to connect to the server
          via TCP at the hostname specified in `OWLS_CACHE_SERVER`
        - `OWLS_CACHE_PORT`: If set alongside `OWLS_CACHE_SERVER`, the value of
          this environment variable will be considered the TCP port on which to
          connect to the redis server (defaults to 6379)
        - `OWLS_CACHE_PASSWORD`: If set, then the value of this environment
          variable will be provided as a password to the redis server

    If neither of `OWLS_CACHE_SERVER` or `OWLS_CACHE_SOCKET` is set, then an
    exception is raised.

    If `OWLS_CACHE_BACKEND` is not specified, its value will default to `fs`.
    """
    # Check if the user has specified a backend
    backend_name = environ.get('OWLS_CACHE_BACKEND', 'fs')

    # Construct the appropriate backend
    if backend_name == 'fs':
        # Check if the user has specified a path for the cache
        cache_path = environ.get('OWLS_CACHE_PATH',
                                 join(environ['HOME'], '.owls-cache'))

        # Create the backend
        return FileSystemPersistentCachingBackend(cache_path)
    elif backend_name == 'redis':
        # Check the user's environment variables
        cache_socket = environ.get('OWLS_CACHE_SOCKET', None)
        cache_server = environ.get('OWLS_CACHE_SERVER', None)
        cache_port = environ.get('OWLS_CACHE_PORT', None)
        cache_password = environ.get('OWLS_CACHE_PASSWORD', None)

        # Create the backend
        if cache_server is not None:
            return RedisPersistentCachingBackend(host = cache_server,
                                                 port = cache_port,
                                                 password = cache_password)
        elif cache_socket is not None:
            return RedisPersistentCachingBackend(
                unix_socket_path = cache_socket,
                password = cache_password
            )
        else:
            raise RuntimeError('no redis connection information specified')
    else:
        raise RuntimeError('invalid cache backend ({0}) specified'.format(
            backend_name
        ))


def persistently_cached():
    pass
