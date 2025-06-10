# BDC Test Suite - Consolidated Edition

## Overview
This directory contains the consolidated and organized test suite for the BDC (Beneficiary Data Center) project. The tests have been restructured for better organization, maintainability, and performance.

## Test Structure

```
tests/
├── unit/                     # Unit tests for individual components
│   ├── api/                  # API endpoint unit tests
│   │   └── test_auth.py      # Authentication API tests
│   ├── models/               # Model unit tests
│   ├── services/             # Service unit tests
│   │   └── test_gamification.py
│   └── utils/                # Utility unit tests
├── integration/              # Integration tests
│   ├── api_integration.py    # API integration tests
│   └── base_integration_test.py
├── e2e/                      # End-to-end workflow tests
│   └── workflow_tests.py     # Complete user workflows
├── performance/              # Performance and load tests
│   └── load_tests.py         # Load testing and benchmarks
├── security/                 # Security-focused tests
│   └── security_tests.py     # Security validation tests
├── consolidated/             # Legacy consolidated tests (kept for reference)
├── archive/                  # Archived old test files
├── conftest.py              # Shared test fixtures
├── factories.py             # Test data factories
├── pytest.ini              # Pytest configuration
├── run_tests.py             # Main test runner
└── README.md                # This file
```

## Test Categories

### 1. Unit Tests (`tests/unit/`)
- **Purpose**: Test individual components in isolation
- **Scope**: Models, services, utilities, API endpoints
- **Speed**: Fast (< 1 second per test)
- **Dependencies**: Minimal, mocked external dependencies

#### API Tests (`tests/unit/api/`)
- Authentication and authorization
- Input validation
- Response formatting
- Error handling

#### Service Tests (`tests/unit/services/`)
- Business logic validation
- Service layer functionality
- Gamification system
- Email and notification services

#### Model Tests (`tests/unit/models/`)
- Database model validation
- Relationship integrity
- Model methods and properties

### 2. Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions
- **Scope**: API endpoints with database, service integrations
- **Speed**: Medium (1-5 seconds per test)
- **Dependencies**: Test database, real components

#### Features Tested:
- Complete API workflows
- Database transactions
- Service layer integration
- Authentication flows
- CRUD operations
- Pagination and filtering

### 3. End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Scope**: Full application features from user perspective
- **Speed**: Slow (5-30 seconds per test)
- **Dependencies**: Full application stack

#### Workflows Tested:
- User registration and login
- Beneficiary management lifecycle
- Document upload and management
- Assessment workflows
- Program enrollment
- Data integrity validation

### 4. Performance Tests (`tests/performance/`)
- **Purpose**: Validate system performance characteristics
- **Scope**: Response times, throughput, resource usage
- **Speed**: Variable (depends on test)
- **Dependencies**: Performance monitoring tools

#### Performance Metrics:
- API response times
- Database query performance
- Concurrent load handling
- Memory usage patterns
- Large data set handling

### 5. Security Tests (`tests/security/`)
- **Purpose**: Validate security measures and protections
- **Scope**: Authentication, authorization, input validation
- **Speed**: Fast to medium
- **Dependencies**: Security frameworks

#### Security Areas:
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Authentication security
- Authorization controls
- Rate limiting
- Secure subprocess execution

## Running Tests

### Prerequisites
```bash
# Install test dependencies
python tests/run_tests.py --install-deps

# Or manually:
pip install pytest pytest-cov pytest-xdist pytest-mock pytest-flask
```

### Basic Usage
```bash
# Run all tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py unit
python tests/run_tests.py integration
python tests/run_tests.py e2e
python tests/run_tests.py performance
python tests/run_tests.py security

# Run tests by functionality
python tests/run_tests.py auth      # Authentication tests
python tests/run_tests.py api       # API tests
python tests/run_tests.py fast      # Fast tests only
python tests/run_tests.py slow      # Slow tests only
```

### Advanced Options
```bash
# Verbose output
python tests/run_tests.py unit -v

# With coverage analysis
python tests/run_tests.py unit -c

# Parallel execution
python tests/run_tests.py unit -p

# Combined options
python tests/run_tests.py integration -v -c -p
```

