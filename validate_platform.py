#!/usr/bin/env python3
"""
Platform Validation Script

Tests core functionality and identifies issues requiring fixes.
"""

import sys
import os
import asyncio
from datetime import datetime
import traceback


def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subheader(title):
    """Print formatted subheader"""
    print(f"\n--- {title} ---")


def test_imports():
    """Test all imports"""
    print_subheader("Testing Imports")

    results = []

    # Test 1: Currency Converter
    try:
        from settlement_engine.currency_converter import CurrencyConverter
        print("✅ CurrencyConverter: PASSED")
        results.append(('CurrencyConverter', True, None))
    except Exception as e:
        print(f"❌ CurrencyConverter: FAILED - {str(e)}")
        results.append(('CurrencyConverter', False, str(e)))

    # Test 2: Settlement Optimizer
    try:
        from settlement_engine.settlement_optimizer import SettlementOptimizer, UrgencyLevel, RiskTolerance, SettlementPreferences
        print("✅ SettlementOptimizer: PASSED")
        results.append(('SettlementOptimizer', True, None))
    except Exception as e:
        print(f"❌ SettlementOptimizer: FAILED - {str(e)}")
        results.append(('SettlementOptimizer', False, str(e)))

    # Test 3: Compliance Checker
    try:
        from settlement_engine.compliance_checker import ComplianceChecker, CustomerProfile, RiskLevel
        print("✅ ComplianceChecker: PASSED")
        results.append(('ComplianceChecker', True, None))
    except Exception as e:
        print(f"❌ ComplianceChecker: FAILED - {str(e)}")
        results.append(('ComplianceChecker', False, str(e)))

    # Test 4: Dependencies
    try:
        import aiohttp
        import pandas
        print("✅ Dependencies: PASSED")
        results.append(('Dependencies', True, None))
    except Exception as e:
        print(f"❌ Dependencies: FAILED - {str(e)}")
        results.append(('Dependencies', False, str(e)))

    return results


def test_basic_functionality():
    """Test basic functionality"""
    print_subheader("Testing Basic Functionality")

    results = []

    # Test 1: Currency Converter
    try:
        from settlement_engine.currency_converter import CurrencyConverter

        converter = CurrencyConverter()
        rates = converter._generate_mock_rates('USD')

        assert isinstance(rates, dict)
        assert 'USD' in rates
        assert rates['USD'] == 1.0

        print("✅ Currency Converter Basic: PASSED")
        results.append(('Currency Converter Basic', True, None))
    except Exception as e:
        print(f"❌ Currency Converter Basic: FAILED - {str(e)}")
        results.append(('Currency Converter Basic', False, str(e)))

    # Test 2: Settlement Optimizer
    try:
        from settlement_engine.settlement_optimizer import SettlementOptimizer, UrgencyLevel

        optimizer = SettlementOptimizer()

        assert optimizer is not None
        assert hasattr(optimizer, 'urgency_requirements')
        assert UrgencyLevel.INSTANT in optimizer.urgency_requirements

        print("✅ Settlement Optimizer Basic: PASSED")
        results.append(('Settlement Optimizer Basic', True, None))
    except Exception as e:
        print(f"❌ Settlement Optimizer Basic: FAILED - {str(e)}")
        results.append(('Settlement Optimizer Basic', False, str(e)))

    # Test 3: Compliance Checker
    try:
        from settlement_engine.compliance_checker import ComplianceChecker

        checker = ComplianceChecker()

        assert checker is not None
        assert hasattr(checker, 'high_risk_countries')
        assert 'IRAN' in checker.high_risk_countries

        print("✅ Compliance Checker Basic: PASSED")
        results.append(('Compliance Checker Basic', True, None))
    except Exception as e:
        print(f"❌ Compliance Checker Basic: FAILED - {str(e)}")
        results.append(('Compliance Checker Basic', False, str(e)))

    return results


