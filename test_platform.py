"""
Comprehensive Platform Tests

pytest test suite for the Cross-Border Settlement Platform.
Run with: pytest test_platform.py -v
"""

import pytest
import asyncio
from datetime import datetime

# Core Platform Tests


class TestPlatformCore:
    """Test core platform functionality"""

    def test_currency_converter_import(self):
        """Test currency converter can be imported"""
        from settlement_engine.currency_converter import CurrencyConverter
        assert CurrencyConverter is not None

    def test_settlement_optimizer_import(self):
        """Test settlement optimizer can be imported"""
        from settlement_engine.settlement_optimizer import SettlementOptimizer, UrgencyLevel, RiskTolerance
        assert SettlementOptimizer is not None
        assert UrgencyLevel is not None
        assert RiskTolerance is not None

    def test_compliance_checker_import(self):
        """Test compliance checker can be imported"""
        from settlement_engine.compliance_checker import ComplianceChecker, CustomerProfile, RiskLevel
        assert ComplianceChecker is not None
        assert CustomerProfile is not None
        assert RiskLevel is not None

    def test_dependencies_available(self):
        """Test required dependencies are available"""
        import aiohttp
        import pandas
        import asyncio
        assert aiohttp is not None
        assert pandas is not None
        assert asyncio is not None


class TestCurrencyConverter:
    """Test currency converter functionality"""

    def test_initialization(self):
        """Test currency converter initialization"""
        from settlement_engine.currency_converter import CurrencyConverter

        converter = CurrencyConverter()
        assert converter is not None
        assert hasattr(converter, 'supported_pairs')
        assert 'USD' in converter.supported_pairs
        assert 'SGD' in converter.supported_pairs

    def test_mock_rates_generation(self):
        """Test mock rate generation"""
        from settlement_engine.currency_converter import CurrencyConverter

        converter = CurrencyConverter()
        rates = converter._generate_mock_rates('USD')

        assert isinstance(rates, dict)
        assert 'USD' in rates
        assert 'SGD' in rates
        assert 'EUR' in rates
        assert rates['USD'] == 1.0
        assert rates['SGD'] > 1.0  # SGD should be more than USD

    @pytest.mark.asyncio
    async def test_real_time_rates(self):
        """Test real-time rate fetching"""
        from settlement_engine.currency_converter import CurrencyConverter

        converter = CurrencyConverter()
        rates = await converter.get_real_time_rates('USD')

        assert isinstance(rates, dict)
        assert 'USD' in rates
        assert rates['USD'] == 1.0
        assert len(rates) > 5  # Should have multiple currencies

    @pytest.mark.asyncio
    async def test_route_calculation(self):
        """Test route calculation functionality"""
        from settlement_engine.currency_converter import CurrencyConverter

        converter = CurrencyConverter()
        routes = await converter.calculate_conversion_routes('USD', 'SGD', 1000.0)

        assert isinstance(routes, list)
        assert len(routes) > 0
        assert routes[0].from_currency == 'USD'
        assert routes[0].to_currency == 'SGD'
        assert routes[0].amount == 1000.0
        assert routes[0].total_cost > 0
        assert routes[0].final_amount > 0


class TestSettlementOptimizer:
    """Test settlement optimizer functionality"""

    def test_initialization(self):
        """Test settlement optimizer initialization"""
        from settlement_engine.settlement_optimizer import SettlementOptimizer, UrgencyLevel

        optimizer = SettlementOptimizer()
        assert optimizer is not None
        assert hasattr(optimizer, 'urgency_requirements')
        assert UrgencyLevel.INSTANT in optimizer.urgency_requirements
        assert UrgencyLevel.STANDARD in optimizer.urgency_requirements

    @pytest.mark.asyncio
    async def test_route_optimization(self):
        """Test route optimization functionality"""
        from settlement_engine.currency_converter import CurrencyConverter
        from settlement_engine.settlement_optimizer import (
            SettlementOptimizer, SettlementPreferences, UrgencyLevel, RiskTolerance
        )

        # Get routes
        converter = CurrencyConverter()
        routes = await converter.calculate_conversion_routes('USD', 'SGD', 1000.0)

        # Optimize routes
        optimizer = SettlementOptimizer()
        preferences = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE,
            compliance_required=True
        )

        result = optimizer.optimize_settlement_route(
            routes, preferences, 1000.0, 'USD-SGD')

        assert result is not None
        assert result.route is not None
        assert result.route in routes
        assert result.selection_reason is not None
        assert isinstance(result.selection_reason, str)
        assert len(result.selection_reason) > 0


