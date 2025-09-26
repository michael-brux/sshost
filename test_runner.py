
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

def run_tests():
    """
    Discover and run all tests in the test directory.
    """
    # Create a test loader
    loader = unittest.TestLoader()
    
    # Discover tests in the test directory
    test_dir = os.path.join(os.path.dirname(__file__), 'test')
    suite = loader.discover(test_dir, pattern='*_test*.py')
    
    # Create a test runner and run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == "__main__":
    run_tests()
