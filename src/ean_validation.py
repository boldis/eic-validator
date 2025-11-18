"""EAN (European Article Number) validation module.

This module implements EAN validation according to GS1 standards,
supporting EAN-8, EAN-13, and EAN-14 formats with the Mod 10 check digit algorithm.

EAN Formats:
- EAN-8:  8 digits  (7 data digits + 1 check digit)
- EAN-13: 13 digits (12 data digits + 1 check digit)
- EAN-14: 14 digits (13 data digits + 1 check digit)

Check Digit Algorithm: Mod 10 with alternating weights of 1 and 3
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


# EAN Format Constants
EAN_8_LENGTH = 8
EAN_13_LENGTH = 13
EAN_14_LENGTH = 14
VALID_EAN_LENGTHS = {EAN_8_LENGTH, EAN_13_LENGTH, EAN_14_LENGTH}

# Regex pattern for EAN validation (numeric only)
EAN_PATTERN = r'^\d+$'


@dataclass
class EANComponents:
    """EAN code components."""
    data_part: str
    check_digit: str
    format: str  # "EAN-8", "EAN-13", or "EAN-14"

    @property
    def full_code(self) -> str:
        """Return the complete EAN code."""
        return f"{self.data_part}{self.check_digit}"


class EANValidationError(Exception):
    """Base exception for EAN validation errors."""
    pass


def _calculate_ean_check_digit(data_part: str) -> str:
    """Calculate the EAN check digit using Mod 10 algorithm with alternating weights.

    The algorithm:
    1. Starting from the rightmost digit of the data part, multiply every other digit by 3
    2. Sum all the results
    3. Calculate (10 - (sum % 10)) % 10

    Args:
        data_part: Data part of EAN (7, 12, or 13 digits)

    Returns:
        Single digit check digit as string

    Raises:
        ValueError: If data part is not numeric or has invalid length
    """
    if not data_part.isdigit():
        raise ValueError(f"EAN data part must be numeric, got: '{data_part}'")

    expected_lengths = {EAN_8_LENGTH - 1, EAN_13_LENGTH - 1, EAN_14_LENGTH - 1}
    if len(data_part) not in expected_lengths:
        raise ValueError(
            f"EAN data part must be 7, 12, or 13 digits long, got {len(data_part)}"
        )

    # Convert to list of integers
    digits = [int(d) for d in data_part]

    # Calculate weighted sum
    # For EAN, positions are numbered from RIGHT to LEFT (GS1 standard)
    # Odd positions from right (1st, 3rd, 5th...) get weight 3
    # Even positions from right (2nd, 4th, 6th...) get weight 1
    total = 0
    for i, digit in enumerate(reversed(digits)):
        # i=0: position 1 from right (odd) → weight 3
        # i=1: position 2 from right (even) → weight 1
        # i=2: position 3 from right (odd) → weight 3
        # etc.
        weight = 3 if i % 2 == 0 else 1
        total += digit * weight

    # Calculate check digit
    check_digit = (10 - (total % 10)) % 10

    return str(check_digit)


def calculate_ean_check_digit(ean_base: str) -> str:
    """Calculate the check digit for an EAN base code.

    This is the public API for check digit calculation.

    Args:
        ean_base: EAN base code (7, 12, or 13 digits)

    Returns:
        Single digit check digit as string

    Raises:
        ValueError: If base is not valid

    Examples:
        >>> calculate_ean_check_digit("1234567")  # EAN-8
        '0'
        >>> calculate_ean_check_digit("400638133393")  # EAN-13
        '1'
    """
    return _calculate_ean_check_digit(ean_base)


def validate_ean_check_digit(ean_code: str) -> bool:
    """Validate the check digit of an EAN code.

    Args:
        ean_code: Complete EAN code (8, 13, or 14 digits)

    Returns:
        True if check digit is valid, False otherwise
    """
    if not ean_code.isdigit():
        return False

    if len(ean_code) not in VALID_EAN_LENGTHS:
        return False

    # Extract data part and provided check digit
    data_part = ean_code[:-1]
    provided_check_digit = ean_code[-1]

    try:
        # Calculate expected check digit
        expected_check_digit = _calculate_ean_check_digit(data_part)
        return expected_check_digit == provided_check_digit
    except ValueError:
        return False


def parse_ean_components(ean_code: str) -> Optional[EANComponents]:
    """Parse an EAN code into its components.

    Args:
        ean_code: Complete EAN code (8, 13, or 14 digits)

    Returns:
        EANComponents object or None if parsing fails
    """
    if not ean_code.isdigit():
        return None

    length = len(ean_code)
    if length not in VALID_EAN_LENGTHS:
        return None

    # Determine format
    format_map = {
        EAN_8_LENGTH: "EAN-8",
        EAN_13_LENGTH: "EAN-13",
        EAN_14_LENGTH: "EAN-14",
    }

    try:
        components = EANComponents(
            data_part=ean_code[:-1],
            check_digit=ean_code[-1],
            format=format_map[length]
        )
        return components
    except Exception:
        return None


def validate_ean_format(ean_code: str) -> Dict[str, Any]:
    """Validate the format of an EAN code with detailed error reporting.

    Args:
        ean_code: EAN code to validate

    Returns:
        Dictionary with validation results:
        {
            'is_valid': bool,
            'format': Optional[str],  # "EAN-8", "EAN-13", or "EAN-14"
            'errors': List[str],
            'components': Optional[EANComponents]
        }
    """
    errors: List[str] = []

    # Remove any spaces or hyphens (sometimes used for display)
    ean_clean = ean_code.replace('-', '').replace(' ', '').strip()

    # Check if numeric
    if not ean_clean.isdigit():
        errors.append("EAN must contain only numeric digits (0-9)")
        return {
            'is_valid': False,
            'format': None,
            'errors': errors,
            'components': None
        }

    # Check length
    if len(ean_clean) not in VALID_EAN_LENGTHS:
        errors.append(
            f"Invalid EAN length: expected 8, 13, or 14 digits, got {len(ean_clean)}"
        )
        return {
            'is_valid': False,
            'format': None,
            'errors': errors,
            'components': None
        }

    # Parse components
    components = parse_ean_components(ean_clean)
    if not components:
        errors.append("Failed to parse EAN components")
        return {
            'is_valid': False,
            'format': None,
            'errors': errors,
            'components': None
        }

    # Validate check digit
    if not validate_ean_check_digit(ean_clean):
        errors.append("Invalid check digit")

    is_valid = len(errors) == 0
    return {
        'is_valid': is_valid,
        'format': components.format if is_valid else None,
        'errors': errors,
        'components': components if is_valid else None
    }


def validate_ean(ean_code: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Main EAN validation function.

    This is the primary public API for EAN validation, matching the pattern
    expected by the task specification.

    Args:
        ean_code: EAN code to validate

    Returns:
        Tuple of (is_valid, format, error_message):
        - is_valid: True if EAN is valid
        - format: "EAN-8", "EAN-13", or "EAN-14" if valid, None otherwise
        - error_message: Error description if invalid, None otherwise

    Examples:
        >>> validate_ean("12345670")
        (True, "EAN-8", None)
        >>> validate_ean("1234567")
        (False, None, "Invalid EAN length: expected 8, 13, or 14 digits, got 7")
    """
    result = validate_ean_format(ean_code)

    if result['is_valid']:
        return (True, result['format'], None)
    else:
        error_msg = "; ".join(result['errors'])
        return (False, None, error_msg)


def is_valid_ean(ean_code: str) -> Dict[str, Any]:
    """Comprehensive EAN validation function with detailed results.

    Alternative validation function that returns a dictionary with full details.

    Args:
        ean_code: EAN code to validate

    Returns:
        Dictionary with validation results:
        {
            'is_valid': bool,
            'ean_code': str,  # normalized (no spaces/hyphens)
            'format': Optional[str],  # "EAN-8", "EAN-13", or "EAN-14"
            'errors': List[str],
            'components': Optional[EANComponents]
        }
    """
    result = validate_ean_format(ean_code)
    ean_clean = ean_code.replace('-', '').replace(' ', '').strip()

    return {
        'is_valid': result['is_valid'],
        'ean_code': ean_clean,
        'format': result['format'],
        'errors': result['errors'],
        'components': result['components']
    }
