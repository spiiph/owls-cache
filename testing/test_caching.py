# System imports
import unittest

# owls-core imports
from owls_core.caching import transiently_cached, persistently_cached


class TestTransientCaching(unittest.TestCase):
    def setUp(self):
        # Create a counter to check cache misses
        self._counter = 0

    @transiently_cached(optional = True, default = True, size = 2)
    def do_computation(self, a, b, operation = 'add'):
        self._counter += 1
        return (a + b) if operation == 'add' else (a - b)

    def test_properties(self):
        # Run some computations which should be cache misses
        value_1 = self.do_computation(1, 2, 'add', cache = True)
        value_2 = self.do_computation(1, 2, 'subtract')

        # Check that both missed
        self.assertEqual(self._counter, 2)

        # Now run again and check for a cache hit
        value_1_cached = self.do_computation(1, 2, 'add')
        self.assertEqual(self._counter, 2)
        self.assertEqual(value_1, value_1_cached)


# Run the tests if this is the main module
if __name__ == '__main__':
    unittest.main()
