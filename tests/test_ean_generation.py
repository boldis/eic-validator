"""Comprehensive unit tests for EAN generation logic."""

import pytest
from src.ean_generation import (
    generate_ean,
    generate_random_ean,
    generate_multiple_eans,
    is_valid_ean_type,
    InvalidEANTypeError,
    InvalidBaseCodeError,
    _validate_base_code,
    _generate_random_base,
)
from src.ean_validation import validate_ean


class TestEANTypeValidation:
    """Tests for EAN type validation."""

    def test_valid_ean_types(self):
        """Test that valid EAN types are recognized."""
        assert is_valid_ean_type("EAN-8") is True
        assert is_valid_ean_type("EAN-13") is True
        assert is_valid_ean_type("EAN-14") is True

    def test_invalid_ean_types(self):
        """Test that invalid EAN types are rejected."""
        assert is_valid_ean_type("EAN-12") is False
        assert is_valid_ean_type("UPC") is False
        assert is_valid_ean_type("") is False
        assert is_valid_ean_type("EAN8") is False  # Missing hyphen


class TestBaseCodeValidation:
    """Tests for base code validation."""

    def test_valid_base_code_ean8(self):
        """Test valid base code for EAN-8."""
        # Should not raise exception
        _validate_base_code("1234567", "EAN-8")

    def test_valid_base_code_ean13(self):
        """Test valid base code for EAN-13."""
        _validate_base_code("123456789012", "EAN-13")

    def test_valid_base_code_ean14(self):
        """Test valid base code for EAN-14."""
        _validate_base_code("1234567890123", "EAN-14")

    def test_invalid_ean_type(self):
        """Test that invalid EAN type raises error."""
        with pytest.raises(InvalidEANTypeError, match="Invalid EAN type"):
            _validate_base_code("1234567", "EAN-12")

    def test_invalid_base_code_length_ean8(self):
        """Test that wrong length for EAN-8 raises error."""
        with pytest.raises(InvalidBaseCodeError, match="must be exactly 7 digits"):
            _validate_base_code("12345678", "EAN-8")

    def test_invalid_base_code_length_ean13(self):
        """Test that wrong length for EAN-13 raises error."""
        with pytest.raises(InvalidBaseCodeError, match="must be exactly 12 digits"):
            _validate_base_code("12345678901", "EAN-13")

    def test_invalid_base_code_length_ean14(self):
        """Test that wrong length for EAN-14 raises error."""
        with pytest.raises(InvalidBaseCodeError, match="must be exactly 13 digits"):
            _validate_base_code("123456789012", "EAN-14")

    def test_non_numeric_base_code(self):
        """Test that non-numeric base code raises error."""
        with pytest.raises(InvalidBaseCodeError, match="must contain only numeric digits"):
            _validate_base_code("123456A", "EAN-8")

    def test_non_string_base_code(self):
        """Test that non-string base code raises error."""
        with pytest.raises(InvalidBaseCodeError, match="must be a string"):
            _validate_base_code(1234567, "EAN-8")


class TestEANGeneration:
    """Tests for EAN generation."""

    def test_generate_ean8(self):
        """Test EAN-8 generation."""
        ean = generate_ean("1234567", "EAN-8")
        assert len(ean) == 8
        assert ean[:7] == "1234567"
        # Validate the generated EAN
        is_valid, format_type, error = validate_ean(ean)
        assert is_valid is True
        assert format_type == "EAN-8"

    def test_generate_ean13(self):
        """Test EAN-13 generation."""
        ean = generate_ean("400638133393", "EAN-13")
        assert len(ean) == 13
        assert ean[:12] == "400638133393"
        # Validate the generated EAN
        is_valid, format_type, error = validate_ean(ean)
        assert is_valid is True
        assert format_type == "EAN-13"

    def test_generate_ean14(self):
        """Test EAN-14 generation."""
        ean = generate_ean("0400638133393", "EAN-14")
        assert len(ean) == 14
        assert ean[:13] == "0400638133393"
        # Validate the generated EAN
        is_valid, format_type, error = validate_ean(ean)
        assert is_valid is True
        assert format_type == "EAN-14"

    def test_generate_ean_case_insensitive(self):
        """Test that EAN type is case-insensitive."""
        ean_lower = generate_ean("1234567", "ean-8")
        ean_upper = generate_ean("1234567", "EAN-8")
        # Both should be valid and same length
        assert len(ean_lower) == 8
        assert len(ean_upper) == 8

    def test_generate_ean_deterministic_check_digit(self):
        """Test that same base code produces same check digit."""
        ean1 = generate_ean("1234567", "EAN-8")
        ean2 = generate_ean("1234567", "EAN-8")
        # Same base should produce same check digit
        assert ean1 == ean2

    def test_generate_ean_invalid_base_code(self):
        """Test that invalid base code raises error."""
        with pytest.raises(InvalidBaseCodeError):
            generate_ean("123456", "EAN-8")  # Too short

    def test_generate_ean_invalid_type(self):
        """Test that invalid EAN type raises error."""
        with pytest.raises(InvalidEANTypeError):
            generate_ean("1234567", "EAN-12")


