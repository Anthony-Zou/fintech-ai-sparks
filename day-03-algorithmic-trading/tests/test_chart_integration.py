"""
Integration test for chart rendering - specifically testing for the infinite extent warnings
"""
from utils.mock_data import generate_mock_market_data
import sys
import os
import unittest
import pandas as pd
import numpy as np
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the necessary modules


class TestChartIntegration(unittest.TestCase):
    """Tests to verify that the chart rendering handles problematic data correctly"""

    def test_clean_dataframe_with_inf_values(self):
        """Test cleaning a dataframe with infinite values"""
        # Create a test dataframe with some infinite values
        df = pd.DataFrame({
            'Open': [100.0, np.inf, 102.0, 103.0],
            'High': [105.0, 106.0, np.inf, 107.0],
            'Low': [95.0, -np.inf, 97.0, 98.0],
            'Close': [103.0, 104.0, 105.0, np.inf],
            'Volume': [1000, 1100, 1200, 1300],
            'Adj Close': [103.0, np.inf, 105.0, 106.0]
        }, index=pd.date_range('2023-01-01', periods=4))

        # Clean the dataframe similar to how the app does it
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.fillna(method='ffill', inplace=True)
        df.fillna(method='bfill', inplace=True)

        # Check that there are no infinite values left
        self.assertFalse(np.isinf(df.values).any(),
                         "Dataframe still contains infinite values")

        # Check that there are no NaN values left
        self.assertFalse(df.isna().any().any(),
                         "Dataframe still contains NaN values")

        # Check that values were correctly filled
        # Should be forward filled from previous
        self.assertAlmostEqual(df['Open'].iloc[1], 100.0)
        # Should be forward filled from previous
        self.assertAlmostEqual(df['High'].iloc[2], 106.0)
        # Should be forward filled from previous (95.0, not backward filled to 97.0)
        self.assertAlmostEqual(df['Low'].iloc[1], 95.0)
        # Should be forward filled from previous
        self.assertAlmostEqual(df['Close'].iloc[3], 105.0)

    def test_prepare_chart_data(self):
        """Test preparing data for chart rendering"""
        # Generate some test data
        mock_data = generate_mock_market_data(
            'AAPL', period='1d', interval='5m')

        # Introduce some infinite values to test the cleaning
        mock_data.loc[mock_data.index[2], 'Close'] = np.inf
        mock_data.loc[mock_data.index[5], 'Close'] = -np.inf

        # Clean the data similar to how the app does it
        mock_data.replace([np.inf, -np.inf], np.nan, inplace=True)
        mock_data.fillna(method='ffill', inplace=True)
        mock_data.fillna(method='bfill', inplace=True)

        # Check that there are no infinite values left
        self.assertFalse(np.isinf(mock_data['Close'].values).any(),
                         "Close column still contains infinite values")

        # Prepare data for chart as the app does
        # Final check for any remaining NaN/inf values and set to a reasonable default
        if mock_data["Close"].isna().any() or np.isinf(mock_data["Close"].values).any():
            mean_close = mock_data["Close"].replace(
                [np.inf, -np.inf], np.nan).dropna().mean()
            if pd.isna(mean_close):
                mean_close = 100.0  # Default value if all are NaN/inf
            mock_data["Close"].replace(
                [np.inf, -np.inf], mean_close, inplace=True)
            mock_data["Close"].fillna(mean_close, inplace=True)

        # Prepare chart data as the app does
        chart_data = pd.DataFrame({
            'AAPL': mock_data["Close"].values
        }, index=mock_data.index)

        # Check that chart data is clean
        self.assertFalse(np.isinf(chart_data['AAPL'].values).any(),
                         "Chart data still contains infinite values")
        self.assertFalse(chart_data['AAPL'].isna().any(),
                         "Chart data still contains NaN values")

    def test_extreme_cases(self):
        """Test handling of extreme edge cases for chart data"""
        # Create a dataframe with all NaN/infinite values
        all_bad_df = pd.DataFrame({
            'Close': [np.nan, np.inf, -np.inf, np.nan]
        }, index=pd.date_range('2023-01-01', periods=4))

        # Clean the data as the app does
        all_bad_df.replace([np.inf, -np.inf], np.nan, inplace=True)
        all_bad_df.fillna(method='ffill', inplace=True)
        all_bad_df.fillna(method='bfill', inplace=True)

        # Check if there are still NaN values (there should be since all were bad)
        if all_bad_df["Close"].isna().any() or np.isinf(all_bad_df["Close"].values).any():
            mean_close = all_bad_df["Close"].replace(
                [np.inf, -np.inf], np.nan).dropna().mean()
            if pd.isna(mean_close):
                mean_close = 100.0  # Default value if all are NaN/inf
            all_bad_df["Close"].replace(
                [np.inf, -np.inf], mean_close, inplace=True)
            all_bad_df["Close"].fillna(mean_close, inplace=True)

        # Verify all values are now the default value
        for val in all_bad_df["Close"].values:
            self.assertEqual(
                val, 100.0, f"Value {val} is not the default 100.0")


if __name__ == "__main__":
    unittest.main()
