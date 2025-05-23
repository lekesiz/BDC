# BDC Backend Test Suite

This directory contains the comprehensive test suite for the BDC (Beneficiary Development Center) backend application.

## Test Structure

```
tests/
├── conftest.py          # Pytest fixtures and configuration
├── test_auth.py         # Authentication endpoint tests
├── test_beneficiaries.py # Beneficiary management tests
├── test_programs.py     # Program management tests
├── test_assessments.py  # Assessment/test engine tests
└── README.md           # This file
```

## Running Tests

### Prerequisites

1. Activate your virtual environment
2. Install test dependencies:
   ```bash
   pip install -r requirements-test.txt
   ```

### Running All Tests

```bash
pytest
```

Or use the test runner script:
```bash
./run_tests.sh
```

### Running Tests with Coverage

```bash
pytest --cov=. --cov-report=html
```

View coverage report in `htmlcov/index.html`

### Running Specific Tests

```bash
# Run a specific test file
pytest tests/test_auth.py

# Run a specific test class
pytest tests/test_auth.py::TestAuth

# Run a specific test method
pytest tests/test_auth.py::TestAuth::test_login_success

# Run tests by marker
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## Test Fixtures

Common fixtures defined in `conftest.py`:

- `test_app`: Flask application instance
- `client`: Test client for making HTTP requests
- `db_session`: Database session for tests
- `test_tenant`: Test tenant/organization
- `test_user`: Test user with tenant_admin role
- `test_trainer`: Test user with trainer role
- `test_student`: Test user with student role
- `test_beneficiary`: Test beneficiary
- `test_program`: Test program
- `test_test`: Test assessment
- `auth_headers`: Authentication headers for requests

## Test Categories

### Authentication Tests (`test_auth.py`)
- User registration
- Login/logout
- Token refresh
- Password reset
- Email verification
- Access control

### Beneficiary Tests (`test_beneficiaries.py`)
- CRUD operations
- Trainer assignment
- Progress tracking
- Export/import functionality
- Document management
- Role-based access control

### Program Tests (`test_programs.py`)
- Program creation and management
- Beneficiary enrollment
- Schedule management
- Progress tracking
- Statistics and analytics
- Cloning programs

### Assessment Tests (`test_assessments.py`)
- Test creation and management
- Question management
- Test sessions
- Answer submission
- Results and analytics
- Bulk operations

## Writing New Tests

1. Create test files with `test_` prefix
2. Use descriptive test names
3. Follow the AAA pattern (Arrange, Act, Assert)
4. Use fixtures for common setup
5. Mark tests appropriately (unit, integration, slow)

Example:

```python
import pytest

class TestNewFeature:
    @pytest.mark.unit
    def test_feature_behavior(self, client, auth_headers):
        """Test that feature behaves correctly."""
        # Arrange
        data = {'key': 'value'}
        
        # Act
        response = client.post('/api/endpoint',
                              json=data,
                              headers=auth_headers)
        
        # Assert
        assert response.status_code == 200
        result = response.get_json()
        assert result['key'] == 'value'
```

## Best Practices

1. **Isolation**: Each test should be independent
2. **Clarity**: Use descriptive names and docstrings
3. **Speed**: Mark slow tests appropriately
4. **Coverage**: Aim for high test coverage (>80%)
5. **Fixtures**: Use fixtures to reduce code duplication
6. **Mocking**: Mock external dependencies
7. **Assertions**: Make assertions specific and meaningful

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Commits to main branch
- Nightly builds

## Troubleshooting

### Common Issues

1. **Database errors**: Ensure test database is clean
2. **Import errors**: Check PYTHONPATH
3. **Fixture errors**: Verify fixture dependencies
4. **Flaky tests**: Look for timing issues or external dependencies

### Debug Mode

Run tests with verbose output:
```bash
pytest -vv -s
```

### Test Database

Tests use an in-memory SQLite database by default. Each test gets a fresh database state through transactions that are rolled back after each test.

## Contributing

1. Write tests for new features
2. Ensure all tests pass before submitting PR
3. Maintain or improve code coverage
4. Follow existing test patterns
5. Update documentation as needed