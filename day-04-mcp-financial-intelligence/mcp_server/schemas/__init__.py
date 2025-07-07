"""
MCP Financial Intelligence Schemas

Pydantic models for data validation and serialization across the platform.
"""

from .market_data import (
    MarketDataRequest,
    MarketDataResponse,
    ForecastRequest,
    ForecastResponse
)
from .portfolio import (
    PortfolioRequest,
    PortfolioResponse,
    RiskMetricsRequest,
    RiskMetricsResponse,
    OptimizationRequest,
    OptimizationResponse
)
from .trading import (
    TradingRequest,
    TradingResponse,
    OrderRequest,
    OrderResponse,
    PositionRequest,
    PositionResponse
)
from .intelligence import (
    IntelligenceRequest,
    IntelligenceResponse,
    CrossPlatformAnalysisRequest,
    CrossPlatformAnalysisResponse
)

__all__ = [
    # Market Data Schemas
    "MarketDataRequest",
    "MarketDataResponse",
    "ForecastRequest",
    "ForecastResponse",
    # Portfolio Schemas
    "PortfolioRequest",
    "PortfolioResponse",
    "RiskMetricsRequest",
    "RiskMetricsResponse",
    "OptimizationRequest",
    "OptimizationResponse",
    # Trading Schemas
    "TradingRequest",
    "TradingResponse",
    "OrderRequest",
    "OrderResponse",
    "PositionRequest",
    "PositionResponse",
    # Intelligence Schemas
    "IntelligenceRequest",
    "IntelligenceResponse",
    "CrossPlatformAnalysisRequest",
    "CrossPlatformAnalysisResponse"
]
