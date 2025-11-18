# Contributing to EIC/EAN Validation Service

Thank you for your interest in contributing to the EIC/EAN Validation Service! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/eic-validator.git
   cd eic-validator
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/eic-validator.git
   ```

## Development Setup

### Prerequisites

- Python 3.11 or higher (3.13 recommended)
- pip (Python package installer)
- git

### Local Environment Setup

1. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Verify installation**:
   ```bash
   pytest --version
   uvicorn --version
   ```

### Running the Application

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or using the provided script
./run.sh
```

Access the API at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Development Workflow

### Creating a New Feature

1. **Update your local main branch**:
   ```bash
   git checkout main
   git pull upstream main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** and commit regularly:
   ```bash
   git add .
   git commit -m "feat: add new validation feature"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub

### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, missing semicolons, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**
```
feat: add EAN-14 validation support
fix: correct check digit calculation for EIC codes
docs: update API usage examples in README
test: add tests for bulk EIC generation
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length**: 100 characters (black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes preferred for strings
- **Import organization**: Use `isort` with black profile

### Code Quality Tools

Before submitting, ensure your code passes all quality checks:

1. **Format code with black**:
   ```bash
   black src/ tests/
   ```

2. **Sort imports with isort**:
   ```bash
   isort src/ tests/ --profile black
   ```

3. **Lint with flake8**:
   ```bash
   flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503
   ```

4. **Type check with mypy**:
   ```bash
   mypy src/ --ignore-missing-imports
   ```

5. **Run all checks at once**:
   ```bash
   black src/ tests/ && \
   isort src/ tests/ --profile black && \
   flake8 src/ tests/ --max-line-length=120 --extend-ignore=E203,W503 && \
   mypy src/ --ignore-missing-imports
   ```

### Code Organization

- **Keep functions focused**: Each function should do one thing well
- **Use type hints**: Always add type annotations for function parameters and return values
- **Write docstrings**: Use Google-style docstrings for all public functions and classes
- **Avoid magic numbers**: Use named constants instead

**Example:**
```python
def validate_eic_code(eic_code: str) -> ValidationResult:
    """Validate an EIC code according to ENTSO-E standards.

    Args:
        eic_code: The EIC code string to validate (16 characters)

    Returns:
        ValidationResult object containing validity status and details

    Raises:
        ValueError: If the input is not a string
    """
    # Implementation
    pass
```

## Testing Guidelines

### Writing Tests

- **Test file naming**: `test_<module_name>.py`
- **Test class naming**: `TestClassName`
- **Test function naming**: `test_<what_is_being_tested>`
- **Coverage target**: Aim for >90% code coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_eic_validation.py -v

# Run specific test class
pytest tests/test_eic_validation.py::TestCheckDigitCalculation -v

# Run specific test function
pytest tests/test_eic_validation.py::TestCheckDigitCalculation::test_valid_check_digit -v
```

### Test Structure

```python
import pytest
from src.eic_validation import validate_eic_code

class TestEICValidation:
    """Test suite for EIC code validation."""

    def test_valid_eic_code(self):
        """Test validation of a valid EIC code."""
        result = validate_eic_code("27XGOEPS000001Z")
        assert result.is_valid is True

    def test_invalid_length(self):
        """Test validation fails for incorrect length."""
        result = validate_eic_code("27XGOEPS")
        assert result.is_valid is False
        assert "length" in result.error_message.lower()
```

### API Testing

For API endpoint tests, use the FastAPI TestClient:

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_validate_eic_endpoint():
    """Test the EIC validation endpoint."""
    response = client.post(
        "/eic/validate",
        json={"eic_code": "27XGOEPS000001Z"}
    )
    assert response.status_code == 200
    assert response.json()["is_valid"] is True
```

## Submitting Changes

### Before Submitting

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black src/ tests/`
- [ ] Imports are sorted: `isort src/ tests/ --profile black`
- [ ] Linting passes: `flake8 src/ tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] Coverage is maintained or improved
- [ ] Documentation is updated (if needed)
- [ ] CHANGELOG is updated (for significant changes)

### Pull Request Process

1. **Update your branch** with the latest main:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Push your changes**:
   ```bash
   git push origin your-feature-branch
   ```

3. **Create a Pull Request** with:
   - Clear title and description
   - Reference to related issues (if any)
   - Screenshots or examples (if applicable)
   - List of changes made

4. **Respond to feedback**:
   - Address reviewer comments
   - Make requested changes
   - Push updates to the same branch

5. **Wait for approval** and merge

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] All existing tests pass
- [ ] New tests added (if applicable)
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Detailed steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**:
   - OS and version
   - Python version
   - Package versions (from `pip list`)
6. **Logs/Screenshots**: Any relevant error messages or screenshots

### Feature Requests

When requesting features, please include:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: Your idea for how to solve it
3. **Alternatives**: Any alternative solutions you've considered
4. **Additional context**: Any other relevant information

## Questions?

If you have questions about contributing, feel free to:

- Open an issue with the `question` label
- Check existing documentation
- Review closed issues for similar questions

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to the EIC/EAN Validation Service!
