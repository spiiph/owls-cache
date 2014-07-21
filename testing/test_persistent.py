# System imports
import unittest
from tempfile import mkdtemp
from os import makedirs
from shutil import rmtree

# Six imports
from six.moves.cPickle import dumps, loads

# owls-cache imports
from owls_cache.persistent import cached as persistently_cached, \
    set_persistent_cache
from owls_cache.persistent.caches.fs import \
    FileSystemPersistentCache
from owls_cache.persistent.caches.redis import RedisPersistentCache


# Create a filesystem backend
fs_backend = FileSystemPersistentCache(mkdtemp())


# Create a redis backend and add it to the list if redis is available
redis_backend = RedisPersistentCache(prefix = 'testing')
redis_available = True
redis_unavailable_message = 'redis unavailable on localhost:6379'
try:
    redis_backend.get('dummy')
except:
    redis_available = False


class TestPersistentBase(unittest.TestCase):
    def setUp(self):
        # Create a counter to check cache misses
        self._counter = 0

    @persistently_cached
    def do_computation(self, a, b, operation = 'add'):
        self._counter += 1
        return (a + b) if operation == 'add' else (a - b)


class TestFileSystemBase(TestPersistentBase):
    def setUp(self):
        # Call the base initialization
        super(TestFileSystemBase, self).setUp()

        # Set the global persistent cache
        set_persistent_cache(fs_backend)

    def tearDown(self):
        # Clear out the cache
        # HACK: Use the underlying path
        rmtree(fs_backend._path)

        # Recreate the directory
        # HACK: Use the underlying path
        makedirs(fs_backend._path)

        # Unset the global persistent cache
        set_persistent_cache(None)


class TestFileSystemMiss(TestFileSystemBase):
    def test(self):
        # Run some computations which should be cache misses
        value_1 = self.do_computation(1, 2, 'add')
        value_2 = self.do_computation(1, 2, 'subtract')

        # Check that both missed
        self.assertEqual(self._counter, 2)


class TestFileSystemHit(TestFileSystemBase):
    def test(self):
        # Run a computation which should trigger a cache miss
        value_1 = self.do_computation(1, 2, 'add')

        # Now run again and check for a cache hit
        value_1_cached = self.do_computation(1, 2, 'add')
        self.assertEqual(self._counter, 1)
        self.assertEqual(value_1, value_1_cached)


class TestFileSystemSkip(TestFileSystemBase):
    def test(self):
        # Run a computation which should trigger a cache miss
        value_1 = self.do_computation(1, 2, 'add')

        # Now run again and check that we skip caching
        value_1_uncached = self.do_computation(1, 2, 'add', cache = None)
        self.assertEqual(self._counter, 2)
        self.assertEqual(value_1, value_1_uncached)


@unittest.skipIf(not redis_available, redis_unavailable_message)
class TestRedisBase(TestPersistentBase):
    def setUp(self):
        # Call the base initialization
        super(TestRedisBase, self).setUp()

        # Set the global persistent cache
        set_persistent_cache(redis_backend)

    def tearDown(self):
        # Clear out the cache
        # HACK: Use underlying client
        redis_backend._client.flushdb()

        # Unset the global persistent cache
        set_persistent_cache(None)


@unittest.skipIf(not redis_available, redis_unavailable_message)
class TestRedisPickle(TestRedisBase):
    def test(self):
        # Test that we can pickle and use the redis backend
        pickled = dumps(redis_backend)
        unpickled = loads(pickled)
        self.assertEqual(unpickled.get('dummy'), None)


@unittest.skipIf(not redis_available, redis_unavailable_message)
class TestRedisMiss(TestRedisBase):
    def test(self):
        # Run some computations which should be cache misses
        value_1 = self.do_computation(1, 2, 'add')
        value_2 = self.do_computation(1, 2, 'subtract')

        # Check that both missed
        self.assertEqual(self._counter, 2)


@unittest.skipIf(not redis_available, redis_unavailable_message)
class TestRedisHit(TestRedisBase):
    def test(self):
        # Run a computation which should trigger a cache miss
        value_1 = self.do_computation(1, 2, 'add')

        # Now run again and check for a cache hit
        value_1_cached = self.do_computation(1, 2, 'add')
        self.assertEqual(self._counter, 1)
        self.assertEqual(value_1, value_1_cached)


@unittest.skipIf(not redis_available, redis_unavailable_message)
class TestRedisSkip(TestRedisBase):
    def test(self):
        # Run a computation which should trigger a cache miss
        value_1 = self.do_computation(1, 2, 'add')

        # Now run again and check that we skip caching
        value_1_uncached = self.do_computation(1, 2, 'add', cache = None)
        self.assertEqual(self._counter, 2)
        self.assertEqual(value_1, value_1_uncached)


# Run the tests if this is the main module
if __name__ == '__main__':
    unittest.main()
