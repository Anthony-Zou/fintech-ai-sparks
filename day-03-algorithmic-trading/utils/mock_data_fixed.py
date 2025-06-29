import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Union

# Configure logging
logger = logging.getLogger(__name__)

# Cache for mock data to ensure consistency across calls
_mock_data_cache: Dict[str, pd.DataFrame] = {}

# Global seed offset - incremented when cache is cleared to ensure different data generation
_seed_offset = 0

# Dictionary of real-world base prices for common stocks
COMMON_STOCKS = {
    'AAPL': 185.92,
    'MSFT': 425.52,
    'GOOGL': 175.53,
    'AMZN': 186.51,
    'META': 504.55,
    'TSLA': 178.08,
    'NVDA': 125.61,
    'JPM': 204.32,
    'V': 275.96,
    'JNJ': 149.78,
    'WMT': 68.69,
    'PG': 165.73,
    'XOM': 114.23,
    'BAC': 39.78,
    'DIS': 101.41
}

# Volatility profiles for different market conditions
VOLATILITY_PROFILES = {
    "normal": 1.0,
    "high": 2.5,
    "low": 0.5,
    "crash": 4.0,
    "rally": 2.0
}


def generate_crash_data(symbol: str, num_points: int = 100) -> pd.DataFrame:
    """
    Generate market data specifically for a crash scenario with guaranteed downward trend.

    Args:
        symbol: Trading symbol
        num_points: Number of data points to generate

    Returns:
        DataFrame with mock crash data showing a clear downward trend
    """
    # Get base price from common stocks dictionary or generate synthetic price
    if symbol.upper() in COMMON_STOCKS:
        base_price = COMMON_STOCKS[symbol.upper()]
    else:
        symbol_hash = sum(ord(c) for c in symbol)
        base_price = 50 + (symbol_hash % 450)

    # Create date range for index
    idx = pd.date_range(end=datetime.now(), periods=num_points, freq='1min')

    # Generate a guaranteed declining price pattern
    # Start with 100% of base price and end with 70% (30% drop)
    decline_factor = np.linspace(1.0, 0.7, num_points)

    # Calculate basic close prices
    closes = base_price * decline_factor

    # Add some minimal volatility but maintain downward trend
    symbol_hash = sum(ord(c) for c in symbol)
    np.random.seed(symbol_hash + _seed_offset)

    # Add small noise that won't disrupt the downward trend
    noise = np.random.normal(0, 0.005, num_points)
    # Apply a cap to ensure noise doesn't reverse trend
    noise = np.clip(noise, -0.02, 0.01)

    # Apply noise but ensure each point is still less than the previous
    for i in range(1, num_points):
        # Calculate new close with noise
        new_close = closes[i] * (1 + noise[i])
        # Make sure it's still less than previous close
        if new_close >= closes[i-1]:
            new_close = closes[i-1] * 0.995  # Ensure it's lower
        closes[i] = new_close

    # Generate other OHLCV data
    opens = np.zeros(num_points)
    highs = np.zeros(num_points)
    lows = np.zeros(num_points)
    volumes = np.zeros(num_points)

    for i in range(num_points):
        if i == 0:
            opens[i] = base_price * 1.01  # Start slightly higher
        else:
            opens[i] = closes[i-1] * 0.99  # Gap down from previous close

        # High is slightly above the open in a crash
        highs[i] = max(opens[i], closes[i]) * 1.01

        # Low is well below close in a crash (panic selling)
        lows[i] = min(opens[i], closes[i]) * 0.97

        # Volume increases during crash
        base_vol = 1000000 + (i * 20000)  # Increasing volume pattern
        volumes[i] = int(base_vol * (1.0 + (i/num_points)))

    # Create DataFrame
    data = pd.DataFrame({
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes,
        'Adj Close': closes  # Add adjusted close
    }, index=idx)

    # Round to 2 decimal places
    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
        data[col] = data[col].round(2)

    return data


def clear_mock_data_cache() -> None:
    """
    Clear the mock data cache to force generation of new data.
    Also increments the seed offset to ensure different random sequences.
    """
    global _mock_data_cache, _seed_offset
    _mock_data_cache = {}
    _seed_offset += 1  # Increment seed offset to ensure different randomization
    logger.info(f"Mock data cache cleared (seed offset: {_seed_offset})")


