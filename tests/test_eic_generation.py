"""Comprehensive unit tests for EIC generation logic."""

import pytest
from src.eic_generation import (
    generate_eic,
    generate_multiple_eics,
    is_valid_country_code,
    is_valid_entity_type,
    _generate_base_identifier,
    _validate_eic_generation_params,
    InvalidCountryCodeError,
    InvalidEntityTypeError,
    VALID_COUNTRY_CODES,
    VALID_ENTITY_TYPES,
)
from src.eic_validation import is_valid_eic


class TestCountryCodeValidation:
    """Tests for country code validation."""

    def test_valid_country_codes(self):
        """Test that valid country codes are accepted."""
        assert is_valid_country_code("27") is True
        assert is_valid_country_code("10") is True
        assert is_valid_country_code("X1") is True

    def test_invalid_country_code_wrong_length(self):
        """Test that wrong length codes are rejected."""
        assert is_valid_country_code("2") is False
        assert is_valid_country_code("270") is False
        assert is_valid_country_code("") is False

    def test_invalid_country_code_not_in_list(self):
        """Test that codes not in ENTSO-E list are rejected."""
        assert is_valid_country_code("99") is False
        assert is_valid_country_code("AB") is False
        assert is_valid_country_code("--") is False

    def test_country_code_case_insensitive(self):
        """Test that country codes are case-insensitive."""
        assert is_valid_country_code("x1") is True
        assert is_valid_country_code("X1") is True

    def test_country_code_non_string(self):
        """Test that non-string input returns False."""
        assert is_valid_country_code(27) is False
        assert is_valid_country_code(None) is False


class TestEntityTypeValidation:
    """Tests for entity type validation."""

    def test_valid_entity_types(self):
        """Test that valid entity types are accepted."""
        assert is_valid_entity_type("T") is True
        assert is_valid_entity_type("X") is True
        assert is_valid_entity_type("Z") is True
        assert is_valid_entity_type("1") is True

    def test_invalid_entity_type_wrong_length(self):
        """Test that wrong length types are rejected."""
        assert is_valid_entity_type("") is False
        assert is_valid_entity_type("TX") is False
        assert is_valid_entity_type("ABC") is False

    def test_invalid_entity_type_not_in_list(self):
        """Test that types not in ENTSO-E list are rejected."""
        assert is_valid_entity_type("Q") is False
        assert is_valid_entity_type("@") is False
        assert is_valid_entity_type("-") is False

    def test_entity_type_case_insensitive(self):
        """Test that entity types are case-insensitive."""
        assert is_valid_entity_type("t") is True
        assert is_valid_entity_type("T") is True
        assert is_valid_entity_type("x") is True

    def test_entity_type_non_string(self):
        """Test that non-string input returns False."""
        assert is_valid_entity_type(1) is False
        assert is_valid_entity_type(None) is False


class TestParameterValidation:
    """Tests for combined parameter validation."""

    def test_valid_parameters(self):
        """Test that valid parameters don't raise exceptions."""
        _validate_eic_generation_params("27", "X")
        _validate_eic_generation_params("10", "T")
        _validate_eic_generation_params("X1", "Z")

    def test_invalid_country_code_raises_exception(self):
        """Test that invalid country code raises InvalidCountryCodeError."""
        with pytest.raises(InvalidCountryCodeError, match="Invalid country code"):
            _validate_eic_generation_params("99", "X")

        with pytest.raises(InvalidCountryCodeError, match="Invalid country code"):
            _validate_eic_generation_params("A", "X")

    def test_invalid_entity_type_raises_exception(self):
        """Test that invalid entity type raises InvalidEntityTypeError."""
        with pytest.raises(InvalidEntityTypeError, match="Invalid entity type"):
            _validate_eic_generation_params("27", "Q")

        with pytest.raises(InvalidEntityTypeError, match="Invalid entity type"):
            _validate_eic_generation_params("27", "XX")


class TestBaseIdentifierGeneration:
    """Tests for random base identifier generation."""

    def test_identifier_length(self):
        """Test that generated identifier is exactly 12 characters."""
        identifier = _generate_base_identifier()
        assert len(identifier) == 12

    def test_identifier_characters(self):
        """Test that identifier contains only uppercase alphanumeric."""
        identifier = _generate_base_identifier()
        assert identifier.isupper()
        assert identifier.isalnum()

    def test_identifier_randomness(self):
        """Test that multiple calls produce different identifiers."""
        identifiers = [_generate_base_identifier() for _ in range(100)]
        # With 36^12 possibilities, getting duplicates in 100 is extremely unlikely
        unique_identifiers = set(identifiers)
        assert len(unique_identifiers) > 90  # Allow some small chance of collision

    def test_identifier_character_set(self):
        """Test that identifier uses correct character set."""
        for _ in range(10):
            identifier = _generate_base_identifier()
            for char in identifier:
                assert char in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class TestGenerateEIC:
    """Tests for the main generate_eic function."""

    def test_generate_eic_valid_inputs(self):
        """Test EIC generation with valid inputs."""
        eic = generate_eic("27", "X")
        assert len(eic) == 16
        assert eic[:2] == "27"
        assert eic[2] == "X"

    def test_generate_eic_format(self):
        """Test that generated EIC follows correct format."""
        eic = generate_eic("10", "T")
        assert len(eic) == 16
        assert eic.isupper()
        assert eic.replace("-", "").isalnum()

    def test_generated_eic_passes_validation(self):
        """Test that generated EICs pass validation."""
        for _ in range(10):
            eic = generate_eic("27", "X")
            result = is_valid_eic(eic)
            assert result['is_valid'] is True
            assert len(result['errors']) == 0

    def test_generate_eic_different_country_codes(self):
        """Test generation with different country codes."""
        eic1 = generate_eic("10", "X")
        eic2 = generate_eic("27", "X")
        assert eic1[:2] == "10"
        assert eic2[:2] == "27"
        assert eic1 != eic2

    def test_generate_eic_different_entity_types(self):
        """Test generation with different entity types."""
        eic1 = generate_eic("27", "T")
        eic2 = generate_eic("27", "Z")
        assert eic1[2] == "T"
        assert eic2[2] == "Z"
        assert eic1 != eic2

    def test_generate_eic_case_normalization(self):
        """Test that inputs are normalized to uppercase."""
        eic1 = generate_eic("27", "x")
        eic2 = generate_eic("x1", "T")
        assert eic1[2] == "X"
        assert eic2[:2] == "X1"

    def test_generate_eic_invalid_country_code(self):
        """Test that invalid country code raises exception."""
        with pytest.raises(InvalidCountryCodeError):
            generate_eic("99", "X")

        with pytest.raises(InvalidCountryCodeError):
            generate_eic("ABC", "X")

    def test_generate_eic_invalid_entity_type(self):
        """Test that invalid entity type raises exception."""
        with pytest.raises(InvalidEntityTypeError):
            generate_eic("27", "Q")

        with pytest.raises(InvalidEntityTypeError):
            generate_eic("27", "XY")

    def test_generate_eic_randomness(self):
        """Test that multiple calls with same parameters produce different EICs."""
        eics = [generate_eic("27", "X") for _ in range(50)]
        unique_eics = set(eics)
        # Should have high uniqueness due to random identifier
        assert len(unique_eics) > 45


class TestGenerateMultipleEICs:
    """Tests for generating multiple EIC codes."""

    def test_generate_multiple_eics_count(self):
        """Test that correct number of EICs are generated."""
        eics = generate_multiple_eics("27", "X", 10)
        assert len(eics) == 10

    def test_generate_multiple_eics_uniqueness(self):
        """Test that all generated EICs are unique."""
        eics = generate_multiple_eics("27", "X", 20)
        assert len(set(eics)) == 20

    def test_generate_multiple_eics_all_valid(self):
        """Test that all generated EICs are valid."""
        eics = generate_multiple_eics("10", "T", 15)
        for eic in eics:
            result = is_valid_eic(eic)
            assert result['is_valid'] is True

    def test_generate_multiple_eics_same_prefix(self):
        """Test that all EICs have same country code and entity type."""
        eics = generate_multiple_eics("27", "Z", 10)
        for eic in eics:
            assert eic[:2] == "27"
            assert eic[2] == "Z"

    def test_generate_multiple_eics_invalid_count(self):
        """Test that invalid count raises ValueError."""
        with pytest.raises(ValueError, match="positive integer"):
            generate_multiple_eics("27", "X", 0)

        with pytest.raises(ValueError, match="positive integer"):
            generate_multiple_eics("27", "X", -5)

    def test_generate_multiple_eics_invalid_params(self):
        """Test that invalid parameters raise appropriate exceptions."""
        with pytest.raises(InvalidCountryCodeError):
            generate_multiple_eics("99", "X", 5)

        with pytest.raises(InvalidEntityTypeError):
            generate_multiple_eics("27", "Q", 5)


class TestIntegrationWithValidation:
    """Integration tests with the validation module."""

    def test_all_entity_types_generate_valid_eics(self):
        """Test that all entity types produce valid EICs."""
        for entity_type in list(VALID_ENTITY_TYPES)[:10]:  # Test subset
            eic = generate_eic("27", entity_type)
            result = is_valid_eic(eic)
            assert result['is_valid'] is True, f"Failed for entity type: {entity_type}"

    def test_all_country_codes_generate_valid_eics(self):
        """Test that all country codes produce valid EICs."""
        for country_code in list(VALID_COUNTRY_CODES)[:10]:  # Test subset
            eic = generate_eic(country_code, "X")
            result = is_valid_eic(eic)
            assert result['is_valid'] is True, f"Failed for country code: {country_code}"

    def test_generated_eic_components(self):
        """Test that generated EIC components are correctly parsed."""
        eic = generate_eic("27", "X")
        result = is_valid_eic(eic)
        assert result['components'] is not None
        assert result['components'].office_id == "27"
        assert result['components'].entity_type == "X"
        assert len(result['components'].individual_id) == 12

    def test_bulk_generation_validation(self):
        """Test bulk generation with validation."""
        eics = generate_multiple_eics("10", "T", 100)
        for eic in eics:
            result = is_valid_eic(eic)
            assert result['is_valid'] is True
            assert result['components'].office_id == "10"
            assert result['components'].entity_type == "T"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_numeric_entity_type(self):
        """Test generation with numeric entity types."""
        eic = generate_eic("27", "1")
        result = is_valid_eic(eic)
        assert result['is_valid'] is True
        assert eic[2] == "1"

    def test_alphanumeric_country_code(self):
        """Test generation with alphanumeric country codes."""
        eic = generate_eic("X1", "T")
        result = is_valid_eic(eic)
        assert result['is_valid'] is True
        assert eic[:2] == "X1"

    def test_mixed_case_inputs(self):
        """Test that mixed case inputs are handled correctly."""
        eic1 = generate_eic("x1", "t")
        eic2 = generate_eic("X1", "T")
        # Both should work and produce uppercase results
        assert eic1[:3].isupper()
        assert eic2[:3].isupper()
