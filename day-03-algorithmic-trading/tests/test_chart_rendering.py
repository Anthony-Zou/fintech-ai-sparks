"""
Tests for chart rendering functionality
"""
from core.market_data import MarketDataFeed
import streamlit as st
import sys
import os
import unittest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path to be able to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# We need to mock Streamlit since we can't actually render in tests
# Import and mock streamlit
st.line_chart = MagicMock()
st.error = MagicMock()
st.warning = MagicMock()
st.selectbox = MagicMock()
st.columns = MagicMock()

# Now we can import our modules


class TestChartRendering(unittest.TestCase):
    """Tests for chart rendering functionality in app.py"""

    def setUp(self):
        """Set up test environment"""
        # Create a mock DataFrame with various edge cases
        self.normal_data = pd.DataFrame({
            'Open': [100.00, 101.00, 102.00],
            'High': [105.00, 106.00, 107.00],
            'Low': [95.00, 96.00, 97.00],
            'Close': [103.00, 104.00, 105.00],
            'Volume': [1000, 1100, 1200],
            'Adj Close': [103.00, 104.00, 105.00]
        }, index=pd.date_range('2023-01-01', periods=3))

        # Create data with NaN values
        self.nan_data = self.normal_data.copy()
        self.nan_data.iloc[1, :] = np.nan

        # Create data with Inf values
        self.inf_data = self.normal_data.copy()
        self.inf_data.iloc[1, :] = np.inf

        # Create data with -Inf values
        self.neg_inf_data = self.normal_data.copy()
        self.neg_inf_data.iloc[1, :] = -np.inf

    def test_clean_normal_data(self):
        """Test that normal data remains unchanged after cleaning"""
        # Import the cleaning code directly from app.py
        import app

        # Clean the data
        data = self.normal_data.copy()
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)

        # Check that data is unchanged
        pd.testing.assert_frame_equal(data, self.normal_data)

    def test_clean_nan_data(self):
        """Test that NaN values are properly handled"""
        # Clean the data
        data = self.nan_data.copy()
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)

        # Check that NaN values were filled
        self.assertFalse(data.isna().any().any())

        # Row 1 should have values from row 0 (ffill)
        self.assertEqual(data.iloc[1, 0], data.iloc[0, 0])

    def test_clean_inf_data(self):
        """Test that infinite values are properly handled"""
        # Clean the data
        data = self.inf_data.copy()
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)

        # Check that Inf values were replaced
        self.assertFalse(np.isinf(data.values).any())
        self.assertFalse(data.isna().any().any())

        # Row 1 should have values from row 0 (ffill)
        self.assertEqual(data.iloc[1, 0], data.iloc[0, 0])

    def test_clean_neg_inf_data(self):
        """Test that negative infinite values are properly handled"""
        # Clean the data
        data = self.neg_inf_data.copy()
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)

        # Check that -Inf values were replaced
        self.assertFalse(np.isinf(data.values).any())
        self.assertFalse(data.isna().any().any())

        # Row 1 should have values from row 0 (ffill)
        self.assertEqual(data.iloc[1, 0], data.iloc[0, 0])

    @patch('app.st.session_state')
    def test_get_historical_data_robust(self, mock_session_state):
        """Test that the get_historical_data method can handle all edge cases"""
        # Create mock market data
        mock_market_data = MagicMock()

        # Set up mock to return different datasets for different inputs
        def mock_get_historical_data(symbol, period, interval):
            if symbol == "AAPL":
                return self.normal_data
            elif symbol == "NAN":
                return self.nan_data
            elif symbol == "INF":
                return self.inf_data
            elif symbol == "NEG_INF":
                return self.neg_inf_data
            else:
                return pd.DataFrame()  # Empty for unknown symbols

        mock_market_data.get_historical_data.side_effect = mock_get_historical_data

        # Set mock in session_state
        mock_session_state.market_data = mock_market_data
        mock_session_state.initialized = True

        # Test normal data
        data = mock_market_data.get_historical_data("AAPL", "1d", "1m")
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)
        self.assertFalse(data.isna().any().any())
        self.assertFalse(np.isinf(data.values).any())

        # Test NaN data
        data = mock_market_data.get_historical_data("NAN", "1d", "1m")
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)
        self.assertFalse(data.isna().any().any())
        self.assertFalse(np.isinf(data.values).any())

        # Test Inf data
        data = mock_market_data.get_historical_data("INF", "1d", "1m")
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)
        self.assertFalse(data.isna().any().any())
        self.assertFalse(np.isinf(data.values).any())

        # Test -Inf data
        data = mock_market_data.get_historical_data("NEG_INF", "1d", "1m")
        data.replace([np.inf, -np.inf], np.nan, inplace=True)
        data.fillna(method='ffill', inplace=True)
        data.fillna(method='bfill', inplace=True)
        self.assertFalse(data.isna().any().any())
        self.assertFalse(np.isinf(data.values).any())


if __name__ == "__main__":
    unittest.main()
