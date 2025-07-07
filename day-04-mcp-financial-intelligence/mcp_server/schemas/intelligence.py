"""
Intelligence Schemas

Pydantic models for cross-platform financial intelligence and unified insights.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class AnalysisScope(str, Enum):
    """Scope of financial intelligence analysis."""
    COMPREHENSIVE = "comprehensive"
    RISK_FOCUSED = "risk_focused"
    TRADING_FOCUSED = "trading_focused"
    FORECAST_FOCUSED = "forecast_focused"


class RiskTolerance(str, Enum):
    """Risk tolerance levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class InvestmentHorizon(str, Enum):
    """Investment time horizon."""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class MarketOutlook(str, Enum):
    """Market outlook sentiment."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class RiskLevel(str, Enum):
    """Overall risk assessment levels."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class TechnicalOutlook(str, Enum):
    """Technical analysis outlook."""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


class TradingSignal(str, Enum):
    """Trading signal types."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class RecommendationAction(str, Enum):
    """Recommendation actions."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    INCREASE = "INCREASE"


class Urgency(str, Enum):
    """Action urgency levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ContextInfo(BaseModel):
    """Context information for intelligence analysis."""
    portfolio_value: float = Field(
        default=100000, description="Current portfolio value")
    risk_tolerance: RiskTolerance = Field(
        default=RiskTolerance.MODERATE, description="Risk tolerance level")
    investment_horizon: InvestmentHorizon = Field(
        default=InvestmentHorizon.MEDIUM, description="Investment horizon")
    market_outlook: MarketOutlook = Field(
        default=MarketOutlook.NEUTRAL, description="Market outlook")


class IntelligenceRequest(BaseModel):
    """Request model for financial intelligence generation."""
    symbols: List[str] = Field(..., description="Symbols to analyze")
    analysis_scope: AnalysisScope = Field(
        default=AnalysisScope.COMPREHENSIVE, description="Scope of analysis")
    context: Optional[ContextInfo] = Field(
        None, description="Analysis context")


class KeyInsight(BaseModel):
    """Individual key insight."""
    category: str = Field(..., description="Insight category")
    title: str = Field(..., description="Insight title")
    description: str = Field(..., description="Detailed description")
    impact: str = Field(..., description="Expected impact")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")


class RiskAssessment(BaseModel):
    """Risk assessment details."""
    overall_risk_level: RiskLevel = Field(...,
                                          description="Overall risk level")
    primary_risks: List[str] = Field(..., description="Primary risk factors")
    risk_mitigation: List[str] = Field(...,
                                       description="Risk mitigation strategies")
    risk_score: float = Field(..., ge=0, le=10,
                              description="Numerical risk score")


class Opportunity(BaseModel):
    """Investment or trading opportunity."""
    title: str = Field(..., description="Opportunity title")
    description: str = Field(..., description="Opportunity description")
    potential_return: Optional[float] = Field(
        None, description="Potential return percentage")
    risk_level: RiskLevel = Field(..., description="Risk level")
    time_horizon: str = Field(..., description="Recommended time horizon")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")


class ImmediateAction(BaseModel):
    """Immediate action recommendation."""
    action: str = Field(..., description="Recommended action")
    symbol: Optional[str] = Field(None, description="Related symbol")
    urgency: Urgency = Field(..., description="Action urgency")
    reasoning: str = Field(..., description="Reasoning for action")
    expected_impact: str = Field(..., description="Expected impact")


class MediumTermAction(BaseModel):
    """Medium-term action recommendation."""
    action: str = Field(..., description="Recommended action")
    timeframe: str = Field(..., description="Recommended timeframe")
    priority: str = Field(..., description="Priority level")
    expected_outcome: str = Field(..., description="Expected outcome")


class Recommendations(BaseModel):
    """Comprehensive recommendations."""
    immediate_actions: List[ImmediateAction] = Field(
        ..., description="Immediate actions to take")
    medium_term_actions: List[MediumTermAction] = Field(
        ..., description="Medium-term strategic actions")
    portfolio_adjustments: List[str] = Field(
        ..., description="Portfolio adjustment recommendations")
    risk_management: List[str] = Field(...,
                                       description="Risk management recommendations")


class CrossPlatformCorrelation(BaseModel):
    """Cross-platform correlation analysis."""
    forecast_trading_alignment: str = Field(
        ..., description="Alignment between forecasts and trading signals")
    risk_strategy_consistency: str = Field(
        ..., description="Consistency between risk metrics and strategy")
    optimization_execution_sync: str = Field(
        ..., description="Sync between optimization and execution")
    overall_coherence: float = Field(..., ge=0, le=1,
                                     description="Overall platform coherence score")


class SymbolInsight(BaseModel):
    """Symbol-specific insights."""
    technical_outlook: TechnicalOutlook = Field(
        ..., description="Technical analysis outlook")
    risk_contribution: float = Field(..., ge=0, le=1,
                                     description="Risk contribution to portfolio")
    trading_signal: TradingSignal = Field(...,
                                          description="Current trading signal")
    forecast_confidence: float = Field(..., ge=0,
                                       le=1, description="Forecast confidence")
    recommended_weight: float = Field(..., ge=0, le=1,
                                      description="Recommended portfolio weight")
    momentum_score: Optional[float] = Field(None, description="Momentum score")
    value_score: Optional[float] = Field(None, description="Value score")
    quality_score: Optional[float] = Field(None, description="Quality score")


class UnifiedInsights(BaseModel):
    """Unified financial intelligence insights."""
    market_outlook: str = Field(..., description="Overall market outlook")
    key_insights: List[KeyInsight] = Field(...,
                                           description="Key insights from analysis")
    risk_assessment: RiskAssessment = Field(...,
                                            description="Comprehensive risk assessment")
    opportunities: List[Opportunity] = Field(...,
                                             description="Identified opportunities")
    recommendations: Recommendations = Field(...,
                                             description="Actionable recommendations")
    confidence_score: float = Field(..., ge=0, le=1,
                                    description="Overall confidence in analysis")


class IntelligenceResponse(BaseModel):
    """Response model for financial intelligence."""
    analysis_timestamp: datetime = Field(...,
                                         description="When analysis was performed")
    symbols_analyzed: List[str] = Field(...,
                                        description="Symbols included in analysis")
    analysis_scope: str = Field(..., description="Scope of analysis performed")
    context: Optional[ContextInfo] = Field(
        None, description="Analysis context used")
    unified_insights: UnifiedInsights = Field(
        ..., description="Unified insights across platforms")
    cross_platform_correlation: CrossPlatformCorrelation = Field(
        ..., description="Cross-platform correlation analysis")
    symbol_specific_insights: Dict[str, SymbolInsight] = Field(
        ..., description="Symbol-specific insights")
    data_sources: List[str] = Field(...,
                                    description="Data sources used in analysis")
    analysis_quality: float = Field(..., ge=0, le=1,
                                    description="Quality score of analysis")


class CrossPlatformAnalysisRequest(BaseModel):
    """Request model for cross-platform analysis."""
    symbols: List[str] = Field(..., description="Symbols to analyze")
    include_forecasts: bool = Field(
        default=True, description="Include forecast analysis")
    include_risk_metrics: bool = Field(
        default=True, description="Include risk analysis")
    include_trading_signals: bool = Field(
        default=True, description="Include trading signals")
    timeframe: str = Field(default="1y", description="Analysis timeframe")


class PlatformInsight(BaseModel):
    """Insight from a specific platform."""
    platform: str = Field(..., description="Platform name (Day1, Day2, Day3)")
    insight_type: str = Field(..., description="Type of insight")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")
    data: Dict[str, Any] = Field(..., description="Insight data")
    timestamp: datetime = Field(..., description="When insight was generated")


class CorrelationMatrix(BaseModel):
    """Correlation between different insights."""
    forecast_vs_risk: float = Field(
        ..., description="Correlation between forecasts and risk metrics")
    risk_vs_trading: float = Field(...,
                                   description="Correlation between risk and trading signals")
    forecast_vs_trading: float = Field(
        ..., description="Correlation between forecasts and trading")
    overall_correlation: float = Field(...,
                                       description="Overall correlation score")


class ConflictResolution(BaseModel):
    """Resolution for conflicting insights."""
    conflict_type: str = Field(..., description="Type of conflict")
    conflicting_platforms: List[str] = Field(
        ..., description="Platforms with conflicting insights")
    resolution: str = Field(..., description="Recommended resolution")
    reasoning: str = Field(..., description="Reasoning for resolution")
    confidence: float = Field(..., ge=0, le=1,
                              description="Confidence in resolution")


class CrossPlatformAnalysisResponse(BaseModel):
    """Response model for cross-platform analysis."""
    analysis_timestamp: datetime = Field(...,
                                         description="When analysis was performed")
    symbols_analyzed: List[str] = Field(..., description="Analyzed symbols")
    platform_insights: List[PlatformInsight] = Field(
        ..., description="Insights from each platform")
    correlation_matrix: CorrelationMatrix = Field(
        ..., description="Inter-platform correlations")
    unified_recommendation: str = Field(...,
                                        description="Unified recommendation")
    conflict_resolutions: List[ConflictResolution] = Field(
        ..., description="Resolved conflicts")
    overall_confidence: float = Field(..., ge=0, le=1,
                                      description="Overall analysis confidence")
    synthesis_quality: float = Field(..., ge=0, le=1,
                                     description="Quality of insight synthesis")
