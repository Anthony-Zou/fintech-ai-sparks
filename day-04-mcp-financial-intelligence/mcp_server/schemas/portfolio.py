"""
Portfolio Schemas

Pydantic models for portfolio optimization and risk management data validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class OptimizationMethod(str, Enum):
    """Portfolio optimization methods."""
    MAX_SHARPE = "max_sharpe"
    MIN_VOLATILITY = "min_volatility"
    RISK_PARITY = "risk_parity"
    BLACK_LITTERMAN = "black_litterman"


class RiskTolerance(str, Enum):
    """Risk tolerance levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class MarketScenario(str, Enum):
    """Market scenarios for stress testing."""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    HIGH_VOLATILITY = "high_volatility"
    RECESSION = "recession"
    MARKET_CRASH = "market_crash"
    RECOVERY = "recovery"


class PortfolioRequest(BaseModel):
    """Request model for portfolio operations."""
    symbols: List[str] = Field(..., description="Portfolio assets")
    weights: Optional[List[float]] = Field(
        None, description="Portfolio weights (must sum to 1)")
    portfolio_value: float = Field(
        default=100000, description="Portfolio value")


class OptimizationConstraints(BaseModel):
    """Portfolio optimization constraints."""
    max_weight: Optional[float] = Field(
        None, ge=0, le=1, description="Maximum weight per asset")
    min_weight: Optional[float] = Field(
        None, ge=0, le=1, description="Minimum weight per asset")
    sector_constraints: Optional[Dict[str, float]] = Field(
        None, description="Sector weight constraints")


class OptimizationRequest(BaseModel):
    """Request model for portfolio optimization."""
    symbols: List[str] = Field(..., description="Portfolio assets")
    optimization_method: OptimizationMethod = Field(
        default=OptimizationMethod.MAX_SHARPE,
        description="Optimization method"
    )
    risk_free_rate: float = Field(
        default=0.02, ge=0, le=0.1, description="Risk-free rate")
    constraints: Optional[OptimizationConstraints] = Field(
        None, description="Optimization constraints")
    views: Optional[Dict[str, float]] = Field(
        None, description="Expected returns views for Black-Litterman")


class PortfolioMetrics(BaseModel):
    """Portfolio performance metrics."""
    expected_return: float = Field(..., description="Expected annual return")
    volatility: float = Field(..., description="Annual volatility")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: Optional[float] = Field(None, description="Maximum drawdown")


class OptimizationResponse(BaseModel):
    """Response model for portfolio optimization."""
    optimization_timestamp: datetime = Field(...,
                                             description="When optimization was performed")
    method: str = Field(..., description="Optimization method used")
    symbols: List[str] = Field(..., description="Portfolio assets")
    optimal_weights: Dict[str,
                          float] = Field(..., description="Optimal weights per asset")
    portfolio_metrics: PortfolioMetrics = Field(
        ..., description="Portfolio performance metrics")
    risk_free_rate: float = Field(..., description="Risk-free rate used")
    constraints_applied: Dict[str,
                              Any] = Field(..., description="Constraints that were applied")
    optimization_status: str = Field(..., description="Optimization status")
    views_incorporated: Optional[Dict[str, float]] = Field(
        None, description="Views used in Black-Litterman")


class RiskMetricsRequest(BaseModel):
    """Request model for risk metrics calculation."""
    symbols: List[str] = Field(..., description="Portfolio assets")
    weights: List[float] = Field(..., description="Portfolio weights")
    confidence_levels: List[float] = Field(
        default=[0.95, 0.99], description="Confidence levels for VaR")
    portfolio_value: float = Field(
        default=100000, description="Portfolio value")


class VarMetrics(BaseModel):
    """Value at Risk metrics."""
    daily: float = Field(..., description="Daily VaR")
    weekly: float = Field(..., description="Weekly VaR")
    monthly: float = Field(..., description="Monthly VaR")
    annual: float = Field(..., description="Annual VaR")


