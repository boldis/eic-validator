"""Main FastAPI application entry point for EIC/EAN validation service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError

from .routes import router as eic_router, ean_router

app = FastAPI(
    title="EIC/EAN Validation Service",
    description=(
        "API for validating Energy Identification Codes (EIC) and "
        "European Article Numbers (EAN) according to ENTSO-E standards"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed error messages."""
    # Convert errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        error_dict = dict(error)
        # Convert ValueError in ctx to string
        if "ctx" in error_dict and "error" in error_dict["ctx"]:
            ctx_error = error_dict["ctx"]["error"]
            if isinstance(ctx_error, ValueError):
                error_dict["ctx"]["error"] = str(ctx_error)
        errors.append(error_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": errors,
        },
    )


# Include routers
app.include_router(eic_router)
app.include_router(ean_router)


@app.get("/")
async def root():
    """Root endpoint returning service information."""
    return {
        "service": "EIC/EAN Validation Service",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "eic_validate": "/eic/validate",
            "eic_generate": "/eic/generate",
            "eic_generate_bulk": "/eic/generate/bulk",
            "ean_validate": "/ean/validate",
            "ean_generate": "/ean/generate",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
