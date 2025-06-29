"""
Tests for the position manager module
"""
from core.position_manager import Position, PositionManager
import sys
import os
import unittest
from pathlib import Path
import numpy as np

# Add the parent directory to sys.path to be able to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the module


class TestPosition(unittest.TestCase):
    """Tests for Position class"""

    def setUp(self):
        """Set up test environment"""
        self.position = Position("AAPL", initial_price=150.0)

    def test_initialization(self):
        """Test position initialization"""
        self.assertEqual(self.position.symbol, "AAPL")
        self.assertEqual(self.position.quantity, 0.0)
        self.assertEqual(self.position.average_price, 0.0)
        self.assertEqual(self.position.realized_pnl, 0.0)
        self.assertEqual(self.position.unrealized_pnl, 0.0)
        self.assertEqual(self.position.last_price, 150.0)

    def test_update_price(self):
        """Test updating position price"""
        # First add some shares to create a position
        self.position.add_trade(10, 150.0)

        # Update price upward and check unrealized P&L
        self.position.update_price(160.0)
        self.assertEqual(self.position.last_price, 160.0)
        self.assertEqual(self.position.unrealized_pnl, 10 * (160.0 - 150.0))

        # Update price downward
        self.position.update_price(140.0)
        self.assertEqual(self.position.last_price, 140.0)
        self.assertEqual(self.position.unrealized_pnl, 10 * (140.0 - 150.0))

        # Test with negative prices (should be ignored)
        last_price = self.position.last_price
        self.position.update_price(-10.0)
        self.assertEqual(self.position.last_price, last_price)  # Unchanged

        # Test with zero price (should be ignored)
        self.position.update_price(0.0)
        self.assertEqual(self.position.last_price, last_price)  # Unchanged

    def test_add_trade_buy(self):
        """Test adding a buy trade"""
        # Add a buy trade
        pnl = self.position.add_trade(10, 150.0)

        # Check position state after the trade
        self.assertEqual(self.position.quantity, 10)
        self.assertEqual(self.position.average_price, 150.0)
        self.assertEqual(pnl, 0.0)  # No realized P&L when buying initially

        # Add another buy trade at a different price
        pnl = self.position.add_trade(5, 160.0)

        # Check position state after the second trade
        self.assertEqual(self.position.quantity, 15)
        # Average price should be weighted: (10*150 + 5*160) / 15
        self.assertEqual(self.position.average_price, (10*150 + 5*160) / 15)
        self.assertEqual(pnl, 0.0)  # No realized P&L when buying more

    def test_add_trade_sell(self):
        """Test adding a sell trade"""
        # First buy some shares
        self.position.add_trade(10, 150.0)

        # Now sell some shares at a profit
        pnl = self.position.add_trade(-5, 170.0)

        # Check position state after the sell
        self.assertEqual(self.position.quantity, 5)
        self.assertEqual(self.position.average_price,
                         150.0)  # Average price unchanged
        # Realized P&L from the sale
        self.assertEqual(pnl, 5 * (170.0 - 150.0))
        self.assertEqual(self.position.realized_pnl, 5 * (170.0 - 150.0))

        # Sell the remaining shares at a loss
        pnl = self.position.add_trade(-5, 130.0)

        # Check position state after the second sell
        self.assertEqual(self.position.quantity, 0)
        # No position, so price is reset
        self.assertEqual(self.position.average_price, 0.0)
        # Realized P&L from the sale
        self.assertEqual(pnl, 5 * (130.0 - 150.0))
        self.assertEqual(self.position.realized_pnl, 5 *
                         (170.0 - 150.0) + 5 * (130.0 - 150.0))

    def test_short_position(self):
        """Test handling of short positions"""
        # Sell shares without owning them (short position)
        pnl = self.position.add_trade(-10, 150.0)

        # Check position state after establishing short position
        self.assertEqual(self.position.quantity, -10)
        self.assertEqual(self.position.average_price, 150.0)
        self.assertEqual(pnl, 0.0)  # No realized P&L when opening a short

        # Cover part of the short at a profit (price decreased)
        pnl = self.position.add_trade(5, 130.0)

        # Check position state after partial cover
        self.assertEqual(self.position.quantity, -5)
        self.assertEqual(self.position.average_price,
                         150.0)  # Average price unchanged
        # Realized P&L from covering
        self.assertEqual(pnl, 5 * (150.0 - 130.0))


