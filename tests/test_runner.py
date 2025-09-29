#!/usr/bin/env python3
"""Test runner for all cost tracking unit tests"""

import unittest
import sys
import os

# Add scripts directory to path for imports
scripts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts')
sys.path.insert(0, scripts_dir)

def run_all_tests():
    """Run all cost tracking unit tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Import all test modules
    test_modules = [
        'test_pricing_database',
        'test_wayback_scraper',
        'test_cost_calculator',
        'test_benchmark_token_estimation'
    ]

    for module_name in test_modules:
        try:
            module = __import__(module_name)
            suite.addTests(loader.loadTestsFromModule(module))
            print(f"✓ Loaded tests from {module_name}")
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {e}")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return True if all tests passed
    return result.wasSuccessful()

def run_specific_test(test_name):
    """Run a specific test module."""
    loader = unittest.TestLoader()

    try:
        module = __import__(f'test_{test_name}')
        suite = loader.loadTestsFromModule(module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return result.wasSuccessful()
    except ImportError as e:
        print(f"✗ Failed to import test_{test_name}: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests
        print("Running all cost tracking tests...")
        print("=" * 50)
        success = run_all_tests()

    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)