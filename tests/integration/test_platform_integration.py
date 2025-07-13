"""
Integration Tests for Cross-Border Settlement Platform

Tests the integration between different components:
- Currency converter + Settlement optimizer
- Settlement optimizer + Compliance checker
- End-to-end payment processing workflows
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime

from settlement_engine.currency_converter import CurrencyConverter
from settlement_engine.settlement_optimizer import (
    SettlementOptimizer,
    UrgencyLevel,
    RiskTolerance,
    SettlementPreferences
)
from settlement_engine.compliance_checker import (
    ComplianceChecker,
    CustomerProfile,
    RiskLevel
)


class TestPlatformIntegration:
    """Integration tests for the entire settlement platform"""

    @pytest.fixture
    def platform_components(self):
        """Create all platform components for testing"""
        return {
            'converter': CurrencyConverter(),
            'optimizer': SettlementOptimizer(),
            'compliance_checker': ComplianceChecker()
        }

    @pytest.fixture
    def test_customer(self):
        """Create test customer for integration tests"""
        return CustomerProfile(
            customer_id="INTEG_CUST_001",
            name="Integration Test Customer",
            country="United States",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="enhanced",
            last_kyc_update=datetime(2024, 6, 1),
            transaction_history={
                "monthly_volume": 25000, "daily_volume": 3000},
            sanctions_checked=True,
            pep_status=False
        )

    @pytest.fixture
    def test_counterparty(self):
        """Create test counterparty for integration tests"""
        return CustomerProfile(
            customer_id="INTEG_COUNTER_001",
            name="Integration Test Counterparty",
            country="Singapore",
            entity_type="individual",
            risk_rating=RiskLevel.LOW,
            kyc_level="basic",
            last_kyc_update=datetime(2024, 3, 1),
            transaction_history={"monthly_volume": 8000, "daily_volume": 1000},
            sanctions_checked=True,
            pep_status=False
        )

    @pytest.mark.asyncio
    async def test_currency_converter_optimizer_integration(self, platform_components):
        """Test integration between currency converter and settlement optimizer"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        # Get routes from converter
        routes = await converter.calculate_conversion_routes('USD', 'SGD', 5000.0)

        assert len(routes) > 0

        # Use optimizer to select best route
        preferences = SettlementPreferences(
            urgency=UrgencyLevel.SAME_DAY,
            risk_tolerance=RiskTolerance.MODERATE,
            compliance_required=True
        )

        optimized_result = optimizer.optimize_settlement_route(
            routes,
            preferences,
            5000.0,
            'USD-SGD'
        )

        assert optimized_result is not None
        assert optimized_result.route in routes
        assert isinstance(optimized_result.selection_reason, str)
        assert len(optimized_result.selection_reason) > 0

    @pytest.mark.asyncio
    async def test_end_to_end_payment_workflow(self, platform_components, test_customer, test_counterparty):
        """Test complete end-to-end payment processing workflow"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']
        compliance_checker = platform_components['compliance_checker']

        # Step 1: Get available routes
        routes = await converter.calculate_conversion_routes('USD', 'PHP', 2500.0)

        assert len(routes) > 0

        # Step 2: Set payment preferences
        preferences = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE,
            compliance_required=True
        )

        # Step 3: Optimize route selection
        optimized_result = optimizer.optimize_settlement_route(
            routes,
            preferences,
            2500.0,
            'USD-PHP'
        )

        assert optimized_result is not None

        # Step 4: Perform compliance check
        compliance_result = compliance_checker.perform_comprehensive_compliance_check(
            test_customer,
            test_counterparty,
            2500.0,
            'USD',
            'PHP',
            'family_support'
        )

        assert compliance_result is not None
        assert compliance_result.transaction_id is not None

        # Step 5: Verify workflow results
        assert optimized_result.route.from_currency == 'USD'
        assert optimized_result.route.to_currency == 'PHP'
        assert optimized_result.route.amount == 2500.0
        assert compliance_result.overall_status is not None
        assert compliance_result.risk_level is not None

    @pytest.mark.asyncio
    async def test_multiple_corridor_analysis(self, platform_components):
        """Test analysis of multiple payment corridors"""
        converter = platform_components['converter']

        corridors = [
            ('USD', 'SGD', 10000.0),
            ('USD', 'PHP', 5000.0),
            ('USD', 'INR', 7500.0),
            ('AED', 'INR', 3000.0)
        ]

        results = []

        for from_curr, to_curr, amount in corridors:
            # Get routes for each corridor
            routes = await converter.calculate_conversion_routes(from_curr, to_curr, amount)

            # Get analytics for each corridor
            analytics = await converter.get_corridor_analytics(from_curr, to_curr)

            results.append({
                'corridor': f"{from_curr}-{to_curr}",
                'routes_count': len(routes),
                'analytics': analytics
            })

        # Verify all corridors were analyzed
        assert len(results) == 4

        for result in results:
            assert result['routes_count'] > 0
            assert isinstance(result['analytics'], dict)
            if 'error' not in result['analytics']:
                assert 'corridor' in result['analytics']
                assert 'test_amount' in result['analytics']

    @pytest.mark.asyncio
    async def test_high_volume_transaction_processing(self, platform_components):
        """Test processing of high-volume transactions"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        # Large transaction
        large_amount = 100000.0

        # Get routes for large transaction
        routes = await converter.calculate_conversion_routes('USD', 'EUR', large_amount)

        assert len(routes) > 0

        # Conservative preferences for large transaction
        conservative_preferences = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.CONSERVATIVE,
            compliance_required=True,
            max_acceptable_fee_pct=0.05
        )

        # Optimize for large transaction
        optimized_result = optimizer.optimize_settlement_route(
            routes,
            conservative_preferences,
            large_amount,
            'USD-EUR'
        )

        assert optimized_result is not None
        assert optimized_result.route.amount == large_amount

        # Verify conservative approach was taken
        assert optimized_result.route.confidence_score >= 0.8

    @pytest.mark.asyncio
    async def test_urgent_payment_processing(self, platform_components):
        """Test processing of urgent payments"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        # Get routes for urgent payment
        routes = await converter.calculate_conversion_routes('USD', 'GBP', 15000.0)

        assert len(routes) > 0

        # Urgent preferences
        urgent_preferences = SettlementPreferences(
            urgency=UrgencyLevel.INSTANT,
            risk_tolerance=RiskTolerance.AGGRESSIVE,
            compliance_required=True
        )

        # Optimize for urgent payment
        optimized_result = optimizer.optimize_settlement_route(
            routes,
            urgent_preferences,
            15000.0,
            'USD-GBP'
        )

        assert optimized_result is not None

        # Verify fast settlement was selected
        selected_route = optimized_result.route
        assert 'minute' in selected_route.estimated_time.lower(
        ) or 'second' in selected_route.estimated_time.lower()

    @pytest.mark.asyncio
    async def test_cost_optimization_across_routes(self, platform_components):
        """Test cost optimization across different settlement routes"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        # Get routes for cost optimization
        routes = await converter.calculate_conversion_routes('USD', 'SGD', 20000.0)

        assert len(routes) > 0

        # Cost-focused preferences
        cost_preferences = SettlementPreferences(
            urgency=UrgencyLevel.ECONOMY,
            risk_tolerance=RiskTolerance.MODERATE,
            compliance_required=True
        )

        # Optimize for cost
        optimized_result = optimizer.optimize_settlement_route(
            routes,
            cost_preferences,
            20000.0,
            'USD-SGD'
        )

        assert optimized_result is not None

        # Verify cost-effective route was selected
        selected_route = optimized_result.route
        all_costs = [route.total_cost for route in routes]
        min_cost = min(all_costs)

        # Selected route should be among the lowest cost options
        assert selected_route.total_cost <= min_cost * 1.1  # Within 10% of minimum

    @pytest.mark.asyncio
    async def test_compliance_integration_with_routing(self, platform_components, test_customer, test_counterparty):
        """Test integration of compliance checking with route selection"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']
        compliance_checker = platform_components['compliance_checker']

        # Get routes
        routes = await converter.calculate_conversion_routes('USD', 'INR', 50000.0)

        assert len(routes) > 0

        # High compliance requirements
        compliance_preferences = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.CONSERVATIVE,
            compliance_required=True,
            max_acceptable_fee_pct=0.10
        )

        # Optimize with compliance focus
        optimized_result = optimizer.optimize_settlement_route(
            routes,
            compliance_preferences,
            50000.0,
            'USD-INR'
        )

        # Perform compliance check
        compliance_result = compliance_checker.perform_comprehensive_compliance_check(
            test_customer,
            test_counterparty,
            50000.0,
            'USD',
            'INR',
            'supplier_payment'
        )

        assert optimized_result is not None
        assert compliance_result is not None

        # Verify compliance-friendly route was selected
        selected_route = optimized_result.route
        assert selected_route.confidence_score >= 0.85

        # Verify compliance was properly checked
        assert compliance_result.overall_status is not None
        assert len(compliance_result.regulatory_requirements) > 0

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, platform_components):
        """Test error handling across integrated components"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        # Test with invalid currency pair
        routes = await converter.calculate_conversion_routes('INVALID', 'CURRENCY', 1000.0)

        # Should still return some routes (fallback to mock data)
        assert isinstance(routes, list)

        if len(routes) > 0:
            # Test optimizer with these routes
            preferences = SettlementPreferences(
                urgency=UrgencyLevel.STANDARD,
                risk_tolerance=RiskTolerance.MODERATE
            )

            try:
                result = optimizer.optimize_settlement_route(
                    routes,
                    preferences,
                    1000.0,
                    'INVALID-CURRENCY'
                )
                assert result is not None
            except Exception as e:
                # Should handle errors gracefully
                assert isinstance(e, (ValueError, RuntimeError))

    @pytest.mark.asyncio
    async def test_concurrent_processing(self, platform_components):
        """Test concurrent processing of multiple payment requests"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        # Create multiple concurrent requests
        tasks = []

        for i in range(5):
            task = asyncio.create_task(
                self._process_payment_request(
                    converter,
                    optimizer,
                    'USD',
                    'EUR',
                    1000.0 * (i + 1)
                )
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all requests were processed
        assert len(results) == 5

        for result in results:
            if not isinstance(result, Exception):
                assert result is not None
                assert 'optimized_result' in result
                assert 'routes' in result

    async def _process_payment_request(self, converter, optimizer, from_curr, to_curr, amount):
        """Helper method for concurrent payment processing"""
        routes = await converter.calculate_conversion_routes(from_curr, to_curr, amount)

        preferences = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE
        )

        optimized_result = optimizer.optimize_settlement_route(
            routes,
            preferences,
            amount,
            f"{from_curr}-{to_curr}"
        )

        return {
            'routes': routes,
            'optimized_result': optimized_result
        }

    @pytest.mark.asyncio
    async def test_performance_benchmarking(self, platform_components):
        """Test performance benchmarking of the platform"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        start_time = asyncio.get_event_loop().time()

        # Process multiple payment scenarios
        scenarios = [
            ('USD', 'SGD', 5000.0),
            ('USD', 'PHP', 2500.0),
            ('USD', 'INR', 7500.0),
            ('EUR', 'USD', 10000.0),
            ('GBP', 'USD', 8000.0)
        ]

        results = []

        for from_curr, to_curr, amount in scenarios:
            routes = await converter.calculate_conversion_routes(from_curr, to_curr, amount)

            preferences = SettlementPreferences(
                urgency=UrgencyLevel.STANDARD,
                risk_tolerance=RiskTolerance.MODERATE
            )

            optimized_result = optimizer.optimize_settlement_route(
                routes,
                preferences,
                amount,
                f"{from_curr}-{to_curr}"
            )

            results.append(optimized_result)

        end_time = asyncio.get_event_loop().time()
        processing_time = end_time - start_time

        # Performance assertions
        assert len(results) == 5
        assert processing_time < 10.0  # Should complete within 10 seconds

        # Verify all results are valid
        for result in results:
            assert result is not None
            assert result.route is not None
            assert result.selection_reason is not None

    @pytest.mark.asyncio
    async def test_data_consistency_across_components(self, platform_components):
        """Test data consistency across different platform components"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        # Get routes and analytics
        routes = await converter.calculate_conversion_routes('USD', 'SGD', 10000.0)
        analytics = await converter.get_corridor_analytics('USD', 'SGD')

        # Optimize route
        preferences = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE
        )

        optimized_result = optimizer.optimize_settlement_route(
            routes,
            preferences,
            10000.0,
            'USD-SGD'
        )

        # Verify data consistency
        assert optimized_result.route in routes
        assert optimized_result.route.from_currency == 'USD'
        assert optimized_result.route.to_currency == 'SGD'
        assert optimized_result.route.amount == 10000.0

        if 'error' not in analytics:
            assert analytics['corridor'] == 'USD -> SGD'
            assert analytics['test_amount'] == 10000
            assert analytics['routes_available'] == len(routes)

    @pytest.mark.asyncio
    async def test_scalability_stress_test(self, platform_components):
        """Test platform scalability under stress conditions"""
        converter = platform_components['converter']
        optimizer = platform_components['optimizer']

        # Create a large number of concurrent requests
        large_batch_size = 20
        tasks = []

        for i in range(large_batch_size):
            from_curr = 'USD'
            to_curr = ['SGD', 'PHP', 'INR', 'EUR', 'GBP'][i % 5]
            amount = 1000.0 + (i * 100)

            task = asyncio.create_task(
                self._process_payment_request(
                    converter,
                    optimizer,
                    from_curr,
                    to_curr,
                    amount
                )
            )
            tasks.append(task)

        # Process all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify scalability
        assert len(results) == large_batch_size

        success_count = sum(1 for r in results if not isinstance(r, Exception))
        success_rate = success_count / large_batch_size

        assert success_rate >= 0.8  # At least 80% success rate

        # Verify successful results
        for result in results:
            if not isinstance(result, Exception):
                assert result is not None
                assert 'optimized_result' in result
                assert result['optimized_result'].route is not None
