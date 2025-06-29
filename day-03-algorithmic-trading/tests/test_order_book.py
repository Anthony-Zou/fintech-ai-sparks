"""
Tests for the order book module
"""
from core.trading_engine import Order, OrderSide, OrderType, OrderStatus
from core.order_book import OrderBook, OrderBookEntry
import sys
import os
import unittest
import uuid
from pathlib import Path
from datetime import datetime

# Add the parent directory to sys.path to be able to import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import the module


class TestOrderBook(unittest.TestCase):
    """Tests for OrderBook class"""

    def setUp(self):
        """Set up test environment"""
        self.order_book = OrderBook("AAPL")

    def create_order(self, side, quantity, order_type, price=None, stop_price=None):
        """Helper to create orders for testing"""
        return Order(
            order_id=str(uuid.uuid4()),
            symbol="AAPL",
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            stop_price=stop_price,
            status=OrderStatus.PENDING,
            created_at=datetime.now()
        )

    def test_initialization(self):
        """Test order book initialization"""
        self.assertEqual(self.order_book.symbol, "AAPL")
        self.assertEqual(len(self.order_book.bids), 0)
        self.assertEqual(len(self.order_book.asks), 0)
        self.assertEqual(len(self.order_book.sorted_bids), 0)
        self.assertEqual(len(self.order_book.sorted_asks), 0)
        self.assertIsNone(self.order_book.last_trade_price)

    def test_add_limit_buy_order(self):
        """Test adding a limit buy order to the book"""
        # Create a limit buy order
        order = self.create_order(
            side=OrderSide.BUY,
            quantity=10,
            order_type=OrderType.LIMIT,
            price=150.0
        )

        # Add the order to the book
        result = self.order_book.add_order_object(order)

        # Check that the order was added successfully
        self.assertTrue(result)
        self.assertEqual(len(self.order_book.bids), 1)
        self.assertEqual(len(self.order_book.sorted_bids), 1)
        self.assertEqual(self.order_book.sorted_bids[0], 150.0)
        self.assertEqual(self.order_book.bids[150.0].size, 10)
        self.assertEqual(len(self.order_book.bids[150.0].orders), 1)
        self.assertEqual(self.order_book.bids[150.0].orders[0], order)

    def test_add_limit_sell_order(self):
        """Test adding a limit sell order to the book"""
        # Create a limit sell order
        order = self.create_order(
            side=OrderSide.SELL,
            quantity=5,
            order_type=OrderType.LIMIT,
            price=160.0
        )

        # Add the order to the book
        result = self.order_book.add_order_object(order)

        # Check that the order was added successfully
        self.assertTrue(result)
        self.assertEqual(len(self.order_book.asks), 1)
        self.assertEqual(len(self.order_book.sorted_asks), 1)
        self.assertEqual(self.order_book.sorted_asks[0], 160.0)
        self.assertEqual(self.order_book.asks[160.0].size, 5)
        self.assertEqual(len(self.order_book.asks[160.0].orders), 1)
        self.assertEqual(self.order_book.asks[160.0].orders[0], order)

    def test_market_order_matching(self):
        """Test matching a market order against the book"""
        # First, add a limit sell order to the book
        sell_order = self.create_order(
            side=OrderSide.SELL,
            quantity=10,
            order_type=OrderType.LIMIT,
            price=155.0
        )
        self.order_book.add_order_object(sell_order)

        # Create a market buy order
        buy_order = self.create_order(
            side=OrderSide.BUY,
            quantity=5,
            order_type=OrderType.MARKET
        )

        # Process the market order
        executions = self.order_book.match_order(buy_order)

        # Check the results
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0].order_id, buy_order.order_id)
        self.assertEqual(executions[0].executed_quantity, 5)
        self.assertEqual(executions[0].execution_price, 155.0)

        # Check that the sell order was partially filled
        self.assertEqual(self.order_book.asks[155.0].size, 5)

    def test_limit_order_matching(self):
        """Test matching limit orders"""
        # Add a limit sell order to the book
        sell_order = self.create_order(
            side=OrderSide.SELL,
            quantity=10,
            order_type=OrderType.LIMIT,
            price=155.0
        )
        self.order_book.add_order_object(sell_order)

        # Add another limit sell order at a better price
        better_sell_order = self.create_order(
            side=OrderSide.SELL,
            quantity=5,
            order_type=OrderType.LIMIT,
            price=153.0
        )
        self.order_book.add_order_object(better_sell_order)

        # Create a limit buy order that crosses with both sells
        buy_order = self.create_order(
            side=OrderSide.BUY,
            quantity=15,
            order_type=OrderType.LIMIT,
            price=156.0
        )

        # Process the limit order
        executions = self.order_book.match_order(buy_order)

        # Check the results
        self.assertEqual(len(executions), 2)

        # First execution should be against the better price
        self.assertEqual(executions[0].order_id, buy_order.order_id)
        self.assertEqual(executions[0].executed_quantity, 5)
        self.assertEqual(executions[0].execution_price, 153.0)

        # Second execution should be against the remaining sell order
        self.assertEqual(executions[1].order_id, buy_order.order_id)
        self.assertEqual(executions[1].executed_quantity, 10)
        self.assertEqual(executions[1].execution_price, 155.0)

        # The sell orders should be fully filled and removed from the book
        self.assertEqual(len(self.order_book.asks), 0)
        self.assertEqual(len(self.order_book.sorted_asks), 0)

    def test_multiple_orders_at_same_price(self):
        """Test handling multiple orders at the same price level"""
        # Add two buy orders at the same price
        order1 = self.create_order(
            side=OrderSide.BUY,
            quantity=5,
            order_type=OrderType.LIMIT,
            price=150.0
        )
        order2 = self.create_order(
            side=OrderSide.BUY,
            quantity=7,
            order_type=OrderType.LIMIT,
            price=150.0
        )

        self.order_book.add_order_object(order1)
        self.order_book.add_order_object(order2)

        # Check that both orders were added at the same price level
        self.assertEqual(len(self.order_book.bids), 1)
        self.assertEqual(len(self.order_book.sorted_bids), 1)
        self.assertEqual(self.order_book.bids[150.0].size, 12)  # 5+7
        self.assertEqual(len(self.order_book.bids[150.0].orders), 2)

    def test_order_book_snapshot(self):
        """Test getting a snapshot of the order book"""
        # Add orders to create a book with multiple levels
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.BUY, quantity=5, order_type=OrderType.LIMIT, price=148.0))
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.BUY, quantity=10, order_type=OrderType.LIMIT, price=150.0))
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.BUY, quantity=3, order_type=OrderType.LIMIT, price=149.0))

        self.order_book.add_order_object(self.create_order(
            side=OrderSide.SELL, quantity=8, order_type=OrderType.LIMIT, price=151.0))
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.SELL, quantity=7, order_type=OrderType.LIMIT, price=152.0))
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.SELL, quantity=4, order_type=OrderType.LIMIT, price=153.0))

        # Get the book snapshot
        bid_levels, ask_levels = self.order_book.get_book_snapshot(
            max_levels=5)

        # Check bid levels (should be sorted in descending order by price)
        self.assertEqual(len(bid_levels), 3)
        self.assertEqual(bid_levels[0], (150.0, 10))  # (price, size)
        self.assertEqual(bid_levels[1], (149.0, 3))
        self.assertEqual(bid_levels[2], (148.0, 5))

        # Check ask levels (should be sorted in ascending order by price)
        self.assertEqual(len(ask_levels), 3)
        self.assertEqual(ask_levels[0], (151.0, 8))  # (price, size)
        self.assertEqual(ask_levels[1], (152.0, 7))
        self.assertEqual(ask_levels[2], (153.0, 4))

        # Test with limited levels
        bid_levels, ask_levels = self.order_book.get_book_snapshot(
            max_levels=2)
        self.assertEqual(len(bid_levels), 2)
        self.assertEqual(len(ask_levels), 2)

    def test_cancel_order(self):
        """Test cancelling an order"""
        # Add an order
        order = self.create_order(
            side=OrderSide.BUY,
            quantity=10,
            order_type=OrderType.LIMIT,
            price=150.0
        )
        self.order_book.add_order_object(order)

        # Cancel the order
        result = self.order_book.cancel_order(order)
        self.assertTrue(result)

        # Check that the order was removed
        self.assertEqual(len(self.order_book.bids), 0)
        self.assertEqual(len(self.order_book.sorted_bids), 0)

        # Try to cancel a non-existent order
        non_existent_order = self.create_order(
            side=OrderSide.BUY,
            quantity=5,
            order_type=OrderType.LIMIT,
            price=152.0
        )
        result = self.order_book.cancel_order(non_existent_order)
        self.assertFalse(result)

    def test_get_mid_price(self):
        """Test calculating the mid price"""
        # With no orders, mid price should be None
        self.assertIsNone(self.order_book.get_mid_price())

        # Add orders to create a book
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.BUY, quantity=5, order_type=OrderType.LIMIT, price=149.0))
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.SELL, quantity=7, order_type=OrderType.LIMIT, price=151.0))

        # Calculate expected mid price
        expected_mid_price = (149.0 + 151.0) / 2

        # Check mid price
        self.assertEqual(self.order_book.get_mid_price(), expected_mid_price)

        # Add more orders at different prices
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.BUY, quantity=10, order_type=OrderType.LIMIT, price=150.0))
        self.order_book.add_order_object(self.create_order(
            side=OrderSide.SELL, quantity=4, order_type=OrderType.LIMIT, price=152.0))

        # Mid price should use best bid and ask
        expected_mid_price = (150.0 + 151.0) / 2
        self.assertEqual(self.order_book.get_mid_price(), expected_mid_price)


if __name__ == "__main__":
    unittest.main()
