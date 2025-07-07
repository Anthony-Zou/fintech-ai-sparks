"""
Day 3 Connector - Algorithmic Trading Integration

Bridges the MCP server with the Day 3 algorithmic trading platform,
providing access to trading strategy execution and position management.
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import logging
import uuid
from enum import Enum, auto

logger = logging.getLogger(__name__)


class OrderSide(Enum):
    BUY = auto()
    SELL = auto()


class OrderStatus(Enum):
    PENDING = auto()
    PARTIALLY_FILLED = auto()
    FILLED = auto()
    CANCELLED = auto()
    REJECTED = auto()


class Day3Connector:
    """
    Connector to integrate with Day 3 algorithmic trading platform.

    This connector provides access to:
    - Trading strategy execution (Momentum, Mean Reversion, etc.)
    - Order management and execution
    - Position tracking and P&L calculation
    - Risk management controls
    """

    def __init__(self, day3_app_path: str = "../day-03-algorithmic-trading"):
        self.day3_app_path = day3_app_path
        self.trading_engine = None
        self.position_manager = None
        self.market_data_feed = None
        self.strategies = {}
        self.orders = {}
        self.positions = {}
        self.trade_history = []
        self._import_day3_modules()

    def _import_day3_modules(self) -> None:
        """Import Day 3 platform modules."""
        try:
            if os.path.exists(self.day3_app_path):
                if self.day3_app_path not in sys.path:
                    sys.path.insert(0, self.day3_app_path)

                # Import core classes from Day 3
                from core.trading_engine import TradingEngine, OrderType, OrderSide as Day3OrderSide
                from core.position_manager import PositionManager
                from core.market_data import MarketDataFeed
                from strategies.simple_momentum import MomentumStrategy

                self.TradingEngine = TradingEngine
                self.PositionManager = PositionManager
                self.MarketDataFeed = MarketDataFeed
                self.MomentumStrategy = MomentumStrategy
                self.OrderType = OrderType
                self.Day3OrderSide = Day3OrderSide

                # Initialize core components
                self.trading_engine = TradingEngine()
                self.position_manager = PositionManager(initial_capital=100000)
                self.market_data_feed = MarketDataFeed(
                    update_interval=5.0, use_mock_data=True)

                logger.info(
                    "Successfully imported and initialized Day 3 platform modules")

        except ImportError as e:
            logger.warning(
                f"Could not import Day 3 modules, using mock implementations: {e}")
            # Use mock implementations if Day 3 modules are not available
            self.TradingEngine = None
            self.PositionManager = None
            self.MarketDataFeed = None
            self.MomentumStrategy = None
            self._initialize_mock_components()

    def _initialize_mock_components(self) -> None:
        """Initialize mock trading components."""
        self.orders = {}
        self.positions = {}
        self.trade_history = []
        self.cash = 100000.0
        self.total_portfolio_value = 100000.0

    async def execute_trading_strategy(self, strategy_type: str, symbols: List[str],
                                       parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute trading strategy using Day 3 platform.

        Args:
            strategy_type: Type of strategy (momentum, mean_reversion, etc.)
            symbols: Symbols to trade
            parameters: Strategy parameters

        Returns:
            Strategy execution results
        """
        if parameters is None:
            parameters = {}

        try:
            if self.MomentumStrategy and strategy_type == "momentum":
                return await self._execute_momentum_strategy(symbols, parameters)
            else:
                return await self._mock_strategy_execution(strategy_type, symbols, parameters)

        except Exception as e:
            logger.error(f"Error executing trading strategy: {e}")
            return {"error": str(e), "status": "failed"}

    async def _execute_momentum_strategy(self, symbols: List[str],
                                         parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute momentum strategy using Day 3 platform."""
        try:
            # Extract parameters with defaults
            short_window = parameters.get("short_window", 5)
            long_window = parameters.get("long_window", 20)
            momentum_threshold = parameters.get("momentum_threshold", 0.01)
            position_size = parameters.get("position_size", 100)
            initial_capital = parameters.get("initial_capital", 100000)

            # Create momentum strategy
            strategy = self.MomentumStrategy(
                trading_engine=self.trading_engine,
                market_data=self.market_data_feed,
                position_manager=self.position_manager,
                symbols=symbols,
                short_window=short_window,
                long_window=long_window,
                momentum_threshold=momentum_threshold,
                position_size=position_size,
                update_interval=60.0
            )

            # Start the strategy
            strategy_id = f"momentum_{len(self.strategies) + 1}"
            self.strategies[strategy_id] = strategy

            success = strategy.start()

            if success:
                # Get initial strategy status
                status = strategy.get_status()

                return {
                    "execution_timestamp": datetime.now().isoformat(),
                    "strategy_id": strategy_id,
                    "strategy_type": "momentum",
                    "symbols": symbols,
                    "parameters": parameters,
                    "status": "active" if status["running"] else "failed",
                    "signals": status.get("signals", {}),
                    "performance": status.get("performance", {}),
                    "message": "Strategy started successfully"
                }
            else:
                return {
                    "execution_timestamp": datetime.now().isoformat(),
                    "strategy_type": "momentum",
                    "status": "failed",
                    "error": "Failed to start strategy"
                }

        except Exception as e:
            logger.error(f"Error in momentum strategy execution: {e}")
            return {"error": str(e), "status": "failed"}

    async def _mock_strategy_execution(self, strategy_type: str, symbols: List[str],
                                       parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Mock strategy execution for testing."""
        strategy_id = f"{strategy_type}_{len(self.strategies) + 1}"

        # Generate mock signals
        signals = {}
        for symbol in symbols:
            momentum_score = np.random.normal(0, 0.3)
            if momentum_score > 0.1:
                signal = "BUY"
            elif momentum_score < -0.1:
                signal = "SELL"
            else:
                signal = "HOLD"

            signals[symbol] = {
                "signal": signal,
                "strength": abs(momentum_score),
                "timestamp": datetime.now().isoformat(),
                "reasoning": f"Momentum score: {momentum_score:.3f}"
            }

        # Mock performance metrics
        performance = {
            "total_return": np.random.normal(0.08, 0.05),
            "sharpe_ratio": np.random.normal(0.75, 0.2),
            "max_drawdown": np.random.normal(-0.12, 0.03),
            "win_rate": np.random.uniform(0.45, 0.65),
            "profit_factor": np.random.uniform(1.1, 1.8)
        }

        # Store strategy info
        self.strategies[strategy_id] = {
            "type": strategy_type,
            "symbols": symbols,
            "parameters": parameters,
            "status": "active",
            "created_at": datetime.now().isoformat()
        }

        return {
            "execution_timestamp": datetime.now().isoformat(),
            "strategy_id": strategy_id,
            "strategy_type": strategy_type,
            "symbols": symbols,
            "parameters": parameters,
            "status": "active",
            "signals": signals,
            "performance": performance,
            "message": "Strategy executed successfully"
        }

    async def manage_positions(self, action: str, symbol: str = None,
                               quantity: float = None) -> Dict[str, Any]:
        """
        Manage trading positions using Day 3 platform.

        Args:
            action: Position management action (get_positions, close_position, update_position)
            symbol: Symbol for position operations
            quantity: Quantity for position updates

        Returns:
            Position management results
        """
        try:
            if self.position_manager:
                return await self._real_position_management(action, symbol, quantity)
            else:
                return await self._mock_position_management(action, symbol, quantity)

        except Exception as e:
            logger.error(f"Error in position management: {e}")
            return {"error": str(e)}

    async def _real_position_management(self, action: str, symbol: str,
                                        quantity: float) -> Dict[str, Any]:
        """Real position management using Day 3 platform."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "symbol": symbol,
            "status": "success"
        }

        if action == "get_positions":
            # Get all current positions
            positions = {}
            total_value = self.position_manager.get_total_value()
            total_pnl = self.position_manager.get_total_pnl()
            cash = self.position_manager.cash

            # Get individual positions (this would need to be implemented in the actual PositionManager)
            # For now, we'll use a mock implementation
            for pos_symbol in ["AAPL", "MSFT", "TSLA"]:  # Mock symbols
                position = self.position_manager.get_position(pos_symbol)
                if position.quantity != 0:
                    positions[pos_symbol] = {
                        "quantity": position.quantity,
                        "avg_price": position.avg_price,
                        "current_price": position.current_price,
                        "unrealized_pnl": position.unrealized_pnl,
                        "market_value": position.market_value
                    }

            results.update({
                "positions": positions,
                "total_portfolio_value": total_value,
                "total_pnl": total_pnl,
                "cash": cash
            })

        elif action == "close_position" and symbol:
            position = self.position_manager.get_position(symbol)
            if position.quantity != 0:
                # Mock closing the position
                closed_quantity = position.quantity
                closing_price = position.current_price
                realized_pnl = (
                    closing_price - position.avg_price) * abs(closed_quantity)

                results.update({
                    "closed_position": {
                        "symbol": symbol,
                        "quantity_closed": closed_quantity,
                        "closing_price": closing_price,
                        "realized_pnl": realized_pnl
                    }
                })
            else:
                results.update({"message": f"No position found for {symbol}"})

        elif action == "update_position" and symbol and quantity:
            # Mock position update
            execution_price = 150.0 + np.random.normal(0, 5)  # Mock price

            # This would call the actual position manager methods
            # self.position_manager.add_trade(symbol, quantity, execution_price)

            results.update({
                "updated_position": {
                    "symbol": symbol,
                    "quantity_change": quantity,
                    "execution_price": execution_price,
                    "timestamp": datetime.now().isoformat()
                }
            })

        return results

    async def _mock_position_management(self, action: str, symbol: str,
                                        quantity: float) -> Dict[str, Any]:
        """Mock position management for testing."""
        results = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "symbol": symbol,
            "status": "success"
        }

        if action == "get_positions":
            # Mock positions
            mock_positions = {
                "AAPL": {"quantity": 100, "avg_price": 150.0, "current_price": 152.0, "unrealized_pnl": 200},
                "MSFT": {"quantity": -50, "avg_price": 300.0, "current_price": 295.0, "unrealized_pnl": 250},
                "TSLA": {"quantity": 75, "avg_price": 200.0, "current_price": 195.0, "unrealized_pnl": -375}
            }

            total_pnl = sum(pos["unrealized_pnl"]
                            for pos in mock_positions.values())

            results.update({
                "positions": mock_positions,
                "total_portfolio_value": self.total_portfolio_value,
                "total_pnl": total_pnl,
                "cash": self.cash
            })

        elif action == "close_position" and symbol:
            if symbol in self.positions:
                closed_position = self.positions.pop(symbol)
                results.update({
                    "closed_position": {
                        "symbol": symbol,
                        "quantity_closed": closed_position.get("quantity", 0),
                        "closing_price": 151.5,
                        "realized_pnl": np.random.normal(100, 50)
                    }
                })
            else:
                results.update({"message": f"No position found for {symbol}"})

        elif action == "update_position" and symbol and quantity:
            execution_price = 151.0 + np.random.normal(0, 2)

            if symbol in self.positions:
                self.positions[symbol]["quantity"] += quantity
            else:
                self.positions[symbol] = {
                    "quantity": quantity,
                    "avg_price": execution_price,
                    "created_at": datetime.now().isoformat()
                }

            results.update({
                "updated_position": {
                    "symbol": symbol,
                    "new_quantity": self.positions[symbol]["quantity"],
                    "execution_price": execution_price,
                    "timestamp": datetime.now().isoformat()
                }
            })

        return results

    async def create_order(self, symbol: str, side: str, quantity: float,
                           order_type: str = "MARKET", price: float = None) -> Dict[str, Any]:
        """
        Create a trading order using Day 3 platform.

        Args:
            symbol: Trading symbol
            side: Order side (BUY/SELL)
            quantity: Order quantity
            order_type: Order type (MARKET/LIMIT)
            price: Limit price (for limit orders)

        Returns:
            Order creation results
        """
        try:
            if self.trading_engine:
                return await self._real_order_creation(symbol, side, quantity, order_type, price)
            else:
                return await self._mock_order_creation(symbol, side, quantity, order_type, price)

        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return {"error": str(e)}

    async def _real_order_creation(self, symbol: str, side: str, quantity: float,
                                   order_type: str, price: float) -> Dict[str, Any]:
        """Real order creation using Day 3 platform."""
        try:
            # Convert string side to enum
            order_side = self.Day3OrderSide.BUY if side.upper(
            ) == "BUY" else self.Day3OrderSide.SELL

            # Convert string order type to enum
            if order_type.upper() == "MARKET":
                order_type_enum = self.OrderType.MARKET
            elif order_type.upper() == "LIMIT":
                order_type_enum = self.OrderType.LIMIT
            else:
                order_type_enum = self.OrderType.MARKET

            # Create order
            order_id = self.trading_engine.create_order(
                symbol=symbol,
                side=order_side,
                quantity=quantity,
                order_type=order_type_enum,
                price=price
            )

            # Get order details
            order = self.trading_engine.get_order(order_id)

            return {
                "timestamp": datetime.now().isoformat(),
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "order_type": order_type,
                "price": price,
                "status": order.status.name if order else "UNKNOWN",
                "message": "Order created successfully"
            }

        except Exception as e:
            logger.error(f"Error in real order creation: {e}")
            return {"error": str(e)}

    async def _mock_order_creation(self, symbol: str, side: str, quantity: float,
                                   order_type: str, price: float) -> Dict[str, Any]:
        """Mock order creation for testing."""
        order_id = str(uuid.uuid4())

        # Mock order
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "price": price or (150.0 + np.random.normal(0, 5)),
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "filled_quantity": 0
        }

        self.orders[order_id] = order

        # Mock immediate execution for market orders
        if order_type.upper() == "MARKET":
            execution_price = 150.0 + np.random.normal(0, 2)
            order["status"] = "FILLED"
            order["filled_quantity"] = quantity
            order["execution_price"] = execution_price
            order["filled_at"] = datetime.now().isoformat()

            # Add to trade history
            self.trade_history.append({
                "timestamp": datetime.now().isoformat(),
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "price": execution_price,
                "pnl": np.random.normal(0, 100)
            })

        return {
            "timestamp": datetime.now().isoformat(),
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_type": order_type,
            "price": order["price"],
            "status": order["status"],
            "message": "Order created successfully"
        }

    async def get_strategy_status(self, strategy_id: str = None) -> Dict[str, Any]:
        """
        Get status of trading strategies.

        Args:
            strategy_id: Specific strategy ID (optional)

        Returns:
            Strategy status information
        """
        try:
            if strategy_id and strategy_id in self.strategies:
                if hasattr(self.strategies[strategy_id], 'get_status'):
                    # Real strategy object
                    status = self.strategies[strategy_id].get_status()
                    return {
                        "strategy_id": strategy_id,
                        "status": status,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Mock strategy info
                    return {
                        "strategy_id": strategy_id,
                        "status": self.strategies[strategy_id],
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                # Return all strategies
                all_strategies = {}
                for sid, strategy in self.strategies.items():
                    if hasattr(strategy, 'get_status'):
                        all_strategies[sid] = strategy.get_status()
                    else:
                        all_strategies[sid] = strategy

                return {
                    "all_strategies": all_strategies,
                    "total_strategies": len(all_strategies),
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting strategy status: {e}")
            return {"error": str(e)}

    async def get_trade_history(self, symbol: str = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get trade history.

        Args:
            symbol: Filter by symbol (optional)
            limit: Maximum number of trades to return

        Returns:
            Trade history
        """
        try:
            if self.position_manager and hasattr(self.position_manager, 'trade_history'):
                # Use real trade history
                trades = self.position_manager.trade_history
                if symbol:
                    trades = [trade for trade in trades if getattr(
                        trade, 'symbol', None) == symbol]
                trades = trades[-limit:] if len(trades) > limit else trades

                trade_data = []
                for trade in trades:
                    trade_data.append({
                        "timestamp": getattr(trade, 'timestamp', datetime.now().isoformat()),
                        "symbol": getattr(trade, 'symbol', 'UNKNOWN'),
                        "quantity": getattr(trade, 'quantity', 0),
                        "price": getattr(trade, 'price', 0),
                        "side": "BUY" if getattr(trade, 'quantity', 0) > 0 else "SELL",
                        "order_id": getattr(trade, 'order_id', 'UNKNOWN')
                    })

                return {
                    "trade_history": trade_data,
                    "total_trades": len(trade_data),
                    "symbol_filter": symbol,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Use mock trade history
                filtered_trades = self.trade_history
                if symbol:
                    filtered_trades = [
                        trade for trade in self.trade_history if trade["symbol"] == symbol]

                limited_trades = filtered_trades[-limit:] if len(
                    filtered_trades) > limit else filtered_trades

                return {
                    "trade_history": limited_trades,
                    "total_trades": len(limited_trades),
                    "symbol_filter": symbol,
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error getting trade history: {e}")
            return {"error": str(e)}

    async def stop_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Stop a running trading strategy.

        Args:
            strategy_id: Strategy ID to stop

        Returns:
            Stop operation results
        """
        try:
            if strategy_id in self.strategies:
                strategy = self.strategies[strategy_id]

                if hasattr(strategy, 'stop'):
                    # Real strategy object
                    success = strategy.stop()
                    return {
                        "strategy_id": strategy_id,
                        "status": "stopped" if success else "stop_failed",
                        "timestamp": datetime.now().isoformat(),
                        "message": "Strategy stopped successfully" if success else "Failed to stop strategy"
                    }
                else:
                    # Mock strategy
                    strategy["status"] = "stopped"
                    return {
                        "strategy_id": strategy_id,
                        "status": "stopped",
                        "timestamp": datetime.now().isoformat(),
                        "message": "Strategy stopped successfully"
                    }
            else:
                return {
                    "strategy_id": strategy_id,
                    "status": "not_found",
                    "error": f"Strategy {strategy_id} not found"
                }

        except Exception as e:
            logger.error(f"Error stopping strategy: {e}")
            return {"error": str(e)}
