#!/usr/bin/env python3
"""
Comprehensive test runner for the algorithmic trading platform.
Runs all diagnostic and integration tests in organized sequence.
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_diagnostic_tests():
    """Run all diagnostic tests for Order Books functionality."""
    print("🔍 Running Diagnostic Tests")
    print("=" * 50)

    diagnostic_dir = Path(__file__).parent / "diagnostics"
    test_files = [
        "test_bid_ask_bug.py",
        "diagnose_order_books.py",
        "test_order_books.py",
        "test_order_books_ui.py",
        "validate_order_books.py"
    ]

    results = {}

    for test_file in test_files:
        test_path = diagnostic_dir / test_file
        if test_path.exists():
            print(f"\n📋 Running {test_file}...")
            try:
                result = subprocess.run([sys.executable, str(test_path)],
                                        capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print(f"✅ {test_file} PASSED")
                    results[test_file] = "PASSED"
                else:
                    print(f"❌ {test_file} FAILED")
                    print(f"Error: {result.stderr}")
                    results[test_file] = "FAILED"
            except subprocess.TimeoutExpired:
                print(f"⏰ {test_file} TIMEOUT")
                results[test_file] = "TIMEOUT"
            except Exception as e:
                print(f"💥 {test_file} ERROR: {e}")
                results[test_file] = "ERROR"
        else:
            print(f"⚠️  {test_file} not found")
            results[test_file] = "NOT_FOUND"

    return results


def run_integration_tests():
    """Run all integration tests."""
    print("\n\n🔗 Running Integration Tests")
    print("=" * 50)

    integration_dir = Path(__file__).parent / "integration"
    test_files = [
        "integration_test.py",
        "end_to_end_test.py",
        "test_app_functionality.py"
    ]

    results = {}

    for test_file in test_files:
        test_path = integration_dir / test_file
        if test_path.exists():
            print(f"\n📋 Running {test_file}...")
            try:
                result = subprocess.run([sys.executable, str(test_path)],
                                        capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    print(f"✅ {test_file} PASSED")
                    results[test_file] = "PASSED"
                else:
                    print(f"❌ {test_file} FAILED")
                    print(f"Error: {result.stderr}")
                    results[test_file] = "FAILED"
            except subprocess.TimeoutExpired:
                print(f"⏰ {test_file} TIMEOUT")
                results[test_file] = "TIMEOUT"
            except Exception as e:
                print(f"💥 {test_file} ERROR: {e}")
                results[test_file] = "ERROR"
        else:
            print(f"⚠️  {test_file} not found")
            results[test_file] = "NOT_FOUND"

    return results


def run_unit_tests():
    """Run unit tests using pytest if available."""
    print("\n\n🧪 Running Unit Tests")
    print("=" * 50)

    try:
        # Try to run pytest
        result = subprocess.run([sys.executable, "-m", "pytest", str(Path(__file__).parent), "-v"],
                                capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print("✅ Unit tests PASSED")
            print(result.stdout)
            return {"pytest": "PASSED"}
        else:
            print("❌ Unit tests FAILED")
            print(result.stderr)
            return {"pytest": "FAILED"}
    except FileNotFoundError:
        print("⚠️  pytest not available, skipping unit tests")
        return {"pytest": "SKIPPED"}
    except subprocess.TimeoutExpired:
        print("⏰ Unit tests TIMEOUT")
        return {"pytest": "TIMEOUT"}
    except Exception as e:
        print(f"💥 Unit tests ERROR: {e}")
        return {"pytest": "ERROR"}


def print_summary(diagnostic_results, integration_results, unit_results):
    """Print a comprehensive test summary."""
    print("\n\n📊 Test Summary")
    print("=" * 50)

    total_tests = 0
    passed_tests = 0

    print("\n🔍 Diagnostic Tests:")
    for test, result in diagnostic_results.items():
        status_emoji = "✅" if result == "PASSED" else "❌"
        print(f"   {status_emoji} {test}: {result}")
        total_tests += 1
        if result == "PASSED":
            passed_tests += 1

    print("\n🔗 Integration Tests:")
    for test, result in integration_results.items():
        status_emoji = "✅" if result == "PASSED" else "❌"
        print(f"   {status_emoji} {test}: {result}")
        total_tests += 1
        if result == "PASSED":
            passed_tests += 1

    print("\n🧪 Unit Tests:")
    for test, result in unit_results.items():
        status_emoji = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "⚠️"
        print(f"   {status_emoji} {test}: {result}")
        if result not in ["SKIPPED", "NOT_FOUND"]:
            total_tests += 1
            if result == "PASSED":
                passed_tests += 1

    print(f"\n🎯 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(
        f"   Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "No tests run")

    if passed_tests == total_tests and total_tests > 0:
        print("\n🎉 All tests passed! The system is ready for deployment.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please review the results above.")
        return False


def main():
    """Main test runner function."""
    print("🚀 Algorithmic Trading Platform - Comprehensive Test Suite")
    print("========================================================")

    # Change to the project root directory
    os.chdir(Path(__file__).parent.parent)

    try:
        # Run all test suites
        diagnostic_results = run_diagnostic_tests()
        integration_results = run_integration_tests()
        unit_results = run_unit_tests()

        # Print comprehensive summary
        all_passed = print_summary(
            diagnostic_results, integration_results, unit_results)

        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n💥 Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