class VolatilityMetrics(BaseModel):
    """Volatility-related metrics."""
    daily_volatility: float = Field(..., description="Daily volatility")
    annual_volatility: float = Field(..., description="Annual volatility")
    downside_deviation: Optional[float] = Field(
        None, description="Downside deviation")


class PerformanceRatios(BaseModel):
    """Performance ratio metrics."""
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    sortino_ratio: float = Field(..., description="Sortino ratio")
    treynor_ratio: Optional[float] = Field(None, description="Treynor ratio")
    information_ratio: Optional[float] = Field(
        None, description="Information ratio")
    calmar_ratio: Optional[float] = Field(None, description="Calmar ratio")


class DrawdownAnalysis(BaseModel):
    """Drawdown analysis metrics."""
    max_drawdown_percent: float = Field(...,
                                        description="Maximum drawdown percentage")
    average_drawdown: Optional[float] = Field(
        None, description="Average drawdown")
    drawdown_duration_days: int = Field(...,
                                        description="Maximum drawdown duration in days")
    recovery_duration_days: Optional[int] = Field(
        None, description="Recovery duration in days")


class VolatilityDecomposition(BaseModel):
    """Volatility decomposition by asset."""
    asset: str = Field(..., description="Asset name")
    weight: float = Field(..., description="Portfolio weight")
    risk_contribution: float = Field(..., description="Risk contribution")
    risk_contribution_pct: float = Field(...,
                                         description="Risk contribution percentage")


class RiskMetrics(BaseModel):
    """Comprehensive risk metrics."""
    value_at_risk: Dict[str, VarMetrics] = Field(
        ..., description="VaR at different confidence levels")
    expected_shortfall: Dict[str, VarMetrics] = Field(
        ..., description="Expected Shortfall metrics")
    volatility_metrics: VolatilityMetrics = Field(
        ..., description="Volatility metrics")
    performance_ratios: PerformanceRatios = Field(
        ..., description="Performance ratios")
    drawdown_analysis: DrawdownAnalysis = Field(
        ..., description="Drawdown analysis")


class RiskMetricsResponse(BaseModel):
    """Response model for risk metrics calculation."""
    calculation_timestamp: datetime = Field(...,
                                            description="When calculation was performed")
    portfolio_composition: Dict[str,
                                float] = Field(..., description="Portfolio composition")
    portfolio_value: float = Field(..., description="Portfolio value")
    risk_metrics: RiskMetrics = Field(...,
                                      description="Comprehensive risk metrics")
    volatility_decomposition: List[VolatilityDecomposition] = Field(
        ..., description="Risk contribution by asset")


class MonteCarloRequest(BaseModel):
    """Request model for Monte Carlo simulation."""
    symbols: List[str] = Field(..., description="Portfolio assets")
    weights: List[float] = Field(..., description="Portfolio weights")
    num_simulations: int = Field(
        default=10000, ge=1000, le=100000, description="Number of simulations")
    time_horizon: int = Field(
        default=252, ge=30, le=1260, description="Time horizon in days")
    scenarios: List[MarketScenario] = Field(
        default=[MarketScenario.BULL_MARKET,
                 MarketScenario.BEAR_MARKET, MarketScenario.MARKET_CRASH],
        description="Market scenarios to test"
    )


class SimulationResults(BaseModel):
    """Monte Carlo simulation results."""
    mean: float = Field(..., description="Mean final value")
    median: Optional[float] = Field(None, description="Median final value")
    std: float = Field(..., description="Standard deviation")
    min: float = Field(..., description="Minimum final value")
    max: float = Field(..., description="Maximum final value")


class ReturnDistribution(BaseModel):
    """Return distribution statistics."""
    mean_return: float = Field(..., description="Mean return")
    volatility: float = Field(..., description="Return volatility")
    skewness: Optional[float] = Field(None, description="Return skewness")
    kurtosis: Optional[float] = Field(None, description="Return kurtosis")


