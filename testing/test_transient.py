# System imports
import unittest

# owls-cache imports
from owls_cache.transient import cached as transiently_cached


class TestTransientCaching(unittest.TestCase):
    def setUp(self):
        # Create a counter to check cache misses
        self._counter = 0

    @transiently_cached
    def do_computation(self, a, b, operation = 'add'):
        self._counter += 1
        return (a + b) if operation == 'add' else (a - b)

    def test_properties(self):
        # Run some computations which should be cache misses
        value_1 = self.do_computation(1, 2, 'add', cache_size = 2)
        value_2 = self.do_computation(1, 2, 'subtract', cache_size = 2)

        # Check that both missed
        self.assertEqual(self._counter, 2)

        # Now run again and check for a cache hit
        value_1_cached = self.do_computation(1, 2, 'add', cache_size = 2)
        self.assertEqual(self._counter, 2)
        self.assertEqual(value_1, value_1_cached)

        # Now run again and check that we skip caching
        value_1_uncached = self.do_computation(1, 2, 'add', cache_name = None)
        self.assertEqual(self._counter, 3)
        self.assertEqual(value_1, value_1_uncached)

        # Try running in a different cache
        value_1_new = self.do_computation(1, 2, 'add', cache_name = 'abc')
        self.assertEqual(self._counter, 4)

        # And verify that that cache is fully functional
        value_1_new_cached = self.do_computation(1, 2, 'add',
                                                 cache_name = 'abc')
        self.assertEqual(self._counter, 4)
        self.assertEqual(value_1_new, value_1_new_cached)


# Run the tests if this is the main module
if __name__ == '__main__':
    unittest.main()
