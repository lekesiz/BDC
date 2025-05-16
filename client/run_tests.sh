#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}BDC Frontend Test Suite${NC}"
echo "========================="

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing dependencies...${NC}"
    npm install
fi

# Install test dependencies if needed
echo -e "${YELLOW}Installing test dependencies...${NC}"
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom @vitest/coverage-v8 @vitest/ui

# Run tests based on argument
case "$1" in
    "watch")
        echo -e "${YELLOW}Running tests in watch mode...${NC}"
        npm run test:watch
        ;;
    "coverage")
        echo -e "${YELLOW}Running tests with coverage...${NC}"
        npm run test:coverage
        ;;
    "ui")
        echo -e "${YELLOW}Running tests with UI...${NC}"
        npm run test:ui
        ;;
    *)
        echo -e "${YELLOW}Running all tests...${NC}"
        npm run test
        ;;
esac

# Check test results
if [ $? -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi