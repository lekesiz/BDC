# BDC Testing Guide

This directory contains all tests for the BDC (Beneficiary Development Center) application.

## Test Structure

### Unit Tests
- `test_auth.py` - Authentication unit tests
- `test_beneficiaries.py` - Beneficiary management tests  
- `test_programs.py` - Program management tests
- `test_assessments.py` - Assessment and evaluation tests

### Integration Tests
- `test_integration.py` - Tests for component integration
- `test_e2e_workflows.py` - End-to-end workflow tests

### API Tests
- `test_api.py` - API endpoint testing
- `test_analytics_api.py` - Analytics API tests

### Performance Tests
- `test_performance.py` - Performance and load testing

### Security Tests
- `test_security.py` - Security vulnerability testing
- `test_security_auth.py` - Authentication security tests
- `test_security_encryption.py` - Encryption tests
- `test_security_input_validation.py` - Input validation tests

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test category
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Performance tests only
pytest -m performance

# Security tests only
pytest -m security
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run in verbose mode
```bash
pytest -v
```

## Test Configuration

Tests use the following fixtures from `conftest.py`:
- `app` - Flask application instance
- `client` - Test client
- `test_db` - Test database
- `test_user` - Test user fixtures
- `test_admin` - Admin user fixture
- `test_trainer` - Trainer user fixture
- `test_beneficiary` - Beneficiary user fixture

## Writing New Tests

1. Create test file with `test_` prefix
2. Use appropriate pytest markers:
   - `@pytest.mark.unit` for unit tests
   - `@pytest.mark.integration` for integration tests
   - `@pytest.mark.api` for API tests
   - `@pytest.mark.performance` for performance tests
   - `@pytest.mark.security` for security tests

3. Follow naming conventions:
   - Test classes: `Test<Feature>`
   - Test methods: `test_<specific_behavior>`

Example:
```python
@pytest.mark.unit
class TestUserAuthentication:
    def test_user_can_login_with_valid_credentials(self, client, test_user):
        # Test implementation
        pass
```

## Coverage Requirements

- Minimum overall coverage: 80%
- Critical paths coverage: 95%
- Security features coverage: 100%

## Performance Benchmarks

- API response time: < 200ms average
- Database queries: < 50ms average
- Concurrent users: Support 100+ simultaneous users
- Memory usage: < 500MB under normal load

## Security Testing

Security tests verify:
- Authentication mechanisms
- Authorization and access control
- Input validation and sanitization
- Protection against common vulnerabilities (XSS, SQL injection, etc.)
- Password security requirements
- Data encryption