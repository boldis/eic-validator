"""API routes for EIC validation and generation."""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any

from .models import (
    EICValidationRequest,
    EICValidationResult,
    EICComponentsResponse,
    EANValidationRequest,
    EANValidationResponse,
    EANGenerationRequest,
    EANGenerationResponse,
)
from .eic_validation import is_valid_eic
from .eic_generation import (
    generate_eic,
    generate_multiple_eics,
    InvalidCountryCodeError,
    InvalidEntityTypeError,
)
from .ean_validation import validate_ean
from .ean_generation import (
    generate_ean,
    InvalidEANTypeError,
    InvalidBaseCodeError,
)
from pydantic import BaseModel, Field


# EIC Generation Models
class EICGenerationRequest(BaseModel):
    """Request model for EIC generation."""
    country_code: str = Field(
        ...,
        description="2-character country code (e.g., '27' for Czech Republic)",
        min_length=2,
        max_length=2,
        examples=["27", "10", "X1"]
    )
    entity_type: str = Field(
        ...,
        description="Single character entity type (e.g., 'T', 'X', 'Z')",
        min_length=1,
        max_length=1,
        examples=["X", "T", "Z"]
    )


class EICGenerationResult(BaseModel):
    """Response model for EIC generation."""
    eic_code: str = Field(..., description="Generated EIC code")
    is_valid: bool = Field(..., description="Confirmation that generated EIC is valid")
    components: EICComponentsResponse = Field(..., description="Parsed components of generated EIC")


class BulkEICGenerationRequest(BaseModel):
    """Request model for bulk EIC generation."""
    country_code: str = Field(..., description="2-character country code", min_length=2, max_length=2)
    entity_type: str = Field(..., description="Single character entity type", min_length=1, max_length=1)
    count: int = Field(..., description="Number of EICs to generate", ge=1, le=100)


class BulkEICGenerationResult(BaseModel):
    """Response model for bulk EIC generation."""
    eic_codes: list[str] = Field(..., description="List of generated EIC codes")
    count: int = Field(..., description="Number of EICs generated")


# Create router
router = APIRouter(prefix="/eic", tags=["EIC"])


@router.post("/validate", response_model=EICValidationResult, status_code=status.HTTP_200_OK)
async def validate_eic_endpoint(request: EICValidationRequest) -> EICValidationResult:
    """Validate an EIC code.

    Validates the format, structure, and check digit of an Energy Identification Code (EIC)
    according to ENTSO-E standards.

    Args:
        request: EIC validation request containing the code to validate

    Returns:
        EICValidationResult with validation status, errors, and parsed components

    Example:
        ```json
        {
            "eic_code": "27XGOEPS000001Z"
        }
        ```

    Response:
        ```json
        {
            "is_valid": true,
            "eic_code": "27XGOEPS000001Z",
            "errors": [],
            "components": {
                "office_id": "27",
                "entity_type": "X",
                "individual_id": "GOEPS000001",
                "check_digit": "Z"
            }
        }
        ```
    """
    try:
        # Validate the EIC
        result = is_valid_eic(request.eic_code)

        # Convert components to response model if available
        components_response = None
        if result['components'] is not None:
            components_response = EICComponentsResponse(
                office_id=result['components'].office_id,
                entity_type=result['components'].entity_type,
                individual_id=result['components'].individual_id,
                check_digit=result['components'].check_digit,
            )

        return EICValidationResult(
            is_valid=result['is_valid'],
            eic_code=result['eic_code'],
            errors=result['errors'],
            components=components_response,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during validation: {str(e)}"
        )


