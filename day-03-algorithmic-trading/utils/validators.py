"""
Validators module for input validation and error handling.
"""
from typing import Any, Callable, List, Optional, Set, Union
import re


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


def validate_symbol(symbol: str) -> bool:
    """
    Validate a trading symbol.

    Args:
        symbol: Trading symbol to validate

    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not isinstance(symbol, str):
        raise ValidationError("Symbol must be a string")

    # Basic validation for common stock symbols
    pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'
    if not re.match(pattern, symbol):
        raise ValidationError(
            f"Invalid symbol format: {symbol}. Should be 1-5 uppercase letters, "
            "optionally followed by a dot and 1-2 uppercase letters."
        )

    return True


def validate_price(price: float) -> bool:
    """
    Validate a price value.

    Args:
        price: Price value to validate

    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not isinstance(price, (int, float)):
        raise ValidationError("Price must be a number")

    if price <= 0:
        raise ValidationError("Price must be positive")

    return True


def validate_quantity(quantity: float) -> bool:
    """
    Validate a quantity value.

    Args:
        quantity: Quantity value to validate

    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not isinstance(quantity, (int, float)):
        raise ValidationError("Quantity must be a number")

    if quantity <= 0:
        raise ValidationError("Quantity must be positive")

    return True


def validate_in_list(value: Any, valid_values: List[Any], name: str = "value") -> bool:
    """
    Validate that a value is in a list of valid values.

    Args:
        value: Value to validate
        valid_values: List of valid values
        name: Name of the value for the error message

    Returns:
        True if valid, raises ValidationError otherwise
    """
    if value not in valid_values:
        raise ValidationError(
            f"{name} must be one of: {', '.join(str(v) for v in valid_values)}")

    return True


def validate_in_range(value: Union[int, float],
                      min_value: Optional[Union[int, float]] = None,
                      max_value: Optional[Union[int, float]] = None,
                      name: str = "value") -> bool:
    """
    Validate that a numeric value is within a range.

    Args:
        value: Value to validate
        min_value: Minimum valid value (optional)
        max_value: Maximum valid value (optional)
        name: Name of the value for the error message

    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be a number")

    if min_value is not None and value < min_value:
        raise ValidationError(f"{name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{name} must be at most {max_value}")

    return True


def validate_type(value: Any, expected_type: Union[type, tuple], name: str = "value") -> bool:
    """
    Validate that a value is of the expected type.

    Args:
        value: Value to validate
        expected_type: Expected type or tuple of types
        name: Name of the value for the error message

    Returns:
        True if valid, raises ValidationError otherwise
    """
    if not isinstance(value, expected_type):
        type_name = expected_type.__name__ if isinstance(expected_type, type) else \
            " or ".join(t.__name__ for t in expected_type)
        raise ValidationError(f"{name} must be of type {type_name}")

    return True


def validate_string_length(value: str,
                           min_length: Optional[int] = None,
                           max_length: Optional[int] = None,
                           name: str = "string") -> bool:
    """
    Validate that a string is within length limits.

    Args:
        value: String to validate
        min_length: Minimum valid length (optional)
        max_length: Maximum valid length (optional)
        name: Name of the value for the error message

    Returns:
        True if valid, raises ValidationError otherwise
    """
    validate_type(value, str, name)

    if min_length is not None and len(value) < min_length:
        raise ValidationError(
            f"{name} must be at least {min_length} characters long")

    if max_length is not None and len(value) > max_length:
        raise ValidationError(
            f"{name} must be at most {max_length} characters long")

    return True


def validate_email(email: str) -> bool:
    """
    Validate an email address.

    Args:
        email: Email address to validate

    Returns:
        True if valid, raises ValidationError otherwise
    """
    validate_type(email, str, "Email")

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")

    return True


def validate_regex(value: str, pattern: str, name: str = "value") -> bool:
    """
    Validate that a string matches a regex pattern.

    Args:
        value: String to validate
        pattern: Regex pattern to match
        name: Name of the value for the error message

    Returns:
        True if valid, raises ValidationError otherwise
    """
    validate_type(value, str, name)

    if not re.match(pattern, value):
        raise ValidationError(f"{name} does not match the required pattern")

    return True


def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """
    Safely execute a function and handle exceptions.

    Args:
        func: Function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of the function or None if an exception occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            f"Error executing {func.__name__}: {str(e)}")
        return None
