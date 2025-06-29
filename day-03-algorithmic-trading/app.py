"""
Main Streamlit application for the algorithmic trading platform.
"""
import logging
import time
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

from core.market_data import MarketDataFeed
from core.order_book import OrderBook
from core.position_manager import PositionManager
from core.trading_engine import OrderSide, OrderType, TradingEngine
from strategies.simple_momentum import MomentumStrategy
from utils.validators import ValidationError, validate_symbol, validate_quantity, validate_price

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Session state initialization
if "initialized" not in st.session_state:
    st.session_state.initialized = False
    st.session_state.trading_engine = None
    st.session_state.market_data = None
    st.session_state.position_manager = None
    st.session_state.order_books = {}
    st.session_state.strategies = {}
    st.session_state.symbols = []
    st.session_state.error_message = None
    st.session_state.success_message = None
    st.session_state.order_history = []
    st.session_state.trade_history = []


def initialize_system(symbols: List[str], initial_capital: float = 100000.0,
                      use_mock_data: bool = False, mock_scenario: str = "normal") -> None:
    """
    Initialize the trading system components.

    Args:
        symbols: List of symbols to trade
        initial_capital: Initial capital amount
        use_mock_data: Whether to use mock data instead of live data
        mock_scenario: Market scenario to use for mock data
    """
    # Create core components
    st.session_state.trading_engine = TradingEngine()
    st.session_state.market_data = MarketDataFeed(
        update_interval=5.0,
        use_mock_data=use_mock_data,
        mock_scenario=mock_scenario
    )
    st.session_state.position_manager = PositionManager(
        initial_capital=initial_capital)

    # Create order books for each symbol
    st.session_state.order_books = {}
    for symbol in symbols:
        st.session_state.order_books[symbol] = OrderBook(symbol)

    # Add symbols to market data feed
    for symbol in symbols:
        st.session_state.market_data.add_symbol(symbol)

    # Start market data feed
    st.session_state.market_data.start()

    # Store symbols
    st.session_state.symbols = symbols

    # Mark as initialized
    st.session_state.initialized = True

    st.session_state.success_message = "Trading system initialized successfully!"


def create_strategy(
    strategy_type: str,
    symbols: List[str],
    **params
) -> None:
    """
    Create and start a trading strategy.

    Args:
        strategy_type: Type of strategy to create
        symbols: List of symbols for the strategy
        **params: Strategy parameters
    """
    if strategy_type == "Momentum":
        strategy = MomentumStrategy(
            trading_engine=st.session_state.trading_engine,
            market_data=st.session_state.market_data,
            position_manager=st.session_state.position_manager,
            symbols=symbols,
            short_window=params.get("short_window", 5),
            long_window=params.get("long_window", 20),
            momentum_threshold=params.get("momentum_threshold", 0.01),
            position_size=params.get("position_size", 100),
            update_interval=params.get("update_interval", 60.0)
        )

        # Store strategy
        strategy_name = f"momentum_{len(st.session_state.strategies) + 1}"
        st.session_state.strategies[strategy_name] = strategy

        # Start strategy
        strategy.start()

        st.session_state.success_message = f"Created and started {strategy_type} strategy!"


