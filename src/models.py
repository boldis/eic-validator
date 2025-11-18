"""Pydantic models for EIC and EAN validation API."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class EICValidationRequest(BaseModel):
    """Request model for EIC validation."""

    eic_code: str = Field(
        ...,
        description="EIC code to validate (16 characters, alphanumeric)",
        min_length=1,
        max_length=20,  # Allow some extra for hyphens
        examples=["27XG-OEPS-000001-Z", "27XGOEPS000001Z"],
    )

    @field_validator("eic_code")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Remove leading/trailing whitespace."""
        return v.strip()


class EICComponentsResponse(BaseModel):
    """EIC components breakdown."""

    office_id: str = Field(..., description="Office identifier (XX)")
    entity_type: str = Field(..., description="Entity type (Y)")
    individual_id: str = Field(..., description="Individual identifier (12 chars)")
    check_digit: str = Field(..., description="Check digit (K)")


class EICValidationResult(BaseModel):
    """Response model for EIC validation."""

    is_valid: bool = Field(..., description="Whether the EIC code is valid")
    eic_code: str = Field(..., description="Normalized EIC code (uppercase, no hyphens)")
    errors: List[str] = Field(
        default_factory=list, description="List of validation errors (empty if valid)"
    )
    components: Optional[EICComponentsResponse] = Field(
        None, description="Parsed EIC components (only if valid)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "eic_code": "27XGOEPS000001Z",
                "errors": [],
                "components": {
                    "office_id": "27",
                    "entity_type": "X",
                    "individual_id": "GOEPS000001",
                    "check_digit": "Z",
                },
            }
        }


class EANValidationRequest(BaseModel):
    """Request model for EAN validation."""

    ean_code: str = Field(
        ...,
        description="EAN code to validate (8, 13, or 14 digits)",
        min_length=1,
        max_length=20,  # Allow some extra for hyphens/spaces
        examples=["12345670", "4006381333931", "04006381333931"],
    )

    @field_validator("ean_code")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        """Remove leading/trailing whitespace."""
        return v.strip()


class EANValidationResponse(BaseModel):
    """Response model for EAN validation."""

    is_valid: bool = Field(..., description="Whether the EAN code is valid")
    format: Optional[str] = Field(
        None, description="EAN format (EAN-8, EAN-13, or EAN-14) if valid"
    )
    error: Optional[str] = Field(None, description="Error message if invalid")

    class Config:
        json_schema_extra = {
            "examples": [
                {"is_valid": True, "format": "EAN-13", "error": None},
                {"is_valid": False, "format": None, "error": "Invalid check digit"},
            ]
        }


class EANGenerationRequest(BaseModel):
    """Request model for EAN generation."""

    base_code: str = Field(
        ...,
        description="Base code (7, 12, or 13 digits) for EAN generation",
        min_length=7,
        max_length=13,
        examples=["1234567", "400638133393", "0400638133393"],
    )
    ean_type: str = Field(
        ..., description="Target EAN type", examples=["EAN-8", "EAN-13", "EAN-14"]
    )

    @field_validator("base_code")
    @classmethod
    def strip_whitespace_and_validate_numeric(cls, v: str) -> str:
        """Remove whitespace and validate numeric."""
        v = v.strip().replace(" ", "").replace("-", "")
        if not v.isdigit():
            raise ValueError("Base code must contain only digits")
        return v

    @field_validator("ean_type")
    @classmethod
    def validate_ean_type(cls, v: str) -> str:
        """Validate EAN type."""
        v = v.upper()
        if v not in {"EAN-8", "EAN-13", "EAN-14"}:
            raise ValueError("EAN type must be EAN-8, EAN-13, or EAN-14")
        return v


class EANGenerationResponse(BaseModel):
    """Response model for EAN generation."""

    generated_ean: str = Field(..., description="Generated EAN code with check digit")

    class Config:
        json_schema_extra = {"example": {"generated_ean": "12345670"}}


class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
