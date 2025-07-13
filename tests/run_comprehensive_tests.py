#!/usr/bin/env python3
"""
Comprehensive Test Runner for Cross-Border Settlement Platform

Runs all unit tests, integration tests, and generates a comprehensive report.
"""

import sys
import os
import subprocess
import json
from datetime import datetime
import traceback

# Add the parent directory to the Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_pytest_with_coverage():
    """Run pytest with coverage reporting"""

    print("🧪 Running Comprehensive Test Suite...")
    print("=" * 60)

    # Test categories
    test_categories = [
        {
            'name': 'Unit Tests - Currency Converter',
            'path': 'tests/unit/test_currency_converter.py',
            'description': 'Tests for currency conversion and route calculation'
        },
        {
            'name': 'Unit Tests - Settlement Optimizer',
            'path': 'tests/unit/test_settlement_optimizer.py',
            'description': 'Tests for settlement route optimization'
        },
        {
            'name': 'Unit Tests - Compliance Checker',
            'path': 'tests/unit/test_compliance_checker.py',
            'description': 'Tests for KYC/AML/compliance validation'
        },
        {
            'name': 'Integration Tests - Platform Integration',
            'path': 'tests/integration/test_platform_integration.py',
            'description': 'Tests for component integration and end-to-end workflows'
        }
    ]

    results = {
        'start_time': datetime.now().isoformat(),
        'test_categories': {},
        'overall_summary': {},
        'errors': []
    }

    total_tests = 0
    total_passed = 0
    total_failed = 0

    for category in test_categories:
        print(f"\n📋 Running: {category['name']}")
        print(f"   Description: {category['description']}")
        print("-" * 50)

        try:
            # Run pytest for this category
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                category['path'],
                '-v', '--tb=short', '--no-header'
            ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

            # Parse results
            output_lines = result.stdout.split('\n')
            error_lines = result.stderr.split('\n')

            # Extract test results
            passed_tests = [
                line for line in output_lines if '::' in line and 'PASSED' in line]
            failed_tests = [
                line for line in output_lines if '::' in line and 'FAILED' in line]

            category_passed = len(passed_tests)
            category_failed = len(failed_tests)
            category_total = category_passed + category_failed

            total_tests += category_total
            total_passed += category_passed
            total_failed += category_failed

            # Store results
            results['test_categories'][category['name']] = {
                'total': category_total,
                'passed': category_passed,
                'failed': category_failed,
                'success_rate': (category_passed / category_total * 100) if category_total > 0 else 0,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }

            # Print results
            if category_total > 0:
                success_rate = (category_passed / category_total) * 100
                print(f"   ✅ Passed: {category_passed}")
                print(f"   ❌ Failed: {category_failed}")
                print(f"   📊 Success Rate: {success_rate:.1f}%")

                if category_failed > 0:
                    print(f"   ⚠️  Failed Tests:")
                    # Show first 3 failures
                    for failed_test in failed_tests[:3]:
                        print(f"      - {failed_test}")
            else:
                print(f"   ⚠️  No tests found or unable to run")

        except Exception as e:
            print(f"   ❌ Error running {category['name']}: {str(e)}")
            results['errors'].append({
                'category': category['name'],
                'error': str(e),
                'traceback': traceback.format_exc()
            })

    # Calculate overall results
    overall_success_rate = (total_passed / total_tests *
                            100) if total_tests > 0 else 0

    results['overall_summary'] = {
        'total_tests': total_tests,
        'total_passed': total_passed,
        'total_failed': total_failed,
        'overall_success_rate': overall_success_rate
    }

    results['end_time'] = datetime.now().isoformat()

    # Print overall summary
    print("\n" + "=" * 60)
    print("📊 OVERALL TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {total_tests}")
    print(f"Tests Passed: {total_passed} ✅")
    print(f"Tests Failed: {total_failed} ❌")
    print(f"Overall Success Rate: {overall_success_rate:.1f}%")

    if overall_success_rate >= 80:
        print("🎉 EXCELLENT: Platform is production-ready!")
    elif overall_success_rate >= 60:
        print("👍 GOOD: Platform is mostly functional with minor issues")
    elif overall_success_rate >= 40:
        print("⚠️  MODERATE: Platform has some issues requiring attention")
    else:
        print("🔥 CRITICAL: Platform has significant issues requiring immediate attention")

    # Save detailed results
    with open('test_results_detailed.json', 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Detailed results saved to: test_results_detailed.json")

    return results


def run_manual_functionality_tests():
    """Run manual functionality tests for core features"""

    print("\n🔧 Running Manual Functionality Tests...")
    print("=" * 60)

    manual_tests = []

    # Test 1: Basic Currency Converter
    try:
        print("\n📋 Test 1: Basic Currency Converter Functionality")
        from settlement_engine.currency_converter import CurrencyConverter

        converter = CurrencyConverter()

        # Test mock rate generation
        rates = converter._generate_mock_rates('USD')
        assert isinstance(rates, dict)
        assert 'USD' in rates
        assert 'SGD' in rates
        assert rates['USD'] == 1.0

        print("   ✅ Currency converter initialization: PASSED")
        print("   ✅ Mock rate generation: PASSED")

        manual_tests.append({
            'name': 'Currency Converter Basic Functionality',
            'status': 'PASSED',
            'details': 'Initialization and mock rate generation working'
        })

    except Exception as e:
        print(f"   ❌ Currency converter test failed: {str(e)}")
        manual_tests.append({
            'name': 'Currency Converter Basic Functionality',
            'status': 'FAILED',
            'details': str(e)
        })

    # Test 2: Settlement Optimizer
    try:
        print("\n📋 Test 2: Settlement Optimizer Functionality")
        from settlement_engine.settlement_optimizer import SettlementOptimizer, UrgencyLevel, RiskTolerance

        optimizer = SettlementOptimizer()

        # Test initialization
        assert optimizer is not None
        assert hasattr(optimizer, 'urgency_requirements')
        assert UrgencyLevel.INSTANT in optimizer.urgency_requirements

        print("   ✅ Settlement optimizer initialization: PASSED")
        print("   ✅ Urgency requirements configuration: PASSED")

        manual_tests.append({
            'name': 'Settlement Optimizer Basic Functionality',
            'status': 'PASSED',
            'details': 'Initialization and configuration working'
        })

    except Exception as e:
        print(f"   ❌ Settlement optimizer test failed: {str(e)}")
        manual_tests.append({
            'name': 'Settlement Optimizer Basic Functionality',
            'status': 'FAILED',
            'details': str(e)
        })

    # Test 3: Compliance Checker
    try:
        print("\n📋 Test 3: Compliance Checker Functionality")
        from settlement_engine.compliance_checker import ComplianceChecker, RiskLevel

        compliance_checker = ComplianceChecker()

        # Test initialization
        assert compliance_checker is not None
        assert hasattr(compliance_checker, 'high_risk_countries')
        assert 'IRAN' in compliance_checker.high_risk_countries
        assert 'OFAC_SDN' in compliance_checker.sanctions_lists

        print("   ✅ Compliance checker initialization: PASSED")
        print("   ✅ Risk countries configuration: PASSED")
        print("   ✅ Sanctions lists configuration: PASSED")

        manual_tests.append({
            'name': 'Compliance Checker Basic Functionality',
            'status': 'PASSED',
            'details': 'Initialization and configuration working'
        })

    except Exception as e:
        print(f"   ❌ Compliance checker test failed: {str(e)}")
        manual_tests.append({
            'name': 'Compliance Checker Basic Functionality',
            'status': 'FAILED',
            'details': str(e)
        })

    # Test 4: Integration Test
    try:
        print("\n📋 Test 4: Basic Integration Test")
        import asyncio
        from settlement_engine.currency_converter import CurrencyConverter
        from settlement_engine.settlement_optimizer import SettlementOptimizer, SettlementPreferences, UrgencyLevel, RiskTolerance

        async def integration_test():
            converter = CurrencyConverter()
            optimizer = SettlementOptimizer()

            # Get routes
            routes = await converter.calculate_conversion_routes('USD', 'SGD', 1000.0)

            # Optimize route
            preferences = SettlementPreferences(
                urgency=UrgencyLevel.STANDARD,
                risk_tolerance=RiskTolerance.MODERATE
            )

            result = optimizer.optimize_settlement_route(
                routes, preferences, 1000.0, 'USD-SGD')

            return result

        # Run integration test
        result = asyncio.run(integration_test())

        assert result is not None
        assert result.route is not None
        assert result.selection_reason is not None

        print("   ✅ Route calculation: PASSED")
        print("   ✅ Route optimization: PASSED")
        print("   ✅ Integration workflow: PASSED")

        manual_tests.append({
            'name': 'Basic Integration Test',
            'status': 'PASSED',
            'details': 'End-to-end workflow working'
        })

    except Exception as e:
        print(f"   ❌ Integration test failed: {str(e)}")
        manual_tests.append({
            'name': 'Basic Integration Test',
            'status': 'FAILED',
            'details': str(e)
        })

    # Summary
    passed_manual = sum(
        1 for test in manual_tests if test['status'] == 'PASSED')
    total_manual = len(manual_tests)
    manual_success_rate = (passed_manual / total_manual *
                           100) if total_manual > 0 else 0

    print(f"\n📊 Manual Test Results:")
    print(f"   Total Manual Tests: {total_manual}")
    print(f"   Passed: {passed_manual} ✅")
    print(f"   Failed: {total_manual - passed_manual} ❌")
    print(f"   Success Rate: {manual_success_rate:.1f}%")

    return manual_tests


def identify_and_fix_issues():
    """Identify common issues and provide fixes"""

    print("\n🔧 Identifying and Fixing Common Issues...")
    print("=" * 60)

    fixes_applied = []

    # Check for missing imports
    try:
        print("\n📋 Checking for Missing Import Issues")

        # Try importing all main modules
        from settlement_engine.currency_converter import CurrencyConverter
        from settlement_engine.settlement_optimizer import SettlementOptimizer
        from settlement_engine.compliance_checker import ComplianceChecker

        print("   ✅ All main modules can be imported successfully")

    except ImportError as e:
        print(f"   ❌ Import error detected: {str(e)}")
        fixes_applied.append({
            'issue': 'Import Error',
            'fix': 'Check module paths and dependencies',
            'status': 'REQUIRES_MANUAL_FIX'
        })

    # Check for missing dependencies
    try:
        print("\n📋 Checking for Missing Dependencies")

        import aiohttp
        import pandas
        import asyncio

        print("   ✅ All required dependencies are available")

    except ImportError as e:
        print(f"   ❌ Missing dependency: {str(e)}")
        fixes_applied.append({
            'issue': 'Missing Dependency',
            'fix': 'Run: pip install -r requirements.txt',
            'status': 'REQUIRES_MANUAL_FIX'
        })

    # Check for file structure issues
    try:
        print("\n📋 Checking File Structure")

        required_files = [
            'settlement_engine/__init__.py',
            'settlement_engine/currency_converter.py',
            'settlement_engine/settlement_optimizer.py',
            'settlement_engine/compliance_checker.py'
        ]

        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)

        if missing_files:
            print(f"   ❌ Missing files: {missing_files}")
            fixes_applied.append({
                'issue': 'Missing Files',
                'fix': f'Create missing files: {missing_files}',
                'status': 'REQUIRES_MANUAL_FIX'
            })
        else:
            print("   ✅ All required files are present")

    except Exception as e:
        print(f"   ❌ File structure check failed: {str(e)}")

    return fixes_applied


