#!/usr/bin/env python
"""
Correct test runner for the algorithmic trading platform
"""

import sys
import os
from pathlib import Path
import unittest

# Add the root project directory to the Python path
BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

# Now run the tests


def run_tests():
    """Run all tests in the tests directory"""
    print("Running unit tests...")
    print("-------------------")

    # Find and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')

    result = unittest.TextTestRunner().run(test_suite)

    print("-------------------")
    print(f"Tests run: {result.testsRun}")
    print(f"Errors: {len(result.errors)}")
    print(f"Failures: {len(result.failures)}")

    return len(result.errors) + len(result.failures)


if __name__ == "__main__":
    # Exit with non-zero exit code if there are test failures
    sys.exit(run_tests())
