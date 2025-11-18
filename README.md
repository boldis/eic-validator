# EIC/EAN Validation Service

A FastAPI-based REST API for validating and generating Energy Identification Codes (EIC) and European Article Numbers (EAN) according to ENTSO-E and GS1 standards.

## Features

- **EIC Validation**: Validate EIC codes with detailed error reporting according to ENTSO-E standards
- **EIC Generation**: Generate valid EIC codes with cryptographically secure random identifiers
- **EAN Validation**: Validate EAN-8, EAN-13, and EAN-14 codes according to GS1 standards
- **EAN Generation**: Generate valid EAN codes with proper check digit calculation
- **Bulk Generation**: Generate multiple unique EIC codes in a single request
- **ISO 7064 Mod 37,36**: Correct implementation of EIC check digit algorithm
- **GS1 Mod 10**: Correct implementation of EAN check digit algorithm
- **OpenAPI Documentation**: Interactive API documentation with Swagger UI
- **Comprehensive Testing**: 112 tests with 100% pass rate
- **Docker Support**: Easy deployment with Docker and Docker Compose

## API Endpoints

### Root & Health
- `GET /` - Service information
- `GET /health` - Health check endpoint

### EIC Operations
- `POST /eic/validate` - Validate an EIC code
- `POST /eic/generate` - Generate a single EIC code
- `POST /eic/generate/bulk` - Generate multiple EIC codes

### EAN Operations
- `POST /ean/validate` - Validate an EAN code (EAN-8, EAN-13, EAN-14)
- `POST /ean/generate` - Generate a valid EAN code with check digit

### Documentation
- `GET /docs` - Interactive Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI 3.0 specification

## Quick Start

### Using Python Virtual Environment

1. **Clone the repository**
```bash
git clone <repository-url>
cd eic-validator
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Using Docker

1. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

2. **Access the API**
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

3. **View logs**
```bash
docker-compose logs -f
```

4. **Stop the service**
```bash
docker-compose down
```

### Using Docker directly

1. **Build the image**
```bash
docker build -t eic-validation-service .
```

2. **Run the container**
```bash
docker run -d -p 8000:8000 --name eic-api eic-validation-service
```

## API Usage Examples

### Validate an EIC Code

**Request:**
```bash
curl -X POST "http://localhost:8000/eic/validate" \
  -H "Content-Type: application/json" \
  -d '{"eic_code": "27XGOEPS000001Z"}'
```

**Response:**
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

### Generate an EIC Code

**Request:**
```bash
curl -X POST "http://localhost:8000/eic/generate" \
  -H "Content-Type: application/json" \
  -d '{"country_code": "27", "entity_type": "X"}'
```

**Response:**
```json
{
  "eic_code": "27XMF6TRD4E5M23G",
  "is_valid": true,
  "components": {
    "office_id": "27",
    "entity_type": "X",
    "individual_id": "MF6TRD4E5M23",
    "check_digit": "G"
  }
}
```

### Generate Multiple EIC Codes

**Request:**
```bash
curl -X POST "http://localhost:8000/eic/generate/bulk" \
  -H "Content-Type: application/json" \
  -d '{"country_code": "27", "entity_type": "X", "count": 10}'
```

**Response:**
```json
{
  "eic_codes": [
    "27XAB12CD34EF567",
    "27XGH89IJ01KL234",
    ...
  ],
  "count": 10
}
```

### Validate an EAN Code

**Request:**
```bash
curl -X POST "http://localhost:8000/ean/validate" \
  -H "Content-Type: application/json" \
  -d '{"ean_code": "4006381333931"}'
```

**Response:**
```json
{
  "is_valid": true,
  "ean_code": "4006381333931",
  "format": "EAN-13",
  "components": {
    "data": "400638133393",
    "check_digit": "1"
  },
  "error_message": null
}
```

### Generate an EAN Code

**Request:**
```bash
curl -X POST "http://localhost:8000/ean/generate" \
  -H "Content-Type: application/json" \
  -d '{"base_code": "400638133393", "ean_type": "EAN-13"}'