def submit_order(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None
) -> None:
    """
    Submit a new order to the trading engine.

    Args:
        symbol: Trading symbol
        side: Order side (buy/sell)
        order_type: Order type (market/limit)
        quantity: Order quantity
        price: Order price (for limit orders)
    """
    try:
        # Validate inputs
        validate_symbol(symbol)
        validate_quantity(quantity)

        if order_type == "LIMIT" and price is not None:
            validate_price(price)

        # Convert inputs to enum types
        order_side = OrderSide.BUY if side == "BUY" else OrderSide.SELL
        order_type_enum = OrderType.MARKET if order_type == "MARKET" else OrderType.LIMIT

        # Create order
        order_id = st.session_state.trading_engine.create_order(
            symbol=symbol,
            side=order_side,
            quantity=quantity,
            order_type=order_type_enum,
            price=price
        )

        # Add to order book if limit order
        if order_type == "LIMIT" and symbol in st.session_state.order_books:
            # Get the Order object from the trading engine to add to order book
            order_object = st.session_state.trading_engine.orders[order_id]
            st.session_state.order_books[symbol].add_order_object(order_object)

        # If market order, execute immediately
        if order_type == "MARKET":
            current_price = st.session_state.market_data.get_latest_price(
                symbol)

            if current_price:
                # Execute the order
                st.session_state.trading_engine.execute_order(
                    order_id=order_id,
                    execution_price=current_price,
                    execution_quantity=quantity
                )

                # Update position
                st.session_state.position_manager.add_trade(
                    symbol=symbol,
                    quantity=quantity if side == "BUY" else -quantity,
                    price=current_price,
                    order_id=order_id
                )

                st.session_state.success_message = f"{side} order executed: {quantity} shares of {symbol} at {current_price:.2f}"
            else:
                st.session_state.error_message = f"No market price available for {symbol}"
        else:
            st.session_state.success_message = f"{side} limit order created: {quantity} shares of {symbol} at {price:.2f}"

    except ValidationError as e:
        st.session_state.error_message = str(e)
    except Exception as e:
        st.session_state.error_message = f"Error submitting order: {e}"


def cancel_order(order_id: str) -> None:
    """
    Cancel an existing order.

    Args:
        order_id: ID of the order to cancel
    """
    try:
        # Get order
        order = st.session_state.trading_engine.get_order(order_id)

        if not order:
            st.session_state.error_message = f"Order {order_id} not found"
            return

        # Cancel the order
        if st.session_state.trading_engine.cancel_order(order_id):
            # Remove from order book if necessary
            if order.symbol in st.session_state.order_books:
                st.session_state.order_books[order.symbol].remove_order(
                    order_id)

            st.session_state.success_message = f"Order {order_id} cancelled"
        else:
            st.session_state.error_message = f"Failed to cancel order {order_id}"

    except Exception as e:
        st.session_state.error_message = f"Error cancelling order: {e}"


def match_orders(symbol: str) -> None:
    """
    Trigger order matching for a symbol's order book.

    Args:
        symbol: Symbol to match orders for
    """
    try:
        if symbol not in st.session_state.order_books:
            st.session_state.error_message = f"No order book found for {symbol}"
            return

        # Match orders
        trades = st.session_state.order_books[symbol].match_orders()

        if trades:
            st.session_state.success_message = f"Matched {len(trades)} trades for {symbol}"

            # Update positions based on trades
            for trade in trades:
                # Get orders
                buy_order = st.session_state.trading_engine.get_order(
                    trade["buy_order_id"])
                sell_order = st.session_state.trading_engine.get_order(
                    trade["sell_order_id"])

                if buy_order and sell_order:
                    # Update positions
                    st.session_state.position_manager.add_trade(
                        symbol=symbol,
                        quantity=trade["quantity"],
                        price=trade["price"],
                        order_id=buy_order.order_id
                    )

                    st.session_state.position_manager.add_trade(
                        symbol=symbol,
                        quantity=-trade["quantity"],
                        price=trade["price"],
                        order_id=sell_order.order_id
                    )
        else:
            st.session_state.error_message = f"No matching trades found for {symbol}"

    except Exception as e:
        st.session_state.error_message = f"Error matching orders: {e}"


def get_symbol_options() -> List[str]:
    """
    Get a list of popular stock symbols.

    Returns:
        List of stock symbols
    """
    popular_stocks = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "JPM",
        "V", "JNJ", "WMT", "PG", "BAC", "MA", "XOM", "DIS", "NFLX", "INTC"
    ]
    return popular_stocks


