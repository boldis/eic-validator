"""EIC (Energy Identification Code) validation module.

This module implements EIC validation according to ENTSO-E standards,
including the ISO 7064 Mod 37,36 check digit algorithm.

EIC Format: XXYAAAAAAAAAAAAK (16 characters)
- XX: Office identifier (2 chars) - e.g., "27" for Czech Republic
- Y: Entity type (1 char) - e.g., "A" for station, "Z" for metering point
- A...: Individual identifier (12 chars) - unique identifier
- K: Check digit (1 char) - calculated using ISO 7064 Mod 37,36
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass


# EIC Format Constants
EIC_LENGTH = 16
EIC_BASE_LENGTH = 15
OFFICE_ID_LENGTH = 2
ENTITY_TYPE_LENGTH = 1
INDIVIDUAL_ID_LENGTH = 12
CHECK_DIGIT_LENGTH = 1

# Regex patterns for EIC components
# Office identifier: 2 alphanumeric characters
OFFICE_ID_PATTERN = r'^[0-9A-Z]{2}$'
# Entity type: 1 alphanumeric character
ENTITY_TYPE_PATTERN = r'^[A-Z0-9]$'
# Individual identifier: 12 alphanumeric characters
INDIVIDUAL_ID_PATTERN = r'^[0-9A-Z]{12}$'
# Full EIC pattern: 16 alphanumeric characters
EIC_FULL_PATTERN = r'^[0-9A-Z]{16}$'


@dataclass
class EICComponents:
    """EIC code components."""
    office_id: str
    entity_type: str
    individual_id: str
    check_digit: str

    @property
    def base(self) -> str:
        """Return the 15-character base (without check digit)."""
        return f"{self.office_id}{self.entity_type}{self.individual_id}"

    @property
    def full_code(self) -> str:
        """Return the complete 16-character EIC code."""
        return f"{self.base}{self.check_digit}"


class EICValidationError(Exception):
    """Base exception for EIC validation errors."""
    pass


def _char_to_value(char: str) -> int:
    """Convert a character to its numerical value for ISO 7064 Mod 37,36.

    Args:
        char: Single character (0-9 or A-Z)

    Returns:
        Numerical value (0-35)

    Raises:
        ValueError: If character is not valid
    """
    if '0' <= char <= '9':
        return int(char)
    elif 'A' <= char <= 'Z':
        return ord(char) - ord('A') + 10
    else:
        raise ValueError(f"Invalid character for EIC calculation: '{char}'")


def _value_to_char(value: int) -> str:
    """Convert a numerical value to its character representation.

    Args:
        value: Numerical value (0-35)

    Returns:
        Character (0-9 or A-Z)

    Raises:
        ValueError: If value is out of range
    """
    if 0 <= value <= 9:
        return str(value)
    elif 10 <= value <= 35:
        return chr(ord('A') + value - 10)
    else:
        raise ValueError(f"Invalid value for EIC character conversion: {value}")


def calculate_eic_check_digit(eic_base: str) -> str:
    """Calculate the check digit for a 15-character EIC base using ISO 7064 Mod 37,36.

    Args:
        eic_base: 15-character EIC base (XXYAAAAAAAAAAAA)

    Returns:
        Single character check digit

    Raises:
        ValueError: If base is not 15 characters or contains invalid characters
    """
    if len(eic_base) != EIC_BASE_LENGTH:
        raise ValueError(f"EIC base must be exactly {EIC_BASE_LENGTH} characters long, got {len(eic_base)}")

    eic_base = eic_base.upper()
    remainder = 0

    for char in eic_base:
        try:
            value = _char_to_value(char)
        except ValueError as e:
            raise ValueError(f"Invalid character in EIC base: {e}") from e
        # ISO 7064 Mod 37,36 algorithm: remainder = (remainder * 36 + value) % 37
        remainder = (remainder * 36 + value) % 37

    check_digit_value = (37 - remainder) % 37

    # Special case: check_digit_value of 36 or 0 both map to '0'
    # This is standard for ISO 7064 Mod 37,36
    if check_digit_value == 36:
        check_digit_value = 0

    return _value_to_char(check_digit_value)


def validate_eic_check_digit(eic_code: str) -> bool:
    """Validate the check digit of a 16-character EIC code using ISO 7064 Mod 37,36.

    This validates by recalculating the check digit and comparing it.

    Args:
        eic_code: 16-character EIC code

    Returns:
        True if check digit is valid, False otherwise
    """
    if len(eic_code) != EIC_LENGTH:
        return False

    eic_code = eic_code.upper()

    # Extract data part and provided check digit
    eic_data_part = eic_code[:15]
    provided_check_digit = eic_code[15]

    try:
        # Calculate expected check digit
        expected_check_digit = calculate_eic_check_digit(eic_data_part)
        return expected_check_digit == provided_check_digit
    except ValueError:
        # Invalid characters or other calculation error
        return False


def parse_eic_components(eic_code: str) -> Optional[EICComponents]:
    """Parse an EIC code into its components.

    Args:
        eic_code: 16-character EIC code

    Returns:
        EICComponents object or None if parsing fails
    """
    if len(eic_code) != EIC_LENGTH:
        return None

    eic_code = eic_code.upper()

    try:
        components = EICComponents(
            office_id=eic_code[0:2],
            entity_type=eic_code[2],
            individual_id=eic_code[3:15],
            check_digit=eic_code[15]
        )
        return components
    except Exception:
        return None


def validate_eic_format(eic_code: str) -> Dict[str, any]:
    """Validate the format of an EIC code with detailed error reporting.

    Args:
        eic_code: EIC code to validate

    Returns:
        Dictionary with validation results:
        {
            'is_valid': bool,
            'errors': List[str],
            'components': Optional[EICComponents]
        }
    """
    errors: List[str] = []

    # Remove any hyphens/dashes (sometimes used for display)
    eic_clean = eic_code.replace('-', '').replace(' ', '').upper()

    # Check length
    if len(eic_clean) != EIC_LENGTH:
        errors.append(f"Invalid EIC length: expected {EIC_LENGTH} characters, got {len(eic_clean)}")
        return {'is_valid': False, 'errors': errors, 'components': None}

    # Check character set
    if not re.match(EIC_FULL_PATTERN, eic_clean):
        errors.append("EIC contains invalid characters. Only 0-9 and A-Z are allowed")
        return {'is_valid': False, 'errors': errors, 'components': None}

    # Parse components
    components = parse_eic_components(eic_clean)
    if not components:
        errors.append("Failed to parse EIC components")
        return {'is_valid': False, 'errors': errors, 'components': None}

    # Validate office identifier
    if not re.match(OFFICE_ID_PATTERN, components.office_id):
        errors.append(f"Invalid office identifier format: '{components.office_id}'")

    # Validate entity type
    if not re.match(ENTITY_TYPE_PATTERN, components.entity_type):
        errors.append(f"Invalid entity type format: '{components.entity_type}'")

    # Validate individual identifier
    if not re.match(INDIVIDUAL_ID_PATTERN, components.individual_id):
        errors.append(f"Invalid individual identifier format: '{components.individual_id}'")

    # Validate check digit
    if not validate_eic_check_digit(eic_clean):
        errors.append("Invalid check digit")

    is_valid = len(errors) == 0
    return {'is_valid': is_valid, 'errors': errors, 'components': components if is_valid else None}


def is_valid_eic(eic_code: str) -> Dict[str, any]:
    """Main EIC validation function with comprehensive checks.

    This is the primary public API for EIC validation.

    Args:
        eic_code: EIC code to validate

    Returns:
        Dictionary with validation results:
        {
            'is_valid': bool,
            'eic_code': str,  # normalized (uppercase, no hyphens)
            'errors': List[str],
            'components': Optional[EICComponents]
        }
    """
    result = validate_eic_format(eic_code)
    eic_clean = eic_code.replace('-', '').replace(' ', '').upper()

    return {
        'is_valid': result['is_valid'],
        'eic_code': eic_clean if len(eic_clean) == EIC_LENGTH else eic_code,
        'errors': result['errors'],
        'components': result['components']
    }
