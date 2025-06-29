"""
Tests for the market data module
"""
from core.market_data import MarketDataFeed, MarketDataUpdate
import sys
import os
import unittest
import time
import pandas as pd
import numpy as np
from pathlib import Path

# Add the parent directory to sys.path to be able to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the module


class TestMarketData(unittest.TestCase):
    """Tests for market data functionality"""

    def setUp(self):
        """Set up test environment"""
        self.market_data = MarketDataFeed(
            update_interval=1.0, use_mock_data=True)

    def tearDown(self):
        """Tear down test environment"""
        if self.market_data.running:
            self.market_data.stop()

    def test_initialization(self):
        """Test market data feed initialization"""
        # Check default values
        self.assertEqual(self.market_data.update_interval, 1.0)
        self.assertTrue(self.market_data.use_mock_data)
        self.assertEqual(self.market_data.mock_scenario, "normal")
        self.assertFalse(self.market_data.running)

    def test_add_remove_symbol(self):
        """Test adding and removing symbols"""
        # Add a symbol
        result = self.market_data.add_symbol("AAPL")
        self.assertTrue(result)
        self.assertEqual(len(self.market_data.symbols), 1)
        self.assertIn("AAPL", self.market_data.symbols)

        # Add the same symbol again (should fail)
        result = self.market_data.add_symbol("AAPL")
        self.assertFalse(result)
        self.assertEqual(len(self.market_data.symbols), 1)

        # Add another symbol
        result = self.market_data.add_symbol("MSFT")
        self.assertTrue(result)
        self.assertEqual(len(self.market_data.symbols), 2)

        # Remove a symbol
        result = self.market_data.remove_symbol("AAPL")
        self.assertTrue(result)
        self.assertEqual(len(self.market_data.symbols), 1)
        self.assertNotIn("AAPL", self.market_data.symbols)

        # Remove a non-existent symbol
        result = self.market_data.remove_symbol("XYZ")
        self.assertFalse(result)

    def test_get_historical_data(self):
        """Test getting historical data"""
        # Add a symbol
        self.market_data.add_symbol("AAPL")

        # Get historical data
        data = self.market_data.get_historical_data(
            "AAPL", period="1d", interval="5m")

        # Check that data is a DataFrame
        self.assertIsInstance(data, pd.DataFrame)

        # Check that data is not empty
        self.assertFalse(data.empty)

        # Check that data has the expected columns
        self.assertTrue(all(col in data.columns for col in [
                        'Open', 'High', 'Low', 'Close', 'Volume']))

        # Check for no NaN or infinite values
        self.assertFalse(data.isnull().any().any(), "Data contains NaN values")
        self.assertFalse(np.isinf(data.values).any(),
                         "Data contains infinite values")

    def test_start_stop(self):
        """Test starting and stopping the market data feed"""
        # Add a symbol
        self.market_data.add_symbol("AAPL")

        # Start the feed
        result = self.market_data.start()
        self.assertTrue(result)
        self.assertTrue(self.market_data.running)

        # Try to start again (should fail)
        result = self.market_data.start()
        self.assertFalse(result)

        # Wait for an update
        time.sleep(2)

        # Check that data was updated
        self.assertGreaterEqual(len(self.market_data.latest_data), 1)
        self.assertIn("AAPL", self.market_data.latest_data)

        # Stop the feed
        result = self.market_data.stop()
        self.assertTrue(result)
        self.assertFalse(self.market_data.running)

        # Try to stop again (should fail)
        result = self.market_data.stop()
        self.assertFalse(result)

    def test_set_data_source(self):
        """Test switching data sources"""
        # Add a symbol
        self.market_data.add_symbol("AAPL")

        # Set to live data
        self.market_data.set_data_source(False)
        self.assertFalse(self.market_data.use_mock_data)

        # Set back to mock data
        self.market_data.set_data_source(True)
        self.assertTrue(self.market_data.use_mock_data)

    def test_set_mock_scenario(self):
        """Test changing mock scenarios"""
        # Test setting valid scenarios
        for scenario in ["normal", "high", "low", "crash", "rally"]:
            result = self.market_data.set_mock_scenario(scenario)
            self.assertTrue(result)
            self.assertEqual(self.market_data.mock_scenario, scenario)

        # Test setting invalid scenario
        result = self.market_data.set_mock_scenario("invalid")
        self.assertFalse(result)
        # Should still be the last valid scenario
        self.assertEqual(self.market_data.mock_scenario, "rally")

    def test_callbacks(self):
        """Test market data callbacks"""
        # Add a symbol
        self.market_data.add_symbol("AAPL")

        # Create callback
        callback_called = False
        callback_data = None

        def callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data

        # Register callback
        self.market_data.register_callback(callback)

        # Start the feed
        self.market_data.start()

        # Wait for an update
        time.sleep(2)

        # Check that callback was called
        self.assertTrue(callback_called)
        self.assertIsInstance(callback_data, MarketDataUpdate)
        self.assertEqual(callback_data.symbol, "AAPL")

        # Stop the feed
        self.market_data.stop()

    def test_update_with_mock_data(self):
        """Test the update_with_mock_data method directly"""
        # Add symbols
        self.market_data.add_symbol("AAPL")
        self.market_data.add_symbol("MSFT")

        # Call the method directly
        self.market_data._update_with_mock_data(["AAPL", "MSFT"])

        # Check that data was updated
        self.assertEqual(len(self.market_data.latest_data), 2)
        self.assertIn("AAPL", self.market_data.latest_data)
        self.assertIn("MSFT", self.market_data.latest_data)

        # Check that the data is valid
        for symbol, update in self.market_data.latest_data.items():
            self.assertIsInstance(update, MarketDataUpdate)
            self.assertEqual(update.symbol, symbol)
            self.assertIsNotNone(update.last_price)
            self.assertIsNotNone(update.bid_price)
            self.assertIsNotNone(update.ask_price)

            # Check for no NaN or infinite values
            for attr in ['last_price', 'bid_price', 'ask_price', 'volume', 'open_price', 'high_price', 'low_price', 'close_price']:
                value = getattr(update, attr)
                if value is not None:  # Some fields might be None
                    self.assertFalse(np.isnan(value), f"{attr} is NaN")
                    self.assertFalse(np.isinf(value), f"{attr} is infinite")


if __name__ == "__main__":
    unittest.main()