def render_sidebar() -> None:
    """Render the sidebar UI."""
    st.sidebar.title("Trading Controls")

    # System initialization
    with st.sidebar.expander("Initialize System", expanded=not st.session_state.initialized):
        if not st.session_state.initialized:
            symbols_options = get_symbol_options()
            selected_symbols = st.multiselect(
                "Select trading symbols",
                options=symbols_options,
                default=["AAPL", "MSFT", "GOOGL"]
            )

            initial_capital = st.number_input(
                "Initial capital ($)",
                min_value=1000.0,
                max_value=10000000.0,
                value=100000.0,
                step=10000.0
            )

            use_mock_data = st.checkbox(
                "Use mock data (select this if Yahoo Finance API is unavailable)",
                value=False,
                help="When enabled, the system will use generated mock data instead of live market data"
            )

            # Mock scenario selection
            mock_scenario = "normal"
            if use_mock_data:
                mock_scenario = st.selectbox(
                    "Mock data scenario",
                    options=["normal", "high", "low", "crash", "rally"],
                    format_func=lambda x: {
                        "normal": "Normal Market",
                        "high": "High Volatility",
                        "low": "Low Volatility",
                        "crash": "Market Crash",
                        "rally": "Market Rally"
                    }.get(x, x.capitalize()),
                    help="Select a market scenario for the mock data generation"
                )

                st.caption({
                    "normal": "Standard market behavior with typical volatility",
                    "high": "Highly volatile market with large price swings",
                    "low": "Calm market with minimal price movement",
                    "crash": "Rapidly declining prices across all symbols",
                    "rally": "Rapidly increasing prices across all symbols"
                }.get(mock_scenario, ""))

            if st.button("Initialize Trading System"):
                if selected_symbols:
                    initialize_system(
                        selected_symbols,
                        initial_capital,
                        use_mock_data,
                        mock_scenario if use_mock_data else "normal"
                    )
                else:
                    st.session_state.error_message = "Please select at least one symbol"
        else:
            st.write("System already initialized")

            if st.button("Reset System"):
                # Stop all components
                if st.session_state.market_data:
                    st.session_state.market_data.stop()

                for strategy in st.session_state.strategies.values():
                    strategy.stop()

                # Reset session state
                st.session_state.initialized = False
                st.session_state.trading_engine = None
                st.session_state.market_data = None
                st.session_state.position_manager = None
                st.session_state.order_books = {}
                st.session_state.strategies = {}
                st.session_state.symbols = []
                st.session_state.success_message = "Trading system reset"
                st.experimental_rerun()

    # Only show these controls if system is initialized
    if st.session_state.initialized:
        # Data Source Control
        with st.sidebar.expander("Data Source Control", expanded=False):
            current_mock_state = getattr(
                st.session_state.market_data, "use_mock_data", False)
            new_mock_state = st.checkbox(
                "Use Mock Data",
                value=current_mock_state,
                help="Switch between real-time market data and mock data"
            )

            # Mock scenario selection (only shown when mock data is selected)
            current_scenario = getattr(
                st.session_state.market_data, "mock_scenario", "normal")
            new_scenario = current_scenario

            if new_mock_state:
                new_scenario = st.selectbox(
                    "Market Scenario",
                    options=["normal", "high", "low", "crash", "rally"],
                    index=["normal", "high", "low", "crash",
                           "rally"].index(current_scenario),
                    format_func=lambda x: {
                        "normal": "Normal Market",
                        "high": "High Volatility",
                        "low": "Low Volatility",
                        "crash": "Market Crash",
                        "rally": "Market Rally"
                    }.get(x, x.capitalize()),
                    help="Select a market scenario for the mock data"
                )

                # Show scenario description
                st.caption({
                    "normal": "Standard market behavior with typical volatility",
                    "high": "Highly volatile market with large price swings",
                    "low": "Calm market with minimal price movement",
                    "crash": "Rapidly declining prices across all symbols",
                    "rally": "Rapidly increasing prices across all symbols"
                }.get(new_scenario, ""))

            # Apply button for changes
            data_source_changed = new_mock_state != current_mock_state
            scenario_changed = new_scenario != current_scenario and new_mock_state

            if (data_source_changed or scenario_changed) and st.button("Apply Data Source Change"):
                # Apply changes to the market data feed
                if data_source_changed:
                    st.session_state.market_data.set_data_source(
                        new_mock_state)
                    data_source_type = "mock" if new_mock_state else "live"
                    st.session_state.success_message = f"Switched to {data_source_type} data source"

                if scenario_changed:
                    st.session_state.market_data.set_mock_scenario(
                        new_scenario)
                    if not data_source_changed:  # Don't overwrite the previous message
                        st.session_state.success_message = f"Switched to '{new_scenario}' market scenario"

                st.experimental_rerun()

        # Strategy creation
        with st.sidebar.expander("Create Strategy", expanded=False):
            strategy_type = st.selectbox(
                "Strategy type",
                options=["Momentum"]
            )

            strategy_symbols = st.multiselect(
                "Strategy symbols",
                options=st.session_state.symbols,
                default=st.session_state.symbols[:1]
            )

            if strategy_type == "Momentum":
                short_window = st.slider(
                    "Short window (minutes)",
                    min_value=1,
                    max_value=30,
                    value=5
                )

                long_window = st.slider(
                    "Long window (minutes)",
                    min_value=5,
                    max_value=60,
                    value=20
                )

                momentum_threshold = st.slider(
                    "Momentum threshold",
                    min_value=0.001,
                    max_value=0.05,
                    value=0.01,
                    step=0.001,
                    format="%.3f"
                )

                position_size = st.slider(
                    "Position size (shares)",
                    min_value=10,
                    max_value=1000,
                    value=100,
                    step=10
                )

                update_interval = st.slider(
                    "Update interval (seconds)",
                    min_value=10,
                    max_value=300,
                    value=60,
                    step=10
                )

                strategy_params = {
                    "short_window": short_window,
                    "long_window": long_window,
                    "momentum_threshold": momentum_threshold,
                    "position_size": position_size,
                    "update_interval": update_interval
                }

                if st.button("Create Strategy"):
                    if strategy_symbols:
                        create_strategy(
                            strategy_type, strategy_symbols, **strategy_params)
                    else:
                        st.session_state.error_message = "Please select at least one symbol"

        # Order submission
        with st.sidebar.expander("Submit Order", expanded=False):
            order_symbol = st.selectbox(
                "Symbol",
                options=st.session_state.symbols
            )

            order_side = st.selectbox(
                "Side",
                options=["BUY", "SELL"]
            )

            order_type = st.selectbox(
                "Type",
                options=["MARKET", "LIMIT"]
            )

            order_quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=10000,
                value=100,
                step=10
            )

            order_price = None
            if order_type == "LIMIT":
                # Get current price as a reference
                current_price = st.session_state.market_data.get_latest_price(
                    order_symbol) or 100.0

                order_price = st.number_input(
                    "Price ($)",
                    min_value=0.01,
                    max_value=100000.0,
                    value=current_price,
                    step=0.01,
                    format="%.2f"
                )

            if st.button("Submit Order"):
                submit_order(
                    symbol=order_symbol,
                    side=order_side,
                    order_type=order_type,
                    quantity=order_quantity,
                    price=order_price
                )

        # Order matching (for development/testing)
        with st.sidebar.expander("Order Book Functions", expanded=False):
            match_symbol = st.selectbox(
                "Symbol for order matching",
                options=st.session_state.symbols
            )

            if st.button("Match Orders"):
                match_orders(match_symbol)


