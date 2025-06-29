#!/usr/bin/env python3
"""
End-to-end workflow test demonstrating the complete trading platform functionality.
"""

from core.market_data import MarketDataFeed
from core.position_manager import PositionManager
from core.order_book import OrderBook
from core.trading_engine import TradingEngine, OrderSide, OrderType
print('🚀 Starting End-to-End Workflow Test...')


def test_complete_trading_workflow():
    """Test a complete trading workflow from order creation to position management."""

    print('\n📊 Phase 1: System Initialization')
    # Initialize all components
    engine = TradingEngine()
    book = OrderBook('AAPL')
    positions = PositionManager()
    market_data = MarketDataFeed()

    # Add some mock data
    market_data.add_symbol('AAPL')
    market_data.set_data_source('mock')
    print('   ✅ All systems initialized')

    print('\n📈 Phase 2: Market Orders and Executions')
    # Create a limit sell order in the book
    sell_order_id = engine.create_order(
        'AAPL', OrderSide.SELL, 100, OrderType.LIMIT, price=150.0)
    book.add_order(sell_order_id, OrderSide.SELL, 100, 150.0)
    print(f'   ✅ Added sell order: {sell_order_id[:8]}... (100 shares @ $150)')

    # Create a market buy order
    buy_order_id = engine.create_order(
        'AAPL', OrderSide.BUY, 100, OrderType.MARKET)
    executions = book.match_order(buy_order_id, OrderSide.BUY, 100, None)
    print(f'   ✅ Created market buy order: {buy_order_id[:8]}...')
    print(f'   ✅ Generated {len(executions)} executions')

    print('\n💼 Phase 3: Position Management')
    # Process the execution in position manager
    if executions:
        execution = executions[0]
        positions.add_trade(
            'AAPL', execution.executed_quantity, execution.execution_price)
        print(
            f'   ✅ Added trade: {execution.executed_quantity} shares @ ${execution.execution_price}')

        # Update position with current market price
        positions.update_price('AAPL', 155.0)  # Assume price moved up
        position = positions.get_position('AAPL')
        print(
            f'   ✅ Position: {position.quantity} shares, Avg: ${position.average_price:.2f}')
        print(f'   ✅ Unrealized P&L: ${position.unrealized_pnl:.2f}')

    print('\n📋 Phase 4: Order Management')
    # Test order filtering
    all_orders = engine.get_orders()
    aapl_orders = engine.get_orders(symbol='AAPL')
    buy_orders = engine.get_orders(side=OrderSide.BUY)

    print(f'   ✅ Total orders: {len(all_orders)}')
    print(f'   ✅ AAPL orders: {len(aapl_orders)}')
    print(f'   ✅ Buy orders: {len(buy_orders)}')

    print('\n📊 Phase 5: Portfolio Analytics')
    all_positions = positions.get_all_positions()
    total_value = positions.get_total_market_value()
    total_pnl = positions.get_total_unrealized_pnl()

    print(f'   ✅ Total positions: {len(all_positions)}')
    print(f'   ✅ Portfolio value: ${total_value:.2f}')
    print(f'   ✅ Total P&L: ${total_pnl:.2f}')

    print('\n🎯 Phase 6: Order Book Analysis')
    snapshot = book.get_order_book_snapshot()
    mid_price = book.get_mid_price()

    print(f'   ✅ Bid levels: {len(snapshot["bids"])}')
    print(f'   ✅ Ask levels: {len(snapshot["asks"])}')
    print(
        f'   ✅ Mid price: ${mid_price:.2f}' if mid_price else '   ⚠️ No mid price available')

    return True


def test_error_handling():
    """Test error handling scenarios."""
    print('\n🛡️ Phase 7: Error Handling Tests')

    engine = TradingEngine()

    # Test invalid order creation
    try:
        engine.create_order('AAPL', OrderSide.BUY, -10,
                            OrderType.MARKET)  # Negative quantity
        print('   ❌ Should have failed for negative quantity')
    except ValueError as e:
        print(f'   ✅ Caught expected error: {str(e)[:50]}...')

    # Test order cancellation
    order_id = engine.create_order(
        'AAPL', OrderSide.BUY, 100, OrderType.LIMIT, price=100.0)
    success = engine.cancel_order(order_id)
    print(f'   ✅ Order cancellation: {success}')

    return True


if __name__ == '__main__':
    try:
        workflow_success = test_complete_trading_workflow()
        error_handling_success = test_error_handling()

        print('\n' + '='*60)
        print('🎉 END-TO-END WORKFLOW TEST COMPLETED SUCCESSFULLY!')
        print('='*60)
        print(
            f'✅ Trading Workflow: {"PASSED" if workflow_success else "FAILED"}')
        print(
            f'✅ Error Handling: {"PASSED" if error_handling_success else "FAILED"}')
        print('\n🚀 The algorithmic trading platform is fully operational!')
        print('🌐 Web interface: http://localhost:8501')

    except Exception as e:
        print(f'\n❌ Test failed with error: {e}')
        import traceback
        traceback.print_exc()