class TestComplianceChecker:
    """Test compliance checker functionality"""

    def test_initialization(self):
        """Test compliance checker initialization"""
        from settlement_engine.compliance_checker import ComplianceChecker

        checker = ComplianceChecker()
        assert checker is not None
        assert hasattr(checker, 'high_risk_countries')
        assert hasattr(checker, 'sanctions_lists')
        assert 'IRAN' in checker.high_risk_countries
        assert 'OFAC_SDN' in checker.sanctions_lists

    def test_customer_profile_creation(self):
        """Test customer profile creation"""
        from settlement_engine.compliance_checker import CustomerProfile, RiskLevel

        customer = CustomerProfile(
            customer_id="TEST001",
            name="Test Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 10000, "daily_volume": 1000},
            sanctions_checked=True,
            pep_status=False
        )

        assert customer.customer_id == "TEST001"
        assert customer.name == "Test Customer"
        assert customer.country == "United States"
        assert customer.risk_rating == RiskLevel.LOW
        assert customer.kyc_level == "enhanced"
        assert customer.pep_status == False

    def test_compliance_check(self):
        """Test comprehensive compliance check"""
        from settlement_engine.compliance_checker import ComplianceChecker, CustomerProfile, RiskLevel

        compliance_checker = ComplianceChecker()

        customer = CustomerProfile(
            customer_id="TEST001",
            name="Test Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 10000, "daily_volume": 1000},
            sanctions_checked=True,
            pep_status=False
        )

        counterparty = CustomerProfile(
            customer_id="TEST002",
            name="Test Counterparty",
            country="Singapore",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 3, 1),
            transaction_history={"monthly_volume": 5000, "daily_volume": 500},
            sanctions_checked=True,
            pep_status=False
        )

        result = compliance_checker.perform_comprehensive_compliance_check(
            customer, counterparty, 5000.0, 'USD', 'SGD', 'personal_transfer'
        )

        assert result is not None
        assert result.transaction_id is not None
        assert result.overall_status is not None
        assert result.risk_level is not None
        assert isinstance(result.compliance_score, float)
        assert 0 <= result.compliance_score <= 100
        assert isinstance(result.review_required, bool)
        assert isinstance(result.auto_approval, bool)


class TestIntegration:
    """Test integration between components"""

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end payment workflow"""
        from settlement_engine.currency_converter import CurrencyConverter
        from settlement_engine.settlement_optimizer import (
            SettlementOptimizer, SettlementPreferences, UrgencyLevel, RiskTolerance
        )
        from settlement_engine.compliance_checker import ComplianceChecker, CustomerProfile, RiskLevel

        # Initialize components
        converter = CurrencyConverter()
        optimizer = SettlementOptimizer()
        compliance_checker = ComplianceChecker()

        # Step 1: Get routes
        routes = await converter.calculate_conversion_routes('USD', 'SGD', 2500.0)
        assert len(routes) > 0

        # Step 2: Optimize route
        preferences = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE,
            compliance_required=True
        )

        optimized_result = optimizer.optimize_settlement_route(
            routes, preferences, 2500.0, 'USD-SGD')
        assert optimized_result is not None
        assert optimized_result.route in routes

        # Step 3: Perform compliance check
        customer = CustomerProfile(
            customer_id="INTEG001",
            name="Integration Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 15000, "daily_volume": 2000},
            sanctions_checked=True,
            pep_status=False
        )

        counterparty = CustomerProfile(
            customer_id="INTEG002",
            name="Integration Counterparty",
            country="Singapore",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 3, 1),
            transaction_history={"monthly_volume": 8000, "daily_volume": 1000},
            sanctions_checked=True,
            pep_status=False
        )

        compliance_result = compliance_checker.perform_comprehensive_compliance_check(
            customer, counterparty, 2500.0, 'USD', 'SGD', 'personal_transfer'
        )

        assert compliance_result is not None
        assert compliance_result.transaction_id is not None

        # Verify workflow results
        assert optimized_result.route.from_currency == 'USD'
        assert optimized_result.route.to_currency == 'SGD'
        assert optimized_result.route.amount == 2500.0
        assert compliance_result.overall_status is not None


class TestFileStructure:
    """Test file structure and UI components"""

    def test_ui_file_exists(self):
        """Test that UI file exists"""
        import os

        ui_path = 'ui/app.py'
        assert os.path.exists(ui_path), f"UI file {ui_path} does not exist"

    def test_ui_file_content(self):
        """Test UI file content"""
        import os

        ui_path = 'ui/app.py'
        with open(ui_path, 'r') as f:
            content = f.read()

        assert 'streamlit' in content.lower(), "Streamlit not found in UI file"
        assert 'main' in content.lower(), "Main function not found in UI file"

    def test_settlement_engine_structure(self):
        """Test settlement engine file structure"""
        import os

        required_files = [
            'settlement_engine/__init__.py',
            'settlement_engine/currency_converter.py',
            'settlement_engine/settlement_optimizer.py',
            'settlement_engine/compliance_checker.py'
        ]

        for file_path in required_files:
            assert os.path.exists(
                file_path), f"Required file {file_path} does not exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
