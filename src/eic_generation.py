"""EIC (Energy Identification Code) generation module.

This module implements EIC generation according to ENTSO-E standards.
"""

import secrets
import string
from typing import Set

from .eic_validation import calculate_eic_check_digit

# ENTSO-E valid country codes (2-character codes)
# Based on European countries participating in ENTSO-E
VALID_COUNTRY_CODES: Set[str] = {
    # Central Europe
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    # Regional codes
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    # Additional codes
    "30",
    "31",
    "32",
    "33",
    "34",
    "35",
    "36",
    "37",
    "38",
    "39",
    # Extended codes
    "40",
    "41",
    "42",
    "43",
    "44",
    "45",
    "46",
    "47",
    "48",
    "49",
    "50",
    "51",
    "52",
    "53",
    "54",
    "55",
    "56",
    "57",
    "58",
    "59",
    # Alphanumeric codes for specific regions
    "X1",
    "X2",
    "X3",
    "X4",
    "X5",
    "X6",
    "X7",
    "X8",
    "X9",
    "Y1",
    "Y2",
    "Y3",
    "Y4",
    "Y5",
    "Y6",
    "Y7",
    "Y8",
    "Y9",
    "Z1",
    "Z2",
    "Z3",
    "Z4",
    "Z5",
    "Z6",
    "Z7",
    "Z8",
    "Z9",
}

# ENTSO-E valid entity types (single character)
# Common entity types used in EIC codes
VALID_ENTITY_TYPES: Set[str] = {
    "T",  # Transmission System Operator control area
    "Y",  # Transmission System Operator
    "A",  # Generation unit
    "V",  # Generation module
    "W",  # Generation resource
    "Z",  # Metering point
    "X",  # Electrical area
    "B",  # Border point
    "C",  # Coordinated capacity calculator
    "D",  # Resource provider
    "E",  # Party
    "F",  # System operator
    "G",  # Resource aggregator
    "H",  # Tie line
    "L",  # Location
    "M",  # Market participant
    "P",  # Production unit
    "S",  # Substation
    # Numeric entity types
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
}


class InvalidCountryCodeError(ValueError):
    """Exception raised for invalid country codes."""

    pass


class InvalidEntityTypeError(ValueError):
    """Exception raised for invalid entity types."""

    pass


def is_valid_country_code(code: str) -> bool:
    """Check if a country code is valid according to ENTSO-E specifications.

    Args:
        code: 2-character country code

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(code, str):
        return False
    if len(code) != 2:
        return False
    return code.upper() in VALID_COUNTRY_CODES


def is_valid_entity_type(entity_type: str) -> bool:
    """Check if an entity type is valid according to ENTSO-E specifications.

    Args:
        entity_type: Single character entity type

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(entity_type, str):
        return False
    if len(entity_type) != 1:
        return False
    return entity_type.upper() in VALID_ENTITY_TYPES


def _validate_eic_generation_params(country_code: str, entity_type: str) -> None:
    """Validate EIC generation parameters.

    Args:
        country_code: 2-character country code
        entity_type: Single character entity type

    Raises:
        InvalidCountryCodeError: If country code is invalid
        InvalidEntityTypeError: If entity type is invalid
    """
    if not is_valid_country_code(country_code):
        raise InvalidCountryCodeError(
            f"Invalid country code: '{country_code}'. Must be 2 characters and in ENTSO-E list."
        )

    if not is_valid_entity_type(entity_type):
        raise InvalidEntityTypeError(
            f"Invalid entity type: '{entity_type}'. Must be 1 character and in ENTSO-E list."
        )


def _generate_base_identifier() -> str:
    """Generate a random 12-character alphanumeric identifier.

    Uses cryptographically secure random generation.

    Returns:
        12-character uppercase alphanumeric string
    """
    # Character set: uppercase letters and digits
    charset = string.ascii_uppercase + string.digits
    # Generate 12 random characters
    identifier = "".join(secrets.choice(charset) for _ in range(12))
    return identifier


def generate_eic(country_code: str, entity_type: str) -> str:
    """Generate a valid EIC code.

    Args:
        country_code: 2-character country code (e.g., "27" for Czech Republic)
        entity_type: Single character entity type (e.g., "X", "Z", "T")

    Returns:
        Complete 16-character EIC code with valid check digit

    Raises:
        InvalidCountryCodeError: If country code is invalid
        InvalidEntityTypeError: If entity type is invalid

    Example:
        >>> eic = generate_eic("27", "X")
        >>> len(eic)
        16
        >>> eic[:2]
        '27'
        >>> eic[2]
        'X'
    """
    # Normalize to uppercase
    country_code = country_code.upper()
    entity_type = entity_type.upper()

    # Validate input parameters
    _validate_eic_generation_params(country_code, entity_type)

    # Generate random 12-character identifier
    base_identifier = _generate_base_identifier()

    # Assemble 15-character EIC prefix
    eic_prefix = f"{country_code}{entity_type}{base_identifier}"

    # Calculate check digit
    check_digit = calculate_eic_check_digit(eic_prefix)

    # Assemble complete EIC
    full_eic = f"{eic_prefix}{check_digit}"

    return full_eic


def generate_multiple_eics(country_code: str, entity_type: str, count: int) -> list[str]:
    """Generate multiple unique EIC codes with the same country code and entity type.

    Args:
        country_code: 2-character country code
        entity_type: Single character entity type
        count: Number of EICs to generate

    Returns:
        List of unique EIC codes

    Raises:
        ValueError: If count is not positive
        InvalidCountryCodeError: If country code is invalid
        InvalidEntityTypeError: If entity type is invalid
    """
    if count <= 0:
        raise ValueError("Count must be a positive integer")

    eics: set[str] = set()
    while len(eics) < count:
        eic = generate_eic(country_code, entity_type)
        eics.add(eic)

    return list(eics)
