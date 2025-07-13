"""
Unit Tests for Settlement Optimizer Module

Tests all functions in the SettlementOptimizer class including:
- Route optimization
- Preference filtering
- Scoring algorithms
- Business rationale generation
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from settlement_engine.settlement_optimizer import (
    SettlementOptimizer,
    UrgencyLevel,
    RiskTolerance,
    SettlementPreferences,
    OptimizedRoute
)
from settlement_engine.currency_converter import ConversionRoute


class TestSettlementOptimizer:
    """Test suite for SettlementOptimizer class"""

    @pytest.fixture
    def optimizer(self):
        """Create a SettlementOptimizer instance for testing"""
        return SettlementOptimizer()

    @pytest.fixture
    def sample_routes(self):
        """Create sample conversion routes for testing"""
        return [
            ConversionRoute(
                from_currency='USD',
                to_currency='SGD',
                method='traditional',
                rate=1.34,
                fee_percentage=0.025,
                fixed_fee=25.0,
                estimated_time='2-3 days',
                total_cost=50.0,
                final_amount=1315.0,
                confidence_score=0.95
            ),
            ConversionRoute(
                from_currency='USD',
                to_currency='SGD',
                method='stablecoin_usdc',
                rate=1.34,
                fee_percentage=0.001,
                fixed_fee=2.5,
                estimated_time='5-10 minutes',
                total_cost=3.5,
                final_amount=1337.0,
                confidence_score=0.88
            ),
            ConversionRoute(
                from_currency='USD',
                to_currency='SGD',
                method='stablecoin_usdt',
                rate=1.34,
                fee_percentage=0.0015,
                fixed_fee=1.8,
                estimated_time='3-8 minutes',
                total_cost=3.3,
                final_amount=1337.2,
                confidence_score=0.89
            )
        ]

    @pytest.fixture
    def standard_preferences(self):
        """Create standard settlement preferences for testing"""
        return SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE,
            max_acceptable_fee_pct=0.05,
            compliance_required=True,
            min_confidence_score=0.7
        )

    def test_initialization(self, optimizer):
        """Test SettlementOptimizer initialization"""
        assert optimizer is not None
        assert hasattr(optimizer, 'urgency_requirements')
        assert hasattr(optimizer, 'reliability_scores')
        assert hasattr(optimizer, 'compliance_support')

        # Test urgency requirements
        assert UrgencyLevel.INSTANT in optimizer.urgency_requirements
        assert UrgencyLevel.STANDARD in optimizer.urgency_requirements
        assert optimizer.urgency_requirements[UrgencyLevel.INSTANT] == 1
        assert optimizer.urgency_requirements[UrgencyLevel.STANDARD] == 120

    def test_urgency_level_enum(self):
        """Test UrgencyLevel enum values"""
        assert UrgencyLevel.INSTANT.value == "instant"
        assert UrgencyLevel.SAME_DAY.value == "same_day"
        assert UrgencyLevel.NEXT_DAY.value == "next_day"
        assert UrgencyLevel.STANDARD.value == "standard"
        assert UrgencyLevel.ECONOMY.value == "economy"

    def test_risk_tolerance_enum(self):
        """Test RiskTolerance enum values"""
        assert RiskTolerance.CONSERVATIVE.value == "conservative"
        assert RiskTolerance.MODERATE.value == "moderate"
        assert RiskTolerance.AGGRESSIVE.value == "aggressive"

    def test_settlement_preferences_dataclass(self):
        """Test SettlementPreferences dataclass"""
        prefs = SettlementPreferences(
            urgency=UrgencyLevel.INSTANT,
            risk_tolerance=RiskTolerance.AGGRESSIVE,
            max_acceptable_fee_pct=0.02,
            compliance_required=False,
            preferred_method='stablecoin_usdc',
            min_confidence_score=0.8
        )

        assert prefs.urgency == UrgencyLevel.INSTANT
        assert prefs.risk_tolerance == RiskTolerance.AGGRESSIVE
        assert prefs.max_acceptable_fee_pct == 0.02
        assert prefs.compliance_required == False
        assert prefs.preferred_method == 'stablecoin_usdc'
        assert prefs.min_confidence_score == 0.8

    def test_reliability_scores_configuration(self, optimizer):
        """Test reliability scores configuration"""
        assert 'traditional' in optimizer.reliability_scores
        assert 'stablecoin_usdc' in optimizer.reliability_scores
        assert 'stablecoin_usdt' in optimizer.reliability_scores
        assert 'direct_crypto' in optimizer.reliability_scores

        # Traditional should have highest reliability
        assert optimizer.reliability_scores['traditional'] == 0.98
        assert optimizer.reliability_scores['stablecoin_usdc'] == 0.92
        assert optimizer.reliability_scores['direct_crypto'] == 0.85

    def test_compliance_support_configuration(self, optimizer):
        """Test compliance support configuration"""
        assert 'traditional' in optimizer.compliance_support
        assert 'stablecoin_usdc' in optimizer.compliance_support
        assert 'direct_crypto' in optimizer.compliance_support

        # Traditional should support all compliance features
        traditional_compliance = optimizer.compliance_support['traditional']
        assert traditional_compliance['kyc'] == True
        assert traditional_compliance['aml'] == True
        assert traditional_compliance['reporting'] == True

        # Direct crypto should support minimal compliance
        crypto_compliance = optimizer.compliance_support['direct_crypto']
        assert crypto_compliance['kyc'] == False
        assert crypto_compliance['aml'] == False
        assert crypto_compliance['reporting'] == False

    def test_meets_risk_tolerance_conservative(self, optimizer):
        """Test risk tolerance checking - conservative"""
        traditional_route = Mock()
        traditional_route.method = 'traditional'

        stablecoin_route = Mock()
        stablecoin_route.method = 'stablecoin_usdc'

        crypto_route = Mock()
        crypto_route.method = 'direct_crypto'

        assert optimizer._meets_risk_tolerance(
            traditional_route, RiskTolerance.CONSERVATIVE) == True
        assert optimizer._meets_risk_tolerance(
            stablecoin_route, RiskTolerance.CONSERVATIVE) == False
        assert optimizer._meets_risk_tolerance(
            crypto_route, RiskTolerance.CONSERVATIVE) == False

    def test_meets_risk_tolerance_moderate(self, optimizer):
        """Test risk tolerance checking - moderate"""
        traditional_route = Mock()
        traditional_route.method = 'traditional'

        stablecoin_route = Mock()
        stablecoin_route.method = 'stablecoin_usdc'

        crypto_route = Mock()
        crypto_route.method = 'direct_crypto'

        assert optimizer._meets_risk_tolerance(
            traditional_route, RiskTolerance.MODERATE) == True
        assert optimizer._meets_risk_tolerance(
            stablecoin_route, RiskTolerance.MODERATE) == True
        assert optimizer._meets_risk_tolerance(
            crypto_route, RiskTolerance.MODERATE) == False

    def test_meets_risk_tolerance_aggressive(self, optimizer):
        """Test risk tolerance checking - aggressive"""
        traditional_route = Mock()
        traditional_route.method = 'traditional'

        stablecoin_route = Mock()
        stablecoin_route.method = 'stablecoin_usdc'

        crypto_route = Mock()
        crypto_route.method = 'direct_crypto'

        assert optimizer._meets_risk_tolerance(
            traditional_route, RiskTolerance.AGGRESSIVE) == True
        assert optimizer._meets_risk_tolerance(
            stablecoin_route, RiskTolerance.AGGRESSIVE) == True
        assert optimizer._meets_risk_tolerance(
            crypto_route, RiskTolerance.AGGRESSIVE) == True

    def test_meets_urgency_instant(self, optimizer):
        """Test urgency requirements checking - instant"""
        fast_route = Mock()
        fast_route.estimated_time = '30 seconds'

        medium_route = Mock()
        medium_route.estimated_time = '5 minutes'

        slow_route = Mock()
        slow_route.estimated_time = '2-3 days'

        assert optimizer._meets_urgency(
            fast_route, UrgencyLevel.INSTANT) == True
        assert optimizer._meets_urgency(
            medium_route, UrgencyLevel.INSTANT) == True
        assert optimizer._meets_urgency(
            slow_route, UrgencyLevel.INSTANT) == False

    def test_meets_urgency_standard(self, optimizer):
        """Test urgency requirements checking - standard"""
        fast_route = Mock()
        fast_route.estimated_time = '30 seconds'

        medium_route = Mock()
        medium_route.estimated_time = '1-2 days'

        slow_route = Mock()
        slow_route.estimated_time = '3-4 days'

        assert optimizer._meets_urgency(
            fast_route, UrgencyLevel.STANDARD) == True
        assert optimizer._meets_urgency(
            medium_route, UrgencyLevel.STANDARD) == True
        assert optimizer._meets_urgency(
            slow_route, UrgencyLevel.STANDARD) == True

    def test_filter_viable_routes_confidence_score(self, optimizer, sample_routes):
        """Test route filtering by confidence score"""
        high_confidence_prefs = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.AGGRESSIVE,
            min_confidence_score=0.9
        )

        viable_routes = optimizer._filter_viable_routes(
            sample_routes, high_confidence_prefs)

        # Only traditional route should pass (confidence 0.95)
        assert len(viable_routes) == 1
        assert viable_routes[0].method == 'traditional'
        assert viable_routes[0].confidence_score >= 0.9

    def test_filter_viable_routes_fee_limits(self, optimizer, sample_routes):
        """Test route filtering by fee limits"""
        low_fee_prefs = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.AGGRESSIVE,
            max_acceptable_fee_pct=0.01
        )

        viable_routes = optimizer._filter_viable_routes(
            sample_routes, low_fee_prefs)

        # Only stablecoin routes should pass (fee < 1%)
        assert len(viable_routes) == 2
        viable_methods = [route.method for route in viable_routes]
        assert 'stablecoin_usdc' in viable_methods
        assert 'stablecoin_usdt' in viable_methods
        assert 'traditional' not in viable_methods

    def test_filter_viable_routes_risk_tolerance(self, optimizer, sample_routes):
        """Test route filtering by risk tolerance"""
        conservative_prefs = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.CONSERVATIVE
        )

        viable_routes = optimizer._filter_viable_routes(
            sample_routes, conservative_prefs)

        # Only traditional route should pass
        assert len(viable_routes) == 1
        assert viable_routes[0].method == 'traditional'

    def test_filter_viable_routes_compliance_required(self, optimizer, sample_routes):
        """Test route filtering by compliance requirements"""
        compliance_prefs = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.AGGRESSIVE,
            compliance_required=True
        )

        viable_routes = optimizer._filter_viable_routes(
            sample_routes, compliance_prefs)

        # All routes should pass as they support basic compliance
        assert len(viable_routes) == 3

    def test_calculate_cost_score(self, optimizer):
        """Test cost scoring algorithm"""
        # Test low cost route (should get high score)
        low_cost_route = Mock()
        low_cost_route.total_cost = 5.0

        score = optimizer._calculate_cost_score(low_cost_route, 1000.0)
        assert score >= 80  # Should get high score

        # Test high cost route (should get low score)
        high_cost_route = Mock()
        high_cost_route.total_cost = 100.0

        score = optimizer._calculate_cost_score(high_cost_route, 1000.0)
        assert score <= 40  # Should get low score

    def test_calculate_speed_score(self, optimizer):
        """Test speed scoring algorithm"""
        # Test fast route
        fast_route = Mock()
        fast_route.estimated_time = '30 seconds'

        score = optimizer._calculate_speed_score(
            fast_route, UrgencyLevel.STANDARD)
        assert score >= 80  # Should get high score

        # Test slow route
        slow_route = Mock()
        slow_route.estimated_time = '5 days'

        score = optimizer._calculate_speed_score(
            slow_route, UrgencyLevel.INSTANT)
        assert score <= 60  # Should get low score

    def test_calculate_reliability_score(self, optimizer):
        """Test reliability scoring algorithm"""
        traditional_route = Mock()
        traditional_route.method = 'traditional'

        stablecoin_route = Mock()
        stablecoin_route.method = 'stablecoin_usdc'

        crypto_route = Mock()
        crypto_route.method = 'direct_crypto'

        traditional_score = optimizer._calculate_reliability_score(
            traditional_route)
        stablecoin_score = optimizer._calculate_reliability_score(
            stablecoin_route)
        crypto_score = optimizer._calculate_reliability_score(crypto_route)

        assert traditional_score > stablecoin_score
        assert stablecoin_score > crypto_score
        assert traditional_score == 98.0  # 0.98 * 100

    def test_calculate_compliance_score(self, optimizer):
        """Test compliance scoring algorithm"""
        compliance_prefs = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE,
            compliance_required=True
        )

        no_compliance_prefs = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE,
            compliance_required=False
        )

        traditional_route = Mock()
        traditional_route.method = 'traditional'

        crypto_route = Mock()
        crypto_route.method = 'direct_crypto'

        # With compliance required
        traditional_score = optimizer._calculate_compliance_score(
            traditional_route, compliance_prefs)
        crypto_score = optimizer._calculate_compliance_score(
            crypto_route, compliance_prefs)

        assert traditional_score > crypto_score
        assert traditional_score == 100  # Full compliance
        assert crypto_score == 0  # No compliance

        # With compliance not required
        no_compliance_score = optimizer._calculate_compliance_score(
            crypto_route, no_compliance_prefs)
        assert no_compliance_score == 100  # Should get full score

    def test_calculate_route_score_speed_priority(self, optimizer):
        """Test route scoring with speed priority"""
        fast_route = Mock()
        fast_route.method = 'stablecoin_usdc'
        fast_route.total_cost = 10.0
        fast_route.estimated_time = '5 minutes'
        fast_route.confidence_score = 0.9

        speed_prefs = SettlementPreferences(
            urgency=UrgencyLevel.INSTANT,
            risk_tolerance=RiskTolerance.MODERATE
        )

        score = optimizer._calculate_route_score(
            fast_route, speed_prefs, 1000.0)

        assert isinstance(score, float)
        assert score > 0
        assert score <= 100

    def test_calculate_route_score_cost_priority(self, optimizer):
        """Test route scoring with cost priority"""
        cheap_route = Mock()
        cheap_route.method = 'stablecoin_usdc'
        cheap_route.total_cost = 2.0
        cheap_route.estimated_time = '10 minutes'
        cheap_route.confidence_score = 0.9

        cost_prefs = SettlementPreferences(
            urgency=UrgencyLevel.ECONOMY,
            risk_tolerance=RiskTolerance.MODERATE
        )

        score = optimizer._calculate_route_score(
            cheap_route, cost_prefs, 1000.0)

        assert isinstance(score, float)
        assert score > 0
        assert score <= 100

    def test_relax_preferences(self, optimizer):
        """Test preference relaxation"""
        strict_prefs = SettlementPreferences(
            urgency=UrgencyLevel.INSTANT,
            risk_tolerance=RiskTolerance.CONSERVATIVE,
            max_acceptable_fee_pct=0.01,
            compliance_required=True,
            preferred_method='traditional',
            min_confidence_score=0.95
        )

        relaxed_prefs = optimizer._relax_preferences(strict_prefs)

        assert relaxed_prefs.urgency == strict_prefs.urgency  # Should remain same
        assert relaxed_prefs.risk_tolerance == strict_prefs.risk_tolerance  # Should remain same
        assert relaxed_prefs.max_acceptable_fee_pct > strict_prefs.max_acceptable_fee_pct
        assert relaxed_prefs.preferred_method is None  # Should be removed
        assert relaxed_prefs.min_confidence_score < strict_prefs.min_confidence_score

    def test_optimize_settlement_route_success(self, optimizer, sample_routes, standard_preferences):
        """Test successful settlement route optimization"""
        result = optimizer.optimize_settlement_route(
            sample_routes,
            standard_preferences,
            1000.0,
            'USD-SGD'
        )

        assert isinstance(result, OptimizedRoute)
        assert result.route in sample_routes
        assert isinstance(result.selection_reason, str)
        assert isinstance(result.cost_vs_alternatives, dict)
        assert isinstance(result.risk_assessment, dict)
        assert isinstance(result.compliance_status, str)
        assert isinstance(result.business_impact, dict)

    def test_optimize_settlement_route_empty_routes(self, optimizer, standard_preferences):
        """Test optimization with empty routes list"""
        with pytest.raises(ValueError, match="No routes available for optimization"):
            optimizer.optimize_settlement_route(
                [],
                standard_preferences,
                1000.0,
                'USD-SGD'
            )

    def test_optimize_settlement_route_no_viable_routes(self, optimizer, sample_routes):
        """Test optimization with no viable routes"""
        impossible_prefs = SettlementPreferences(
            urgency=UrgencyLevel.INSTANT,
            risk_tolerance=RiskTolerance.CONSERVATIVE,
            max_acceptable_fee_pct=0.001,  # Impossibly low
            compliance_required=True,
            min_confidence_score=0.99  # Impossibly high
        )

        with pytest.raises(ValueError, match="No viable routes found"):
            optimizer.optimize_settlement_route(
                sample_routes,
                impossible_prefs,
                1000.0,
                'USD-SGD'
            )

    def test_optimize_settlement_route_relaxed_constraints(self, optimizer, sample_routes):
        """Test optimization with constraint relaxation"""
        # Create slightly impossible preferences that can be relaxed
        tight_prefs = SettlementPreferences(
            urgency=UrgencyLevel.STANDARD,
            risk_tolerance=RiskTolerance.MODERATE,
            max_acceptable_fee_pct=0.005,  # Very low but relaxable
            compliance_required=True,
            min_confidence_score=0.92  # High but relaxable
        )

        result = optimizer.optimize_settlement_route(
            sample_routes,
            tight_prefs,
            1000.0,
            'USD-SGD'
        )

        # Should succeed with relaxed constraints
        assert isinstance(result, OptimizedRoute)
        assert result.route in sample_routes

    def test_generate_optimization_result_components(self, optimizer, sample_routes, standard_preferences):
        """Test optimization result generation components"""
        # Choose the best route manually
        best_route = min(sample_routes, key=lambda r: r.total_cost)

        result = optimizer._generate_optimization_result(
            best_route,
            sample_routes,
            standard_preferences,
            1000.0,
            'USD-SGD'
        )

        assert isinstance(result, OptimizedRoute)
        assert result.route == best_route
        assert 'lowest cost' in result.selection_reason.lower()
        assert len(result.cost_vs_alternatives) > 0
        assert 'counterparty_risk' in result.risk_assessment
        assert 'operational_risk' in result.risk_assessment
        assert 'compliance_risk' in result.risk_assessment
        assert 'estimated_annual_savings' in result.business_impact

    def test_generate_corridor_recommendations(self, optimizer):
        """Test corridor recommendation generation"""
        high_savings_analytics = {
            'max_savings_pct': 85.0,
            'routes_available': 3,
            'annual_savings_10m': 500000
        }

        recommendations = optimizer.generate_corridor_recommendations(
            high_savings_analytics)

        assert isinstance(recommendations, dict)
        assert 'cost_optimization' in recommendations
        assert 'route_diversification' in recommendations
        assert 'business_case' in recommendations
        assert '85.0%' in recommendations['cost_optimization']
        assert '$500,000' in recommendations['business_case']

    def test_generate_corridor_recommendations_low_opportunity(self, optimizer):
        """Test corridor recommendations for low opportunity corridors"""
        low_opportunity_analytics = {
            'max_savings_pct': 15.0,
            'routes_available': 1,
            'annual_savings_10m': 50000
        }

        recommendations = optimizer.generate_corridor_recommendations(
            low_opportunity_analytics)

        assert isinstance(recommendations, dict)
        # Should have fewer recommendations for low opportunity
        assert len(recommendations) <= 2

    def test_optimized_route_dataclass(self):
        """Test OptimizedRoute dataclass functionality"""
        sample_route = Mock()

        optimized_route = OptimizedRoute(
            route=sample_route,
            selection_reason='Test reason',
            cost_vs_alternatives={'traditional': 50.0},
            risk_assessment={'counterparty_risk': 'low'},
            compliance_status='full compliance',
            business_impact={'estimated_annual_savings': 10000}
        )

        assert optimized_route.route == sample_route
        assert optimized_route.selection_reason == 'Test reason'
        assert optimized_route.cost_vs_alternatives == {'traditional': 50.0}
        assert optimized_route.risk_assessment == {'counterparty_risk': 'low'}
        assert optimized_route.compliance_status == 'full compliance'
        assert optimized_route.business_impact == {
            'estimated_annual_savings': 10000}