class TestRandomEANGeneration:
    """Tests for random EAN generation."""

    def test_generate_random_ean8(self):
        """Test random EAN-8 generation."""
        ean = generate_random_ean("EAN-8")
        assert len(ean) == 8
        assert ean.isdigit()
        # Validate the generated EAN
        is_valid, format_type, error = validate_ean(ean)
        assert is_valid is True
        assert format_type == "EAN-8"

    def test_generate_random_ean13(self):
        """Test random EAN-13 generation."""
        ean = generate_random_ean("EAN-13")
        assert len(ean) == 13
        assert ean.isdigit()
        is_valid, format_type, error = validate_ean(ean)
        assert is_valid is True
        assert format_type == "EAN-13"

    def test_generate_random_ean14(self):
        """Test random EAN-14 generation."""
        ean = generate_random_ean("EAN-14")
        assert len(ean) == 14
        assert ean.isdigit()
        is_valid, format_type, error = validate_ean(ean)
        assert is_valid is True
        assert format_type == "EAN-14"

    def test_generate_random_ean_uniqueness(self):
        """Test that multiple random EANs are different."""
        eans = {generate_random_ean("EAN-13") for _ in range(100)}
        # With random generation, we should get mostly unique values
        # (though collisions are theoretically possible)
        assert len(eans) > 90

    def test_generate_random_ean_invalid_type(self):
        """Test that invalid type raises error."""
        with pytest.raises(InvalidEANTypeError):
            generate_random_ean("EAN-12")


class TestMultipleEANsGeneration:
    """Tests for generating multiple EANs."""

    def test_generate_multiple_eans_ean8(self):
        """Test generating multiple EAN-8 codes."""
        eans = generate_multiple_eans("EAN-8", 10)
        assert len(eans) == 10
        assert all(len(ean) == 8 for ean in eans)
        # All should be valid
        for ean in eans:
            is_valid, format_type, error = validate_ean(ean)
            assert is_valid is True
            assert format_type == "EAN-8"

    def test_generate_multiple_eans_ean13(self):
        """Test generating multiple EAN-13 codes."""
        eans = generate_multiple_eans("EAN-13", 5)
        assert len(eans) == 5
        assert all(len(ean) == 13 for ean in eans)

    def test_generate_multiple_eans_uniqueness(self):
        """Test that generated EANs are unique."""
        eans = generate_multiple_eans("EAN-13", 50)
        assert len(set(eans)) == 50  # All unique

    def test_generate_multiple_eans_invalid_count(self):
        """Test that invalid count raises error."""
        with pytest.raises(ValueError, match="must be a positive integer"):
            generate_multiple_eans("EAN-13", 0)
        with pytest.raises(ValueError, match="must be a positive integer"):
            generate_multiple_eans("EAN-13", -5)

    def test_generate_multiple_eans_invalid_type(self):
        """Test that invalid EAN type raises error."""
        with pytest.raises(InvalidEANTypeError):
            generate_multiple_eans("EAN-12", 10)


class TestRandomBaseGeneration:
    """Tests for random base code generation."""

    def test_generate_random_base_ean8(self):
        """Test random base generation for EAN-8."""
        base = _generate_random_base("EAN-8")
        assert len(base) == 7
        assert base.isdigit()

    def test_generate_random_base_ean13(self):
        """Test random base generation for EAN-13."""
        base = _generate_random_base("EAN-13")
        assert len(base) == 12
        assert base.isdigit()

    def test_generate_random_base_ean14(self):
        """Test random base generation for EAN-14."""
        base = _generate_random_base("EAN-14")
        assert len(base) == 13
        assert base.isdigit()

    def test_generate_random_base_invalid_type(self):
        """Test that invalid type raises error."""
        with pytest.raises(InvalidEANTypeError):
            _generate_random_base("INVALID")


class TestKnownEANs:
    """Tests with known real-world EAN codes."""

    def test_known_ean13_codes(self):
        """Test generation matches known EAN-13 codes."""
        test_cases = [
            ("400638133393", "4006381333931"),
            ("501234567890", "5012345678900"),  # Fixed: correct check digit is 0
        ]

        for base_code, expected_ean in test_cases:
            generated = generate_ean(base_code, "EAN-13")
            assert generated == expected_ean

    def test_known_ean8_codes(self):
        """Test generation matches known EAN-8 codes."""
        test_cases = [
            ("1234567", "12345670"),
            ("9638507", "96385074"),
        ]

        for base_code, expected_ean in test_cases:
            generated = generate_ean(base_code, "EAN-8")
            assert generated == expected_ean


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_generate_all_zeros_ean8(self):
        """Test generation with all zeros for EAN-8."""
        ean = generate_ean("0000000", "EAN-8")
        assert len(ean) == 8
        is_valid, _, _ = validate_ean(ean)
        assert is_valid is True

    def test_generate_all_nines_ean13(self):
        """Test generation with all nines for EAN-13."""
        ean = generate_ean("999999999999", "EAN-13")
        assert len(ean) == 13
        is_valid, _, _ = validate_ean(ean)
        assert is_valid is True

    def test_generate_leading_zeros_ean14(self):
        """Test generation with leading zeros for EAN-14."""
        ean = generate_ean("0000000000001", "EAN-14")
        assert len(ean) == 14
        assert ean[:13] == "0000000000001"
        is_valid, _, _ = validate_ean(ean)
        assert is_valid is True


class TestIntegrationWithValidation:
    """Integration tests ensuring generated EANs pass validation."""

    def test_generated_eans_always_valid(self):
        """Test that all generated EANs pass validation."""
        for ean_type in ["EAN-8", "EAN-13", "EAN-14"]:
            for _ in range(20):  # Test multiple times
                ean = generate_random_ean(ean_type)
                is_valid, format_type, error = validate_ean(ean)
                assert (
                    is_valid is True
                ), f"Generated {ean_type} {ean} should be valid, error: {error}"
                assert format_type == ean_type

    def test_bulk_generation_all_valid(self):
        """Test that bulk generated EANs are all valid."""
        eans = generate_multiple_eans("EAN-13", 50)
        for ean in eans:
            is_valid, format_type, error = validate_ean(ean)
            assert is_valid is True
            assert format_type == "EAN-13"