def render_market_data() -> None:
    """Render market data section."""
    st.header("Market Data")

    if not st.session_state.initialized:
        st.info("Initialize the system to view market data")
        return

    # Create a DataFrame for market data
    market_data = []
    for symbol in st.session_state.symbols:
        data = st.session_state.market_data.get_latest_data(symbol)
        if data:
            market_data.append({
                "Symbol": symbol,
                "Last Price": f"${data.last_price:.2f}",
                "Bid": f"${data.bid_price:.2f}" if data.bid_price else "N/A",
                "Ask": f"${data.ask_price:.2f}" if data.ask_price else "N/A",
                "Volume": f"{data.volume:,}" if data.volume else "N/A",
                "Time": data.timestamp.strftime("%H:%M:%S")
            })

    if market_data:
        st.dataframe(pd.DataFrame(market_data), hide_index=True)
    else:
        st.info("Waiting for market data...")


def render_portfolio() -> None:
    """Render portfolio section."""
    st.header("Portfolio")

    if not st.session_state.initialized:
        st.info("Initialize the system to view portfolio")
        return

    # Get portfolio summary
    portfolio = st.session_state.position_manager.get_portfolio_summary()

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Value", f"${portfolio['total_value']:.2f}")
    col2.metric("Cash", f"${portfolio['cash']:.2f}")
    col3.metric("P&L", f"${portfolio['total_pnl']:.2f}")
    col4.metric("Positions", len(portfolio['positions']))

    # Display positions
    st.subheader("Positions")
    if portfolio['positions']:
        positions_data = []
        for pos in portfolio['positions']:
            positions_data.append({
                "Symbol": pos['symbol'],
                "Quantity": f"{pos['quantity']:.0f}",
                "Avg. Price": f"${pos['average_price']:.2f}",
                "Market Value": f"${pos['market_value']:.2f}",
                "Unrealized P&L": f"${pos['unrealized_pnl']:.2f}",
                "Realized P&L": f"${pos['realized_pnl']:.2f}"
            })

        st.dataframe(pd.DataFrame(positions_data), hide_index=True)
    else:
        st.info("No open positions")


