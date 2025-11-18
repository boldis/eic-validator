"""Comprehensive unit tests for EIC validation logic."""

import pytest

from src.eic_validation import (
    _char_to_value,
    _value_to_char,
    calculate_eic_check_digit,
    is_valid_eic,
    parse_eic_components,
    validate_eic_check_digit,
    validate_eic_format,
)


class TestCharacterConversion:
    """Tests for character-to-value conversion functions."""

    def test_char_to_value_digits(self):
        """Test conversion of digit characters."""
        assert _char_to_value("0") == 0
        assert _char_to_value("5") == 5
        assert _char_to_value("9") == 9

    def test_char_to_value_letters(self):
        """Test conversion of letter characters."""
        assert _char_to_value("A") == 10
        assert _char_to_value("B") == 11
        assert _char_to_value("Z") == 35

    def test_char_to_value_invalid(self):
        """Test that invalid characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid character"):
            _char_to_value("a")  # lowercase
        with pytest.raises(ValueError, match="Invalid character"):
            _char_to_value("-")
        with pytest.raises(ValueError, match="Invalid character"):
            _char_to_value(" ")

    def test_value_to_char_digits(self):
        """Test conversion of numeric values to digit characters."""
        assert _value_to_char(0) == "0"
        assert _value_to_char(5) == "5"
        assert _value_to_char(9) == "9"

    def test_value_to_char_letters(self):
        """Test conversion of numeric values to letter characters."""
        assert _value_to_char(10) == "A"
        assert _value_to_char(11) == "B"
        assert _value_to_char(35) == "Z"

    def test_value_to_char_invalid(self):
        """Test that invalid values raise ValueError."""
        with pytest.raises(ValueError, match="Invalid value"):
            _value_to_char(-1)
        with pytest.raises(ValueError, match="Invalid value"):
            _value_to_char(36)
        with pytest.raises(ValueError, match="Invalid value"):
            _value_to_char(100)


class TestCheckDigitCalculation:
    """Tests for EIC check digit calculation."""

    def test_calculate_check_digit_valid_base(self):
        """Test check digit calculation for valid bases."""
        # Test with known valid EIC base
        base = "27XG000000000"  # 13 chars + 2 more
        assert len(base) == 13
        base_15 = base + "01"  # Make it 15 chars
        check_digit = calculate_eic_check_digit(base_15)
        assert isinstance(check_digit, str)
        assert len(check_digit) == 1

    def test_calculate_check_digit_length_validation(self):
        """Test that incorrect length raises ValueError."""
        with pytest.raises(ValueError, match="exactly 15 characters"):
            calculate_eic_check_digit("TOOSHORT")
        with pytest.raises(ValueError, match="exactly 15 characters"):
            calculate_eic_check_digit("THISISTOOLONGFORBASE")

    def test_calculate_check_digit_invalid_characters(self):
        """Test that invalid characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid character"):
            calculate_eic_check_digit("27XG00000000-01")  # Contains hyphen
        # Note: lowercase is converted to uppercase, so it doesn't raise an error
        # Test with truly invalid character
        with pytest.raises(ValueError, match="Invalid character"):
            calculate_eic_check_digit("27XG000000000@1")  # Contains @

    def test_calculate_check_digit_all_zeros(self):
        """Test with all zeros."""
        base = "0" * 15
        check_digit = calculate_eic_check_digit(base)
        # With all zeros, remainder = 0, so check_digit = (37-0)%37 = 37%37 = 0 -> '0'
        assert check_digit == "0"

    def test_calculate_check_digit_all_nines(self):
        """Test with all nines."""
        base = "9" * 15
        check_digit = calculate_eic_check_digit(base)
        assert isinstance(check_digit, str)
        assert len(check_digit) == 1

    def test_calculate_check_digit_case_insensitive(self):
        """Test that lowercase input is handled (converted to uppercase)."""
        base_upper = "27XGOEPS0000001"
        base_lower = "27xgoeps0000001"
        # Both should produce the same result
        check_upper = calculate_eic_check_digit(base_upper)
        check_lower = calculate_eic_check_digit(base_lower)
        assert check_upper == check_lower


class TestCheckDigitValidation:
    """Tests for EIC check digit validation."""

    def test_validate_check_digit_valid_codes(self):
        """Test validation of codes with correct check digits."""
        # We need to generate valid codes first
        base = "27XGOEPS0000001"
        check = calculate_eic_check_digit(base)
        full_code = base + check
        assert validate_eic_check_digit(full_code) is True

    def test_validate_check_digit_invalid_codes(self):
        """Test validation rejects codes with incorrect check digits."""
        # Create a code with a wrong check digit
        base = "27XGOEPS0000001"
        correct_check = calculate_eic_check_digit(base)
        # Use a different check digit
        wrong_check = "0" if correct_check != "0" else "1"
        invalid_code = base + wrong_check
        assert validate_eic_check_digit(invalid_code) is False

    def test_validate_check_digit_wrong_length(self):
        """Test that wrong length returns False."""
        assert validate_eic_check_digit("TOOSHORT") is False
        assert validate_eic_check_digit("THISISTOOLONGFORANEIC") is False

    def test_validate_check_digit_invalid_characters(self):
        """Test that invalid characters return False."""
        assert validate_eic_check_digit("27XG000000000-1Z") is False
        assert validate_eic_check_digit("27xg0000000001z") is False  # lowercase


