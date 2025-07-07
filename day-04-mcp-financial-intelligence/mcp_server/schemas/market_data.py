"""
Market Data Schemas

Pydantic models for market analysis and forecasting data validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class AnalysisType(str, Enum):
    """Types of market analysis."""
    VOLUME = "volume"
    PRICE = "price"
    VOLATILITY = "volatility"


class TimeFrame(str, Enum):
    """Data timeframe options."""
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"


class MarketDataRequest(BaseModel):
    """Request model for market data fetching."""
    symbols: List[str] = Field(...,
                               description="List of stock symbols to analyze")
    timeframe: TimeFrame = Field(
        default=TimeFrame.ONE_YEAR, description="Historical data timeframe")
    forecast_days: int = Field(
        default=30, ge=7, le=90, description="Number of days to forecast")
    analysis_type: List[AnalysisType] = Field(
        default=[AnalysisType.VOLUME, AnalysisType.PRICE],
        description="Types of analysis to perform"
    )


class FinancialMetrics(BaseModel):
    """Financial metrics for a symbol."""
    current_price: float = Field(..., description="Current stock price")
    price_change: float = Field(...,
                                description="Price change from previous day")
    price_change_pct: float = Field(..., description="Price change percentage")
    volatility: float = Field(..., description="Annualized volatility")
    avg_volume: float = Field(..., description="Average daily volume")
    volume_trend: float = Field(..., description="Volume trend ratio")
    total_return: float = Field(..., description="Total return percentage")


class TechnicalIndicators(BaseModel):
    """Technical indicators for a symbol."""
    sma_20: Optional[float] = Field(
        None, description="20-day simple moving average")
    sma_50: Optional[float] = Field(
        None, description="50-day simple moving average")
    rsi: Optional[float] = Field(None, description="Relative Strength Index")
    bb_upper: Optional[float] = Field(None, description="Upper Bollinger Band")
    bb_lower: Optional[float] = Field(None, description="Lower Bollinger Band")
    bb_position: Optional[float] = Field(
        None, description="Position within Bollinger Bands")
    volume_ratio: Optional[float] = Field(
        None, description="Current volume vs average ratio")
    price_momentum_10d: Optional[float] = Field(
        None, description="10-day price momentum")


class ForecastData(BaseModel):
    """Forecast data for a symbol."""
    model_results: Dict[str, Dict[str, float]
                        ] = Field(..., description="ML model performance metrics")
    forecast: List[Dict[str, Any]
                   ] = Field(..., description="Forecast time series data")
    forecast_summary: Dict[str,
                           Any] = Field(..., description="Summary of forecast results")


class Recommendation(BaseModel):
    """Trading recommendation."""
    symbol: str = Field(..., description="Stock symbol")
    action: str = Field(..., description="Recommended action (BUY/SELL/HOLD)")
    confidence: float = Field(..., ge=0, le=1, description="Confidence level")
    reasoning: str = Field(..., description="Reasoning for the recommendation")


class MarketDataResponse(BaseModel):
    """Response model for market data analysis."""
    analysis_timestamp: datetime = Field(...,
                                         description="When the analysis was performed")
    symbols_analyzed: List[str] = Field(...,
                                        description="Symbols that were analyzed")
    timeframe: str = Field(..., description="Data timeframe used")
    forecast_horizon: int = Field(..., description="Forecast horizon in days")
    market_analysis: Dict[str, FinancialMetrics] = Field(
        ..., description="Financial metrics per symbol")
    forecasts: Dict[str, Dict[str, ForecastData]
                    ] = Field(..., description="Forecast results per symbol")
    technical_indicators: Dict[str, TechnicalIndicators] = Field(
        ..., description="Technical indicators per symbol")
    recommendations: List[Recommendation] = Field(
        ..., description="Trading recommendations")


class ForecastRequest(BaseModel):
    """Request model for specific forecasting."""
    symbol: str = Field(..., description="Symbol to forecast")
    target_column: str = Field(...,
                               description="Target column (close, volume, etc.)")
    forecast_days: int = Field(
        default=30, ge=7, le=90, description="Number of days to forecast")
    timeframe: TimeFrame = Field(
        default=TimeFrame.ONE_YEAR, description="Historical data timeframe")


class ModelMetrics(BaseModel):
    """ML model performance metrics."""
    mae: float = Field(..., description="Mean Absolute Error")
    rmse: float = Field(..., description="Root Mean Square Error")
    r2: float = Field(..., description="R-squared coefficient")


class ForecastResponse(BaseModel):
    """Response model for forecasting."""
    symbol: str = Field(..., description="Forecasted symbol")
    target_column: str = Field(..., description="Forecasted column")
    forecast_timestamp: datetime = Field(...,
                                         description="When forecast was generated")
    model_results: Dict[str, ModelMetrics] = Field(
        ..., description="Model performance metrics")
    forecast_data: List[Dict[str, Any]
                        ] = Field(..., description="Forecast time series")
    forecast_summary: Dict[str,
                           Any] = Field(..., description="Forecast summary statistics")
    confidence_intervals: Optional[Dict[str, List[float]]] = Field(
        None, description="Confidence intervals")
