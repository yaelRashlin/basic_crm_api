#!/usr/bin/env python3
"""
Test runner for the User Management Flask Server.

This script runs all tests and provides a summary of results.
"""

import unittest
import sys
import os

# Add the parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_all_tests():
    """Run all tests and return results."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return result

def run_specific_test_module(module_name):
    """Run tests from a specific module."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(f'test_{module_name}')
    
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    return result

def print_test_summary(result):
    """Print a summary of test results."""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    
    print(f"Total tests run: {total_tests}")
    print(f"Successes: {total_tests - failures - errors - skipped}")
    print(f"Failures: {failures}")
    print(f"Errors: {errors}")
    print(f"Skipped: {skipped}")
    
    if result.wasSuccessful():
        print("\nALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED!")
        
        if result.failures:
            print("\nFAILURES:")
            for test, traceback in result.failures:
                try:
                    error_msg = traceback.split('AssertionError: ')[-1].split('\\n')[0]
                except (IndexError, AttributeError):
                    error_msg = "Assertion failed"
                print(f"- {test}: {error_msg}")
        
        if result.errors:
            print("\nERRORS:")
            for test, traceback in result.errors:
                lines = traceback.split('\\n')
                error_line = lines[-2] if len(lines) >= 2 else lines[-1] if lines else "Unknown error"
                print(f"- {test}: {error_line}")
    
    print("="*60)

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for User Management Flask Server')
    parser.add_argument('--module', '-m', type=str, help='Run tests from specific module (models, schemas, database, validators, integration)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("User Management Flask Server - Test Runner")
    print("="*60)
    
    if args.module:
        print(f"Running tests for module: {args.module}")
        result = run_specific_test_module(args.module)
    else:
        print("Running all tests...")
        result = run_all_tests()
    
    print_test_summary(result)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == '__main__':
    main()