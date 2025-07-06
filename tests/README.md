# Receipt OCR App - Testing Guide

## Overview
Comprehensive test suite for the Receipt OCR App with unit tests, integration tests, and mocked external services.

## Test Structure

```
tests/
├── test_models.py           # Data model validation tests
├── test_categories.py       # Category system tests  
├── test_file_handler.py     # File handling and validation tests
├── test_export_service.py   # Export functionality tests
├── test_ocr_service.py      # OCR service tests (mocked)
├── test_api.py             # FastAPI endpoint integration tests
└── README.md               # This file
```

## Running Tests

### Quick Start
```bash
# Install dependencies and run all tests
python run_tests.py

# Run specific test types
python run_tests.py unit
python run_tests.py integration
python run_tests.py fast

# Run with coverage report
python run_tests.py coverage
```

### Manual Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock httpx pytest-cov

# Run all tests
pytest -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run tests by marker
pytest -m "not slow" -v
```

## Test Categories

### Unit Tests
- **Models**: Data validation, serialization, field handling
- **Categories**: Classification logic, keyword matching, custom categories
- **File Handler**: File validation, size limits, format checking
- **Export Service**: CSV/Excel generation, summary statistics

### Integration Tests
- **API Endpoints**: Request/response handling, error cases
- **Service Integration**: Component interaction testing

### Mocked Tests
- **OCR Service**: Google Cloud Vision API calls (mocked)
- **External Dependencies**: Third-party service simulation

## Test Coverage

The test suite covers:
- ✅ Data model validation and serialization
- ✅ Receipt categorization logic
- ✅ File handling and validation
- ✅ Export functionality (CSV/Excel)
- ✅ API endpoint behavior
- ✅ OCR text parsing and extraction
- ✅ Error handling and edge cases
- ✅ Multi-language support (English/Chinese)
- ✅ Multi-currency handling (USD/NTD/HKD)

## Test Data

Tests use realistic sample data:
- Receipt text in multiple languages
- Various date formats
- Different currency formats
- Mixed valid/invalid data scenarios
- Edge cases and error conditions

## Mocking Strategy

External services are mocked to ensure:
- Fast test execution
- No external dependencies
- Predictable test results
- Cost control (no API charges)

Mocked services:
- Google Cloud Vision API
- File system operations (when needed)
- Network requests

## Writing New Tests

### Test File Template
```python
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from your_module import YourClass

class TestYourClass:
    def setup_method(self):
        self.instance = YourClass()
    
    def test_basic_functionality(self):
        result = self.instance.method()
        assert result == expected_value
```

### Test Naming Convention
- `test_[function]_[scenario]`
- `test_[function]_[expected_behavior]`
- `test_[function]_[error_condition]`

### Test Markers
```python
@pytest.mark.unit          # Unit test
@pytest.mark.integration   # Integration test  
@pytest.mark.slow         # Slow test (external services)
@pytest.mark.asyncio      # Async test
```

## CI/CD Integration

Tests are designed to run in CI/CD environments:
- No external service dependencies
- Consistent across platforms
- Fast execution (< 30 seconds)
- Clear pass/fail reporting

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure you're running from project root
   cd /path/to/receipt-filing-app
   python run_tests.py
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Path Issues**
   - Tests use relative imports with `sys.path.insert()`
   - Run tests from project root directory

4. **Async Test Issues**
   ```bash
   # Ensure pytest-asyncio is installed
   pip install pytest-asyncio
   ```

### Test Environment

Tests assume:
- Python 3.8+
- Project structure as documented
- No Google Cloud credentials needed (mocked)
- Standard pytest configuration

## Performance

Test suite performance:
- **Total runtime**: ~10-30 seconds
- **Unit tests**: ~5-10 seconds  
- **Integration tests**: ~5-15 seconds
- **Coverage generation**: +5-10 seconds

## Maintenance

Regular maintenance tasks:
- Update test data as features evolve
- Add tests for new functionality
- Review and update mocked responses
- Monitor test execution time
- Update dependencies in requirements.txt