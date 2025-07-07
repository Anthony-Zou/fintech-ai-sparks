"""
Trading Schemas

Pydantic models for algorithmic trading and position management data validation.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    """Order side enumeration."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type enumeration."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "PENDING"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class StrategyType(str, Enum):
    """Trading strategy types."""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    PAIRS_TRADING = "pairs_trading"
    ARBITRAGE = "arbitrage"


class StrategyStatus(str, Enum):
    """Strategy status enumeration."""
    ACTIVE = "active"
    STOPPED = "stopped"
    PAUSED = "paused"
    FAILED = "failed"


class PositionAction(str, Enum):
    """Position management actions."""
    GET_POSITIONS = "get_positions"
    CLOSE_POSITION = "close_position"
    UPDATE_POSITION = "update_position"


class TradingRequest(BaseModel):
    """Base request model for trading operations."""
    symbols: List[str] = Field(..., description="Symbols to trade")
    strategy_type: StrategyType = Field(
        default=StrategyType.MOMENTUM, description="Trading strategy type")


class StrategyParameters(BaseModel):
    """Trading strategy parameters."""
    short_window: int = Field(default=5, ge=1, le=50,
                              description="Short moving average window")
    long_window: int = Field(default=20, ge=5, le=200,
                             description="Long moving average window")
    momentum_threshold: float = Field(
        default=0.01, ge=0, le=1, description="Momentum threshold for signals")
    position_size: float = Field(
        default=100, ge=1, description="Default position size")
    initial_capital: float = Field(
        default=100000, ge=1000, description="Initial capital")
    stop_loss: Optional[float] = Field(
        None, ge=0, le=1, description="Stop loss percentage")
    take_profit: Optional[float] = Field(
        None, ge=0, description="Take profit percentage")
    max_positions: int = Field(
        default=10, ge=1, le=50, description="Maximum number of positions")


class StrategyRequest(BaseModel):
    """Request model for strategy execution."""
    strategy_type: StrategyType = Field(...,
                                        description="Type of strategy to execute")
    symbols: List[str] = Field(..., description="Symbols to trade")
    parameters: Optional[StrategyParameters] = Field(
        None, description="Strategy parameters")


class Signal(BaseModel):
    """Trading signal model."""
    signal: str = Field(..., description="Signal type (BUY/SELL/HOLD)")
    strength: float = Field(..., ge=0, le=1, description="Signal strength")
    timestamp: datetime = Field(..., description="When signal was generated")
    reasoning: str = Field(..., description="Reasoning for the signal")


class PerformanceMetrics(BaseModel):
    """Strategy performance metrics."""
    total_return: float = Field(..., description="Total return percentage")
    sharpe_ratio: float = Field(..., description="Sharpe ratio")
    max_drawdown: float = Field(..., description="Maximum drawdown")
    win_rate: float = Field(..., ge=0, le=1, description="Win rate")
    profit_factor: float = Field(..., description="Profit factor")
    total_trades: Optional[int] = Field(
        None, description="Total number of trades")
    avg_trade_return: Optional[float] = Field(
        None, description="Average trade return")


class StrategyResponse(BaseModel):
    """Response model for strategy execution."""
    execution_timestamp: datetime = Field(...,
                                          description="When strategy was executed")
    strategy_id: str = Field(..., description="Unique strategy identifier")
    strategy_type: str = Field(..., description="Strategy type")
    symbols: List[str] = Field(..., description="Symbols being traded")
    parameters: Dict[str, Any] = Field(..., description="Strategy parameters")
    status: StrategyStatus = Field(..., description="Strategy status")
    signals: Dict[str, Signal] = Field(...,
                                       description="Current trading signals")
    performance: PerformanceMetrics = Field(...,
                                            description="Performance metrics")
    message: str = Field(..., description="Status message")


class OrderRequest(BaseModel):
    """Request model for order creation."""
    symbol: str = Field(..., description="Trading symbol")
    side: OrderSide = Field(..., description="Order side (BUY/SELL)")
    quantity: float = Field(..., gt=0, description="Order quantity")
    order_type: OrderType = Field(
        default=OrderType.MARKET, description="Order type")
    price: Optional[float] = Field(
        None, gt=0, description="Limit price (for limit orders)")
    stop_price: Optional[float] = Field(
        None, gt=0, description="Stop price (for stop orders)")


class OrderInfo(BaseModel):
    """Order information model."""
    order_id: str = Field(..., description="Unique order identifier")
    symbol: str = Field(..., description="Trading symbol")
    side: str = Field(..., description="Order side")
    quantity: float = Field(..., description="Order quantity")
    order_type: str = Field(..., description="Order type")
    price: Optional[float] = Field(None, description="Order price")
    status: str = Field(..., description="Order status")
    filled_quantity: float = Field(default=0, description="Filled quantity")
    execution_price: Optional[float] = Field(
        None, description="Execution price")
    created_at: datetime = Field(..., description="Order creation time")
    filled_at: Optional[datetime] = Field(None, description="Order fill time")


class OrderResponse(BaseModel):
    """Response model for order operations."""
    timestamp: datetime = Field(..., description="Response timestamp")
    order_id: str = Field(..., description="Order identifier")
    symbol: str = Field(..., description="Trading symbol")
    side: str = Field(..., description="Order side")
    quantity: float = Field(..., description="Order quantity")
    order_type: str = Field(..., description="Order type")
    price: Optional[float] = Field(None, description="Order price")
    status: str = Field(..., description="Order status")
    message: str = Field(..., description="Status message")


