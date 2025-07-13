"""
Settlement Route Optimizer

Intelligent routing engine that selects optimal settlement paths based on:
- Cost efficiency (fees, exchange rates)
- Settlement speed (urgency requirements)
- Regulatory compliance (KYC/AML requirements)
- Liquidity availability (real-time capacity)
- Risk tolerance (counterparty, operational risk)
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class UrgencyLevel(Enum):
    INSTANT = "instant"        # < 1 hour
    SAME_DAY = "same_day"      # < 24 hours
    NEXT_DAY = "next_day"      # 1-2 days
    STANDARD = "standard"      # 2-5 days
    ECONOMY = "economy"        # 5+ days, lowest cost


class RiskTolerance(Enum):
    CONSERVATIVE = "conservative"  # Traditional rails only
    MODERATE = "moderate"         # Stablecoins + traditional
    AGGRESSIVE = "aggressive"     # All routes including crypto


@dataclass
class SettlementPreferences:
    """Customer settlement preferences and constraints"""
    urgency: UrgencyLevel
    risk_tolerance: RiskTolerance
    max_acceptable_fee_pct: float = 0.05  # 5% max fee
    compliance_required: bool = True
    preferred_method: Optional[str] = None
    min_confidence_score: float = 0.7


@dataclass
class OptimizedRoute:
    """Optimized settlement route with business rationale"""
    route: 'ConversionRoute'
    selection_reason: str
    cost_vs_alternatives: Dict[str, float]
    risk_assessment: Dict[str, str]
    compliance_status: str
    business_impact: Dict[str, float]


class SettlementOptimizer:
    """
    Advanced settlement optimization engine

    Evaluates all available routes and selects optimal path based on:
    - Customer preferences (speed vs cost trade-offs)
    - Regulatory requirements (compliance obligations)
    - Market conditions (liquidity, volatility)
    - Business objectives (profit margins, risk limits)
    """

    def __init__(self):
        # Urgency-based time requirements (in hours)
        self.urgency_requirements = {
            UrgencyLevel.INSTANT: 1,
            UrgencyLevel.SAME_DAY: 24,
            UrgencyLevel.NEXT_DAY: 48,
            UrgencyLevel.STANDARD: 120,  # 5 days
            UrgencyLevel.ECONOMY: 240    # 10 days
        }

        # Method reliability scores (0-1)
        self.reliability_scores = {
            'traditional': 0.98,
            'stablecoin_usdc': 0.92,
            'stablecoin_usdt': 0.89,
            'direct_crypto': 0.85
        }

        # Regulatory compliance by method
        self.compliance_support = {
            'traditional': {'kyc': True, 'aml': True, 'reporting': True},
            'stablecoin_usdc': {'kyc': True, 'aml': True, 'reporting': True},
            'stablecoin_usdt': {'kyc': True, 'aml': True, 'reporting': False},
            'direct_crypto': {'kyc': False, 'aml': False, 'reporting': False}
        }

    def optimize_settlement_route(
        self,
        routes: List['ConversionRoute'],
        preferences: SettlementPreferences,
        amount: float,
        corridor: str
    ) -> OptimizedRoute:
        """
        Select optimal settlement route based on preferences and constraints

        Returns the best route with detailed business rationale
        """
        if not routes:
            raise ValueError("No routes available for optimization")

        # Filter routes by preferences
        viable_routes = self._filter_viable_routes(routes, preferences)

        if not viable_routes:
            # Relax constraints and try again
            relaxed_preferences = self._relax_preferences(preferences)
            viable_routes = self._filter_viable_routes(
                routes, relaxed_preferences)

        if not viable_routes:
            raise ValueError(
                "No viable routes found even with relaxed constraints")

        # Score each route
        scored_routes = []
        for route in viable_routes:
            score = self._calculate_route_score(route, preferences, amount)
            scored_routes.append((route, score))

        # Select highest scoring route
        best_route, best_score = max(scored_routes, key=lambda x: x[1])

        # Generate business rationale
        return self._generate_optimization_result(
            best_route, routes, preferences, amount, corridor
        )

    def _filter_viable_routes(
        self,
        routes: List['ConversionRoute'],
        preferences: SettlementPreferences
    ) -> List['ConversionRoute']:
        """Filter routes based on hard constraints"""
        viable = []

        for route in routes:
            # Check confidence score
            if route.confidence_score < preferences.min_confidence_score:
                continue

            # Check fee limits
            if route.fee_percentage > preferences.max_acceptable_fee_pct:
                continue

            # Check risk tolerance
            if not self._meets_risk_tolerance(route, preferences.risk_tolerance):
                continue

            # Check compliance requirements
            if preferences.compliance_required:
                compliance = self.compliance_support.get(route.method, {})
                if not compliance.get('kyc', False) or not compliance.get('aml', False):
                    continue

            # Check urgency requirements
            if not self._meets_urgency(route, preferences.urgency):
                continue

            viable.append(route)

        return viable

    def _meets_risk_tolerance(self, route: 'ConversionRoute', risk_tolerance: RiskTolerance) -> bool:
        """Check if route meets risk tolerance requirements"""
        method = route.method

        if risk_tolerance == RiskTolerance.CONSERVATIVE:
            return method == 'traditional'
        elif risk_tolerance == RiskTolerance.MODERATE:
            return method in ['traditional', 'stablecoin_usdc', 'stablecoin_usdt']
        else:  # AGGRESSIVE
            return True  # All methods acceptable

    def _meets_urgency(self, route: 'ConversionRoute', urgency: UrgencyLevel) -> bool:
        """Check if route meets urgency requirements"""
        required_hours = self.urgency_requirements[urgency]

        # Parse estimated time to hours (simplified)
        time_str = route.estimated_time.lower()

        if 'second' in time_str or 'minute' in time_str:
            return True  # Faster than any requirement
        elif 'hour' in time_str:
            return True  # Assume < 24 hours
        elif 'day' in time_str:
            if '1' in time_str or '2' in time_str:
                return required_hours >= 24
            elif '3' in time_str or '4' in time_str:
                return required_hours >= 72
            else:
                return required_hours >= 120

        return True  # Default to acceptable

    def _calculate_route_score(
        self,
        route: 'ConversionRoute',
        preferences: SettlementPreferences,
        amount: float
    ) -> float:
        """Calculate composite score for route optimization"""

        # Base scoring components (0-100 each)
        cost_score = self._calculate_cost_score(route, amount)
        speed_score = self._calculate_speed_score(route, preferences.urgency)
        reliability_score = self._calculate_reliability_score(route)
        compliance_score = self._calculate_compliance_score(route, preferences)

        # Weighted scoring based on urgency
        if preferences.urgency in [UrgencyLevel.INSTANT, UrgencyLevel.SAME_DAY]:
            # Speed prioritized
            weights = {'cost': 0.2, 'speed': 0.5,
                       'reliability': 0.2, 'compliance': 0.1}
        elif preferences.urgency == UrgencyLevel.ECONOMY:
            # Cost prioritized
            weights = {'cost': 0.6, 'speed': 0.1,
                       'reliability': 0.2, 'compliance': 0.1}
        else:
            # Balanced approach
            weights = {'cost': 0.3, 'speed': 0.3,
                       'reliability': 0.25, 'compliance': 0.15}

        total_score = (
            cost_score * weights['cost'] +
            speed_score * weights['speed'] +
            reliability_score * weights['reliability'] +
            compliance_score * weights['compliance']
        )

        return total_score

    def _calculate_cost_score(self, route: 'ConversionRoute', amount: float) -> float:
        """Score based on total cost efficiency (0-100)"""
        # Calculate total cost percentage
        total_cost_pct = (route.total_cost / amount) * 100

        # Score inversely related to cost (lower cost = higher score)
        if total_cost_pct <= 0.1:  # <= 0.1%
            return 100
        elif total_cost_pct <= 0.5:  # <= 0.5%
            return 90
        elif total_cost_pct <= 1.0:  # <= 1.0%
            return 80
        elif total_cost_pct <= 2.0:  # <= 2.0%
            return 60
        elif total_cost_pct <= 5.0:  # <= 5.0%
            return 40
        else:
            return 20

    def _calculate_speed_score(self, route: 'ConversionRoute', urgency: UrgencyLevel) -> float:
        """Score based on settlement speed (0-100)"""
        time_str = route.estimated_time.lower()

        # Convert to estimated hours
        if 'second' in time_str:
            estimated_hours = 0.017  # 1 minute
        elif 'minute' in time_str:
            estimated_hours = 0.17   # 10 minutes average
        elif '1' in time_str and 'hour' in time_str:
            estimated_hours = 1
        elif 'hour' in time_str:
            estimated_hours = 12     # Half day average
        elif '1' in time_str and 'day' in time_str:
            estimated_hours = 24
        elif '2' in time_str and 'day' in time_str:
            estimated_hours = 48
        elif '3' in time_str and 'day' in time_str:
            estimated_hours = 72
        else:
            estimated_hours = 120    # 5 days default

        required_hours = self.urgency_requirements[urgency]

        if estimated_hours <= required_hours * 0.1:  # Much faster than needed
            return 100
        elif estimated_hours <= required_hours * 0.5:  # Faster than needed
            return 90
        elif estimated_hours <= required_hours:  # Meets requirement
            return 80
        elif estimated_hours <= required_hours * 2:  # Slightly slower
            return 60
        else:  # Much slower
            return 30

    def _calculate_reliability_score(self, route: 'ConversionRoute') -> float:
        """Score based on method reliability (0-100)"""
        reliability = self.reliability_scores.get(route.method, 0.8)
        return reliability * 100

    def _calculate_compliance_score(self, route: 'ConversionRoute', preferences: SettlementPreferences) -> float:
        """Score based on compliance capabilities (0-100)"""
        if not preferences.compliance_required:
            return 100  # Compliance not needed

        compliance = self.compliance_support.get(route.method, {})

        score = 0
        if compliance.get('kyc', False):
            score += 40
        if compliance.get('aml', False):
            score += 40
        if compliance.get('reporting', False):
            score += 20

        return score

    def _relax_preferences(self, preferences: SettlementPreferences) -> SettlementPreferences:
        """Relax constraints to find viable routes"""
        relaxed = SettlementPreferences(
            urgency=preferences.urgency,
            risk_tolerance=preferences.risk_tolerance,
            max_acceptable_fee_pct=preferences.max_acceptable_fee_pct *
            1.5,  # Increase fee tolerance
            compliance_required=preferences.compliance_required,
            preferred_method=None,  # Remove method preference
            # Lower confidence requirement
            min_confidence_score=max(
                0.5, preferences.min_confidence_score - 0.2)
        )
        return relaxed

    def _generate_optimization_result(
        self,
        selected_route: 'ConversionRoute',
        all_routes: List['ConversionRoute'],
        preferences: SettlementPreferences,
        amount: float,
        corridor: str
    ) -> OptimizedRoute:
        """Generate comprehensive optimization result with business rationale"""

        # Calculate cost comparison
        cost_comparison = {}
        for route in all_routes:
            if route.method != selected_route.method:
                cost_diff = route.total_cost - selected_route.total_cost
                cost_comparison[route.method] = cost_diff

        # Generate selection reason
        reasons = []
        if selected_route.total_cost == min(r.total_cost for r in all_routes):
            reasons.append("lowest cost option")
        if 'stablecoin' in selected_route.method and any('traditional' in r.method for r in all_routes):
            traditional_cost = next(
                r.total_cost for r in all_routes if 'traditional' in r.method)
            savings_pct = (
                (traditional_cost - selected_route.total_cost) / traditional_cost) * 100
            reasons.append(f"{savings_pct:.1f}% cost savings vs traditional")
        if 'minute' in selected_route.estimated_time or 'second' in selected_route.estimated_time:
            reasons.append("near-instant settlement")

        selection_reason = "; ".join(
            reasons) if reasons else "best overall score for requirements"

        # Risk assessment
        risk_assessment = {
            "counterparty_risk": "low" if selected_route.confidence_score > 0.9 else "moderate",
            "operational_risk": "low" if 'traditional' in selected_route.method else "moderate",
            "compliance_risk": "low" if self.compliance_support.get(selected_route.method, {}).get('reporting') else "moderate"
        }

        # Compliance status
        compliance = self.compliance_support.get(selected_route.method, {})
        compliance_status = "full compliance" if all(
            compliance.values()) else "partial compliance"

        # Business impact
        annual_volume_estimate = amount * 12  # Monthly to annual
        annual_cost_savings = 0
        if cost_comparison:
            traditional_annual_cost = min(cost_comparison.values()) * 12
            annual_cost_savings = max(0, traditional_annual_cost)

        business_impact = {
            "estimated_annual_savings": annual_cost_savings,
            "cost_as_percentage": (selected_route.total_cost / amount) * 100,
            "roi_improvement": annual_cost_savings / max(1, selected_route.total_cost) if annual_cost_savings > 0 else 0
        }

        return OptimizedRoute(
            route=selected_route,
            selection_reason=selection_reason,
            cost_vs_alternatives=cost_comparison,
            risk_assessment=risk_assessment,
            compliance_status=compliance_status,
            business_impact=business_impact
        )

    def generate_corridor_recommendations(self, corridor_analytics: Dict) -> Dict[str, str]:
        """Generate business recommendations for a corridor"""

        recommendations = {}

        if corridor_analytics.get("max_savings_pct", 0) > 50:
            recommendations["cost_optimization"] = (
                f"High savings potential: {corridor_analytics['max_savings_pct']}% cost reduction available. "
                "Consider stablecoin settlement for large volumes."
            )

        if corridor_analytics.get("routes_available", 0) > 2:
            recommendations["route_diversification"] = (
                "Multiple settlement options available. Implement dynamic routing "
                "based on amount thresholds and urgency requirements."
            )

        annual_savings = corridor_analytics.get("annual_savings_10m", 0)
        if annual_savings > 100000:  # $100k+ savings potential
            recommendations["business_case"] = (
                f"Strong business case: ${annual_savings:,.0f} annual savings potential "
                f"on $10M volume. ROI justifies technology investment."
            )

        return recommendations
