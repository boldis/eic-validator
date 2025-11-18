# EIC/EAN Validation Service

A FastAPI-based REST API for validating and generating Energy Identification Codes (EIC) according to ENTSO-E standards.

## Features

- **EIC Validation**: Validate EIC codes with detailed error reporting
- **EIC Generation**: Generate valid EIC codes with random identifiers
- **Bulk Generation**: Generate multiple unique EIC codes in a single request
- **ISO 7064 Mod 37,36**: Correct implementation of check digit algorithm
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

### Documentation
- `GET /docs` - Interactive Swagger UI documentation
- `GET /redoc` - ReDoc documentation
- `GET /openapi.json` - OpenAPI 3.0 specification

## Quick Start

### Using Python Virtual Environment

1. **Clone the repository**
```bash
git clone <repository-url>
cd test-task
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
- **API Integration Tests**: 35
- **EIC Validation Tests**: 38
- **EIC Generation Tests**: 39
- **Pass Rate**: 100%

### Project Structure

```
test-task/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── routes.py            # API endpoints
│   ├── models.py            # Pydantic models
│   ├── eic_validation.py    # EIC validation logic
│   └── eic_generation.py    # EIC generation logic
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # API integration tests
│   ├── test_eic_validation.py  # Validation unit tests
│   └── test_eic_generation.py  # Generation unit tests
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── README.md              # This file
```

## Dependencies

### Core
- **FastAPI** (0.115.5): Modern web framework
- **Uvicorn** (0.32.1): ASGI server
- **Pydantic** (2.10.3): Data validation

### Testing
- **pytest** (8.3.4): Testing framework
- **pytest-cov** (6.0.0): Coverage reporting
- **pytest-asyncio** (0.24.0): Async test support

### Development
- **black** (24.10.0): Code formatting
- **flake8** (7.1.1): Linting
- **mypy** (1.13.0): Type checking

## Environment Variables

The application can be configured using environment variables:

- `ENVIRONMENT`: Set to `production` or `development` (default: `development`)
- `HOST`: Host to bind to (default: `0.0.0.0`)
- `PORT`: Port to listen on (default: `8000`)

## Standards & References

- **ENTSO-E**: European Network of Transmission System Operators for Electricity
- **ISO 7064 Mod 37,36**: Check digit algorithm specification
- **OpenAPI 3.0**: API specification standard

### Official Documentation
- [ENTSO-E EIC Codes](https://www.entsoe.eu/data/energy-identification-codes-eic/)
- [ISO 7064](https://en.wikipedia.org/wiki/ISO_7064)

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