### Direct Pytest Usage
```bash
# Run specific test file
pytest tests/unit/api/test_auth.py -v

# Run tests with markers
pytest -m "auth and not slow"
pytest -m "unit or integration"

# Run with coverage
pytest --cov=app --cov-report=html tests/unit/

# Run failed tests only
pytest --lf
```

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.auth` - Authentication-related tests
- `@pytest.mark.api` - API tests
- `@pytest.mark.database` - Database tests

## Test Data and Fixtures

### Shared Fixtures (`conftest.py`)
- `app` - Flask application instance
- `client` - Test client for API requests
- `db_session` - Database session for testing
- `admin_user` - Admin user for authentication
- `auth_headers` - Authentication headers
- `valid_jwt_token` - Valid JWT token for testing

### Test Data Factories (`factories.py`)
- User factory
- Beneficiary factory
- Document factory
- Test data generators

## Best Practices

### Writing Tests
1. **Use descriptive test names**: `test_user_login_with_valid_credentials`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **One assertion per test** (when possible)
4. **Use appropriate markers**: Mark tests with their category
5. **Mock external dependencies**: Use `pytest-mock` for external services

### Test Organization
1. **Group related tests** in classes
2. **Use setUp/tearDown** for common test data
3. **Keep tests independent**: Each test should work in isolation
4. **Use meaningful test data**: Make test data relevant to what's being tested

### Performance Considerations
1. **Use fixtures wisely**: Share expensive setup across tests
2. **Mock external services**: Don't hit real APIs in tests
3. **Clean up test data**: Remove test data after tests complete
4. **Use transactions**: Rollback database changes when possible

## Continuous Integration

### GitHub Actions Integration
```yaml
# Example CI configuration
- name: Run Tests
  run: |
    python tests/run_tests.py fast
    python tests/run_tests.py security
    python tests/run_tests.py integration
```

### Coverage Requirements
- **Unit tests**: Target 90%+ coverage
- **Integration tests**: Cover critical user paths
- **E2E tests**: Cover main user workflows
- **Performance tests**: Validate response time requirements

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure `PYTHONPATH` includes project root
2. **Database errors**: Check test database configuration
3. **Permission errors**: Ensure test user has required permissions
4. **Timeout errors**: Increase timeout for slow tests

### Debug Mode
```bash
# Run with debug output
pytest tests/unit/api/test_auth.py -v -s --tb=long

# Run single test with debugging
pytest tests/unit/api/test_auth.py::TestAuthenticationAPI::test_login_success -v -s
```

### Test Data Cleanup
```bash
# Clean test database
python -c "from app import create_app, db; app=create_app('testing'); db.drop_all(); db.create_all()"
```

## Migration from Old Tests

### Archived Tests
Old test files have been moved to `tests/archive/` for reference:
- `test_auth_*.py` → `tests/unit/api/test_auth.py`
- `test_api_*.py` → `tests/integration/api_integration.py`
- `test_*_integration.py` → `tests/unit/services/`

### Maintaining Compatibility
- Old test runners are kept in archive
- Legacy consolidated tests remain for reference
- Gradual migration approach preserves functionality

## Contributing

### Adding New Tests
1. Place tests in appropriate category directory
2. Use consistent naming: `test_feature_name.py`
3. Add appropriate markers
4. Include docstrings for test purposes
5. Update this README if adding new categories

### Code Review Checklist
- [ ] Tests are in correct directory
- [ ] Appropriate markers are used
- [ ] Test names are descriptive
- [ ] Fixtures are used appropriately
- [ ] External dependencies are mocked
- [ ] Tests clean up after themselves

## Test Coverage Goals

| Category | Current | Target |
|----------|---------|--------|
| Unit Tests | 65% | 90% |
| Integration Tests | 45% | 80% |
| E2E Tests | 30% | 70% |
| Security Tests | 80% | 95% |
| Performance Tests | N/A | Benchmarks |

## Consolidation Summary

### Before Consolidation:
- 24 scattered test files
- Inconsistent naming and organization
- Duplicate test logic
- Mixed test types in single files
- Difficult maintenance and discovery

### After Consolidation:
- 12 organized test files
- Clear separation by test type
- Eliminated duplicate logic
- Consistent naming conventions
- Easy test discovery and maintenance
- Improved CI/CD integration

### Files Consolidated:

#### Authentication Tests:
- `test_auth_direct.py` ✓
- `test_auth_error.py` ✓  
- `test_auth_simple.py` ✓
- `test_jwt_decode.py` ✓
- `test_login_api.py` ✓
- `test_login_detailed.py` ✓
→ **Consolidated into**: `tests/unit/api/test_auth.py`

#### API Tests:
- `test_api_direct.py` ✓
- `direct_api_test.py` ✓
- `test_improved_architecture.py` ✓
→ **Consolidated into**: `tests/integration/api_integration.py`

#### Security Tests:
- `test_rate_limiting_fix.py` ✓
- `test_security_encryption.py.disabled` ✓
→ **Consolidated into**: `tests/security/security_tests.py`

#### Service Tests:
- `test_gamification_integration.py` ✓
→ **Consolidated into**: `tests/unit/services/test_gamification.py`

#### Legacy Files Archived:
- HTML test files ✓
- Legacy runners ✓
- Duplicate utilities ✓

## Contact

For questions about the test suite:
- Check existing tests for examples
- Review this README
- Consult the archived tests for legacy patterns
- Follow pytest best practices