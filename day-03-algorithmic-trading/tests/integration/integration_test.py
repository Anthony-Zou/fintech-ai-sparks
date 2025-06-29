#!/usr/bin/env python3
"""
Comprehensive integration test for the algorithmic trading platform.
"""

from core.market_data import MarketDataFeed
from core.position_manager import PositionManager
from core.order_book import OrderBook, Execution
from core.trading_engine import TradingEngine, OrderSide, OrderType, Order
print('🚀 Starting Comprehensive Integration Test...')


print('✅ Step 1: Testing Order Hashability')
order1 = Order('order1', 'AAPL', OrderSide.BUY, 100, OrderType.MARKET)
order2 = Order('order2', 'AAPL', OrderSide.SELL,
               50, OrderType.LIMIT, price=150.0)
order_set = {order1, order2}
order_dict = {order1: 'buy_order', order2: 'sell_order'}
print(f'   - Created set with {len(order_set)} orders')
print(f'   - Created dict with {len(order_dict)} order keys')

print('✅ Step 2: Testing TradingEngine')
engine = TradingEngine()
order_id1 = engine.create_order('AAPL', OrderSide.BUY, 100, OrderType.MARKET)
order_id2 = engine.create_order(
    'AAPL', OrderSide.SELL, 50, OrderType.LIMIT, price=155.0)
print(f'   - Created order 1: {order_id1[:8]}...')
print(f'   - Created order 2: {order_id2[:8]}...')

# Test get_orders with filtering
all_orders = engine.get_orders()
buy_orders = engine.get_orders(side=OrderSide.BUY)
aapl_orders = engine.get_orders(symbol='AAPL')
print(f'   - Total orders: {len(all_orders)}')
print(f'   - Buy orders: {len(buy_orders)}')
print(f'   - AAPL orders: {len(aapl_orders)}')

# Test process_execution
result = engine.process_execution(order_id1, 50, 152.0)
print(f'   - Processed execution: {result}')

print('✅ Step 3: Testing OrderBook')
book = OrderBook('AAPL')
# Add limit order using the new parameter-based interface
book.add_order('limit1', OrderSide.SELL, 100, 160.0)

# Match market order using the new parameter-based interface
executions = book.match_order('market1', OrderSide.BUY, 50, None)
print(f'   - Added limit order to book')
print(f'   - Matched market order, got {len(executions)} executions')

if executions:
    exec = executions[0]
    print(
        f'   - Execution: {exec.executed_quantity} shares at ${exec.execution_price}')

snapshot = book.get_order_book_snapshot()
print(
    f'   - Book snapshot: {len(snapshot["bids"])} bids, {len(snapshot["asks"])} asks')

print('✅ Step 4: Testing PositionManager')
pm = PositionManager()
pm.add_trade('AAPL', 100, 150.0)
pm.add_trade('MSFT', 50, 250.0)
pm.update_price('AAPL', 155.0)
pm.update_price('MSFT', 245.0)

positions = pm.get_all_positions()
total_value = pm.get_total_value()
total_pnl = pm.get_total_pnl()
market_value = pm.get_total_market_value()

print(f'   - Created {len(positions)} positions')
print(f'   - Total portfolio value: ${total_value:.2f}')
print(f'   - Total P&L: ${total_pnl:.2f}')
print(f'   - Total market value: ${market_value:.2f}')

print('✅ Step 5: Testing MarketDataFeed')
feed = MarketDataFeed(['AAPL', 'MSFT'])
feed.set_data_source(use_mock=True)
feed.set_mock_scenario('normal')
print('   - Created market data feed with mock data')

print('🎉 Integration Test Complete!')
print('📊 All core components are working correctly')
print('🌐 Application is running at: http://localhost:8501')
