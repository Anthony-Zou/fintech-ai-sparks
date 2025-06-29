"""
Simple momentum trading strategy implementation.
"""
import logging
import threading
import time
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from core.market_data import MarketDataFeed, MarketDataUpdate
from core.position_manager import PositionManager
from core.trading_engine import OrderSide, OrderType, TradingEngine


class MomentumStrategy:
    """
    Simple momentum-based trading strategy.

    This strategy calculates momentum based on recent price movements
    and generates trading signals based on momentum strength.
    """

    def __init__(self,
                 trading_engine: TradingEngine,
                 market_data: MarketDataFeed,
                 position_manager: PositionManager,
                 symbols: List[str],
                 short_window: int = 5,
                 long_window: int = 20,
                 momentum_threshold: float = 0.01,
                 position_size: float = 100,
                 update_interval: float = 60.0):
        """
        Initialize the momentum strategy.

        Args:
            trading_engine: Trading engine instance
            market_data: Market data feed instance
            position_manager: Position manager instance
            symbols: List of symbols to trade
            short_window: Short moving average window (in minutes)
            long_window: Long moving average window (in minutes)
            momentum_threshold: Momentum threshold for trading signals
            position_size: Default position size (number of shares)
            update_interval: Strategy update interval (in seconds)
        """
        self.trading_engine = trading_engine
        self.market_data = market_data
        self.position_manager = position_manager
        self.symbols = symbols
        self.short_window = short_window
        self.long_window = long_window
        self.momentum_threshold = momentum_threshold
        self.position_size = position_size
        self.update_interval = update_interval

        # Historical price data for momentum calculation
        self.price_history: Dict[str, List[float]] = {
            symbol: [] for symbol in symbols}

        # Strategy state
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)

        # Metrics
        self.signals: Dict[str, Dict] = {}
        self.performance_metrics: Dict[str, float] = {}

    def calculate_momentum(self, symbol: str) -> Optional[float]:
        """
        Calculate momentum indicator for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Momentum indicator or None if insufficient data
        """
        prices = self.price_history.get(symbol, [])

        if len(prices) < self.long_window:
            return None

        # Convert to numpy array for calculations
        prices_array = np.array(prices[-self.long_window:])

        # Calculate short and long moving averages
        short_ma = np.mean(prices_array[-self.short_window:])
        long_ma = np.mean(prices_array)

        # Calculate momentum as the difference between short and long MAs
        momentum = (short_ma - long_ma) / long_ma

        return momentum

    def generate_signals(self) -> Dict[str, int]:
        """
        Generate trading signals for all symbols.

        Returns:
            Dictionary mapping symbols to signals (1 for buy, -1 for sell, 0 for hold)
        """
        signals = {}

        for symbol in self.symbols:
            momentum = self.calculate_momentum(symbol)

            if momentum is None:
                signals[symbol] = 0  # Not enough data
                continue

            # Generate signal based on momentum
            if momentum > self.momentum_threshold:
                signal = 1  # Buy signal
            elif momentum < -self.momentum_threshold:
                signal = -1  # Sell signal
            else:
                signal = 0  # Hold signal

            signals[symbol] = signal

            # Store signal and momentum data
            self.signals[symbol] = {
                "momentum": momentum,
                "signal": signal,
                "timestamp": time.time()
            }

        return signals

    def execute_signals(self, signals: Dict[str, int]) -> None:
        """
        Execute trading signals.

        Args:
            signals: Dictionary of symbols and their signals
        """
        for symbol, signal in signals.items():
            if signal == 0:
                continue

            # Get current position
            position = self.position_manager.get_position(symbol)
            current_qty = position.quantity

            # Get current market price
            market_price = self.market_data.get_latest_price(symbol)

            if not market_price:
                self.logger.warning(f"No market price available for {symbol}")
                continue

            # Determine order parameters
            order_side = OrderSide.BUY if signal > 0 else OrderSide.SELL

            # Simple position sizing logic
            if signal > 0 and current_qty <= 0:
                # Buy signal with no current position or short position
                order_qty = self.position_size + abs(current_qty)
            elif signal < 0 and current_qty >= 0:
                # Sell signal with no current position or long position
                order_qty = self.position_size + abs(current_qty)
            else:
                # Adding to existing position in the same direction
                order_qty = self.position_size

            # Adjust order quantity sign for sells
            if signal < 0:
                order_qty = -order_qty

            try:
                # Create the order
                order_id = self.trading_engine.create_order(
                    symbol=symbol,
                    side=order_side,
                    quantity=abs(order_qty),
                    order_type=OrderType.MARKET
                )

                # Simulate execution (in a real system, this would come from exchange callbacks)
                self.trading_engine.execute_order(
                    order_id=order_id,
                    execution_price=market_price,
                    execution_quantity=abs(order_qty)
                )

                # Update position
                self.position_manager.add_trade(
                    symbol=symbol,
                    quantity=order_qty,
                    price=market_price,
                    order_id=order_id
                )

                self.logger.info(
                    f"Executed {order_side.name} order for {abs(order_qty)} shares of {symbol} "
                    f"at {market_price:.2f} based on momentum: {self.signals[symbol]['momentum']:.4f}"
                )

            except Exception as e:
                self.logger.error(f"Error executing signal for {symbol}: {e}")

    def on_market_data(self, data: MarketDataUpdate) -> None:
        """
        Handle market data updates.

        Args:
            data: Market data update
        """
        symbol = data.symbol

        if symbol not in self.price_history:
            self.price_history[symbol] = []

        # Add price to history
        self.price_history[symbol].append(data.last_price)

        # Keep history length reasonable
        max_history = max(100, self.long_window * 3)
        if len(self.price_history[symbol]) > max_history:
            self.price_history[symbol] = self.price_history[symbol][-max_history:]

        # Update position
        self.position_manager.update_prices(symbol, data.last_price)

    def update_strategy(self) -> None:
        """Update strategy and generate signals."""
        signals = self.generate_signals()
        self.execute_signals(signals)

        # Update performance metrics
        portfolio_value = self.position_manager.get_total_value()
        pnl = self.position_manager.get_total_pnl()

        self.performance_metrics = {
            "portfolio_value": portfolio_value,
            "total_pnl": pnl,
            "timestamp": time.time()
        }

        self.logger.info(
            f"Strategy updated: Portfolio value: ${portfolio_value:.2f}, P&L: ${pnl:.2f}")

    def _run_updates(self) -> None:
        """Run the strategy update loop."""
        while self.running:
            try:
                self.update_strategy()
            except Exception as e:
                self.logger.error(f"Error updating strategy: {e}")
            time.sleep(self.update_interval)

    def start(self) -> bool:
        """
        Start the strategy.

        Returns:
            True if started, False if already running
        """
        if self.running:
            return False

        # Register for market data updates
        self.market_data.register_callback(self.on_market_data)

        # Add symbols to market data feed
        for symbol in self.symbols:
            # Initialize price history with recent data
            self.market_data.add_symbol(symbol)
            hist_data = self.market_data.get_historical_data(
                symbol=symbol,
                period="1d",
                interval="1m"
            )

            if hist_data is not None and not hist_data.empty:
                # Handle potential multi-index dataframes (for multiple symbols)
                if isinstance(hist_data.columns, pd.MultiIndex):
                    # Get data for this specific symbol
                    if ('Close', symbol) in hist_data.columns:
                        close_prices = hist_data[('Close', symbol)]
                        self.price_history[symbol] = close_prices.dropna(
                        ).tolist()
                    else:
                        self.logger.warning(
                            f"No Close price data found for {symbol}")
                        self.price_history[symbol] = []
                else:
                    # Single symbol data
                    if 'Close' in hist_data.columns:
                        close_prices = hist_data['Close']
                        self.price_history[symbol] = close_prices.dropna(
                        ).tolist()
                    else:
                        self.logger.warning(
                            f"No Close price data found for {symbol}")
                        self.price_history[symbol] = []

        # Start strategy update loop
        self.running = True
        self.update_thread = threading.Thread(
            target=self._run_updates, daemon=True)
        self.update_thread.start()

        self.logger.info(
            f"Started momentum strategy with {len(self.symbols)} symbols")
        return True

    def stop(self) -> bool:
        """
        Stop the strategy.

        Returns:
            True if stopped, False if not running
        """
        if not self.running:
            return False

        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
            self.update_thread = None

        self.logger.info("Stopped momentum strategy")
        return True

    def get_status(self) -> Dict:
        """
        Get the current status of the strategy.

        Returns:
            Dictionary with strategy status information
        """
        return {
            "running": self.running,
            "symbols": self.symbols,
            "signals": self.signals,
            "performance": self.performance_metrics,
            "parameters": {
                "short_window": self.short_window,
                "long_window": self.long_window,
                "momentum_threshold": self.momentum_threshold,
                "position_size": self.position_size,
                "update_interval": self.update_interval
            }
        }
