"""
Order book implementation for simulating market depth and price discovery.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import bisect
import logging
from datetime import datetime

from core.trading_engine import Order, OrderSide, OrderStatus, OrderType


@dataclass
class Execution:
    """Represents an order execution."""
    order_id: str
    executed_quantity: float
    execution_price: float
    timestamp: str
    counter_party_id: str = ""


@dataclass
class OrderBookEntry:
    """Represents a single entry in the order book."""
    price: float
    size: float
    orders: List[Order] = field(default_factory=list)


class OrderBook:
    """
    Simulates a market order book with price levels, depth, and matching logic.
    """

    def __init__(self, symbol: str):
        """
        Initialize an order book for a specific symbol.

        Args:
            symbol: Trading symbol (ticker)
        """
        self.symbol = symbol
        self.bids: Dict[float, OrderBookEntry] = {}  # Buy side
        self.asks: Dict[float, OrderBookEntry] = {}  # Sell side
        self.sorted_bids: List[float] = []  # Sorted bid prices (descending)
        self.sorted_asks: List[float] = []  # Sorted ask prices (ascending)
        self.last_trade_price: Optional[float] = None
        self.last_trade_size: Optional[float] = None
        self.last_trade_time: Optional[datetime] = None
        self.logger = logging.getLogger(__name__)

    def add_order(self, order_id: str, side: OrderSide, quantity: float, price: float) -> bool:
        """
        Add an order to the book.

        Args:
            order_id: Unique identifier for the order
            side: Order side (BUY or SELL)
            quantity: Order quantity
            price: Order price

        Returns:
            True if the order was added, False otherwise
        """
        # Create Order object from parameters
        from datetime import datetime
        order = Order(
            order_id=order_id,
            symbol=self.symbol,
            side=side,
            quantity=quantity,
            order_type=OrderType.LIMIT,
            price=price,
            status=OrderStatus.PENDING
        )
        if order.symbol != self.symbol:
            self.logger.warning(
                f"Order symbol {order.symbol} does not match book symbol {self.symbol}")
            return False

        if order.order_type != OrderType.LIMIT:
            self.logger.warning(
                "Only limit orders can be added to the order book")
            return False

        if not order.price:
            self.logger.warning("Limit orders require a price")
            return False

        # Select the appropriate side of the book
        if order.side == OrderSide.BUY:
            book_side = self.bids
            sorted_prices = self.sorted_bids
            # For bids, we sort in descending order (highest first)
            insert_index = bisect.bisect_left(
                [-p for p in sorted_prices], -order.price)
        else:
            book_side = self.asks
            sorted_prices = self.sorted_asks
            # For asks, we sort in ascending order (lowest first)
            insert_index = bisect.bisect_left(sorted_prices, order.price)

        # If this price level doesn't exist yet, create it
        if order.price not in book_side:
            book_side[order.price] = OrderBookEntry(order.price, 0.0)

            # Insert price into sorted list
            if order.side == OrderSide.BUY:
                self.sorted_bids.insert(insert_index, order.price)
            else:
                self.sorted_asks.insert(insert_index, order.price)

        # Add the order to the price level
        book_side[order.price].orders.append(order)
        book_side[order.price].size += order.quantity - order.filled_quantity

        self.logger.info(
            f"Added order {order.order_id} to {self.symbol} {order.side.name} book at {order.price}")
        return True

    def remove_order(self, order_id: str) -> bool:
        """
        Remove an order from the book.

        Args:
            order_id: ID of the order to remove

        Returns:
            True if the order was removed, False if not found
        """
        # Search in both sides of the book
        for book_side, sorted_prices in [(self.bids, self.sorted_bids), (self.asks, self.sorted_asks)]:
            for price, entry in list(book_side.items()):
                for idx, order in enumerate(entry.orders):
                    if order.order_id == order_id:
                        # Remove the order
                        removed_order = entry.orders.pop(idx)
                        entry.size -= removed_order.quantity - removed_order.filled_quantity

                        # If no orders left at this price level, remove the level
                        if not entry.orders:
                            del book_side[price]
                            sorted_prices.remove(price)

                        self.logger.info(
                            f"Removed order {order_id} from {self.symbol} book")
                        return True

        self.logger.warning(
            f"Order {order_id} not found in {self.symbol} book")
        return False

    def update_order(self, order_id: str, new_quantity: Optional[float] = None,
                     new_price: Optional[float] = None) -> bool:
        """
        Update an existing order in the book.

        Args:
            order_id: ID of the order to update
            new_quantity: New order quantity (optional)
            new_price: New order price (optional)

        Returns:
            True if the order was updated, False if not found
        """
        # If price is changing, it's easier to remove and re-add the order
        if new_price is not None:
            # Find the order first
            for book_side in [self.bids, self.asks]:
                for price, entry in list(book_side.items()):
                    for order in entry.orders:
                        if order.order_id == order_id:
                            # Remove the order
                            if self.remove_order(order_id):
                                # Update the order
                                order.price = new_price
                                if new_quantity is not None:
                                    order.quantity = new_quantity
                                # Add it back to the book
                                return self.add_order(order)
                            return False
            return False

        # If only quantity is changing, we can update in place
        if new_quantity is not None:
            for book_side in [self.bids, self.asks]:
                for price, entry in book_side.items():
                    for order in entry.orders:
                        if order.order_id == order_id:
                            # Calculate the change in quantity
                            quantity_delta = new_quantity - order.quantity
                            # Update the order
                            order.quantity = new_quantity
                            # Update the price level size
                            entry.size += quantity_delta
                            self.logger.info(
                                f"Updated order {order_id} quantity to {new_quantity}")
                            return True

        self.logger.warning(f"Order {order_id} not found for update")
        return False

    def get_order_book_snapshot(self, depth: int = 10) -> Dict:
        """
        Get a snapshot of the order book.

        Args:
            depth: Number of price levels to include

        Returns:
            Dictionary containing bids and asks at the specified depth
        """
        bids = []
        asks = []

        # Get bid levels (buy orders)
        for price in self.sorted_bids[:depth]:
            entry = self.bids[price]
            bids.append({
                "price": price,
                "size": entry.size,
                "order_count": len(entry.orders)
            })

        # Get ask levels (sell orders)
        for price in self.sorted_asks[:depth]:
            entry = self.asks[price]
            asks.append({
                "price": price,
                "size": entry.size,
                "order_count": len(entry.orders)
            })

        return {
            "symbol": self.symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": datetime.now().isoformat()
        }

    def get_best_bid_ask(self) -> Tuple[Optional[float], Optional[float]]:
        """
        Get the best bid and ask prices.

        Returns:
            Tuple of (best_bid, best_ask), either may be None if no orders
        """
        best_bid = self.sorted_bids[0] if self.sorted_bids else None
        best_ask = self.sorted_asks[0] if self.sorted_asks else None
        return (best_bid, best_ask)

    def get_mid_price(self) -> Optional[float]:
        """
        Calculate the mid price between best bid and best ask.

        Returns:
            Mid price or None if either bid or ask is missing
        """
        best_bid, best_ask = self.get_best_bid_ask()
        if best_bid and best_ask:
            return (best_bid + best_ask) / 2
        return None

    def get_spread(self) -> Optional[float]:
        """
        Calculate the spread between best bid and best ask.

        Returns:
            Spread or None if either bid or ask is missing
        """
        best_bid, best_ask = self.get_best_bid_ask()
        if best_bid and best_ask:
            return best_ask - best_bid
        return None

    def match_orders(self) -> List[Dict]:
        """
        Match orders in the book and generate trades.

        Returns:
            List of executed trades
        """
        trades = []

        # Continue matching while there are matching orders
        while self.sorted_bids and self.sorted_asks:
            best_bid = self.sorted_bids[0]
            best_ask = self.sorted_asks[0]

            # Check if orders match
            if best_bid >= best_ask:
                bid_entry = self.bids[best_bid]
                ask_entry = self.asks[best_ask]

                # Take the first orders from each side
                buy_order = bid_entry.orders[0]
                sell_order = ask_entry.orders[0]

                # Determine execution quantity
                buy_remaining = buy_order.quantity - buy_order.filled_quantity
                sell_remaining = sell_order.quantity - sell_order.filled_quantity
                exec_quantity = min(buy_remaining, sell_remaining)

                # Determine execution price (usually the resting order's price)
                # In this simple implementation, we use the ask price
                exec_price = best_ask

                # Record the trade
                trade = {
                    "symbol": self.symbol,
                    "price": exec_price,
                    "quantity": exec_quantity,
                    "buy_order_id": buy_order.order_id,
                    "sell_order_id": sell_order.order_id,
                    "timestamp": datetime.now().isoformat()
                }
                trades.append(trade)

                # Update the orders
                buy_order.filled_quantity += exec_quantity
                sell_order.filled_quantity += exec_quantity

                # Update the book entries
                bid_entry.size -= exec_quantity
                ask_entry.size -= exec_quantity

                # Update last trade info
                self.last_trade_price = exec_price
                self.last_trade_size = exec_quantity
                self.last_trade_time = datetime.now()

                # Check if orders are fully filled
                if buy_order.filled_quantity >= buy_order.quantity:
                    buy_order.status = OrderStatus.FILLED
                    bid_entry.orders.pop(0)
                    if not bid_entry.orders:
                        del self.bids[best_bid]
                        self.sorted_bids.pop(0)
                else:
                    buy_order.status = OrderStatus.PARTIALLY_FILLED

                if sell_order.filled_quantity >= sell_order.quantity:
                    sell_order.status = OrderStatus.FILLED
                    ask_entry.orders.pop(0)
                    if not ask_entry.orders:
                        del self.asks[best_ask]
                        self.sorted_asks.pop(0)
                else:
                    sell_order.status = OrderStatus.PARTIALLY_FILLED

                self.logger.info(
                    f"Matched trade: {exec_quantity} shares of {self.symbol} at {exec_price}")
            else:
                # No more matches possible
                break

        return trades

    def cancel_order(self, order) -> bool:
        """
        Cancel an order in the order book.

        Args:
            order: The order object to cancel

        Returns:
            True if the order was cancelled, False otherwise
        """
        # Search for the order in the appropriate side of the book
        book_side = self.bids if order.side == OrderSide.BUY else self.asks

        # Try to find the order at its price level
        if order.price in book_side:
            entry = book_side[order.price]
            for idx, existing_order in enumerate(entry.orders):
                if existing_order.order_id == order.order_id:
                    # Remove the order
                    removed_order = entry.orders.pop(idx)
                    entry.size -= removed_order.quantity - removed_order.filled_quantity

                    # If no orders left at this price level, remove the level
                    if not entry.orders:
                        del book_side[order.price]
                        sorted_prices = self.sorted_bids if order.side == OrderSide.BUY else self.sorted_asks
                        sorted_prices.remove(order.price)

                    self.logger.info(
                        f"Cancelled order {order.order_id} in {self.symbol} book")
                    return True

        self.logger.warning(
            f"Order {order.order_id} not found in {self.symbol} book for cancellation")
        return False

    def match_order(self, order_id_or_order, side=None, quantity=None, price=None) -> List[Execution]:
        """
        Match a new order against the book.

        Args:
            order_id_or_order: Either an Order object or order_id string
            side: Order side (if using parameters instead of Order object)
            quantity: Order quantity (if using parameters instead of Order object)
            price: Order price (if using parameters instead of Order object, can be None for market orders)

        Returns:
            List of execution records
        """
        # Handle different input types
        if isinstance(order_id_or_order, Order):
            order = order_id_or_order
        else:
            # Create Order object from parameters
            order_type = OrderType.MARKET if price is None else OrderType.LIMIT
            order = Order(
                order_id=order_id_or_order,
                symbol=self.symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=price,
                status=OrderStatus.PENDING
            )
        executions = []

        # For market orders or marketable limit orders
        if order.order_type == OrderType.MARKET or (
            order.order_type == OrderType.LIMIT and
            ((order.side == OrderSide.BUY and self.sorted_asks and order.price >= self.sorted_asks[0]) or
             (order.side == OrderSide.SELL and self.sorted_bids and order.price <= self.sorted_bids[0]))
        ):
            # Select the opposite side of the book
            if order.side == OrderSide.BUY:
                book_side = self.asks
                sorted_prices = self.sorted_asks
            else:
                book_side = self.bids
                sorted_prices = self.sorted_bids

            remaining_quantity = order.quantity

            # Continue matching while there are orders to match and liquidity in the book
            while remaining_quantity > 0 and sorted_prices:
                best_price = sorted_prices[0]
                entry = book_side[best_price]

                # Match against orders at this price level
                for idx, resting_order in list(enumerate(entry.orders)):
                    if remaining_quantity <= 0:
                        break

                    # Determine match quantity
                    resting_available = resting_order.quantity - resting_order.filled_quantity
                    match_quantity = min(remaining_quantity, resting_available)

                    # Record execution
                    execution = Execution(
                        order_id=order.order_id,
                        executed_quantity=match_quantity,
                        execution_price=best_price,
                        timestamp=datetime.now().isoformat(),
                        counter_party_id=resting_order.order_id
                    )
                    executions.append(execution)

                    # Update the resting order
                    resting_order.filled_quantity += match_quantity
                    if resting_order.filled_quantity >= resting_order.quantity:
                        resting_order.status = OrderStatus.FILLED
                        entry.orders.pop(idx)
                    else:
                        resting_order.status = OrderStatus.PARTIALLY_FILLED

                    # Update entry size
                    entry.size -= match_quantity

                    # Update remaining quantity
                    remaining_quantity -= match_quantity

                    # Update last trade info
                    self.last_trade_price = best_price
                    self.last_trade_size = match_quantity
                    self.last_trade_time = datetime.now()

                # If no orders left at this price level, remove it
                if not entry.orders:
                    del book_side[best_price]
                    sorted_prices.pop(0)

            # Update the incoming order
            order.filled_quantity = order.quantity - remaining_quantity
            if order.filled_quantity >= order.quantity:
                order.status = OrderStatus.FILLED
            elif order.filled_quantity > 0:
                order.status = OrderStatus.PARTIALLY_FILLED

            # If it's a limit order and not fully filled, add to book
            if order.order_type == OrderType.LIMIT and remaining_quantity > 0:
                # Create a new order for the remaining quantity
                remaining_order = Order(
                    order_id=order.order_id,
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.quantity,
                    order_type=order.order_type,
                    price=order.price,
                    stop_price=order.stop_price,
                    filled_quantity=order.filled_quantity,
                    status=order.status,
                    created_at=order.created_at
                )
                self.add_order(remaining_order)

        # If it's a non-marketable limit order, just add to the book
        elif order.order_type == OrderType.LIMIT:
            self.add_order(order)

        return executions

    def get_book_snapshot(self, max_levels=10) -> tuple:
        """
        Get a snapshot of the order book with bid and ask levels.

        Args:
            max_levels: Maximum number of price levels to include

        Returns:
            Tuple of (bid_levels, ask_levels) where each level is (price, size)
        """
        bid_levels = []
        ask_levels = []

        # Get bid levels (buy orders) - highest first
        for price in self.sorted_bids[:max_levels]:
            entry = self.bids[price]
            bid_levels.append((price, entry.size))

        # Get ask levels (sell orders) - lowest first
        for price in self.sorted_asks[:max_levels]:
            entry = self.asks[price]
            ask_levels.append((price, entry.size))

        return bid_levels, ask_levels

    def add_order_object(self, order: Order) -> bool:
        """
        Add an Order object to the book (for backward compatibility).

        Args:
            order: The order to add to the book

        Returns:
            True if the order was added, False otherwise
        """
        return self.add_order(order.order_id, order.side, order.quantity, order.price)
