"""
Trading engine module for processing orders and executing trades.
"""
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional


class OrderType(Enum):
    MARKET = auto()
    LIMIT = auto()
    STOP = auto()
    STOP_LIMIT = auto()


class OrderSide(Enum):
    BUY = auto()
    SELL = auto()


class OrderStatus(Enum):
    PENDING = auto()
    FILLED = auto()
    PARTIALLY_FILLED = auto()
    CANCELLED = auto()
    REJECTED = auto()


@dataclass
class Order:
    """Represents a trading order in the system."""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    price: Optional[float] = None
    stop_price: Optional[float] = None
    filled_quantity: float = 0.0
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()
        self.updated_at = self.created_at

    def __hash__(self):
        """Make Order objects hashable by using the unique order_id"""
        return hash(self.order_id)

    def __eq__(self, other):
        """Define equality based on order_id"""
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id


class TradingEngine:
    """Core trading engine for order processing and execution."""

    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.logger = logging.getLogger(__name__)

    def create_order(self, symbol: str, side: OrderSide, quantity: float,
                     order_type: OrderType, price: Optional[float] = None,
                     stop_price: Optional[float] = None) -> str:
        """
        Create a new order in the trading system.

        Args:
            symbol: Trading symbol (ticker)
            side: Buy or sell
            quantity: Order size
            order_type: Market, limit, stop, or stop-limit
            price: Limit price (required for limit and stop-limit orders)
            stop_price: Stop price (required for stop and stop-limit orders)

        Returns:
            The order ID of the created order
        """
        # Validate inputs
        if quantity <= 0:
            raise ValueError("Order quantity must be greater than 0")

        if order_type in (OrderType.LIMIT, OrderType.STOP_LIMIT) and price is None:
            raise ValueError("Price must be specified for limit orders")

        if order_type in (OrderType.STOP, OrderType.STOP_LIMIT) and stop_price is None:
            raise ValueError("Stop price must be specified for stop orders")

        # Generate unique order ID
        order_id = str(uuid.uuid4())

        # Create order object
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            stop_price=stop_price
        )

        # Store order
        self.orders[order_id] = order
        self.logger.info(
            f"Created order: {order_id} for {symbol}, {side.name} {quantity} shares")

        return order_id

    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an existing order.

        Args:
            order_id: The ID of the order to cancel

        Returns:
            True if order was successfully cancelled, False otherwise
        """
        if order_id not in self.orders:
            self.logger.warning(f"Order {order_id} not found for cancellation")
            return False

        order = self.orders[order_id]

        if order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED):
            self.logger.warning(
                f"Cannot cancel order {order_id} with status {order.status.name}")
            return False

        order.status = OrderStatus.CANCELLED
        order.updated_at = datetime.now()
        self.logger.info(f"Cancelled order: {order_id}")
        return True

    def execute_order(self, order_id: str, execution_price: float,
                      execution_quantity: float) -> bool:
        """
        Execute an order (fully or partially).

        Args:
            order_id: The ID of the order to execute
            execution_price: The price at which the order is executed
            execution_quantity: The quantity of shares executed

        Returns:
            True if execution was successful, False otherwise
        """
        if order_id not in self.orders:
            self.logger.warning(f"Order {order_id} not found for execution")
            return False

        order = self.orders[order_id]

        if order.status in (OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.FILLED):
            self.logger.warning(
                f"Cannot execute order {order_id} with status {order.status.name}")
            return False

        if execution_quantity <= 0 or execution_quantity > (order.quantity - order.filled_quantity):
            self.logger.error(
                f"Invalid execution quantity for order {order_id}")
            return False

        # Update order with execution details
        order.filled_quantity += execution_quantity
        order.updated_at = datetime.now()

        # Update order status
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity  # Ensure we don't exceed order quantity
        else:
            order.status = OrderStatus.PARTIALLY_FILLED

        self.logger.info(
            f"Executed order {order_id}: {execution_quantity} shares at {execution_price}")
        return True

    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get an order by ID.

        Args:
            order_id: The ID of the order to retrieve

        Returns:
            The order object if found, None otherwise
        """
        return self.orders.get(order_id)

    def get_active_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """
        Get all active (pending or partially filled) orders.

        Args:
            symbol: Filter by trading symbol (optional)

        Returns:
            List of active order objects
        """
        active_statuses = {OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED}

        if symbol:
            return [order for order in self.orders.values()
                    if order.status in active_statuses and order.symbol == symbol]

        return [order for order in self.orders.values()
                if order.status in active_statuses]

    def get_orders(self, symbol: Optional[str] = None,
                   status: Optional[OrderStatus] = None,
                   side: Optional[OrderSide] = None) -> List[Order]:
        """
        Get orders with optional filtering.

        Args:
            symbol: Filter by trading symbol (optional)
            status: Filter by order status (optional)
            side: Filter by order side (optional)

        Returns:
            List of order objects matching the filters
        """
        orders = list(self.orders.values())

        if symbol:
            orders = [order for order in orders if order.symbol == symbol]

        if status:
            orders = [order for order in orders if order.status == status]

        if side:
            orders = [order for order in orders if order.side == side]

        return orders

    def process_execution(self, order_id: str, executed_quantity: float,
                          execution_price: float) -> bool:
        """
        Process an order execution (fully or partially).

        Args:
            order_id: The ID of the order to execute
            executed_quantity: The quantity of shares executed
            execution_price: The price at which the order is executed

        Returns:
            True if execution was successful, False otherwise
        """
        if order_id not in self.orders:
            self.logger.warning(f"Order {order_id} not found for execution")
            return False

        order = self.orders[order_id]

        if order.status in (OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.FILLED):
            self.logger.warning(
                f"Cannot execute order {order_id} with status {order.status.name}")
            return False

        if executed_quantity <= 0 or executed_quantity > (order.quantity - order.filled_quantity):
            self.logger.error(
                f"Invalid execution quantity for order {order_id}")
            return False

        # Update order with execution details
        order.filled_quantity += executed_quantity
        order.updated_at = datetime.now()

        # Update order status
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity  # Ensure we don't exceed order quantity
        else:
            order.status = OrderStatus.PARTIALLY_FILLED

        self.logger.info(
            f"Executed order {order_id}: {executed_quantity} shares at {execution_price}")
        return True