def render_order_book() -> None:
    """Render order book section."""
    st.header("Order Books")

    if not st.session_state.initialized:
        st.info("Initialize the system to view order books")
        return

    # Symbol selection
    selected_symbol = st.selectbox(
        "Select symbol",
        options=st.session_state.symbols
    )

    if selected_symbol in st.session_state.order_books:
        order_book = st.session_state.order_books[selected_symbol]
        snapshot = order_book.get_order_book_snapshot()

        # Check if order book is empty and provide guidance
        is_empty = len(snapshot['bids']) == 0 and len(snapshot['asks']) == 0

        if is_empty:
            st.info("""
            📖 **Order Book is Empty**
            
            This is normal when no limit orders have been submitted. To populate the order book:
            
            1. Navigate to **"Market Data"** tab → **"Order Submission"**
            2. Submit a **BUY limit order** below current market price
            3. Submit a **SELL limit order** above current market price
            4. Return here to see bids and asks
            
            💡 **Note**: Market orders execute immediately and don't appear in the order book - only pending limit orders are shown.
            """)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Bids (Buy Orders)")
            if snapshot['bids']:
                bids_data = []
                for bid in snapshot['bids']:
                    bids_data.append({
                        "Price": f"${bid['price']:.2f}",
                        "Size": f"{bid['size']:.0f}",
                        "Orders": bid['order_count']
                    })
                st.dataframe(pd.DataFrame(bids_data), hide_index=True)
            else:
                st.info("No bids")

        with col2:
            st.subheader("Asks (Sell Orders)")
            if snapshot['asks']:
                asks_data = []
                for ask in snapshot['asks']:
                    asks_data.append({
                        "Price": f"${ask['price']:.2f}",
                        "Size": f"{ask['size']:.0f}",
                        "Orders": ask['order_count']
                    })
                st.dataframe(pd.DataFrame(asks_data), hide_index=True)
            else:
                st.info("No asks")

        # Order book metrics
        mid_price = order_book.get_mid_price()
        spread = order_book.get_spread()
        best_bid, best_ask = order_book.get_best_bid_ask()

        st.subheader("Order Book Metrics")
        metrics_col1, metrics_col2, metrics_col3 = st.columns(3)

        metrics_col1.metric(
            "Best Bid", f"${best_bid:.2f}" if best_bid else "N/A")
        metrics_col2.metric(
            "Mid Price", f"${mid_price:.2f}" if mid_price else "N/A")
        metrics_col3.metric(
            "Best Ask", f"${best_ask:.2f}" if best_ask else "N/A")

        if spread is not None:
            st.metric(
                "Spread", f"${spread:.4f} ({(spread / mid_price * 100):.2f}% of mid)" if mid_price else "N/A")
    else:
        st.info(f"No order book found for {selected_symbol}")


