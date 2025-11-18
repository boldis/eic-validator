"""Comprehensive unit tests for EAN validation logic."""

import pytest
from src.ean_validation import (
    calculate_ean_check_digit,
    validate_ean_check_digit,
    validate_ean,
    parse_ean_components,
    validate_ean_format,
    is_valid_ean,
    _calculate_ean_check_digit,
    EAN_8_LENGTH,
    EAN_13_LENGTH,
    EAN_14_LENGTH,
)


class TestCheckDigitCalculation:
    """Tests for EAN check digit calculation."""

    def test_ean8_check_digit_calculation(self):
        """Test EAN-8 check digit calculation with known values."""
        # Known valid EAN-8 codes
        assert calculate_ean_check_digit("1234567") == "0"
        assert calculate_ean_check_digit("9638507") == "4"
        assert calculate_ean_check_digit("5012345") == "2"  # Fixed: correct check digit is 2

    def test_ean13_check_digit_calculation(self):
        """Test EAN-13 check digit calculation with known values."""
        # Known valid EAN-13 codes
        assert calculate_ean_check_digit("400638133393") == "1"
        assert calculate_ean_check_digit("501234567890") == "0"  # Fixed: correct check digit is 0
        assert calculate_ean_check_digit("978014300723") == "4"  # Fixed: correct check digit is 4

    def test_ean14_check_digit_calculation(self):
        """Test EAN-14 check digit calculation with known values."""
        # Known valid EAN-14 codes
        assert calculate_ean_check_digit("0400638133393") == "1"  # Fixed: correct check digit is 1
        assert calculate_ean_check_digit("1234567890123") == "1"  # Fixed: correct check digit is 1

    def test_check_digit_invalid_length(self):
        """Test that invalid length raises ValueError."""
        with pytest.raises(ValueError, match="must be 7, 12, or 13 digits"):
            calculate_ean_check_digit("123")
        with pytest.raises(ValueError, match="must be 7, 12, or 13 digits"):
            calculate_ean_check_digit("12345678901234")

    def test_check_digit_non_numeric(self):
        """Test that non-numeric input raises ValueError."""
        with pytest.raises(ValueError, match="must be numeric"):
            calculate_ean_check_digit("123456A")
        with pytest.raises(ValueError, match="must be numeric"):
            calculate_ean_check_digit("12345-7")


class TestCheckDigitValidation:
    """Tests for EAN check digit validation."""

    def test_validate_ean8_valid(self):
        """Test validation of valid EAN-8 codes."""
        assert validate_ean_check_digit("12345670") is True
        assert validate_ean_check_digit("96385074") is True

    def test_validate_ean13_valid(self):
        """Test validation of valid EAN-13 codes."""
        assert validate_ean_check_digit("4006381333931") is True
        assert validate_ean_check_digit("5012345678900") is True  # Fixed: correct full code

    def test_validate_ean14_valid(self):
        """Test validation of valid EAN-14 codes."""
        assert validate_ean_check_digit("04006381333931") is True  # Fixed: correct full code

    def test_validate_invalid_check_digit(self):
        """Test validation fails with incorrect check digit."""
        assert validate_ean_check_digit("12345671") is False  # Wrong check digit
        assert validate_ean_check_digit("4006381333932") is False  # Wrong check digit

    def test_validate_non_numeric(self):
        """Test validation fails with non-numeric input."""
        assert validate_ean_check_digit("1234567A") is False
        assert validate_ean_check_digit("400638133393X") is False

    def test_validate_invalid_length(self):
        """Test validation fails with invalid length."""
        assert validate_ean_check_digit("123") is False
        assert validate_ean_check_digit("12345") is False


