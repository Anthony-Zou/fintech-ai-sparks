#!/usr/bin/env python3
"""
Test script to identify issues with Order Books functionality
"""
from core.position_manager import PositionManager
from core.order_book import OrderBook
from core.trading_engine import TradingEngine, OrderSide, OrderType
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_order_books_functionality():
    """Test the Order Books functionality"""
    print("🧪 Testing Order Books Functionality")
    print("=" * 50)

    # Initialize components
    try:
        trading_engine = TradingEngine()
        position_manager = PositionManager(initial_capital=100000.0)
        symbols = ["AAPL", "MSFT", "GOOGL"]
        order_books = {}

        # Create order books for each symbol
        for symbol in symbols:
            order_books[symbol] = OrderBook(symbol)
            print(f"✅ Created order book for {symbol}")

        print(f"✅ Created {len(order_books)} order books")

        # Test order book snapshot
        for symbol, order_book in order_books.items():
            snapshot = order_book.get_order_book_snapshot()
            print(f"📊 {symbol} order book snapshot:")
            print(f"   - Bids: {len(snapshot['bids'])}")
            print(f"   - Asks: {len(snapshot['asks'])}")
            print(f"   - Symbol: {snapshot['symbol']}")
            print(f"   - Timestamp: {snapshot['timestamp']}")

        # Test creating an order and adding to order book
        test_symbol = "AAPL"
        print(f"\n🔧 Testing order creation for {test_symbol}")

        # Create a buy order
        order_id = trading_engine.create_order(
            symbol=test_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=150.00
        )
        print(f"✅ Created buy order: {order_id}")

        # Get the order object
        order = trading_engine.get_order(order_id)
        if order:
            # Add to order book
            print(f"✅ Order object retrieved: {order.order_id}")
            success = order_books[test_symbol].add_order_object(order)
            print(f"✅ Added order to book: {success}")

            # Check order book snapshot again
            snapshot = order_books[test_symbol].get_order_book_snapshot()
            print(f"📊 Updated {test_symbol} order book snapshot:")
            print(f"   - Bids: {len(snapshot['bids'])}")
            print(f"   - Asks: {len(snapshot['asks'])}")

            if snapshot['bids']:
                print(f"   - Best bid: ${snapshot['bids'][0]['price']:.2f}")
            if snapshot['asks']:
                print(f"   - Best ask: ${snapshot['asks'][0]['price']:.2f}")
        else:
            print("❌ Failed to retrieve order object")

        # Create a sell order for testing
        sell_order_id = trading_engine.create_order(
            symbol=test_symbol,
            side=OrderSide.SELL,
            order_type=OrderType.LIMIT,
            quantity=50,
            price=155.00
        )
        sell_order = trading_engine.get_order(sell_order_id)
        if sell_order:
            order_books[test_symbol].add_order_object(sell_order)
            print(f"✅ Added sell order to book: {sell_order_id}")

        # Final snapshot
        final_snapshot = order_books[test_symbol].get_order_book_snapshot()
        print(f"\n📊 Final {test_symbol} order book snapshot:")
        print(f"   - Bids: {len(final_snapshot['bids'])}")
        print(f"   - Asks: {len(final_snapshot['asks'])}")

        # Test order book metrics
        best_bid, best_ask = order_books[test_symbol].get_best_bid_ask()
        mid_price = order_books[test_symbol].get_mid_price()
        spread = order_books[test_symbol].get_spread()

        print(f"\n📈 Order Book Metrics for {test_symbol}:")
        print(
            f"   - Best Bid: ${best_bid:.2f}" if best_bid else "   - Best Bid: N/A")
        print(
            f"   - Best Ask: ${best_ask:.2f}" if best_ask else "   - Best Ask: N/A")
        print(
            f"   - Mid Price: ${mid_price:.2f}" if mid_price else "   - Mid Price: N/A")
        print(f"   - Spread: ${spread:.4f}" if spread else "   - Spread: N/A")

        print("\n✅ Order Books functionality test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    success = test_order_books_functionality()
    if success:
        print("\n🎉 All tests passed! Order Books functionality is working correctly.")
    else:
        print("\n💥 Tests failed! There are issues with the Order Books functionality.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
