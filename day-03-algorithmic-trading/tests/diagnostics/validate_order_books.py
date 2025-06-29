#!/usr/bin/env python3
"""
Comprehensive Order Books validation script

This script validates that the Order Books functionality is working correctly
and provides detailed diagnostics to help identify any issues.
"""

from core.trading_engine import TradingEngine, OrderSide, OrderType
from core.order_book import OrderBook


def validate_order_books():
    """Comprehensive validation of order book functionality"""
    print("🔍 Order Books Validation Report")
    print("=" * 50)

    issues_found = []
    tests_passed = 0
    total_tests = 0

    # Test 1: Basic Order Creation and Placement
    print("\n📋 Test 1: Basic Order Creation and Placement")
    total_tests += 1

    try:
        engine = TradingEngine()
        book = OrderBook('AAPL')

        # Create BUY order
        buy_id = engine.create_order(
            'AAPL', OrderSide.BUY, 100, OrderType.LIMIT, 150.0)
        buy_order = engine.orders[buy_id]

        # Create SELL order
        sell_id = engine.create_order(
            'AAPL', OrderSide.SELL, 75, OrderType.LIMIT, 155.0)
        sell_order = engine.orders[sell_id]

        # Add to order book
        buy_added = book.add_order_object(buy_order)
        sell_added = book.add_order_object(sell_order)

        if not buy_added:
            issues_found.append("BUY order failed to add to order book")
        if not sell_added:
            issues_found.append("SELL order failed to add to order book")

        # Check placement
        snapshot = book.get_order_book_snapshot()

        if len(snapshot['bids']) != 1:
            issues_found.append(
                f"Expected 1 bid level, got {len(snapshot['bids'])}")
        if len(snapshot['asks']) != 1:
            issues_found.append(
                f"Expected 1 ask level, got {len(snapshot['asks'])}")

        # Verify order sides
        bid_has_buy = any(order.side == OrderSide.BUY for entry in book.bids.values(
        ) for order in entry.orders)
        ask_has_sell = any(order.side == OrderSide.SELL for entry in book.asks.values(
        ) for order in entry.orders)

        if not bid_has_buy:
            issues_found.append("BUY order not found in bids section")
        if not ask_has_sell:
            issues_found.append("SELL order not found in asks section")

        # Check for incorrect placements
        bid_has_sell = any(order.side == OrderSide.SELL for entry in book.bids.values(
        ) for order in entry.orders)
        ask_has_buy = any(order.side == OrderSide.BUY for entry in book.asks.values(
        ) for order in entry.orders)

        if bid_has_sell:
            issues_found.append(
                "❌ CRITICAL: SELL order found in bids section!")
        if ask_has_buy:
            issues_found.append("❌ CRITICAL: BUY order found in asks section!")

        if not issues_found:
            print("✅ PASSED - Orders correctly placed")
            tests_passed += 1
        else:
            print("❌ FAILED - Issues found:")
            for issue in issues_found:
                print(f"   - {issue}")

    except Exception as e:
        issues_found.append(f"Exception in test 1: {str(e)}")
        print(f"❌ FAILED - Exception: {str(e)}")

    # Test 2: Multiple Orders of Same Side
    print("\n📋 Test 2: Multiple Orders of Same Side")
    total_tests += 1

    try:
        engine2 = TradingEngine()
        book2 = OrderBook('MSFT')

        # Create multiple BUY orders
        buy1_id = engine2.create_order(
            'MSFT', OrderSide.BUY, 100, OrderType.LIMIT, 200.0)
        buy2_id = engine2.create_order(
            'MSFT', OrderSide.BUY, 50, OrderType.LIMIT, 199.0)

        # Create multiple SELL orders
        sell1_id = engine2.create_order(
            'MSFT', OrderSide.SELL, 75, OrderType.LIMIT, 205.0)
        sell2_id = engine2.create_order(
            'MSFT', OrderSide.SELL, 25, OrderType.LIMIT, 206.0)

        # Add all orders
        for order_id in [buy1_id, buy2_id, sell1_id, sell2_id]:
            book2.add_order_object(engine2.orders[order_id])

        snapshot = book2.get_order_book_snapshot()

        if len(snapshot['bids']) != 2:
            issues_found.append(
                f"Expected 2 bid levels, got {len(snapshot['bids'])}")
        if len(snapshot['asks']) != 2:
            issues_found.append(
                f"Expected 2 ask levels, got {len(snapshot['asks'])}")

        # Verify all BUY orders are in bids
        total_buy_in_bids = sum(len([o for o in entry.orders if o.side == OrderSide.BUY])
                                for entry in book2.bids.values())
        total_sell_in_asks = sum(len([o for o in entry.orders if o.side == OrderSide.SELL])
                                 for entry in book2.asks.values())

        if total_buy_in_bids != 2:
            issues_found.append(
                f"Expected 2 BUY orders in bids, got {total_buy_in_bids}")
        if total_sell_in_asks != 2:
            issues_found.append(
                f"Expected 2 SELL orders in asks, got {total_sell_in_asks}")

        if total_buy_in_bids == 2 and total_sell_in_asks == 2 and len(snapshot['bids']) == 2 and len(snapshot['asks']) == 2:
            print("✅ PASSED - Multiple orders correctly placed")
            tests_passed += 1
        else:
            print("❌ FAILED - Multiple order placement issues")

    except Exception as e:
        issues_found.append(f"Exception in test 2: {str(e)}")
        print(f"❌ FAILED - Exception: {str(e)}")

    # Test 3: Order Book Metrics
    print("\n📋 Test 3: Order Book Metrics")
    total_tests += 1

    try:
        best_bid, best_ask = book.get_best_bid_ask()
        mid_price = book.get_mid_price()
        spread = book.get_spread()

        if best_bid != 150.0:
            issues_found.append(f"Expected best bid 150.0, got {best_bid}")
        if best_ask != 155.0:
            issues_found.append(f"Expected best ask 155.0, got {best_ask}")
        if mid_price != 152.5:
            issues_found.append(f"Expected mid price 152.5, got {mid_price}")
        if spread != 5.0:
            issues_found.append(f"Expected spread 5.0, got {spread}")

        if best_bid == 150.0 and best_ask == 155.0 and mid_price == 152.5 and spread == 5.0:
            print("✅ PASSED - Order book metrics correct")
            tests_passed += 1
        else:
            print("❌ FAILED - Order book metrics incorrect")

    except Exception as e:
        issues_found.append(f"Exception in test 3: {str(e)}")
        print(f"❌ FAILED - Exception: {str(e)}")

    # Summary
    print(f"\n📊 Validation Summary")
    print(f"=" * 30)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    print(f"Issues found: {len(issues_found)}")

    if issues_found:
        print(f"\n❌ Issues Detected:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        return False
    else:
        print(f"\n✅ All tests passed! Order Books functionality is working correctly.")
        return True


def generate_user_guidance():
    """Generate user guidance for Order Books"""
    print(f"\n\n📖 User Guidance for Order Books")
    print(f"=" * 40)
    print(f"""
🎯 **Understanding Order Books**

The Order Books page shows pending limit orders waiting to be executed:

📈 **Bids (Buy Orders)**: Orders to buy at or below a specific price
📉 **Asks (Sell Orders)**: Orders to sell at or above a specific price

🔧 **How to Populate Order Books**:

1. Go to "Market Data" → "Order Submission"
2. Submit LIMIT orders (not MARKET orders)
3. BUY limits below current price appear in Bids
4. SELL limits above current price appear in Asks
5. Return to Order Books to see the results

⚠️ **Common Misunderstandings**:

• Market orders execute immediately and don't appear in order books
• Only pending limit orders are shown
• Empty order books are normal when no limits are active
• Orders may execute if they cross the spread

💡 **Troubleshooting**:

• If orders don't appear: Check they are LIMIT orders
• If wrong section: Verify BUY/SELL selection
• If page seems broken: Try refreshing browser
• If persistent issues: Initialize system again
""")


if __name__ == "__main__":
    success = validate_order_books()
    generate_user_guidance()

    if success:
        print(f"\n🎉 Order Books functionality validated successfully!")
        print(f"   If users report issues, they may be experiencing:")
        print(f"   • Browser caching problems")
        print(f"   • Confusion about limit vs market orders")
        print(f"   • Normal empty order book state")
    else:
        print(f"\n💥 Order Books validation failed!")
        print(f"   Please review the issues above and fix them.")