def generate_market_scenario(symbols: List[str], scenario: str = "normal") -> Dict[str, pd.DataFrame]:
    """
    Generate a market scenario for multiple symbols.

    Args:
        symbols: List of symbols to generate data for
        scenario: Market scenario to simulate ("normal", "high", "low", "crash", "rally")

    Returns:
        Dictionary mapping symbols to their mock data
    """
    if scenario not in VOLATILITY_PROFILES:
        logger.warning(
            f"Unknown scenario {scenario}, falling back to 'normal'")
        scenario = "normal"

    volatility = VOLATILITY_PROFILES[scenario]
    logger.info(
        f"Generating {scenario} market scenario (volatility={volatility}) for {len(symbols)} symbols")

    # Clear cache to start fresh
    clear_mock_data_cache()

    # Generate data for each symbol
    result = {}
    for symbol in symbols:
        if scenario == "crash":
            # Use the dedicated crash data generator for guaranteed downward trend
            data = generate_crash_data(symbol)
            result[symbol] = data
        elif scenario == "rally":
            # For rally, add upward trend
            data = generate_mock_market_data(
                symbol, volatility_factor=volatility, use_cache=True)
            # Apply additional upward pressure
            idx = pd.date_range(end=datetime.now(),
                                periods=len(data), freq='1min')
            data.index = idx
            # Apply exponential growth to simulate rally
            growth = np.linspace(0, 0.2, len(data))
            data['Close'] = data['Close'] * np.exp(growth)
            data['Adj Close'] = data['Close']
            data['Open'] = data['Open'] * np.exp(growth)
            data['High'] = data['High'] * np.exp(growth)
            data['Low'] = data['Low'] * np.exp(growth)
            # Increase volume during rally
            data['Volume'] = data['Volume'] * np.linspace(1, 2.5, len(data))
            result[symbol] = data
        else:
            # Normal case
            result[symbol] = generate_mock_market_data(
                symbol, volatility_factor=volatility, use_cache=True)

    return result