```

**Response:**
```json
{
  "generated_ean": "4006381333931",
  "ean_type": "EAN-13",
  "components": {
    "data": "400638133393",
    "check_digit": "1"
  }
}
```

## EIC Code Format

EIC codes follow the ENTSO-E 16-character format: `XXYAAAAAAAAAAAAK`

- **XX** (2 chars): Office identifier / Country code
- **Y** (1 char): Entity type
- **A...** (12 chars): Individual identifier
- **K** (1 char): Check digit (ISO 7064 Mod 37,36)

### Valid Country Codes
Supported country codes include: `10`, `27`, `X1`, and many others as defined by ENTSO-E.

### Valid Entity Types
- `T` - Transmission System Operator control area
- `Y` - Transmission System Operator
- `X` - Electrical area
- `Z` - Metering point
- `A` - Generation unit
- And more (see source code for complete list)

## EAN Code Format

EAN (European Article Number) codes follow GS1 standards and come in three formats:

### EAN-8
- **Format**: 8 digits total
- **Structure**: 7 data digits + 1 check digit
- **Example**: `12345670`
- **Usage**: Small product packaging

### EAN-13
- **Format**: 13 digits total
- **Structure**: 12 data digits + 1 check digit
- **Example**: `4006381333931`
- **Usage**: Standard product barcodes, energy sector identification

### EAN-14
- **Format**: 14 digits total
- **Structure**: 13 data digits + 1 check digit
- **Example**: `14006381333938`
- **Usage**: Logistic units, packaging

### Check Digit Calculation
EAN codes use the **GS1 Mod 10** algorithm (positions counted from **right to left**):
1. Sum digits at odd positions from right (1st, 3rd, 5th...) and multiply by 3
2. Sum digits at even positions from right (2nd, 4th, 6th...)
3. Add both sums
4. Check digit = (10 - (sum mod 10)) mod 10

**Example for `400638133393`:**
```
Position from right: 12 11 10  9  8  7  6  5  4  3  2  1
Digit:                4  0  0  6  3  8  1  3  3  3  9  3
```
- Odd positions from right (1,3,5,7,9,11): 3+3+3+8+6+0 = 23 × 3 = **69**
- Even positions from right (2,4,6,8,10,12): 9+3+1+3+0+4 = **20**
- Total: 69 + 20 = 89
- Check digit: (10 - 9) mod 10 = **1** → Full EAN: `4006381333931`

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run specific test class
pytest tests/test_eic_validation.py::TestCheckDigitCalculation -v
```

### Test Coverage

- **Total Tests**: 112
- **API Integration Tests**: 35 (covering both EIC and EAN endpoints)
- **EIC Validation Tests**: 38
- **EIC Generation Tests**: 39
- **EAN Validation Tests**: (comprehensive EAN-8/13/14 validation)
- **EAN Generation Tests**: (EAN generation and check digit calculation)
- **Pass Rate**: 100%

### Project Structure

```
eic-validator/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── routes.py            # API endpoints (EIC and EAN)
│   ├── models.py            # Pydantic models
│   ├── eic_validation.py    # EIC validation logic
│   ├── eic_generation.py    # EIC generation logic
│   ├── ean_validation.py    # EAN validation logic
│   └── ean_generation.py    # EAN generation logic
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # API integration tests
│   ├── test_eic_validation.py  # EIC validation unit tests
│   ├── test_eic_generation.py  # EIC generation unit tests
│   ├── test_ean_validation.py  # EAN validation unit tests
│   └── test_ean_generation.py  # EAN generation unit tests
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── EIC_EAN_podklad.md      # Czech standards documentation
└── README.md              # This file
```

## Dependencies

### Core
- **FastAPI** (0.115.5): Modern, fast web framework with automatic OpenAPI documentation
- **Uvicorn** (0.32.1): Lightning-fast ASGI server
- **Pydantic** (2.10.3): Data validation using Python type annotations

### Testing
- **pytest** (8.3.4): Full-featured testing framework
- **pytest-cov** (6.0.0): Coverage reporting
- **pytest-asyncio** (0.24.0): Async test support
- **httpx** (0.28.1): HTTP client required by FastAPI TestClient

### Code Quality
- **black** (24.10.0): Opinionated code formatter
- **flake8** (7.1.1): Style guide enforcement
- **mypy** (1.13.0): Static type checker
- **isort** (5.13.2): Import statement organizer

## Environment Variables

The application can be configured using environment variables:

- `ENVIRONMENT`: Set to `production` or `development` (default: `development`)
- `HOST`: Host to bind to (default: `0.0.0.0`)
- `PORT`: Port to listen on (default: `8000`)

## Standards & References

### EIC Standards
- **ENTSO-E**: European Network of Transmission System Operators for Electricity
- **ISO 7064 Mod 37,36**: Check digit algorithm specification for EIC codes
- [ENTSO-E EIC Codes](https://www.entsoe.eu/data/energy-identification-codes-eic/)
- [ENTSO-E EDI Library](https://www.entsoe.eu/publications/electronic-data-interchange-edi-library/)

### EAN Standards
- **GS1**: Global standards organization for supply chain identification
- **ISO/IEC 15420**: International standard for EAN/UPC barcodes
- **GS1 Mod 10**: Check digit algorithm for EAN codes
- [GS1 Standards](https://www.gs1.org/standards/barcode-standards)
- [GS1 Czech Republic](https://www.gs1cz.org/)

### API Documentation
- **OpenAPI 3.1.0**: API specification standard (auto-generated by FastAPI)

## License

This project is created for demonstration purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## Support

For issues or questions, please open an issue on the repository.
