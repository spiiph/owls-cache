# System imports
from os import environ
from os.path import join

# owls-cache imports
from owls_cache.persistent.backends.redis import RedisPersistentCachingBackend
from owls_cache.persistent.backends.fs import \
    FileSystemPersistentCachingBackend


# Global persistent cache
_persistent_cache = None


def _get_persistent_cache():
    """Factory method which returns the correct persistent caching backend
    based on the user's `OWLS_CACHE_BACKEND` environment variable.  The result
    is cached in the global `_persistent_cache` variable, and subsequent calls
    will return this cached value.

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
    # Switch to the global persistent cache
    global _persistent_cache

    # Check if the global persistent cache already exists
    if _persistent_cache is not None:
        return _persistent_cache

    # Check if the user has specified a backend
    backend_name = environ.get('OWLS_CACHE_BACKEND', 'fs')

    # Construct the appropriate backend
    if backend_name == 'fs':
        # Check if the user has specified a path for the cache
        cache_path = environ.get('OWLS_CACHE_PATH',
                                 join(environ['HOME'], '.owls-cache'))

        # Create the backend
        _persistent_cache = FileSystemPersistentCachingBackend(cache_path)
    elif backend_name == 'redis':
        # Check the user's environment variables
        cache_socket = environ.get('OWLS_CACHE_SOCKET', None)
        cache_server = environ.get('OWLS_CACHE_SERVER', None)
        cache_port = environ.get('OWLS_CACHE_PORT', None)
        cache_password = environ.get('OWLS_CACHE_PASSWORD', None)

        # Create the backend
        if cache_server is not None:
            _persistent_cache = RedisPersistentCachingBackend(
                host = cache_server,
                port = cache_port,
                password = cache_password
            )
        elif cache_socket is not None:
            _persistent_cache = RedisPersistentCachingBackend(
                unix_socket_path = cache_socket,
                password = cache_password
            )
        else:
            raise RuntimeError('no redis connection information specified')
    else:
        raise RuntimeError('invalid cache backend ({0}) specified'.format(
            backend_name
        ))

    # All done
    return _persistent_cache


def persistently_cached():
    pass
