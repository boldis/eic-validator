"""EAN (European Article Number) generation module.

This module implements EAN generation according to GS1 standards.
"""

import secrets
import string
from typing import Literal

from .ean_validation import calculate_ean_check_digit

# Valid EAN types
EANType = Literal["EAN-8", "EAN-13", "EAN-14"]


class InvalidEANTypeError(ValueError):
    """Exception raised for invalid EAN types."""

    pass


class InvalidBaseCodeError(ValueError):
    """Exception raised for invalid base codes."""

    pass


def is_valid_ean_type(ean_type: str) -> bool:
    """Check if an EAN type is valid.

    Args:
        ean_type: EAN type string ("EAN-8", "EAN-13", or "EAN-14")

    Returns:
        True if valid, False otherwise
    """
    return ean_type in {"EAN-8", "EAN-13", "EAN-14"}


def _validate_base_code(base_code: str, ean_type: str) -> None:
    """Validate the base code for EAN generation.

    Args:
        base_code: Numeric string representing the data part
        ean_type: Target EAN type

    Raises:
        InvalidBaseCodeError: If base code is invalid
        InvalidEANTypeError: If EAN type is invalid
    """
    if not is_valid_ean_type(ean_type):
        raise InvalidEANTypeError(
            f"Invalid EAN type: '{ean_type}'. Must be 'EAN-8', 'EAN-13', or 'EAN-14'."
        )

    if not isinstance(base_code, str):
        raise InvalidBaseCodeError("Base code must be a string")

    if not base_code.isdigit():
        raise InvalidBaseCodeError(
            f"Base code must contain only numeric digits, got: '{base_code}'"
        )

    # Determine expected length based on EAN type
    expected_length_map = {
        "EAN-8": 7,
        "EAN-13": 12,
        "EAN-14": 13,
    }

    expected_length = expected_length_map[ean_type]
    if len(base_code) != expected_length:
        raise InvalidBaseCodeError(
            f"Base code for {ean_type} must be exactly {expected_length} digits, "
            f"got {len(base_code)}"
        )


def _generate_random_base(ean_type: str) -> str:
    """Generate a random numeric base code for the specified EAN type.

    Args:
        ean_type: Target EAN type

    Returns:
        Random numeric string of appropriate length

    Raises:
        InvalidEANTypeError: If EAN type is invalid
    """
    if not is_valid_ean_type(ean_type):
        raise InvalidEANTypeError(
            f"Invalid EAN type: '{ean_type}'. Must be 'EAN-8', 'EAN-13', or 'EAN-14'."
        )

    length_map = {
        "EAN-8": 7,
        "EAN-13": 12,
        "EAN-14": 13,
    }

    length = length_map[ean_type]
    # Generate random digits
    base_code = "".join(secrets.choice(string.digits) for _ in range(length))
    return base_code


def generate_ean(base_code: str, ean_type: str) -> str:
    """Generate a valid EAN code from a base code.

    Args:
        base_code: Numeric string representing the data part
                  - 7 digits for EAN-8
                  - 12 digits for EAN-13
                  - 13 digits for EAN-14
        ean_type: Target EAN type ("EAN-8", "EAN-13", or "EAN-14")

    Returns:
        Complete EAN code with valid check digit

    Raises:
        InvalidBaseCodeError: If base code is invalid
        InvalidEANTypeError: If EAN type is invalid

    Examples:
        >>> ean = generate_ean("1234567", "EAN-8")
        >>> len(ean)
        8
        >>> ean[:7]
        '1234567'
        >>> generate_ean("400638133393", "EAN-13")
        '4006381333931'
    """
    # Normalize EAN type
    ean_type = ean_type.upper()

    # Validate inputs
    _validate_base_code(base_code, ean_type)

    # Calculate check digit
    check_digit = calculate_ean_check_digit(base_code)

    # Assemble complete EAN
    full_ean = f"{base_code}{check_digit}"

    return full_ean


def generate_random_ean(ean_type: str) -> str:
    """Generate a random valid EAN code.

    Args:
        ean_type: Target EAN type ("EAN-8", "EAN-13", or "EAN-14")

    Returns:
        Complete random EAN code with valid check digit

    Raises:
        InvalidEANTypeError: If EAN type is invalid

    Examples:
        >>> ean = generate_random_ean("EAN-8")
        >>> len(ean)
        8
        >>> ean = generate_random_ean("EAN-13")
        >>> len(ean)
        13
    """
    # Normalize EAN type
    ean_type = ean_type.upper()

    # Generate random base code
    base_code = _generate_random_base(ean_type)

    # Generate EAN with check digit
    return generate_ean(base_code, ean_type)


def generate_multiple_eans(ean_type: str, count: int) -> list[str]:
    """Generate multiple unique random EAN codes.

    Args:
        ean_type: Target EAN type ("EAN-8", "EAN-13", or "EAN-14")
        count: Number of EANs to generate

    Returns:
        List of unique EAN codes

    Raises:
        ValueError: If count is not positive
        InvalidEANTypeError: If EAN type is invalid
    """
    if count <= 0:
        raise ValueError("Count must be a positive integer")

    # Normalize EAN type
    ean_type = ean_type.upper()

    if not is_valid_ean_type(ean_type):
        raise InvalidEANTypeError(
            f"Invalid EAN type: '{ean_type}'. Must be 'EAN-8', 'EAN-13', or 'EAN-14'."
        )

    eans: set[str] = set()
    while len(eans) < count:
        ean = generate_random_ean(ean_type)
        eans.add(ean)

    return list(eans)