def render_orders() -> None:
    """Render orders section."""
    st.header("Orders")

    if not st.session_state.initialized:
        st.info("Initialize the system to view orders")
        return

    # Get active orders
    active_orders = st.session_state.trading_engine.get_active_orders()

    if active_orders:
        orders_data = []
        for order in active_orders:
            orders_data.append({
                # Truncated for display
                "Order ID": order.order_id[:8] + "...",
                "Symbol": order.symbol,
                "Side": order.side.name,
                "Type": order.order_type.name,
                "Quantity": order.quantity,
                "Filled": order.filled_quantity,
                "Price": f"${order.price:.2f}" if order.price else "Market",
                "Status": order.status.name
            })

        st.dataframe(pd.DataFrame(orders_data), hide_index=True)

        # Cancel order
        selected_order = st.selectbox(
            "Select order to cancel",
            options=[order.order_id for order in active_orders],
            format_func=lambda x: f"{x[:8]}... - {next(o.symbol for o in active_orders if o.order_id == x)} {next(o.side.name for o in active_orders if o.order_id == x)} {next(o.quantity for o in active_orders if o.order_id == x)}"
        )

        if st.button("Cancel Selected Order"):
            cancel_order(selected_order)
    else:
        st.info("No active orders")


def render_strategies() -> None:
    """Render strategies section."""
    st.header("Strategies")

    if not st.session_state.initialized:
        st.info("Initialize the system to view strategies")
        return

    if not st.session_state.strategies:
        st.info("No active strategies")
        return

    for name, strategy in st.session_state.strategies.items():
        status = strategy.get_status()

        st.subheader(f"Strategy: {name}")

        # Status info
        status_col1, status_col2 = st.columns(2)
        status_col1.write(
            f"Status: {'Running' if status['running'] else 'Stopped'}")
        status_col1.write(f"Symbols: {', '.join(status['symbols'])}")

        # Parameters
        status_col2.write("Parameters:")
        for param, value in status['parameters'].items():
            status_col2.write(f"- {param}: {value}")

        # Show signals if available
        if status['signals']:
            signals_data = []
            for symbol, signal_info in status['signals'].items():
                signals_data.append({
                    "Symbol": symbol,
                    "Momentum": f"{signal_info['momentum']:.4f}",
                    "Signal": "Buy" if signal_info['signal'] == 1 else ("Sell" if signal_info['signal'] == -1 else "Hold"),
                    "Time": time.strftime("%H:%M:%S", time.localtime(signal_info['timestamp']))
                })

            st.write("Trading Signals:")
            st.dataframe(pd.DataFrame(signals_data), hide_index=True)

        # Strategy control buttons
        col1, col2 = st.columns(2)
        if status['running']:
            if col1.button(f"Stop {name}", key=f"stop_{name}"):
                strategy.stop()
                st.session_state.success_message = f"Stopped strategy {name}"
        else:
            if col1.button(f"Start {name}", key=f"start_{name}"):
                strategy.start()
                st.session_state.success_message = f"Started strategy {name}"

        if col2.button(f"Delete {name}", key=f"delete_{name}"):
            if status['running']:
                strategy.stop()
            del st.session_state.strategies[name]
            st.session_state.success_message = f"Deleted strategy {name}"
            st.experimental_rerun()