class TestPositionManager(unittest.TestCase):
    """Tests for PositionManager class"""

    def setUp(self):
        """Set up test environment"""
        self.manager = PositionManager()

    def test_initialize_position(self):
        """Test initializing a new position"""
        # Get a position for a new symbol
        position = self.manager.get_position("AAPL")

        # Check that the position was created
        self.assertIsNotNone(position)
        self.assertEqual(position.symbol, "AAPL")
        self.assertEqual(position.quantity, 0.0)

        # Check that the position is stored in the manager
        self.assertTrue("AAPL" in self.manager.positions)
        self.assertEqual(self.manager.positions["AAPL"], position)

    def test_update_position_price(self):
        """Test updating position prices"""
        # Create positions for two symbols
        self.manager.get_position("AAPL").add_trade(10, 150.0)
        self.manager.get_position("MSFT").add_trade(5, 250.0)

        # Update prices
        self.manager.update_price("AAPL", 160.0)
        self.manager.update_price("MSFT", 240.0)

        # Check that prices were updated
        self.assertEqual(self.manager.positions["AAPL"].last_price, 160.0)
        self.assertEqual(self.manager.positions["MSFT"].last_price, 240.0)

        # Check unrealized P&L
        self.assertEqual(
            self.manager.positions["AAPL"].unrealized_pnl, 10 * (160.0 - 150.0))
        self.assertEqual(
            self.manager.positions["MSFT"].unrealized_pnl, 5 * (240.0 - 250.0))

    def test_add_trades(self):
        """Test adding trades through the position manager"""
        # Add trades for a symbol
        self.manager.add_trade("AAPL", 10, 150.0)
        self.manager.add_trade("AAPL", -5, 160.0)

        # Check position state
        position = self.manager.get_position("AAPL")
        self.assertEqual(position.quantity, 5)
        self.assertEqual(position.realized_pnl, 5 * (160.0 - 150.0))

    def test_portfolio_values(self):
        """Test portfolio value calculations"""
        # Add positions for several symbols
        self.manager.add_trade("AAPL", 10, 150.0)
        self.manager.update_price("AAPL", 160.0)

        self.manager.add_trade("MSFT", 5, 250.0)
        self.manager.update_price("MSFT", 240.0)

        self.manager.add_trade("GOOGL", 2, 2500.0)
        self.manager.update_price("GOOGL", 2550.0)

        # Calculate expected values
        expected_market_value = 10 * 160.0 + 5 * 240.0 + 2 * 2550.0
        expected_cost_basis = 10 * 150.0 + 5 * 250.0 + 2 * 2500.0
        expected_unrealized_pnl = (
            10 * (160.0 - 150.0) +
            5 * (240.0 - 250.0) +
            2 * (2550.0 - 2500.0)
        )

        # Check portfolio values
        self.assertAlmostEqual(
            self.manager.get_total_market_value(), expected_market_value, places=2)
        self.assertAlmostEqual(
            self.manager.get_total_cost_basis(), expected_cost_basis, places=2)
        self.assertAlmostEqual(
            self.manager.get_total_unrealized_pnl(), expected_unrealized_pnl, places=2)

    def test_get_all_positions(self):
        """Test retrieving all positions"""
        # Add positions for several symbols
        self.manager.add_trade("AAPL", 10, 150.0)
        self.manager.add_trade("MSFT", 5, 250.0)
        self.manager.add_trade("GOOGL", 2, 2500.0)

        # Get all positions
        positions = self.manager.get_all_positions()

        # Check that all positions are returned
        self.assertEqual(len(positions), 3)
        symbols = [position.symbol for position in positions]
        self.assertIn("AAPL", symbols)
        self.assertIn("MSFT", symbols)
        self.assertIn("GOOGL", symbols)


if __name__ == "__main__":
    unittest.main()
