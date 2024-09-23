from typing import Any


def validate(
    value: Any,
    expected_type: type,
    allow_none: bool = False,
    name: str = "Response",
) -> None:
    """
    Validate that a value is of the expected type.

    Args:
        value: The value to validate.
        expected_type: The expected type of the value.
        name: The name of the value (for error messages).
        allow_none: Whether None is an allowed value.

    Raises:
        ValueError: If the value is None and allow_none is False.
        TypeError: If the value is not of the expected type.
    """
    if value is None:
        if not allow_none:
            raise ValueError(f"{name} must have a value")
        return

    if not isinstance(value, expected_type):
        raise TypeError(f"{name} must be of type {expected_type.__name__}")
