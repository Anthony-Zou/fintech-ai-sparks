"""
Tests for the mock data module
"""
from utils.mock_data import (
    generate_mock_market_data,
    generate_market_scenario,
    clear_mock_data_cache,
    VOLATILITY_PROFILES
)
import sys
import os
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

# Add the parent directory to sys.path to be able to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the module


class TestMockData(unittest.TestCase):
    """Tests for mock data generation"""

    def setUp(self):
        """Set up test environment"""
        clear_mock_data_cache()

    def test_generate_mock_market_data(self):
        """Test basic mock data generation for a single symbol"""
        symbol = "AAPL"
        data = generate_mock_market_data(symbol)

        # Check that data is a DataFrame
        self.assertIsInstance(data, pd.DataFrame)

        # Check that data is not empty
        self.assertFalse(data.empty)

        # Check that data has the expected columns
        self.assertTrue(all(col in data.columns for col in [
                        'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']))

        # Check for no NaN or infinite values
        self.assertFalse(data.isnull().any().any(), "Data contains NaN values")
        self.assertFalse(np.isinf(data.values).any(),
                         "Data contains infinite values")

        # Check that High is always >= Low
        self.assertTrue((data['High'] >= data['Low']).all())

    def test_different_symbols_have_different_prices(self):
        """Test that different symbols generate different price ranges"""
        data_aapl = generate_mock_market_data("AAPL")
        data_msft = generate_mock_market_data("MSFT")

        # Check that the price ranges are different
        self.assertNotEqual(
            data_aapl['Close'].mean(), data_msft['Close'].mean())

    def test_consistent_data_between_calls(self):
        """Test that the same data is generated for the same symbol when using cache"""
        data1 = generate_mock_market_data("NVDA", use_cache=True)
        data2 = generate_mock_market_data("NVDA", use_cache=True)

        # Check that the data is the same
        self.assertTrue((data1['Close'] == data2['Close']).all())

        # Clear cache and generate again, should be different
        clear_mock_data_cache()
        data3 = generate_mock_market_data("NVDA", use_cache=True)

        # Data should be different after clearing cache
        # Note: This could fail by random chance, but it's very unlikely
        # Reset index to safely compare values even if indices differ
        self.assertFalse(data1['Close'].reset_index(
            drop=True).equals(data3['Close'].reset_index(drop=True)))

    def test_data_with_different_time_periods(self):
        """Test data generation with different time periods"""
        data_1d = generate_mock_market_data("AAPL", period="1d")
        data_5d = generate_mock_market_data("AAPL", period="5d")

        # 5d should generally have more data points than 1d
        self.assertTrue(len(data_5d) > len(data_1d))

    def test_market_scenarios(self):
        """Test different market scenarios"""
        symbols = ["AAPL", "MSFT", "GOOGL"]

        # Test normal scenario
        scenario_normal = generate_market_scenario(symbols, "normal")

        # Check that the result includes data for all symbols
        self.assertEqual(len(scenario_normal), len(symbols))

        # Test crash scenario
        scenario_crash = generate_market_scenario(symbols, "crash")

        # In a crash scenario, end prices should generally be lower than start prices
        for symbol, data in scenario_crash.items():
            self.assertTrue(data['Close'].iloc[-1] < data['Close'].iloc[0])

        # Test rally scenario
        scenario_rally = generate_market_scenario(symbols, "rally")

        # In a rally scenario, end prices should generally be higher than start prices
        for symbol, data in scenario_rally.items():
            self.assertTrue(data['Close'].iloc[-1] > data['Close'].iloc[0])

    def test_volatility_differences(self):
        """Test that different volatility settings produce different price variations"""
        # Clear the cache first to ensure fresh data generation
        clear_mock_data_cache()

        # Use separate symbols to avoid any caching issues
        data_low = generate_mock_market_data(
            "LOW_VOL", volatility_factor=0.1, use_cache=False)

        # Clear cache again to ensure separation
        clear_mock_data_cache()

        # Use extremely high volatility
        data_high = generate_mock_market_data(
            "HIGH_VOL", volatility_factor=5.0, use_cache=False)

        # Measure the price range (high/low difference) as a percentage of price
        # This is a more reliable measure of volatility than standard deviation
        range_low = ((data_low['High'] - data_low['Low']
                      ) / data_low['Close']).mean()
        range_high = (
            (data_high['High'] - data_high['Low']) / data_high['Close']).mean()

        # Print the values to help debug
        print(f"Low volatility range: {range_low}")
        print(f"High volatility range: {range_high}")

        # High volatility should have larger price ranges
        self.assertTrue(range_high > range_low)

    def test_invalid_inputs(self):
        """Test handling of invalid inputs"""
        # Invalid period
        data = generate_mock_market_data("AAPL", period="invalid")
        self.assertFalse(data.empty)

        # Invalid interval
        data = generate_mock_market_data("AAPL", interval="invalid")
        self.assertFalse(data.empty)

        # Invalid scenario
        scenario_data = generate_market_scenario(["AAPL"], "invalid")
        self.assertFalse(scenario_data["AAPL"].empty)

    def test_no_infinite_values(self):
        """Specifically test for absence of infinite values in all scenarios"""
        for scenario in list(VOLATILITY_PROFILES.keys()) + ["invalid"]:
            data = generate_market_scenario(["MSFT", "GOOGL"], scenario)

            for symbol, df in data.items():
                # Check for NaN or Inf values
                self.assertFalse(np.isnan(df.values).any(
                ), f"NaN values found in {scenario} scenario for {symbol}")
                self.assertFalse(np.isinf(df.values).any(
                ), f"Infinite values found in {scenario} scenario for {symbol}")


if __name__ == "__main__":
    unittest.main()