class TestEANComponents:
    """Tests for EAN component parsing."""

    def test_parse_ean8_components(self):
        """Test parsing EAN-8 components."""
        components = parse_ean_components("12345670")
        assert components is not None
        assert components.data_part == "1234567"
        assert components.check_digit == "0"
        assert components.format == "EAN-8"
        assert components.full_code == "12345670"

    def test_parse_ean13_components(self):
        """Test parsing EAN-13 components."""
        components = parse_ean_components("4006381333931")
        assert components is not None
        assert components.data_part == "400638133393"
        assert components.check_digit == "1"
        assert components.format == "EAN-13"

    def test_parse_ean14_components(self):
        """Test parsing EAN-14 components."""
        components = parse_ean_components("04006381333931")  # Fixed: correct full code
        assert components is not None
        assert components.data_part == "0400638133393"
        assert components.check_digit == "1"  # Fixed: correct check digit
        assert components.format == "EAN-14"

    def test_parse_invalid_length(self):
        """Test parsing returns None for invalid length."""
        assert parse_ean_components("123") is None
        assert parse_ean_components("12345") is None

    def test_parse_non_numeric(self):
        """Test parsing returns None for non-numeric input."""
        assert parse_ean_components("1234567A") is None
        assert parse_ean_components("ABC1234567890") is None


class TestEANValidation:
    """Tests for main EAN validation function."""

    def test_validate_ean8_valid(self):
        """Test validation of valid EAN-8."""
        is_valid, format_type, error = validate_ean("12345670")
        assert is_valid is True
        assert format_type == "EAN-8"
        assert error is None

    def test_validate_ean13_valid(self):
        """Test validation of valid EAN-13."""
        is_valid, format_type, error = validate_ean("4006381333931")
        assert is_valid is True
        assert format_type == "EAN-13"
        assert error is None

    def test_validate_ean14_valid(self):
        """Test validation of valid EAN-14."""
        is_valid, format_type, error = validate_ean("04006381333931")  # Fixed: correct check digit is 1
        assert is_valid is True
        assert format_type == "EAN-14"
        assert error is None

    def test_validate_with_spaces(self):
        """Test validation with spaces (should be cleaned)."""
        is_valid, format_type, error = validate_ean(" 12345670 ")
        assert is_valid is True
        assert format_type == "EAN-8"

    def test_validate_with_hyphens(self):
        """Test validation with hyphens (should be cleaned)."""
        is_valid, format_type, error = validate_ean("1234-5670")
        assert is_valid is True
        assert format_type == "EAN-8"

    def test_validate_invalid_check_digit(self):
        """Test validation fails with invalid check digit."""
        is_valid, format_type, error = validate_ean("12345671")
        assert is_valid is False
        assert format_type is None
        assert "Invalid check digit" in error

    def test_validate_invalid_length(self):
        """Test validation fails with invalid length."""
        is_valid, format_type, error = validate_ean("12345")
        assert is_valid is False
        assert format_type is None
        assert "Invalid EAN length" in error

    def test_validate_non_numeric(self):
        """Test validation fails with non-numeric characters."""
        is_valid, format_type, error = validate_ean("1234567A")
        assert is_valid is False
        assert format_type is None
        assert "must contain only numeric digits" in error

    def test_validate_empty_string(self):
        """Test validation fails with empty string."""
        is_valid, format_type, error = validate_ean("")
        assert is_valid is False
        assert format_type is None

    def test_validate_special_characters(self):
        """Test validation fails with special characters."""
        is_valid, format_type, error = validate_ean("1234567!")
        assert is_valid is False
        assert "must contain only numeric digits" in error


class TestEANFormatValidation:
    """Tests for detailed EAN format validation."""

    def test_format_validation_valid_ean8(self):
        """Test format validation for valid EAN-8."""
        result = validate_ean_format("12345670")
        assert result['is_valid'] is True
        assert result['format'] == "EAN-8"
        assert len(result['errors']) == 0
        assert result['components'] is not None

    def test_format_validation_valid_ean13(self):
        """Test format validation for valid EAN-13."""
        result = validate_ean_format("4006381333931")
        assert result['is_valid'] is True
        assert result['format'] == "EAN-13"
        assert len(result['errors']) == 0

    def test_format_validation_invalid_check_digit(self):
        """Test format validation detects invalid check digit."""
        result = validate_ean_format("12345679")
        assert result['is_valid'] is False
        assert "Invalid check digit" in result['errors']

    def test_format_validation_non_numeric(self):
        """Test format validation detects non-numeric input."""
        result = validate_ean_format("ABC12345")
        assert result['is_valid'] is False
        assert any("numeric digits" in err for err in result['errors'])

    def test_format_validation_spaces_cleaned(self):
        """Test that spaces are properly cleaned before validation."""
        result = validate_ean_format("  12345670  ")
        assert result['is_valid'] is True


