# System imports
import unittest

# owls-cache imports
from owls_cache.transient import set_cache_limit, \
    cached as transiently_cached, clear_transient_caches


# Set transient cache limits, just for kicks
set_cache_limit('abc', 2)


class TestTransientBase(unittest.TestCase):
    def setUp(self):
        # Create a counter to check cache misses
        self._counter = 0

    @transiently_cached
    def do_computation(self, a, b, operation = 'add'):
        self._counter += 1
        return (a + b) if operation == 'add' else (a - b)

    def tearDown(self):
        clear_transient_caches()


class TestTransientMiss(TestTransientBase):
    def test(self):
        # Run some computations which should be cache misses
        value_1 = self.do_computation(1, 2, 'add')
        value_2 = self.do_computation(1, 2, 'subtract')

        # Check that both missed
        self.assertEqual(self._counter, 2)


class TestTransientHit(TestTransientBase):
    def test(self):
        # Run a computation which should trigger a cache miss
        value_1 = self.do_computation(1, 2, 'add')

        # Now run again and check for a cache hit
        value_1_cached = self.do_computation(1, 2, 'add')
        self.assertEqual(self._counter, 1)
        self.assertEqual(value_1, value_1_cached)


class TestTransientSkip(TestTransientBase):
    def test(self):
        # Run a computation which should trigger a cache miss
        value_1 = self.do_computation(1, 2, 'add')

        # Now run again and check that we skip caching
        value_1_uncached = self.do_computation(1, 2, 'add', cache = None)
        self.assertEqual(self._counter, 2)
        self.assertEqual(value_1, value_1_uncached)


class TestTransientCustom(TestTransientBase):
    def test(self):
        # Run a computation in a custom cache
        value_1 = self.do_computation(1, 2, 'add', cache = 'abc')
        self.assertEqual(self._counter, 1)

        # And verify that that cache is fully functional
        value_1_cached = self.do_computation(1, 2, 'add', cache = 'abc')
        self.assertEqual(self._counter, 1)
        self.assertEqual(value_1, value_1_cached)


# Run the tests if this is the main module
if __name__ == '__main__':
    unittest.main()