def render_charts() -> None:
    """Render charts section."""
    st.header("Charts")

    if not st.session_state.initialized:
        st.info("Initialize the system to view charts")
        return

    # Symbol selection
    selected_symbol = st.selectbox(
        "Select symbol for chart",
        options=st.session_state.symbols,
        key="chart_symbol"
    )

    period_options = {
        "1d": "1 Day",
        "5d": "5 Days",
        "1mo": "1 Month",
        "3mo": "3 Months",
        "6mo": "6 Months",
        "1y": "1 Year",
        "ytd": "Year to Date"
    }

    selected_period = st.selectbox(
        "Select time period",
        options=list(period_options.keys()),
        format_func=lambda x: period_options[x],
        index=1
    )

    interval_options = {
        "1m": "1 Minute",
        "5m": "5 Minutes",
        "15m": "15 Minutes",
        "30m": "30 Minutes",
        "60m": "1 Hour",
        "1d": "1 Day"
    }

    selected_interval = st.selectbox(
        "Select interval",
        options=list(interval_options.keys()),
        format_func=lambda x: interval_options[x],
        index=1 if selected_period in ["1d", "5d"] else 5
    )

    try:
        data = st.session_state.market_data.get_historical_data(
            symbol=selected_symbol,
            period=selected_period,
            interval=selected_interval
        )

        if data is not None and not data.empty:
            # Clean data - replace any infinite values with NaN and then forward-fill
            data.replace([np.inf, -np.inf], np.nan, inplace=True)
            data.fillna(method='ffill', inplace=True)  # Forward fill
            # Backward fill for any remaining NaN values
            data.fillna(method='bfill', inplace=True)

            # Final check for any remaining NaN/inf values and set to a reasonable default
            if data["Close"].isna().any() or np.isinf(data["Close"].values).any():
                # Replace any remaining NaN or inf with the mean
                mean_close = data["Close"].replace(
                    [np.inf, -np.inf], np.nan).dropna().mean()
                if pd.isna(mean_close):
                    mean_close = 100.0  # Default value if all are NaN/inf
                data["Close"].replace(
                    [np.inf, -np.inf], mean_close, inplace=True)
                data["Close"].fillna(mean_close, inplace=True)

            # Prepare data for chart - create a new DataFrame to avoid issues with multi-index
            chart_data = pd.DataFrame({
                selected_symbol: data["Close"].values
            }, index=data.index)

            # Create the chart with clean data
            st.line_chart(chart_data)

            # Display some statistics - with error handling
            st.subheader("Statistics")
            stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)

            # Use get() with default value for safe access
            try:
                open_val = f"${data['Open'].iloc[0]:.2f}" if len(
                    data) > 0 else "N/A"
            except (KeyError, ValueError):
                open_val = "N/A"

            try:
                close_val = f"${data['Close'].iloc[-1]:.2f}" if len(
                    data) > 0 else "N/A"
            except (KeyError, ValueError):
                close_val = "N/A"

            try:
                high_val = f"${data['High'].max():.2f}" if not data['High'].empty else "N/A"
            except (KeyError, ValueError):
                high_val = "N/A"

            try:
                low_val = f"${data['Low'].min():.2f}" if not data['Low'].empty else "N/A"
            except (KeyError, ValueError):
                low_val = "N/A"

            stats_col1.metric("Open", open_val)
            stats_col2.metric("Close", close_val)
            stats_col3.metric("High", high_val)
            stats_col4.metric("Low", low_val)

            # Calculate returns
            returns = data["Close"].pct_change().dropna()
            if len(returns) > 0:
                st.write(f"Return: {returns.sum():.2%}")
                st.write(f"Volatility: {returns.std():.2%}")
        else:
            st.warning(
                f"No data available for {selected_symbol} with the selected parameters")
    except Exception as e:
        st.error(f"Error displaying chart: {e}")


def main() -> None:
    """Main application entry point."""
    st.set_page_config(
        page_title="Algorithmic Trading Platform",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("Algorithmic Trading Platform")
    st.caption("Core Trading Platform with Order Book Management")

    # Render the sidebar
    render_sidebar()

    # Display messages
    if st.session_state.error_message:
        st.error(st.session_state.error_message)
        st.session_state.error_message = None

    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Market Data", "Portfolio", "Order Book", "Orders", "Strategies", "Charts"
    ])

    with tab1:
        render_market_data()

    with tab2:
        render_portfolio()

    with tab3:
        render_order_book()

    with tab4:
        render_orders()

    with tab5:
        render_strategies()

    with tab6:
        render_charts()

    # Add a footer
    st.markdown("---")
    st.caption("FinTech AI Sparks Challenge - Day 3: Algorithmic Trading Platform")


if __name__ == "__main__":
    main()
