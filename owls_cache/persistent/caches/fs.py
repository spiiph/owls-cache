"""Provides a file system-based persistent caching backend.
"""


# System imports
from os.path import exists, isdir, isfile, join, expanduser
from os import makedirs

# Six imports
from six.moves.cPickle import dump, load

# owls-cache imports
from owls_cache.persistent.caches import PersistentCache


class FileSystemPersistentCache(PersistentCache):
    """Implements a persistent cache on the file system.
    """

    def __init__(self, path = None):
        """Initializes a new instance of the FileSystemPersistentCache.

        This method will raise an exception if the specified path exists and is
        not a directory, or if directory creation fails.

        Args:
            path: The path in which to store cached items.  If None (the
                default), `~/.owls-cache` will be used.
        """
        # Use home-based path if path unavailable
        if path is None:
            path = join(expanduser("~"), '.owls-cache')

        # Check that the path does not exist (and create it) or that it does
        # exist and that it is a directory
        if exists(path):
            if not isdir(path):
                raise OSError('cache path exists and is not a directory')
        else:
            # Just pass on exceptions
            makedirs(path)

        # Store the path
        self._path = path

    def set(self, key, value):
        """Sets the cache value for a given key, overwriting any previous
        value set for that key.

        Args:
            key: The key to update
            value: The value to set
        """
        # Compute the file path for the key
        path = join(self._path, '{0}.pickle'.format(key))

        # Open the file and write the data
        with open(path, 'wb') as f:
            dump(value, f, protocol = 2)

    def get(self, key):
        """Gets the cache value for a given key, if any.

        Args:
            key: The key to locate

        Returns:
            The associated value, or None if the key is not found.
        """
        # Compute the file path for the key
        path = join(self._path, '{0}.pickle'.format(key))

        # Check if it exists and whether or not it's a file
        if not exists(path) or not isfile(path):
            return None

        # Try to load it
        with open(path, 'rb') as f:
            return load(f)