class Percentiles(BaseModel):
    """Percentile values."""
    fifth: float = Field(..., alias="5th", description="5th percentile")
    twenty_fifth: float = Field(..., alias="25th",
                                description="25th percentile")
    fiftieth: float = Field(..., alias="50th",
                            description="50th percentile (median)")
    seventy_fifth: float = Field(..., alias="75th",
                                 description="75th percentile")
    ninety_fifth: float = Field(..., alias="95th",
                                description="95th percentile")


class ScenarioAnalysis(BaseModel):
    """Scenario analysis results."""
    expected_return: float = Field(...,
                                   description="Expected return under scenario")
    volatility: float = Field(..., description="Volatility under scenario")
    probability_of_loss: float = Field(..., description="Probability of loss")
    worst_case_loss: float = Field(..., description="Worst case loss")
    best_case_gain: float = Field(..., description="Best case gain")


class MonteCarloResponse(BaseModel):
    """Response model for Monte Carlo simulation."""
    simulation_timestamp: datetime = Field(...,
                                           description="When simulation was performed")
    parameters: Dict[str, Any] = Field(...,
                                       description="Simulation parameters")
    simulation_results: Dict[str,
                             Any] = Field(..., description="Simulation results")
    scenario_analysis: Dict[str, ScenarioAnalysis] = Field(
        ..., description="Scenario-specific results")


class RebalancingRequest(BaseModel):
    """Request model for rebalancing analysis."""
    current_portfolio: Dict[str,
                            float] = Field(..., description="Current portfolio weights")
    target_allocation: Optional[Dict[str, float]] = Field(
        None, description="Target allocation")
    rebalancing_frequency: str = Field(
        default="quarterly", description="Rebalancing frequency")
    transaction_cost: float = Field(
        default=0.001, description="Transaction cost percentage")


class RebalancingAnalysis(BaseModel):
    """Rebalancing analysis results."""
    rebalancing_needed: bool = Field(...,
                                     description="Whether rebalancing is needed")
    total_drift: float = Field(..., description="Total drift from target")
    rebalancing_cost: float = Field(..., description="Cost of rebalancing")
    expected_benefit: float = Field(..., description="Expected benefit")
    net_benefit: float = Field(..., description="Net benefit after costs")
    recommendation: str = Field(..., description="Rebalancing recommendation")


class AssetAdjustment(BaseModel):
    """Individual asset adjustment details."""
    current_weight: float = Field(..., description="Current weight")
    target_weight: float = Field(..., description="Target weight")
    adjustment_needed: float = Field(..., description="Adjustment needed")
    action: str = Field(..., description="Required action (BUY/SELL)")
    urgency: str = Field(..., description="Urgency level")


class ImplementationPlan(BaseModel):
    """Rebalancing implementation plan."""
    execution_order: List[Dict[str, Any]
                          ] = Field(..., description="Order of execution")
    timing_recommendation: str = Field(...,
                                       description="Timing recommendation")
    risk_considerations: List[str] = Field(...,
                                           description="Risk considerations")


class RebalancingResponse(BaseModel):
    """Response model for rebalancing analysis."""
    analysis_timestamp: datetime = Field(...,
                                         description="When analysis was performed")
    current_portfolio: Dict[str,
                            float] = Field(..., description="Current portfolio")
    rebalancing_frequency: str = Field(...,
                                       description="Rebalancing frequency")
    transaction_cost_percent: float = Field(...,
                                            description="Transaction cost percentage")
    rebalancing_analysis: RebalancingAnalysis = Field(
        ..., description="Rebalancing analysis")
    detailed_adjustments: Dict[str, AssetAdjustment] = Field(
        ..., description="Asset-specific adjustments")
    implementation_plan: ImplementationPlan = Field(
        ..., description="Implementation plan")
    alternative_strategies: List[str] = Field(
        ..., description="Alternative rebalancing strategies")


class PortfolioResponse(BaseModel):
    """General portfolio response model."""
    timestamp: datetime = Field(..., description="Response timestamp")
    portfolio_composition: Dict[str,
                                float] = Field(..., description="Portfolio composition")
    status: str = Field(..., description="Operation status")
    message: Optional[str] = Field(None, description="Status message")
    error: Optional[str] = Field(None, description="Error message if any")