class TestIsValidEAN:
    """Tests for is_valid_ean comprehensive validation."""

    def test_is_valid_ean_valid_ean8(self):
        """Test comprehensive validation for valid EAN-8."""
        result = is_valid_ean("12345670")
        assert result['is_valid'] is True
        assert result['ean_code'] == "12345670"
        assert result['format'] == "EAN-8"
        assert len(result['errors']) == 0
        assert result['components'] is not None

    def test_is_valid_ean_valid_ean13(self):
        """Test comprehensive validation for valid EAN-13."""
        result = is_valid_ean("4006381333931")
        assert result['is_valid'] is True
        assert result['ean_code'] == "4006381333931"
        assert result['format'] == "EAN-13"

    def test_is_valid_ean_invalid(self):
        """Test comprehensive validation for invalid EAN."""
        result = is_valid_ean("12345679")
        assert result['is_valid'] is False
        assert len(result['errors']) > 0

    def test_is_valid_ean_normalized(self):
        """Test that EAN code is normalized in response."""
        result = is_valid_ean(" 1234-5670 ")
        assert result['ean_code'] == "12345670"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_all_zeros_ean8(self):
        """Test EAN-8 with all zeros."""
        # 0000000 -> check digit should be 0
        is_valid, format_type, error = validate_ean("00000000")
        assert is_valid is True
        assert format_type == "EAN-8"

    def test_all_nines_ean13(self):
        """Test EAN-13 with all nines."""
        # Calculate check digit for 999999999999
        check_digit = calculate_ean_check_digit("999999999999")
        ean = f"999999999999{check_digit}"
        is_valid, format_type, error = validate_ean(ean)
        assert is_valid is True
        assert format_type == "EAN-13"

    def test_boundary_length_7(self):
        """Test with exactly 7 digits (too short for EAN-8)."""
        is_valid, format_type, error = validate_ean("1234567")
        assert is_valid is False

    def test_boundary_length_9(self):
        """Test with 9 digits (between EAN-8 and EAN-13)."""
        is_valid, format_type, error = validate_ean("123456789")
        assert is_valid is False

    def test_boundary_length_12(self):
        """Test with 12 digits (too short for EAN-13)."""
        is_valid, format_type, error = validate_ean("123456789012")
        assert is_valid is False

    def test_boundary_length_15(self):
        """Test with 15 digits (too long for EAN-14)."""
        is_valid, format_type, error = validate_ean("123456789012345")
        assert is_valid is False


class TestRealWorldEANs:
    """Tests with real-world EAN codes."""

    def test_common_product_eans(self):
        """Test with common product EAN-13 codes."""
        # These are examples of real EAN-13 patterns
        # Note: Check digits may need adjustment for actual products
        test_codes = [
            "5901234123457",  # Polish product
            "4006381333931",  # German product
        ]

        for code in test_codes:
            is_valid, format_type, error = validate_ean(code)
            assert is_valid is True, f"EAN {code} should be valid"
            assert format_type == "EAN-13"

    def test_isbn_as_ean13(self):
        """Test ISBN-13 (which is EAN-13 with 978 prefix)."""
        # ISBN-13: 978-0-14-300723-4 = 9780143007234 (Fixed: correct check digit)
        is_valid, format_type, error = validate_ean("9780143007234")
        assert is_valid is True
        assert format_type == "EAN-13"