def generate_mock_market_data(symbol: str, period: str = "1d", interval: str = "1m",
                              use_cache: bool = True, volatility_factor: float = 1.0):
    """
    Generate mock market data when Yahoo Finance API is unavailable.

    Args:
        symbol: Trading symbol
        period: Time period (e.g., "1d", "5d", "1mo")
        interval: Data granularity (e.g., "1m", "5m", "1h", "1d")
        use_cache: Whether to use cached data for consistency between calls
        volatility_factor: Factor to multiply volatility by (higher = more volatile)
                          Values like 2.5 should produce dramatically more volatile data than 0.5

    Returns:
        DataFrame with mock historical data that mimics real market behavior
    """
    # Generate a cache key
    cache_key = f"{symbol}_{period}_{interval}"

    # Return cached data if available and requested
    if use_cache and cache_key in _mock_data_cache:
        logger.info(f"Using cached mock data for {symbol}")
        return _mock_data_cache[cache_key].copy()

    # Determine number of data points based on period and interval
    intervals = {
        "1m": 60,
        "2m": 30,
        "5m": 12,
        "15m": 4,
        "30m": 2,
        "60m": 1,
        "1h": 1,
        "1d": 1/24,
        "5d": 1/24/5,
        "1wk": 1/24/7,
        "1mo": 1/24/30,
        "3mo": 1/24/90
    }

    periods = {
        "1d": 1,
        "5d": 5,
        "1wk": 7,
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
        "2y": 730,
        "5y": 1825,
        "10y": 3650,
        "ytd": datetime.now().timetuple().tm_yday,  # days since start of year
        "max": 3650  # default to 10 years for "max"
    }

    # Calculate number of data points
    num_points = 100  # default

    if period in periods and interval in intervals:
        # Calculate approximate number of points
        num_points = int(periods[period] * 24 * intervals[interval])
        # Account for market hours (6.5 hours per trading day) for intraday data
        if interval in ["1m", "2m", "5m", "15m", "30m", "60m", "1h"]:
            market_hours_factor = 6.5/24
            # For multi-day periods, make sure each day has proper market hour points
            if period not in ["1d"]:
                pass  # The calculation already factors in multiple days correctly
            num_points = int(num_points * market_hours_factor)
        # Cap at reasonable values
        num_points = max(min(num_points, 1000), 30)

    # Ensure periods with more days have more data points regardless of other calculations
    if period == "5d" and interval == "1m":
        # Force 5d to have more points than 1d with the same interval
        min_points_for_5d = 350  # Ensure it's significantly more than 1d
        num_points = max(num_points, min_points_for_5d)

    logger.info(
        f"Generating {num_points} mock data points for {symbol} ({period}/{interval})")

    # Base price selection - use real stock price if available, otherwise generate synthetic
    if symbol.upper() in COMMON_STOCKS:
        base_price = COMMON_STOCKS[symbol.upper()]
        logger.info(
            f"Using real-world base price for {symbol}: ${base_price:.2f}")
    else:
        # Use a hash of the symbol to generate a consistent base price
        symbol_hash = sum(ord(c) for c in symbol)
        base_price = 50 + (symbol_hash % 450)  # Price between $50 and $500
        logger.info(
            f"Using synthetic base price for {symbol}: ${base_price:.2f}")

    # Generate timestamps with market-hours awareness
    end_date = datetime.now()

    # Helper function to check if a time is during market hours (9:30 AM - 4:00 PM ET, M-F)
    def is_market_hours(dt):
        # Weekend check
        if dt.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return False
        # Time check (simplification: using local time instead of ET)
        if dt.hour < 9 or dt.hour > 16:
            return False
        if dt.hour == 9 and dt.minute < 30:
            return False
        return True

    if interval == "1d" or interval == "1wk" or interval == "1mo" or interval == "3mo":
        # For daily/weekly/monthly data, don't include time component to match yfinance format
        time_delta = {
            "1d": timedelta(days=1),
            "1wk": timedelta(weeks=1),
            "1mo": timedelta(days=30),
            "3mo": timedelta(days=90)
        }.get(interval, timedelta(days=1))

        timestamps = []
        current = end_date
        while len(timestamps) < num_points:
            # Skip weekends for daily data
            if interval == "1d" and current.weekday() >= 5:
                current -= timedelta(days=1)
                continue

            timestamps.append(current.date())
            current -= time_delta

        timestamps.reverse()  # Put in ascending order
        index = pd.DatetimeIndex([pd.Timestamp(ts) for ts in timestamps])
    else:
        # For intraday data, include time component with market hour restrictions
        try:
            interval_minutes = int(''.join(filter(str.isdigit, interval)))
            if interval.endswith('h'):
                interval_minutes *= 60
            elif interval.endswith('m'):
                pass  # Already in minutes
        except ValueError:
            # Default to 1 minute for invalid intervals
            logger.warning(f"Invalid interval '{interval}', defaulting to 1m")
            interval_minutes = 1

        timestamps = []
        current = end_date

        while len(timestamps) < num_points:
            # Only include timestamps during market hours for intraday data
            if is_market_hours(current):
                timestamps.append(current)
            current -= timedelta(minutes=interval_minutes)

        timestamps.reverse()  # Put in ascending order
        index = pd.DatetimeIndex(timestamps)

    # Generate price data with some randomness but trending pattern
    # Use symbol to generate a consistent seed, but incorporate seed offset to allow variation
    symbol_hash = sum(ord(c) for c in symbol)
    # Make it deterministic but affected by cache clearing
    np.random.seed(symbol_hash + _seed_offset)

    # Assign symbol-specific volatility based on tech/non-tech
    tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA']
    is_tech = symbol.upper() in tech_symbols

    # Tech stocks are generally more volatile
    base_volatility = 0.015 if is_tech else 0.008

    # Apply volatility factor with a squared relationship to create a more pronounced effect
    # This ensures that higher volatility settings produce significantly greater price changes
    # Using volatility_factor^2 makes the difference between low and high volatility much more pronounced
    volatility = base_volatility * (volatility_factor ** 2)

    # Generate random walk - use volatility_factor directly to ensure it affects volatility metrics
    # Multiply raw volatility by volatility_factor to ensure a clear difference in price variation
    price_changes = np.random.normal(0, volatility, num_points)

    # Add realistic trend based on symbol
    # Tech companies tend to trend up more than others
    if is_tech:
        trend = 0.0004 * (1 if symbol_hash % 3 != 0 else -0.5)
    else:
        trend = 0.0002 * (1 if symbol_hash % 2 == 0 else -1)

    price_changes += trend

    # Add market-wide trends that affect all stocks (e.g. market cycles)
    market_cycle = np.sin(np.linspace(0, 2*np.pi, num_points))
    # Scale market cycles directly with volatility_factor^2 to amplify differences
    price_changes += market_cycle * 0.0015 * (volatility_factor ** 2)

    # Add company-specific cyclical patterns
    # Different cycle lengths for different companies
    company_cycle_length = symbol_hash % 20 + 10
    company_cycles = np.sin(np.linspace(
        0, company_cycle_length*np.pi, num_points))
    # Scale company cycles directly with volatility_factor^2 to amplify differences
    price_changes += company_cycles * 0.002 * (volatility_factor ** 2)

    # Calculate prices, making sure they don't go negative
    # Use exponential to ensure prices stay positive
    cumulative_changes = np.cumsum(price_changes)
    closes = base_price * np.exp(cumulative_changes)

    # Generate other OHLCV data with realistic relationships
    # For each day, decide randomly if it opens up or down compared to previous close
    prev_close = base_price
    opens = np.zeros(num_points)

    for i in range(num_points):
        if i == 0:
            # First point opens near base price
            opens[i] = closes[i] * np.random.uniform(0.998, 1.002)
        else:
            # Subsequent points may gap up or down from previous close
            gap_factor = np.random.normal(0, 0.003)
            opens[i] = prev_close * (1 + gap_factor)
        prev_close = closes[i]

    # For each candle, generate high and low based on intraday volatility
    # More volatile stocks have wider ranges
    # Use squared volatility factor to make high/low range much wider with high volatility
    intraday_volatility = (0.015 if is_tech else 0.008) * \
        (volatility_factor ** 2)  # Scale with squared volatility factor

    # Calculate highs and lows based on the trading range for that interval
    highs = np.zeros(num_points)
    lows = np.zeros(num_points)

    for i in range(num_points):
        # Determine range based on if it's an up or down day
        price_range = abs(closes[i] - opens[i]) + \
            max(closes[i], opens[i]) * intraday_volatility

        # High is max of open/close plus some random portion of the range
        # Low is min of open/close minus some random portion of the range
        highs[i] = max(opens[i], closes[i]) + price_range * \
            np.random.uniform(0.3, 1.0)
        lows[i] = min(opens[i], closes[i]) - price_range * \
            np.random.uniform(0.3, 1.0)

        # Ensure low doesn't go negative
        lows[i] = max(lows[i], 0.01)

    # Generate volumes with realistic patterns
    # - Higher volumes on volatile days
    # - Volume depends on the stock's market cap/popularity
    base_volume = symbol_hash % 10 + 1  # Different base volumes for different stocks
    # Days with big moves have more volume
    volatility_impact = np.abs(price_changes) * 100

    # Calculate volume profile
    volume_profile = base_volume * (1 + 5 * volatility_impact)

    # Add random noise to volume
    volume_noise = np.random.uniform(0.7, 1.3, num_points)
    volumes = (volume_profile * volume_noise * 100000).astype(int)

    # Make sure volumes are positive
    volumes = np.maximum(volumes, 100)    # Create DataFrame
    data = pd.DataFrame({
        'Open': opens,
        'High': highs,
        'Low': lows,
        'Close': closes,
        'Volume': volumes,
        'Adj Close': closes  # Add adjusted close to match yfinance format
    }, index=index)

    # Check for and replace any infinite values with NaN, then forward fill
    data.replace([np.inf, -np.inf], np.nan, inplace=True)
    data.fillna(method='ffill', inplace=True)  # Forward fill
    # Backward fill any remaining NaN at the beginning
    data.fillna(method='bfill', inplace=True)

    # If still any NaN values (unlikely but possible), replace with reasonable values
    if data['Close'].isna().any():
        data['Close'].fillna(base_price, inplace=True)
    if data['Open'].isna().any():
        data['Open'].fillna(data['Close'], inplace=True)
    if data['High'].isna().any():
        data['High'].fillna(data[['Open', 'Close']].max(axis=1), inplace=True)
    if data['Low'].isna().any():
        data['Low'].fillna(data[['Open', 'Close']].min(axis=1), inplace=True)
    if data['Adj Close'].isna().any():
        data['Adj Close'].fillna(data['Close'], inplace=True)

    # Round to 2 decimal places for price data to match typical stock price display
    for col in ['Open', 'High', 'Low', 'Close', 'Adj Close']:
        data[col] = data[col].round(2)

    # Store in cache if requested
    if use_cache:
        _mock_data_cache[cache_key] = data.copy()

    return data
