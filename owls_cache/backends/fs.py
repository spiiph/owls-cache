"""Provides a file system-based persistent caching backend.
"""


# System imports
from os.path import exists, isdir, isfile, join
from os import makedirs

# Six imports
from six.moves.cPickle import dump, load

# owls-core imports
from owls_core.caching.backends import PersistentCachingBackend


class FileSystemPersistentCachingBackend(PersistentCachingBackend):
    """Implements a persistent cache on the file system.
    """

    def __init__(self, path):
        """Initializes a new instance of the
        FileSystemPersistentCachingBackend.

        This method will raise an exception if the specified path exists and is
        not a directory, or if directory creation fails.

        Args:
            path: The path in which to store cached items
        """
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

    def _path_for_key(self, key):
        """Returns the full path corresponding to the given key, which may or
        may not exist.

        Args:
            key: The key to convert

        Returns:
            A file name suitable for on-disk encoding.
        """
        return join(self._path, '{0}.pickle'.format(hash(key)))

    def set(self, key, value):
        """Sets the cache value for a given key, overwriting any previous
        value set for that key.

        Args:
            key: The key to update
            value: The value to set
        """
        # Open the file and write the data
        with open(self._path_for_key(key), 'wb') as f:
            dump(value, f, protocol = 2)

    def get(self, key):
        """Gets the cache value for a given key, if any.

        Args:
            key: The key to locate

        Returns:
            The associated value, or None if the key is not found.
        """
        # Compute the path for the key
        key_path = self._path_for_key(key)

        # Check if it exists and whether or not it's a file
        if not exists(key_path) or not isfile(key_path):
            return None

        # Try to load it
        # NOTE: I don't normally like catch-alls, but there is a big stack here
        # and a lot of things could go wrong
        try:
            with open(key_path, 'rb') as f:
                return load(f)
        except:
            return None
