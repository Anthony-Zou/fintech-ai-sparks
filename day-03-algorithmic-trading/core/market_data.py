"""
Market data module for fetching and streaming real-time price data.
"""
import logging
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional, Set

import pandas as pd
import yfinance as yf

# Import mock data generator for fallback when API fails
from utils.mock_data import generate_mock_market_data, generate_market_scenario, VOLATILITY_PROFILES


@dataclass
class MarketDataUpdate:
    """Market data update event."""
    symbol: str
    timestamp: datetime
    last_price: float
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    volume: Optional[int] = None
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None


class MarketDataFeed:
    """
    Real-time market data feed using Yahoo Finance.
    """

    def __init__(self, update_interval: float = 5.0, use_mock_data: bool = False,
                 max_retries: int = 3, retry_delay: float = 1.0,
                 mock_scenario: str = "normal"):
        """
        Initialize the market data feed.

        Args:
            update_interval: Interval in seconds between data updates
            use_mock_data: Whether to use mock data instead of live data (default: False)
            max_retries: Maximum number of API call retries on failure (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
            mock_scenario: Market scenario to use when in mock mode ("normal", "high", "low", "crash", "rally")
        """
        self.symbols: Set[str] = set()
        self.update_interval = update_interval
        self.running = False
        self.update_thread: Optional[threading.Thread] = None
        self.callbacks: List[Callable[[MarketDataUpdate], None]] = []
        self.latest_data: Dict[str, MarketDataUpdate] = {}
        self.logger = logging.getLogger(__name__)
        self.use_mock_data = use_mock_data
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.api_error_count = 0
        # After this many consecutive errors, switch to mock data
        self.api_error_threshold = 5

        # Mock data configuration
        self.mock_scenario = mock_scenario if mock_scenario in VOLATILITY_PROFILES else "normal"
        self.mock_data_cache: Dict[str, pd.DataFrame] = {}

    def add_symbol(self, symbol: str) -> bool:
        """
        Add a symbol to the market data feed.

        Args:
            symbol: Trading symbol to add

        Returns:
            True if symbol was added, False if already present
        """
        if symbol in self.symbols:
            return False

        self.symbols.add(symbol)
        self.logger.info(f"Added symbol {symbol} to market data feed")
        return True

    def remove_symbol(self, symbol: str) -> bool:
        """
        Remove a symbol from the market data feed.

        Args:
            symbol: Trading symbol to remove

        Returns:
            True if symbol was removed, False if not found
        """
        if symbol not in self.symbols:
            return False

        self.symbols.remove(symbol)
        if symbol in self.latest_data:
            del self.latest_data[symbol]

        self.logger.info(f"Removed symbol {symbol} from market data feed")
        return True

    def register_callback(self, callback: Callable[[MarketDataUpdate], None]) -> None:
        """
        Register a callback function for market data updates.

        Args:
            callback: Function to call with each market data update
        """
        self.callbacks.append(callback)
        self.logger.info(
            f"Registered market data callback: {callback.__name__}")

    def get_latest_price(self, symbol: str) -> Optional[float]:
        """
        Get the latest price for a symbol.

        Args:
            symbol: Symbol to get price for

        Returns:
            Latest price or None if not available
        """
        if symbol in self.latest_data:
            return self.latest_data[symbol].last_price
        return None

    def get_latest_data(self, symbol: str) -> Optional[MarketDataUpdate]:
        """
        Get the latest market data for a symbol.

        Args:
            symbol: Symbol to get data for

        Returns:
            Latest market data or None if not available
        """
        return self.latest_data.get(symbol)

    def get_historical_data(self, symbol: str, period: str = "1d",
                            interval: str = "1m") -> Optional[pd.DataFrame]:
        """
        Get historical market data for a symbol.

        Args:
            symbol: Symbol to get data for
            period: Time period (e.g., "1d", "5d", "1mo")
            interval: Data granularity (e.g., "1m", "5m", "1h", "1d")

        Returns:
            DataFrame with historical data or None on error
        """
        # Use mock data if configured to do so
        if self.use_mock_data:
            self.logger.info(
                f"Using mock data for {symbol} (scenario: {self.mock_scenario})")
            # Use the specific volatility factor for the current scenario
            volatility = VOLATILITY_PROFILES.get(self.mock_scenario, 1.0)
            return generate_mock_market_data(
                symbol,
                period,
                interval,
                volatility_factor=volatility
            )

        # Try with retries
        for attempt in range(self.max_retries):
            try:
                data = yf.download(
                    tickers=symbol,
                    period=period,
                    interval=interval,
                    auto_adjust=True,
                    progress=False
                )

                # Check if data is valid
                if data is None or data.empty:
                    if attempt < self.max_retries - 1:
                        self.logger.warning(
                            f"Empty data for {symbol}, retrying ({attempt+1}/{self.max_retries})...")
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        self.logger.warning(
                            f"No data available for {symbol} after {self.max_retries} attempts, using mock data")
                        self.api_error_count += 1
                        return generate_mock_market_data(symbol, period, interval)

                # Reset error counter on success
                self.api_error_count = 0
                return data

            except Exception as e:
                self.logger.error(
                    f"Error fetching historical data for {symbol}: {e}")
                if attempt < self.max_retries - 1:
                    self.logger.warning(
                        f"Retrying ({attempt+1}/{self.max_retries})...")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.warning(f"All retries failed, using mock data")
                    self.api_error_count += 1

        # If API errors are consistent, switch to mock data mode automatically
        if self.api_error_count >= self.api_error_threshold and not self.use_mock_data:
            self.logger.warning(
                f"Too many API errors ({self.api_error_count}), switching to mock data mode")
            self.use_mock_data = True

        # Fall back to mock data
        volatility = VOLATILITY_PROFILES.get(self.mock_scenario, 1.0)
        return generate_mock_market_data(symbol, period, interval, volatility_factor=volatility)

    def _update_data(self) -> None:
        """Update market data for all symbols."""
        if not self.symbols:
            return

        try:
            # Convert set to list for yfinance
            symbol_list = list(self.symbols)

            # Check if we should use mock data
            if self.use_mock_data:
                self._update_with_mock_data(symbol_list)
                return

            # Try to get current data for all symbols using YFinance API
            data = yf.download(
                tickers=symbol_list if len(
                    symbol_list) > 1 else symbol_list[0],
                period="1d",
                interval="1m",
                auto_adjust=True,
                progress=False
            )

            # Process data for each symbol
            now = datetime.now()

            # Handle single symbol case
            if len(symbol_list) == 1:
                symbol = symbol_list[0]
                try:
                    if data.empty:
                        self.logger.warning(f"No data available for {symbol}")
                        return  # Return instead of continue, as we're not in a loop

                    latest = data.iloc[-1]

                    # Handle NaN values, especially for Volume which needs integer conversion
                    volume = latest.get("Volume", 0)
                    volume = 0 if pd.isna(volume) else int(volume)

                    update = MarketDataUpdate(
                        symbol=symbol,
                        timestamp=now,
                        last_price=latest["Close"],
                        # Simulated bid (slightly lower)
                        bid_price=latest["Close"] * 0.9999,
                        # Simulated ask (slightly higher)
                        ask_price=latest["Close"] * 1.0001,
                        volume=volume,
                        open_price=latest["Open"],
                        high_price=latest["High"],
                        low_price=latest["Low"],
                        close_price=latest["Close"]
                    )

                    self.latest_data[symbol] = update

                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(update)
                        except Exception as e:
                            self.logger.error(
                                f"Error in market data callback: {e}")
                except Exception as e:
                    self.logger.error(
                        f"Error processing data for {symbol}: {e}")
            else:
                # Multiple symbols case
                for symbol in symbol_list:
                    try:
                        if symbol not in data.columns.levels[1]:
                            self.logger.warning(
                                f"No data available for {symbol}")
                            continue

                        symbol_data = data.xs(symbol, level=1, axis=1)
                        if symbol_data.empty:
                            continue

                        latest = symbol_data.iloc[-1]

                        # Handle NaN values, especially for Volume which needs integer conversion
                        volume = latest.get("Volume", 0)
                        volume = 0 if pd.isna(volume) else int(volume)

                        update = MarketDataUpdate(
                            symbol=symbol,
                            timestamp=now,
                            last_price=latest["Close"],
                            bid_price=latest["Close"] * 0.9999,
                            ask_price=latest["Close"] * 1.0001,
                            volume=volume,
                            open_price=latest["Open"],
                            high_price=latest["High"],
                            low_price=latest["Low"],
                            close_price=latest["Close"]
                        )

                        self.latest_data[symbol] = update

                        # Notify callbacks
                        for callback in self.callbacks:
                            try:
                                callback(update)
                            except Exception as e:
                                self.logger.error(
                                    f"Error in market data callback for {symbol}: {e}")
                    except Exception as e:
                        self.logger.error(
                            f"Error processing data for {symbol}: {e}")

        except Exception as e:
            self.logger.error(f"Error updating market data: {e}")
            self.api_error_count += 1

            # If we've had too many consecutive errors, switch to mock data mode
            if self.api_error_count >= self.api_error_threshold and not self.use_mock_data:
                self.logger.warning(
                    f"Too many consecutive API errors ({self.api_error_count}), switching to mock data mode")
                self.use_mock_data = True
                # Now update with mock data instead
                self._update_with_mock_data(list(self.symbols))
            elif self.api_error_count >= 1:  # Even on first error, provide mock data for this update
                self.logger.warning(
                    f"API error occurred, falling back to mock data for this update")
                self._update_with_mock_data(list(self.symbols))

    def _run_updates(self) -> None:
        """Run the update loop."""
        while self.running:
            self._update_data()
            time.sleep(self.update_interval)

    def start(self) -> bool:
        """
        Start the market data feed.

        Returns:
            True if started, False if already running
        """
        if self.running:
            return False

        self.running = True
        self.update_thread = threading.Thread(
            target=self._run_updates, daemon=True)
        self.update_thread.start()
        self.logger.info(
            f"Started market data feed with {len(self.symbols)} symbols")
        return True

    def stop(self) -> bool:
        """
        Stop the market data feed.

        Returns:
            True if stopped, False if not running
        """
        if not self.running:
            return False

        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
            self.update_thread = None

        self.logger.info("Stopped market data feed")
        return True

    def set_data_source(self, use_mock: bool) -> None:
        """
        Switch between live and mock data sources.

        Args:
            use_mock: True to use mock data, False to use live data
        """
        if self.use_mock_data != use_mock:
            self.use_mock_data = use_mock
            self.api_error_count = 0  # Reset error count
            self.logger.info(
                f"Switched to {'mock' if use_mock else 'live'} data source")
            # Force an immediate update with the new data source
            if self.running:
                self._update_data()

    def set_mock_scenario(self, scenario: str) -> bool:
        """
        Change the mock data market scenario.

        Args:
            scenario: Market scenario ("normal", "high", "low", "crash", "rally")

        Returns:
            True if scenario was valid and set, False otherwise
        """
        if scenario not in VOLATILITY_PROFILES:
            self.logger.error(
                f"Invalid scenario: {scenario}. Must be one of: {', '.join(VOLATILITY_PROFILES.keys())}")
            return False

        self.mock_scenario = scenario
        self.logger.info(
            f"Set mock data scenario to '{scenario}' (volatility={VOLATILITY_PROFILES[scenario]:.1f}x)")

        # Clear mock data cache to force regeneration with new scenario
        self.mock_data_cache = {}

        # If using mock data, update immediately with new scenario
        if self.use_mock_data and self.running:
            self._update_data()

        return True

    def _update_with_mock_data(self, symbol_list: List[str]) -> None:
        """
        Update market data using mock data generator with the current scenario.

        Args:
            symbol_list: List of symbols to update
        """
        self.logger.info(
            f"Using mock data for {len(symbol_list)} symbols (scenario: {self.mock_scenario})")
        now = datetime.now()

        try:
            # Generate market data for all symbols at once using the current scenario
            # This ensures coordinated market movements according to the scenario
            market_data = generate_market_scenario(
                symbol_list,
                scenario=self.mock_scenario
            )

            # Update market data for each symbol
            for symbol, mock_df in market_data.items():
                try:
                    if mock_df.empty:
                        self.logger.warning(
                            f"Failed to generate mock data for {symbol}")
                        continue

                    latest = mock_df.iloc[-1]

                    # Create market data update from mock data
                    volume = latest.get("Volume", 0)
                    volume = 0 if pd.isna(volume) else int(volume)

                    # Calculate realistic bid/ask spread based on price and volatility
                    price = latest["Close"]
                    volatility = VOLATILITY_PROFILES.get(
                        self.mock_scenario, 1.0)

                    # Higher priced stocks have wider spreads in absolute terms but narrower in percentage
                    if price < 10:
                        spread_pct = 0.002 * volatility  # 0.2% for low-priced stocks
                    elif price < 50:
                        spread_pct = 0.0012 * volatility  # 0.12% for mid-priced stocks
                    elif price < 200:
                        spread_pct = 0.0008 * volatility  # 0.08% for high-priced stocks
                    else:
                        spread_pct = 0.0005 * volatility  # 0.05% for very high-priced stocks

                    half_spread = price * spread_pct / 2

                    update = MarketDataUpdate(
                        symbol=symbol,
                        timestamp=now,
                        last_price=price,
                        bid_price=price - half_spread,
                        ask_price=price + half_spread,
                        volume=volume,
                        open_price=latest["Open"],
                        high_price=latest["High"],
                        low_price=latest["Low"],
                        close_price=latest["Close"]
                    )

                    self.latest_data[symbol] = update

                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(update)
                        except Exception as e:
                            self.logger.error(
                                f"Error in market data callback for {symbol}: {e}")

                except Exception as e:
                    self.logger.error(
                        f"Error processing mock data for {symbol}: {e}")

        except Exception as e:
            self.logger.error(f"Error generating mock market scenario: {e}")

            # Fall back to individual symbol generation if the scenario generation fails
            for symbol in symbol_list:
                try:
                    # Generate individual mock data
                    mock_df = generate_mock_market_data(
                        symbol, period="1d", interval="1m")

                    if mock_df.empty:
                        continue

                    latest = mock_df.iloc[-1]

                    volume = latest.get("Volume", 0)
                    volume = 0 if pd.isna(volume) else int(volume)

                    update = MarketDataUpdate(
                        symbol=symbol,
                        timestamp=now,
                        last_price=latest["Close"],
                        bid_price=latest["Close"] * 0.9999,
                        ask_price=latest["Close"] * 1.0001,
                        volume=volume,
                        open_price=latest["Open"],
                        high_price=latest["High"],
                        low_price=latest["Low"],
                        close_price=latest["Close"]
                    )

                    self.latest_data[symbol] = update

                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            callback(update)
                        except Exception as e:
                            self.logger.error(
                                f"Error in market data callback for {symbol}: {e}")
                except Exception as e:
                    self.logger.error(
                        f"Error generating mock data for {symbol}: {e}")

        self.logger.info("Mock data update completed")
