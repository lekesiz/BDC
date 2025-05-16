#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}BDC Backend Test Suite${NC}"
echo "========================"

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${RED}Warning: No virtual environment detected${NC}"
    echo "Please activate your virtual environment first"
    exit 1
fi

# Install test dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -r requirements-test.txt

# Run tests with coverage
echo -e "${YELLOW}Running tests with coverage...${NC}"
pytest --cov=. --cov-report=html --cov-report=term-missing

# Run specific test categories
if [ "$1" == "unit" ]; then
    echo -e "${YELLOW}Running unit tests only...${NC}"
    pytest -m unit
elif [ "$1" == "integration" ]; then
    echo -e "${YELLOW}Running integration tests only...${NC}"
    pytest -m integration
elif [ "$1" == "slow" ]; then
    echo -e "${YELLOW}Running slow tests...${NC}"
    pytest -m slow
fi

# Generate coverage report
echo -e "${YELLOW}Coverage report generated in htmlcov/index.html${NC}"

# Check test results
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi