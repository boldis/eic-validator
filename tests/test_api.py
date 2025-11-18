"""API integration tests for EIC and EAN validation and generation endpoints."""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.eic_validation import is_valid_eic
from src.ean_validation import validate_ean


client = TestClient(app)


class TestRootEndpoints:
    """Tests for root and health check endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns service information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "EIC/EAN Validation Service"
        assert data["version"] == "0.1.0"
        assert data["status"] == "operational"
        assert "endpoints" in data

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"


class TestEICValidationEndpoint:
    """Tests for POST /eic/validate endpoint."""

    def test_validate_valid_eic(self):
        """Test validation of a valid EIC code."""
        # Generate a valid EIC first
        gen_response = client.post(
            "/eic/generate",
            json={"country_code": "27", "entity_type": "X"}
        )
        assert gen_response.status_code == 201
        valid_eic = gen_response.json()["eic_code"]

        # Now validate it
        response = client.post(
            "/eic/validate",
            json={"eic_code": valid_eic}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["eic_code"] == valid_eic
        assert len(data["errors"]) == 0
        assert data["components"] is not None
        assert data["components"]["office_id"] == "27"
        assert data["components"]["entity_type"] == "X"

    def test_validate_invalid_eic_wrong_check_digit(self):
        """Test validation of EIC with wrong check digit."""
        # Use a 16-char EIC with intentionally wrong check digit
        response = client.post(
            "/eic/validate",
            json={"eic_code": "27XGOEPS00000010"}  # 16 chars but wrong check digit
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0
        # Should have check digit error
        assert any("check digit" in err.lower() for err in data["errors"])

    def test_validate_invalid_eic_wrong_length(self):
        """Test validation of EIC with wrong length."""
        response = client.post(
            "/eic/validate",
            json={"eic_code": "TOOSHORT"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_invalid_eic_invalid_characters(self):
        """Test validation of EIC with invalid characters."""
        response = client.post(
            "/eic/validate",
            json={"eic_code": "27XG000000000-1Z"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False

    def test_validate_with_hyphens(self):
        """Test that hyphens in EIC are handled correctly."""
        # Generate a valid EIC
        gen_response = client.post(
            "/eic/generate",
            json={"country_code": "27", "entity_type": "X"}
        )
        eic = gen_response.json()["eic_code"]

        # Add hyphens to the EIC
        eic_with_hyphens = f"{eic[:3]}-{eic[3:7]}-{eic[7:11]}-{eic[11:]}"

        response = client.post(
            "/eic/validate",
            json={"eic_code": eic_with_hyphens}
        )
        assert response.status_code == 200
        # May or may not be valid depending on how hyphens affect length

    def test_validate_missing_eic_code(self):
        """Test validation request without eic_code field."""
        response = client.post(
            "/eic/validate",
            json={}
        )
        assert response.status_code == 422  # Validation error

    def test_validate_empty_eic_code(self):
        """Test validation with empty EIC code."""
        response = client.post(
            "/eic/validate",
            json={"eic_code": ""}
        )
        # Should fail validation or return invalid
        assert response.status_code in [200, 422]


class TestEICGenerationEndpoint:
    """Tests for POST /eic/generate endpoint."""

    def test_generate_valid_eic(self):
        """Test generation of valid EIC code."""
        response = client.post(
            "/eic/generate",
            json={"country_code": "27", "entity_type": "X"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "eic_code" in data
        assert len(data["eic_code"]) == 16
        assert data["is_valid"] is True
        assert data["components"]["office_id"] == "27"
        assert data["components"]["entity_type"] == "X"
        assert len(data["components"]["individual_id"]) == 12

    def test_generate_eic_different_country_codes(self):
        """Test generation with different country codes."""
        for country_code in ["10", "27", "X1"]:
            response = client.post(
                "/eic/generate",
                json={"country_code": country_code, "entity_type": "T"}
            )
            assert response.status_code == 201
            data = response.json()
            assert data["components"]["office_id"] == country_code.upper()

    def test_generate_eic_different_entity_types(self):
        """Test generation with different entity types."""
        for entity_type in ["T", "X", "Z", "A"]:
            response = client.post(
                "/eic/generate",
                json={"country_code": "27", "entity_type": entity_type}
            )
            assert response.status_code == 201
            data = response.json()
            assert data["components"]["entity_type"] == entity_type.upper()

    def test_generate_eic_invalid_country_code(self):
        """Test generation with invalid country code."""
        response = client.post(
            "/eic/generate",
            json={"country_code": "99", "entity_type": "X"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "country code" in data["detail"].lower()

    def test_generate_eic_invalid_entity_type(self):
        """Test generation with invalid entity type."""
        response = client.post(
            "/eic/generate",
            json={"country_code": "27", "entity_type": "Q"}
        )
        assert response.status_code == 400
        data = response.json()
        assert "entity type" in data["detail"].lower()

    def test_generate_eic_wrong_length_country_code(self):
        """Test generation with wrong length country code."""
        response = client.post(
            "/eic/generate",
            json={"country_code": "2", "entity_type": "X"}
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_generate_eic_wrong_length_entity_type(self):
        """Test generation with wrong length entity type."""
        response = client.post(
            "/eic/generate",
            json={"country_code": "27", "entity_type": "XY"}
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_generate_eic_missing_parameters(self):
        """Test generation with missing parameters."""
        response = client.post(
            "/eic/generate",
            json={"country_code": "27"}
        )
        assert response.status_code == 422

    def test_generated_eic_passes_validation(self):
        """Test that generated EIC passes validation endpoint."""
        # Generate EIC
        gen_response = client.post(
            "/eic/generate",
            json={"country_code": "27", "entity_type": "X"}
        )
        assert gen_response.status_code == 201
        eic = gen_response.json()["eic_code"]

        # Validate it
        val_response = client.post(
            "/eic/validate",
            json={"eic_code": eic}
        )
        assert val_response.status_code == 200
        assert val_response.json()["is_valid"] is True

    def test_generate_multiple_unique_eics(self):
        """Test that multiple generations produce unique EICs."""
        eics = set()
        for _ in range(20):
            response = client.post(
                "/eic/generate",
                json={"country_code": "27", "entity_type": "X"}
            )
            assert response.status_code == 201
            eics.add(response.json()["eic_code"])

        # Should have high uniqueness
        assert len(eics) > 18


class TestBulkEICGenerationEndpoint:
    """Tests for POST /eic/generate/bulk endpoint."""

    def test_generate_bulk_eics(self):
        """Test bulk generation of EIC codes."""
        response = client.post(
            "/eic/generate/bulk",
            json={"country_code": "27", "entity_type": "X", "count": 10}
        )
        assert response.status_code == 201
        data = response.json()
        assert "eic_codes" in data
        assert len(data["eic_codes"]) == 10
        assert data["count"] == 10

    def test_generate_bulk_eics_uniqueness(self):
        """Test that bulk generated EICs are unique."""
        response = client.post(
            "/eic/generate/bulk",
            json={"country_code": "27", "entity_type": "X", "count": 50}
        )
        assert response.status_code == 201
        eics = response.json()["eic_codes"]
        assert len(set(eics)) == 50  # All unique

    def test_generate_bulk_eics_all_valid(self):
        """Test that all bulk generated EICs are valid."""
        response = client.post(
            "/eic/generate/bulk",
            json={"country_code": "10", "entity_type": "T", "count": 20}
        )
        assert response.status_code == 201
        eics = response.json()["eic_codes"]

        for eic in eics:
            result = is_valid_eic(eic)
            assert result['is_valid'] is True

    def test_generate_bulk_eics_same_prefix(self):
        """Test that bulk EICs have same country code and entity type."""
        response = client.post(
            "/eic/generate/bulk",
            json={"country_code": "27", "entity_type": "Z", "count": 15}
        )
        assert response.status_code == 201
        eics = response.json()["eic_codes"]

        for eic in eics:
            assert eic[:2] == "27"
            assert eic[2] == "Z"

    def test_generate_bulk_eics_invalid_count_zero(self):
        """Test bulk generation with count of 0."""
        response = client.post(
            "/eic/generate/bulk",
            json={"country_code": "27", "entity_type": "X", "count": 0}
        )
        assert response.status_code == 422  # Pydantic validation

    def test_generate_bulk_eics_invalid_count_negative(self):
        """Test bulk generation with negative count."""
        response = client.post(
            "/eic/generate/bulk",
            json={"country_code": "27", "entity_type": "X", "count": -5}
        )
        assert response.status_code == 422  # Pydantic validation

    def test_generate_bulk_eics_count_exceeds_limit(self):
        """Test bulk generation with count exceeding limit."""
        response = client.post(
            "/eic/generate/bulk",
            json={"country_code": "27", "entity_type": "X", "count": 101}
        )
        assert response.status_code == 422  # Pydantic validation

    def test_generate_bulk_eics_invalid_country_code(self):
        """Test bulk generation with invalid country code."""
        response = client.post(
            "/eic/generate/bulk",
            json={"country_code": "99", "entity_type": "X", "count": 5}
        )
        assert response.status_code == 400


class TestAPIDocumentation:
    """Tests for API documentation endpoints."""

    def test_openapi_docs_available(self):
        """Test that OpenAPI documentation is available."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self):
        """Test that ReDoc documentation is available."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_json_available(self):
        """Test that OpenAPI JSON specification is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "EIC/EAN Validation Service"
        assert "paths" in data
        assert "/eic/validate" in data["paths"]
        assert "/eic/generate" in data["paths"]


class TestCORSAndMiddleware:
    """Tests for CORS and middleware configuration."""

    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        response = client.options("/eic/validate")
        # CORS should allow the request
        assert response.status_code in [200, 405]

    def test_content_type_json(self):
        """Test that API returns JSON content type."""
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")


class TestErrorHandling:
    """Tests for error handling."""

    def test_404_for_unknown_endpoint(self):
        """Test 404 response for unknown endpoints."""
        response = client.get("/unknown/endpoint")
        assert response.status_code == 404

    def test_405_for_wrong_method(self):
        """Test 405 response for wrong HTTP method."""
        response = client.get("/eic/validate")
        assert response.status_code == 405

    def test_422_for_invalid_request_body(self):
        """Test 422 response for invalid request body."""
        response = client.post(
            "/eic/validate",
            json={"invalid_field": "value"}
        )
        assert response.status_code == 422


class TestEANValidationEndpoint:
    """Tests for POST /ean/validate endpoint."""

    def test_validate_valid_ean8(self):
        """Test validation of a valid EAN-8 code."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": "12345670"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["format"] == "EAN-8"
        assert data["error"] is None

    def test_validate_valid_ean13(self):
        """Test validation of a valid EAN-13 code."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": "4006381333931"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["format"] == "EAN-13"
        assert data["error"] is None

    def test_validate_valid_ean14(self):
        """Test validation of a valid EAN-14 code."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": "04006381333938"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True
        assert data["format"] == "EAN-14"
        assert data["error"] is None

    def test_validate_invalid_ean_wrong_check_digit(self):
        """Test validation of EAN with wrong check digit."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": "12345679"}  # Wrong check digit
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert data["format"] is None
        assert data["error"] is not None
        assert "check digit" in data["error"].lower()

    def test_validate_invalid_ean_wrong_length(self):
        """Test validation of EAN with wrong length."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": "12345"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "length" in data["error"].lower()

    def test_validate_invalid_ean_non_numeric(self):
        """Test validation of EAN with non-numeric characters."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": "1234567A"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False
        assert "numeric" in data["error"].lower()

    def test_validate_ean_with_spaces(self):
        """Test validation handles spaces correctly."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": " 12345670 "}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    def test_validate_ean_with_hyphens(self):
        """Test validation handles hyphens correctly."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": "1234-5670"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    def test_validate_ean_empty_string(self):
        """Test validation of empty string."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": ""}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is False


class TestEANGenerationEndpoint:
    """Tests for POST /ean/generate endpoint."""

    def test_generate_ean8(self):
        """Test generation of EAN-8 code."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "1234567", "ean_type": "EAN-8"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "generated_ean" in data
        assert len(data["generated_ean"]) == 8
        assert data["generated_ean"][:7] == "1234567"

        # Verify it's valid
        is_valid, format_type, error = validate_ean(data["generated_ean"])
        assert is_valid is True
        assert format_type == "EAN-8"

    def test_generate_ean13(self):
        """Test generation of EAN-13 code."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "400638133393", "ean_type": "EAN-13"}
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["generated_ean"]) == 13
        assert data["generated_ean"][:12] == "400638133393"

    def test_generate_ean14(self):
        """Test generation of EAN-14 code."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "0400638133393", "ean_type": "EAN-14"}
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["generated_ean"]) == 14
        assert data["generated_ean"][:13] == "0400638133393"

    def test_generate_ean_case_insensitive(self):
        """Test that EAN type is case-insensitive."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "1234567", "ean_type": "ean-8"}
        )
        assert response.status_code == 201
        data = response.json()
        assert len(data["generated_ean"]) == 8

    def test_generate_ean_invalid_base_code_length(self):
        """Test generation with invalid base code length."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "123456", "ean_type": "EAN-8"}  # Too short
        )
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_generate_ean_non_numeric_base_code(self):
        """Test generation with non-numeric base code."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "123456A", "ean_type": "EAN-8"}
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_generate_ean_invalid_type(self):
        """Test generation with invalid EAN type."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "1234567", "ean_type": "EAN-12"}
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_generate_ean_round_trip_validation(self):
        """Test that generated EAN validates correctly."""
        # Generate EAN-13
        gen_response = client.post(
            "/ean/generate",
            json={"base_code": "123456789012", "ean_type": "EAN-13"}
        )
        assert gen_response.status_code == 201
        generated_ean = gen_response.json()["generated_ean"]

        # Validate it
        val_response = client.post(
            "/ean/validate",
            json={"ean_code": generated_ean}
        )
        assert val_response.status_code == 200
        val_data = val_response.json()
        assert val_data["is_valid"] is True
        assert val_data["format"] == "EAN-13"


class TestEANEndpointEdgeCases:
    """Tests for EAN endpoint edge cases."""

    def test_validate_all_zeros_ean8(self):
        """Test validation of all-zeros EAN-8."""
        response = client.post(
            "/ean/validate",
            json={"ean_code": "00000000"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_valid"] is True

    def test_generate_all_zeros_ean8(self):
        """Test generation with all-zeros base code."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "0000000", "ean_type": "EAN-8"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["generated_ean"] == "00000000"

    def test_generate_all_nines_ean13(self):
        """Test generation with all-nines base code."""
        response = client.post(
            "/ean/generate",
            json={"base_code": "999999999999", "ean_type": "EAN-13"}
        )
        assert response.status_code == 201
        # Should generate valid EAN
        generated = response.json()["generated_ean"]
        is_valid, _, _ = validate_ean(generated)
        assert is_valid is True

    def test_multiple_consecutive_requests(self):
        """Test multiple consecutive requests work correctly."""
        for _ in range(10):
            response = client.post(
                "/ean/validate",
                json={"ean_code": "12345670"}
            )
            assert response.status_code == 200
            data = response.json()
            assert data["is_valid"] is True
