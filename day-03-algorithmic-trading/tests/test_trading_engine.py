"""
Tests for the trading engine module
"""
from core.trading_engine import TradingEngine, OrderSide, OrderType, OrderStatus, Order
import sys
import os
import unittest
import uuid
from datetime import datetime
from pathlib import Path

# Add the parent directory to sys.path to be able to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the module


class TestTradingEngine(unittest.TestCase):
    """Tests for trading engine functionality"""

    def setUp(self):
        """Set up test environment"""
        self.engine = TradingEngine()

    def test_order_creation(self):
        """Test creating an order with the trading engine"""
        # Create a market buy order
        order_id = self.engine.create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            order_type=OrderType.MARKET
        )

        # Verify order was created
        self.assertIsNotNone(order_id)
        self.assertTrue(order_id in self.engine.orders)

        # Check order properties
        order = self.engine.orders[order_id]
        self.assertEqual(order.symbol, "AAPL")
        self.assertEqual(order.side, OrderSide.BUY)
        self.assertEqual(order.quantity, 10)
        self.assertEqual(order.order_type, OrderType.MARKET)
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_limit_order(self):
        """Test creating a limit order"""
        # Create a limit buy order
        order_id = self.engine.create_order(
            symbol="MSFT",
            side=OrderSide.BUY,
            quantity=5,
            order_type=OrderType.LIMIT,
            price=150.0
        )

        # Verify order was created
        self.assertIsNotNone(order_id)
        self.assertTrue(order_id in self.engine.orders)

        # Check order properties
        order = self.engine.orders[order_id]
        self.assertEqual(order.symbol, "MSFT")
        self.assertEqual(order.side, OrderSide.BUY)
        self.assertEqual(order.quantity, 5)
        self.assertEqual(order.order_type, OrderType.LIMIT)
        self.assertEqual(order.price, 150.0)
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_stop_order(self):
        """Test creating a stop order"""
        # Create a stop sell order
        order_id = self.engine.create_order(
            symbol="GOOGL",
            side=OrderSide.SELL,
            quantity=3,
            order_type=OrderType.STOP,
            stop_price=2500.0
        )

        # Verify order was created
        self.assertIsNotNone(order_id)
        self.assertTrue(order_id in self.engine.orders)

        # Check order properties
        order = self.engine.orders[order_id]
        self.assertEqual(order.symbol, "GOOGL")
        self.assertEqual(order.side, OrderSide.SELL)
        self.assertEqual(order.quantity, 3)
        self.assertEqual(order.order_type, OrderType.STOP)
        self.assertEqual(order.stop_price, 2500.0)
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_cancel_order(self):
        """Test cancelling an order"""
        # Create an order
        order_id = self.engine.create_order(
            symbol="NVDA",
            side=OrderSide.BUY,
            quantity=7,
            order_type=OrderType.MARKET
        )

        # Cancel the order
        result = self.engine.cancel_order(order_id)
        self.assertTrue(result)

        # Verify order status is updated
        order = self.engine.orders[order_id]
        self.assertEqual(order.status, OrderStatus.CANCELLED)

        # Try to cancel non-existent order
        result = self.engine.cancel_order("non-existent-id")
        self.assertFalse(result)

    def test_process_order_execution(self):
        """Test processing an order execution"""
        # Create an order
        order_id = self.engine.create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            order_type=OrderType.MARKET
        )

        # Process execution for the order (full fill)
        result = self.engine.process_execution(
            order_id=order_id,
            executed_quantity=10,
            execution_price=150.0
        )

        self.assertTrue(result)
        order = self.engine.orders[order_id]
        self.assertEqual(order.status, OrderStatus.FILLED)
        self.assertEqual(order.filled_quantity, 10)

        # Test partial fill
        order_id2 = self.engine.create_order(
            symbol="MSFT",
            side=OrderSide.SELL,
            quantity=20,
            order_type=OrderType.LIMIT,
            price=250.0
        )

        result = self.engine.process_execution(
            order_id=order_id2,
            executed_quantity=10,
            execution_price=250.0
        )

        self.assertTrue(result)
        order = self.engine.orders[order_id2]
        self.assertEqual(order.status, OrderStatus.PARTIALLY_FILLED)
        self.assertEqual(order.filled_quantity, 10)

    def test_get_orders(self):
        """Test retrieving orders"""
        # Create several orders
        id1 = self.engine.create_order(
            symbol="AAPL", side=OrderSide.BUY, quantity=10, order_type=OrderType.MARKET)
        id2 = self.engine.create_order(
            symbol="MSFT", side=OrderSide.BUY, quantity=5, order_type=OrderType.LIMIT, price=150.0)
        id3 = self.engine.create_order(
            symbol="AAPL", side=OrderSide.SELL, quantity=7, order_type=OrderType.LIMIT, price=180.0)

        # Get all orders
        orders = self.engine.get_orders()
        self.assertEqual(len(orders), 3)

        # Get orders by symbol
        aapl_orders = self.engine.get_orders(symbol="AAPL")
        self.assertEqual(len(aapl_orders), 2)
        symbols = [order.symbol for order in aapl_orders]
        self.assertTrue(all(symbol == "AAPL" for symbol in symbols))

        # Get orders by status
        pending_orders = self.engine.get_orders(status=OrderStatus.PENDING)
        self.assertEqual(len(pending_orders), 3)

        # Get orders by side
        buy_orders = self.engine.get_orders(side=OrderSide.BUY)
        self.assertEqual(len(buy_orders), 2)
        sides = [order.side for order in buy_orders]
        self.assertTrue(all(side == OrderSide.BUY for side in sides))

    def test_order_validation(self):
        """Test order validation"""
        # Test invalid quantity
        with self.assertRaises(ValueError):
            self.engine.create_order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=0,  # Invalid quantity
                order_type=OrderType.MARKET
            )

        # Test missing price for limit order
        with self.assertRaises(ValueError):
            self.engine.create_order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=10,
                order_type=OrderType.LIMIT,
                # Missing price
            )

        # Test missing stop price for stop order
        with self.assertRaises(ValueError):
            self.engine.create_order(
                symbol="AAPL",
                side=OrderSide.BUY,
                quantity=10,
                order_type=OrderType.STOP,
                # Missing stop_price
            )


if __name__ == "__main__":
    unittest.main()