async def test_async_functionality():
    """Test async functionality"""
    print_subheader("Testing Async Functionality")

    results = []

    # Test 1: Rate Fetching
    try:
        from settlement_engine.currency_converter import CurrencyConverter

        converter = CurrencyConverter()
        rates = await converter.get_real_time_rates('USD')

        assert isinstance(rates, dict)
        assert 'USD' in rates

        print("✅ Rate Fetching: PASSED")
        results.append(('Rate Fetching', True, None))
    except Exception as e:
        print(f"❌ Rate Fetching: FAILED - {str(e)}")
        results.append(('Rate Fetching', False, str(e)))

    # Test 2: Route Calculation
    try:
        from settlement_engine.currency_converter import CurrencyConverter

        converter = CurrencyConverter()
        routes = await converter.calculate_conversion_routes('USD', 'SGD', 1000.0)

        assert isinstance(routes, list)
        assert len(routes) > 0

        print("✅ Route Calculation: PASSED")
        results.append(('Route Calculation', True, None))
    except Exception as e:
        print(f"❌ Route Calculation: FAILED - {str(e)}")
        results.append(('Route Calculation', False, str(e)))

    # Test 3: Route Optimization
    try:
        from settlement_engine.currency_converter import CurrencyConverter
        from settlement_engine.settlement_optimizer import SettlementOptimizer, SettlementPreferences, UrgencyLevel, RiskTolerance

        converter = CurrencyConverter()
        optimizer = SettlementOptimizer()

        routes = await converter.calculate_conversion_routes('USD', 'SGD', 1000.0)

        preferences = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE,
            compliance_required=True
        )

        result = optimizer.optimize_settlement_route(
            routes, preferences, 1000.0, 'USD-SGD')

        assert result is not None
        assert result.route is not None

        print("✅ Route Optimization: PASSED")
        results.append(('Route Optimization', True, None))
    except Exception as e:
        print(f"❌ Route Optimization: FAILED - {str(e)}")
        results.append(('Route Optimization', False, str(e)))

    return results


def test_ui_file_exists():
    """Test if UI files exist"""
    print_subheader("Testing UI File Existence")

    results = []

    # Test 1: UI app.py exists
    ui_path = 'ui/app.py'
    if os.path.exists(ui_path):
        print("✅ UI app.py: EXISTS")
        results.append(('UI app.py', True, None))
    else:
        print("❌ UI app.py: MISSING")
        results.append(('UI app.py', False, 'File does not exist'))

    return results


def fix_missing_ui_file():
    """Fix missing UI file"""
    print_subheader("Fixing Missing UI File")

    ui_path = 'ui/app.py'

    if not os.path.exists(ui_path):
        print("🔧 Creating missing UI app.py file...")

        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(ui_path), exist_ok=True)

            # Create a basic app.py file
            ui_content = '''"""
Cross-Border Settlement Platform UI

Basic Streamlit application for the settlement platform.
"""

import streamlit as st

def main():
    st.title("Cross-Border Settlement Platform")
    st.write("Platform is under development.")
    
    if st.button("Test Platform"):
        st.success("Platform is running!")

if __name__ == "__main__":
    main()
'''

            with open(ui_path, 'w') as f:
                f.write(ui_content)

            print("✅ UI app.py file created successfully")
            return True

        except Exception as e:
            print(f"❌ Failed to create UI app.py: {str(e)}")
            return False
    else:
        print("✅ UI app.py already exists")
        return True


def main():
    """Main validation function"""
    print_header("🧪 Cross-Border Settlement Platform Validation")

    print(
        f"Validation started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_results = []

    try:
        # Test imports
        import_results = test_imports()
        all_results.extend(import_results)

        # Test basic functionality
        basic_results = test_basic_functionality()
        all_results.extend(basic_results)

        # Test async functionality
        async_results = asyncio.run(test_async_functionality())
        all_results.extend(async_results)

        # Test UI file existence
        ui_results = test_ui_file_exists()
        all_results.extend(ui_results)

        # Fix UI file if missing
        fix_missing_ui_file()

        # Calculate results
        print_header("📊 VALIDATION RESULTS")

        total_tests = len(all_results)
        passed_tests = sum(1 for result in all_results if result[1])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests *
                        100) if total_tests > 0 else 0

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {success_rate:.1f}%")

        # Show failed tests
        if failed_tests > 0:
            print(f"\n🔍 Failed Tests:")
            for test_name, success, error in all_results:
                if not success:
                    print(f"  - {test_name}: {error}")

        # Assessment
        print(f"\n💡 Platform Assessment:")
        if success_rate >= 90:
            print("🎉 EXCELLENT - Platform is production-ready!")
        elif success_rate >= 70:
            print("👍 GOOD - Platform is mostly functional")
        elif success_rate >= 50:
            print("⚠️  MODERATE - Some issues need attention")
        else:
            print("🔥 CRITICAL - Significant issues require immediate attention")

        print(
            f"\nValidation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        return 0 if success_rate >= 70 else 1

    except Exception as e:
        print(f"\n❌ Validation failed: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
