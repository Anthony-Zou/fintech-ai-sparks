"""
Position manager module for tracking positions, P&L, and risk metrics.
"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


class Position:
    """Represents a trading position in a single instrument."""

    def __init__(self, symbol: str, initial_price: Optional[float] = None):
        """
        Initialize a position for a trading symbol.

        Args:
            symbol: Trading symbol
            initial_price: Initial price for the position (optional)
        """
        self.symbol = symbol
        self.quantity = 0.0
        self.average_price = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0
        self.last_price = initial_price
        self.last_update = datetime.now()

    def update_price(self, price: float) -> None:
        """
        Update the position with a new market price.

        Args:
            price: Current market price
        """
        if price <= 0:
            return

        self.last_price = price
        self.last_update = datetime.now()

        if self.quantity != 0 and self.average_price > 0:
            self.unrealized_pnl = self.quantity * (price - self.average_price)

    def add_trade(self, quantity: float, price: float) -> float:
        """
        Add a trade to the position.

        Args:
            quantity: Trade quantity (positive for buys, negative for sells)
            price: Trade price

        Returns:
            Realized P&L from the trade (if any)
        """
        if price <= 0:
            raise ValueError("Price must be positive")

        realized_pnl = 0.0

        # If reducing or flipping position, calculate realized P&L
        if (self.quantity > 0 and quantity < 0) or (self.quantity < 0 and quantity > 0):
            # Determine how much of the position is being closed
            closing_quantity = min(abs(self.quantity), abs(quantity))
            if self.quantity > 0:
                # Long position being reduced
                realized_pnl = closing_quantity * (price - self.average_price)
            else:
                # Short position being reduced
                realized_pnl = closing_quantity * (self.average_price - price)

            self.realized_pnl += realized_pnl

        # Update position
        if self.quantity == 0:
            # New position
            self.quantity = quantity
            self.average_price = price
        elif (self.quantity > 0 and quantity > 0) or (self.quantity < 0 and quantity < 0):
            # Increasing existing position
            total_cost = self.quantity * self.average_price + quantity * price
            self.quantity += quantity
            self.average_price = total_cost / self.quantity
        else:
            # Reducing or flipping position
            if abs(quantity) > abs(self.quantity):
                # Position flips from long to short or vice versa
                # Will have opposite sign of original quantity
                new_quantity = self.quantity + quantity
                self.quantity = new_quantity
                self.average_price = price
            else:
                # Position reduced but not flipped
                self.quantity += quantity
                # Average price stays the same

        # Reset average price if position becomes flat
        if abs(self.quantity) < 1e-6:  # Using epsilon for float comparison
            self.average_price = 0.0
            self.quantity = 0.0

        # Update unrealized P&L
        if self.last_price is not None:
            self.update_price(self.last_price)

        return realized_pnl

    def get_market_value(self) -> float:
        """
        Calculate the current market value of the position.

        Returns:
            Current market value
        """
        if self.last_price is None:
            return 0.0
        return self.quantity * self.last_price

    def get_cost_basis(self) -> float:
        """
        Calculate the cost basis of the position.

        Returns:
            Total cost basis
        """
        return self.quantity * self.average_price

    def get_total_pnl(self) -> float:
        """
        Calculate total P&L (realized + unrealized).

        Returns:
            Total P&L
        """
        return self.realized_pnl + self.unrealized_pnl

    def is_flat(self) -> bool:
        """
        Check if the position is flat (no open quantity).

        Returns:
            True if position is flat, False otherwise
        """
        return abs(self.quantity) < 1e-6  # Using epsilon for float comparison

    def __str__(self) -> str:
        return (f"Position({self.symbol}): {self.quantity} @ {self.average_price:.2f}, "
                f"Last: {self.last_price:.2f if self.last_price else 'N/A'}, "
                f"Unrealized P&L: {self.unrealized_pnl:.2f}, "
                f"Realized P&L: {self.realized_pnl:.2f}")


@dataclass
class TradeRecord:
    """Record of a trade execution."""
    symbol: str
    quantity: float
    price: float
    timestamp: datetime = field(default_factory=datetime.now)
    trade_id: str = ""
    order_id: str = ""
    commission: float = 0.0

    @property
    def value(self) -> float:
        """Calculate the trade value."""
        return abs(self.quantity * self.price)


class PositionManager:
    """
    Position manager for tracking trading positions and P&L.
    """

    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize the position manager.

        Args:
            initial_capital: Initial capital for the portfolio
        """
        self.positions: Dict[str, Position] = {}
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.trade_history: List[TradeRecord] = []
        self.logger = logging.getLogger(__name__)

    def get_position(self, symbol: str) -> Position:
        """
        Get or create a position for a symbol.

        Args:
            symbol: Trading symbol

        Returns:
            Position object for the symbol
        """
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol)
        return self.positions[symbol]

    def add_trade(self, symbol: str, quantity: float, price: float,
                  order_id: str = "", commission: float = 0.0) -> float:
        """
        Add a trade to the positions and update cash balance.

        Args:
            symbol: Trading symbol
            quantity: Trade quantity (positive for buys, negative for sells)
            price: Trade price
            order_id: Associated order ID (optional)
            commission: Trade commission (optional)

        Returns:
            Realized P&L from the trade (if any)
        """
        # Record the trade
        trade = TradeRecord(
            symbol=symbol,
            quantity=quantity,
            price=price,
            order_id=order_id,
            commission=commission
        )
        self.trade_history.append(trade)

        # Get or create position
        position = self.get_position(symbol)

        # Add trade to position
        realized_pnl = position.add_trade(quantity, price)

        # Update cash balance
        trade_value = quantity * price
        self.cash -= trade_value  # Negative for buys, positive for sells
        self.cash -= commission

        self.logger.info(
            f"Trade added: {symbol} {quantity} @ {price:.2f}, "
            f"Realized P&L: {realized_pnl:.2f}, Cash: {self.cash:.2f}"
        )

        return realized_pnl

    def update_price(self, symbol: str, price: float) -> None:
        """
        Update price for a position.

        Args:
            symbol: Trading symbol
            price: Current market price
        """
        if symbol in self.positions:
            self.positions[symbol].update_price(price)

    def update_prices(self, symbol: str, price: float) -> None:
        """
        Update price for a position.

        Args:
            symbol: Trading symbol
            price: Current market price
        """
        if symbol in self.positions:
            self.positions[symbol].update_price(price)

    def get_total_value(self) -> float:
        """
        Calculate the total portfolio value.

        Returns:
            Total portfolio value (cash + positions)
        """
        position_value = sum(position.get_market_value()
                             for position in self.positions.values())
        return self.cash + position_value

    def get_total_market_value(self) -> float:
        """
        Calculate the total market value of all positions.

        Returns:
            Total market value of positions (excluding cash)
        """
        return sum(position.get_market_value()
                   for position in self.positions.values())

    def get_total_cost_basis(self) -> float:
        """
        Calculate the total cost basis of all positions.

        Returns:
            Total cost basis of positions
        """
        return sum(position.get_cost_basis()
                   for position in self.positions.values())

    def get_total_unrealized_pnl(self) -> float:
        """
        Calculate the total unrealized P&L of all positions.

        Returns:
            Total unrealized P&L of positions
        """
        return sum(position.unrealized_pnl
                   for position in self.positions.values())

    def get_total_pnl(self) -> float:
        """
        Calculate the total portfolio P&L.

        Returns:
            Total portfolio P&L
        """
        position_pnl = sum(position.get_total_pnl()
                           for position in self.positions.values())
        return position_pnl + (self.cash - self.initial_capital)

    def get_portfolio_summary(self) -> Dict:
        """
        Get a summary of the portfolio.

        Returns:
            Dictionary with portfolio summary information
        """
        positions = []
        for symbol, position in self.positions.items():
            if not position.is_flat():
                positions.append({
                    "symbol": symbol,
                    "quantity": position.quantity,
                    "average_price": position.average_price,
                    "last_price": position.last_price,
                    "market_value": position.get_market_value(),
                    "unrealized_pnl": position.unrealized_pnl,
                    "realized_pnl": position.realized_pnl,
                    "total_pnl": position.get_total_pnl()
                })

        return {
            "cash": self.cash,
            "initial_capital": self.initial_capital,
            "total_value": self.get_total_value(),
            "total_pnl": self.get_total_pnl(),
            "positions": positions,
            "trade_count": len(self.trade_history)
        }

    def get_all_positions(self):
        """
        Get all current positions.

        Returns:
            list: List of all Position objects
        """
        return list(self.positions.values())
