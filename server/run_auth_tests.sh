#!/bin/bash

# Run refactored auth tests with coverage

echo "Running refactored authentication tests..."
echo "========================================"

# Run the specific test files
pytest -v tests/test_auth_service_refactored.py tests/test_auth_api_refactored.py

echo ""
echo "Running coverage analysis..."
echo "=========================="

# Run with coverage
coverage run -m pytest tests/test_auth_service_refactored.py tests/test_auth_api_refactored.py
coverage report --include="app/services/auth_service_refactored.py,app/api/auth_refactored.py,app/container.py,app/repositories/*.py"

echo ""
echo "Coverage Details:"
echo "================"
coverage report -m --include="app/services/auth_service_refactored.py,app/api/auth_refactored.py"