class Position(BaseModel):
    """Position model."""
    symbol: str = Field(..., description="Trading symbol")
    quantity: float = Field(..., description="Position quantity")
    avg_price: float = Field(..., description="Average purchase price")
    current_price: float = Field(..., description="Current market price")
    unrealized_pnl: float = Field(..., description="Unrealized profit/loss")
    market_value: float = Field(..., description="Current market value")
    percent_of_portfolio: Optional[float] = Field(
        None, description="Percentage of total portfolio")


class PositionRequest(BaseModel):
    """Request model for position management."""
    action: PositionAction = Field(...,
                                   description="Position management action")
    symbol: Optional[str] = Field(
        None, description="Symbol for position operations")
    quantity: Optional[float] = Field(
        None, description="Quantity for position updates")


class ClosedPosition(BaseModel):
    """Closed position details."""
    symbol: str = Field(..., description="Trading symbol")
    quantity_closed: float = Field(..., description="Quantity that was closed")
    closing_price: float = Field(...,
                                 description="Price at which position was closed")
    realized_pnl: float = Field(..., description="Realized profit/loss")


class UpdatedPosition(BaseModel):
    """Updated position details."""
    symbol: str = Field(..., description="Trading symbol")
    quantity_change: float = Field(...,
                                   description="Change in position quantity")
    new_quantity: float = Field(..., description="New total quantity")
    execution_price: float = Field(..., description="Execution price")
    timestamp: datetime = Field(..., description="Update timestamp")


class PositionResponse(BaseModel):
    """Response model for position management."""
    timestamp: datetime = Field(..., description="Response timestamp")
    action: str = Field(..., description="Action performed")
    symbol: Optional[str] = Field(None, description="Symbol")
    status: str = Field(..., description="Operation status")
    positions: Optional[Dict[str, Position]] = Field(
        None, description="Current positions")
    total_portfolio_value: Optional[float] = Field(
        None, description="Total portfolio value")
    total_pnl: Optional[float] = Field(
        None, description="Total unrealized P&L")
    cash: Optional[float] = Field(None, description="Available cash")
    closed_position: Optional[ClosedPosition] = Field(
        None, description="Details of closed position")
    updated_position: Optional[UpdatedPosition] = Field(
        None, description="Details of updated position")
    message: Optional[str] = Field(None, description="Status message")


class Trade(BaseModel):
    """Trade execution model."""
    timestamp: datetime = Field(..., description="Trade timestamp")
    order_id: str = Field(..., description="Associated order ID")
    symbol: str = Field(..., description="Trading symbol")
    side: str = Field(..., description="Trade side")
    quantity: float = Field(..., description="Trade quantity")
    price: float = Field(..., description="Trade price")
    pnl: Optional[float] = Field(None, description="Profit/loss from trade")
    commission: Optional[float] = Field(None, description="Commission paid")


class TradeHistoryRequest(BaseModel):
    """Request model for trade history."""
    symbol: Optional[str] = Field(None, description="Filter by symbol")
    start_date: Optional[datetime] = Field(
        None, description="Start date filter")
    end_date: Optional[datetime] = Field(None, description="End date filter")
    limit: int = Field(default=100, ge=1, le=1000,
                       description="Maximum number of trades")


class TradeHistoryResponse(BaseModel):
    """Response model for trade history."""
    trade_history: List[Trade] = Field(..., description="List of trades")
    total_trades: int = Field(..., description="Total number of trades")
    symbol_filter: Optional[str] = Field(
        None, description="Symbol filter applied")
    timestamp: datetime = Field(..., description="Response timestamp")


class StrategyStatusRequest(BaseModel):
    """Request model for strategy status."""
    strategy_id: Optional[str] = Field(
        None, description="Specific strategy ID")


class StrategyStatusResponse(BaseModel):
    """Response model for strategy status."""
    strategy_id: Optional[str] = Field(None, description="Strategy ID")
    status: Optional[Dict[str, Any]] = Field(
        None, description="Strategy status")
    all_strategies: Optional[Dict[str, Any]] = Field(
        None, description="All strategies status")
    total_strategies: Optional[int] = Field(
        None, description="Total number of strategies")
    timestamp: datetime = Field(..., description="Response timestamp")


class RiskControls(BaseModel):
    """Risk control parameters."""
    max_portfolio_exposure: float = Field(
        default=0.95, ge=0, le=1, description="Maximum portfolio exposure")
    max_position_size: float = Field(
        default=0.1, ge=0, le=1, description="Maximum position size as % of portfolio")
    daily_loss_limit: float = Field(
        default=0.05, ge=0, le=1, description="Daily loss limit as % of portfolio")
    var_limit: Optional[float] = Field(None, description="VaR limit")
    correlation_limit: float = Field(
        default=0.7, ge=0, le=1, description="Maximum correlation between positions")


class MarketDataSnapshot(BaseModel):
    """Market data snapshot."""
    symbol: str = Field(..., description="Trading symbol")
    last_price: float = Field(..., description="Last traded price")
    bid_price: Optional[float] = Field(None, description="Best bid price")
    ask_price: Optional[float] = Field(None, description="Best ask price")
    volume: Optional[float] = Field(None, description="Trading volume")
    timestamp: datetime = Field(..., description="Data timestamp")


class TradingResponse(BaseModel):
    """General trading response model."""
    timestamp: datetime = Field(..., description="Response timestamp")
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if any")