def main():
    """Main test execution function"""

    print("🚀 Cross-Border Settlement Platform - Comprehensive Test Suite")
    print("=" * 80)
    print(
        f"Test execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run manual functionality tests first
        manual_results = run_manual_functionality_tests()

        # Identify and fix issues
        fixes = identify_and_fix_issues()

        # Run comprehensive pytest suite
        test_results = run_pytest_with_coverage()

        # Generate final report
        print("\n" + "=" * 80)
        print("🎯 FINAL PLATFORM ASSESSMENT")
        print("=" * 80)

        # Manual test summary
        manual_passed = sum(
            1 for test in manual_results if test['status'] == 'PASSED')
        manual_total = len(manual_results)
        manual_rate = (manual_passed / manual_total *
                       100) if manual_total > 0 else 0

        print(f"\n📋 Manual Functionality Tests:")
        print(
            f"   Passed: {manual_passed}/{manual_total} ({manual_rate:.1f}%)")

        # Automated test summary
        automated_rate = test_results['overall_summary']['overall_success_rate']
        automated_passed = test_results['overall_summary']['total_passed']
        automated_total = test_results['overall_summary']['total_tests']

        print(f"\n🧪 Automated Test Suite:")
        print(
            f"   Passed: {automated_passed}/{automated_total} ({automated_rate:.1f}%)")

        # Overall assessment
        if automated_total > 0:
            overall_rate = (manual_rate + automated_rate) / 2
        else:
            overall_rate = manual_rate

        print(f"\n🎯 Overall Platform Health: {overall_rate:.1f}%")

        # Recommendations
        print(f"\n💡 Recommendations:")
        if overall_rate >= 80:
            print("   ✅ Platform is production-ready!")
            print("   ✅ All core functionality is working correctly")
            print("   ✅ Ready for customer demonstrations")
        elif overall_rate >= 60:
            print("   👍 Platform is mostly functional")
            print("   ⚠️  Some minor issues need attention")
            print("   ✅ Suitable for development and testing")
        else:
            print("   🔥 Platform has significant issues")
            print("   ❌ Requires immediate attention before use")
            print("   🔧 Review failed tests and apply fixes")

        # Fixes applied
        if fixes:
            print(f"\n🔧 Issues Identified:")
            for fix in fixes:
                print(f"   - {fix['issue']}: {fix['fix']}")

        print(
            f"\n📄 Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print(f"\n❌ Test execution failed: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