@router.post("/generate", response_model=EICGenerationResult, status_code=status.HTTP_201_CREATED)
async def generate_eic_endpoint(request: EICGenerationRequest) -> EICGenerationResult:
    """Generate a valid EIC code.

    Generates a new Energy Identification Code (EIC) based on the provided country code
    and entity type. The 12-character identifier is randomly generated, and a valid
    check digit is calculated according to ISO 7064 Mod 37,36.

    Args:
        request: EIC generation request with country code and entity type

    Returns:
        EICGenerationResult with the generated EIC and its components

    Raises:
        HTTPException 400: If country code or entity type is invalid

    Example:
        ```json
        {
            "country_code": "27",
            "entity_type": "X"
        }
        ```

    Response:
        ```json
        {
            "eic_code": "27XABC123DEF456G",
            "is_valid": true,
            "components": {
                "office_id": "27",
                "entity_type": "X",
                "individual_id": "ABC123DEF456",
                "check_digit": "G"
            }
        }
        ```
    """
    try:
        # Generate EIC
        eic_code = generate_eic(request.country_code, request.entity_type)

        # Validate the generated EIC to get components
        validation_result = is_valid_eic(eic_code)

        if not validation_result['is_valid']:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Generated EIC failed validation - this should not happen"
            )

        # Convert components to response model
        components_response = EICComponentsResponse(
            office_id=validation_result['components'].office_id,
            entity_type=validation_result['components'].entity_type,
            individual_id=validation_result['components'].individual_id,
            check_digit=validation_result['components'].check_digit,
        )

        return EICGenerationResult(
            eic_code=eic_code,
            is_valid=True,
            components=components_response,
        )

    except InvalidCountryCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidEntityTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during generation: {str(e)}"
        )


@router.post("/generate/bulk", response_model=BulkEICGenerationResult, status_code=status.HTTP_201_CREATED)
async def generate_bulk_eic_endpoint(request: BulkEICGenerationRequest) -> BulkEICGenerationResult:
    """Generate multiple unique EIC codes.

    Generates multiple unique Energy Identification Codes (EICs) with the same
    country code and entity type. Useful for batch operations.

    Args:
        request: Bulk generation request with country code, entity type, and count

    Returns:
        BulkEICGenerationResult with list of generated EICs

    Raises:
        HTTPException 400: If parameters are invalid or count exceeds limit

    Example:
        ```json
        {
            "country_code": "27",
            "entity_type": "X",
            "count": 10
        }
        ```
    """
    try:
        # Generate multiple EICs
        eic_codes = generate_multiple_eics(
            request.country_code,
            request.entity_type,
            request.count
        )

        return BulkEICGenerationResult(
            eic_codes=eic_codes,
            count=len(eic_codes)
        )

    except InvalidCountryCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidEntityTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during bulk generation: {str(e)}"
        )


# EAN Router
ean_router = APIRouter(prefix="/ean", tags=["EAN"])


@ean_router.post("/validate", response_model=EANValidationResponse, status_code=status.HTTP_200_OK)
async def validate_ean_endpoint(request: EANValidationRequest) -> EANValidationResponse:
    """Validate an EAN code.

    Validates the format, length, and check digit of a European Article Number (EAN)
    according to GS1 standards. Supports EAN-8, EAN-13, and EAN-14 formats.

    Args:
        request: EAN validation request containing the code to validate

    Returns:
        EANValidationResponse with validation status, format, and error message if invalid

    Example:
        ```json
        {
            "ean_code": "4006381333931"
        }
        ```

    Response:
        ```json
        {
            "is_valid": true,
            "format": "EAN-13",
            "error": null
        }
        ```
    """
    try:
        # Validate the EAN
        is_valid, ean_format, error_message = validate_ean(request.ean_code)

        return EANValidationResponse(
            is_valid=is_valid,
            format=ean_format,
            error=error_message
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during validation: {str(e)}"
        )


@ean_router.post("/generate", response_model=EANGenerationResponse, status_code=status.HTTP_201_CREATED)
async def generate_ean_endpoint(request: EANGenerationRequest) -> EANGenerationResponse:
    """Generate a valid EAN code.

    Generates a European Article Number (EAN) from the provided base code and EAN type.
    Calculates the check digit using the Mod 10 algorithm with alternating weights.

    Args:
        request: EAN generation request with base code and EAN type

    Returns:
        EANGenerationResponse with the generated EAN code

    Raises:
        HTTPException 400: If base code or EAN type is invalid
        HTTPException 422: If request validation fails

    Example:
        ```json
        {
            "base_code": "400638133393",
            "ean_type": "EAN-13"
        }
        ```

    Response:
        ```json
        {
            "generated_ean": "4006381333931"
        }
        ```
    """
    try:
        # Generate EAN
        generated_ean = generate_ean(request.base_code, request.ean_type)

        return EANGenerationResponse(generated_ean=generated_ean)

    except InvalidBaseCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidEANTypeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during generation: {str(e)}"
        )