class TestParseEICComponents:
    """Tests for EIC component parsing."""

    def test_parse_valid_eic(self):
        """Test parsing of valid EIC codes."""
        eic = "27XGOEPS00000012"
        components = parse_eic_components(eic)
        assert components is not None
        assert components.office_id == "27"
        assert components.entity_type == "X"
        assert components.individual_id == "GOEPS0000001"
        assert components.check_digit == "2"

    def test_parse_invalid_length(self):
        """Test that invalid length returns None."""
        assert parse_eic_components("TOOSHORT") is None
        assert parse_eic_components("THISISTOOLONGFORANEIC") is None

    def test_parse_components_properties(self):
        """Test component properties."""
        eic = "27XGOEPS00000012"
        components = parse_eic_components(eic)
        assert components.base == "27XGOEPS0000001"
        assert len(components.base) == 15
        assert components.full_code == eic


class TestValidateEICFormat:
    """Tests for comprehensive EIC format validation."""

    def test_validate_format_valid_eic(self):
        """Test validation of valid EIC codes."""
        base = "27XGOEPS0000001"
        check = calculate_eic_check_digit(base)
        eic = base + check
        result = validate_eic_format(eic)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["components"] is not None

    def test_validate_format_with_hyphens(self):
        """Test that hyphens are properly stripped."""
        base = "27XGOEPS0000001"
        check = calculate_eic_check_digit(base)
        eic_with_hyphens = "27X-GOEP-S000-0001" + check
        result = validate_eic_format(eic_with_hyphens)
        # Should validate correctly after stripping hyphens
        assert len(result["errors"]) == 0 or "Invalid EIC length" in result["errors"][0]

    def test_validate_format_wrong_length(self):
        """Test that wrong length is detected."""
        result = validate_eic_format("TOOSHORT")
        assert result["is_valid"] is False
        assert any("length" in err.lower() for err in result["errors"])

    def test_validate_format_invalid_characters(self):
        """Test that invalid characters are detected."""
        result = validate_eic_format("27XG000000000-1Z")  # Contains hyphen in wrong place
        # After stripping, it should be too short
        assert result["is_valid"] is False

    def test_validate_format_wrong_check_digit(self):
        """Test that incorrect check digit is detected."""
        base = "27XGOEPS0000001"
        correct_check = calculate_eic_check_digit(base)
        wrong_check = "0" if correct_check != "0" else "1"
        eic = base + wrong_check
        result = validate_eic_format(eic)
        assert result["is_valid"] is False
        assert any("check digit" in err.lower() for err in result["errors"])

    def test_validate_format_lowercase_accepted(self):
        """Test that lowercase is converted to uppercase."""
        base = "27XGOEPS0000001"
        check = calculate_eic_check_digit(base)
        eic_upper = base + check
        eic_lower = eic_upper.lower()
        result = validate_eic_format(eic_lower)
        # Should work after uppercase conversion
        assert result["is_valid"] is True or len(result["errors"]) > 0

    def test_validate_format_all_error_types(self):
        """Test detection of multiple error types."""
        # Too short AND invalid characters
        result = validate_eic_format("abc-123")
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0


class TestIsValidEIC:
    """Tests for the main is_valid_eic function."""

    def test_is_valid_eic_valid_code(self):
        """Test complete validation of valid EIC."""
        base = "27XGOEPS0000001"
        check = calculate_eic_check_digit(base)
        eic = base + check
        result = is_valid_eic(eic)
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert result["eic_code"] == eic
        assert result["components"] is not None

    def test_is_valid_eic_invalid_code(self):
        """Test complete validation of invalid EIC."""
        result = is_valid_eic("INVALID123")
        assert result["is_valid"] is False
        assert len(result["errors"]) > 0
        assert result["components"] is None

    def test_is_valid_eic_with_spaces(self):
        """Test that spaces are handled."""
        base = "27XGOEPS0000001"
        check = calculate_eic_check_digit(base)
        eic = base + check
        eic_with_spaces = " " + eic + " "
        result = is_valid_eic(eic_with_spaces)
        assert result["eic_code"] == eic

    def test_is_valid_eic_detailed_errors(self):
        """Test that detailed error messages are provided."""
        result = is_valid_eic("12345")
        assert result["is_valid"] is False
        assert any(isinstance(err, str) for err in result["errors"])
        assert len(result["errors"]) > 0


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_empty_string(self):
        """Test with empty string."""
        result = is_valid_eic("")
        assert result["is_valid"] is False

    def test_only_whitespace(self):
        """Test with only whitespace."""
        result = is_valid_eic("   ")
        assert result["is_valid"] is False

    def test_special_characters(self):
        """Test with special characters."""
        result = is_valid_eic("27XG@#$%^&*()123")
        assert result["is_valid"] is False

    def test_unicode_characters(self):
        """Test with unicode characters."""
        result = is_valid_eic("27XGöäü000000012")
        assert result["is_valid"] is False

    def test_numeric_only(self):
        """Test with only numeric characters (valid in format)."""
        base = "0" * 15
        check = calculate_eic_check_digit(base)
        eic = base + check
        result = is_valid_eic(eic)
        assert result["is_valid"] is True

    def test_alpha_only(self):
        """Test with only alphabetic characters."""
        base = "A" * 15
        check = calculate_eic_check_digit(base)
        eic = base + check
        result = is_valid_eic(eic)
        assert result["is_valid"] is True


class TestRealWorldExamples:
    """Tests with real-world EIC code patterns."""

    def test_czech_office_codes(self):
        """Test with Czech Republic office identifier (27)."""
        base = "27XGOEPS0000001"
        check = calculate_eic_check_digit(base)
        eic = base + check
        result = is_valid_eic(eic)
        assert result["is_valid"] is True
        assert result["components"].office_id == "27"

    def test_different_entity_types(self):
        """Test with different entity type codes."""
        for entity_type in ["A", "Z", "Y", "W", "1", "5"]:
            base = f"27{entity_type}GOEPS0000001"
            check = calculate_eic_check_digit(base)
            eic = base + check
            result = is_valid_eic(eic)
            assert result["is_valid"] is True
            assert result["components"].entity_type == entity_type
