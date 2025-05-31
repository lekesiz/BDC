#!/bin/bash
# Master script to run all tests for BDC project and generate a comprehensive report

# Set up coloring for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT=$(pwd)
REPORT_FILE="$PROJECT_ROOT/TEST_REPORT_$(date +%Y-%m-%d_%H-%M-%S).md"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  BDC Comprehensive Testing Suite${NC}"
echo -e "${BLUE}========================================${NC}"

# Create report file with header
cat > $REPORT_FILE << EOF
# BDC Project Test Report
**Generated:** $(date)

## Summary

EOF

echo -e "\n${BLUE}[1/6] Running Backend Unit Tests...${NC}"
cd $PROJECT_ROOT/server

# Make run_tests.py executable if it isn't already
chmod +x run_tests.py

# Create a temporary file to capture pytest output
BACKEND_OUTPUT_FILE=$(mktemp)

# Run backend tests and capture output
./run_tests.py | tee $BACKEND_OUTPUT_FILE
BACKEND_STATUS=$?

# Extract coverage information
BACKEND_COVERAGE=$(grep -A 2 "TOTAL" $BACKEND_OUTPUT_FILE | tail -n 1 | awk '{print $4}')

if [ $BACKEND_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Backend tests passed!${NC}"
    BACKEND_RESULT="✅ PASSED"
else
    echo -e "${RED}✗ Backend tests failed!${NC}"
    BACKEND_RESULT="❌ FAILED"
fi

echo -e "\n${BLUE}[2/6] Running Backend Security Tests...${NC}"
cd $PROJECT_ROOT/server

# Make run_security_tests.py executable
chmod +x run_security_tests.py

# Run security tests
./run_security_tests.py
SECURITY_STATUS=$?

if [ $SECURITY_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Security tests passed!${NC}"
    SECURITY_RESULT="✅ PASSED"
else
    echo -e "${RED}✗ Security tests failed!${NC}"
    SECURITY_RESULT="❌ FAILED"
fi

echo -e "\n${BLUE}[3/6] Running Frontend Unit Tests...${NC}"
cd $PROJECT_ROOT/client

# Create a temporary file to capture vitest output
FRONTEND_OUTPUT_FILE=$(mktemp)

# Run frontend tests
npm test | tee $FRONTEND_OUTPUT_FILE
FRONTEND_STATUS=$?

# Extract coverage information (this depends on the format of vitest output)
FRONTEND_COVERAGE=$(grep "All files" $FRONTEND_OUTPUT_FILE | awk '{print $4}' | sed 's/%//')

if [ $FRONTEND_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend tests passed!${NC}"
    FRONTEND_RESULT="✅ PASSED"
else
    echo -e "${RED}✗ Frontend tests failed!${NC}"
    FRONTEND_RESULT="❌ FAILED"
fi

echo -e "\n${BLUE}[4/6] Running Frontend Component Tests with Coverage...${NC}"
cd $PROJECT_ROOT/client

# Run frontend tests with coverage
npm run test:coverage
FRONTEND_COV_STATUS=$?

if [ $FRONTEND_COV_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend coverage tests passed!${NC}"
    FRONTEND_COV_RESULT="✅ PASSED"
else
    echo -e "${RED}✗ Frontend coverage tests failed!${NC}"
    FRONTEND_COV_RESULT="❌ FAILED"
fi

echo -e "\n${BLUE}[5/6] Running Linters...${NC}"
cd $PROJECT_ROOT/client

# Run ESLint
npm run lint
LINT_STATUS=$?

if [ $LINT_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ Linting passed!${NC}"
    LINT_RESULT="✅ PASSED"
else
    echo -e "${RED}✗ Linting failed!${NC}"
    LINT_RESULT="❌ FAILED"
fi

echo -e "\n${BLUE}[6/6] Running End-to-End Tests...${NC}"
cd $PROJECT_ROOT/client

# Check if the server is already running
if ! nc -z localhost 5173 >/dev/null 2>&1; then
    echo -e "${YELLOW}Starting development server for E2E tests...${NC}"
    # Start the server in the background
    npm run dev &
    SERVER_PID=$!
    
    # Wait for the server to start
    echo -e "${YELLOW}Waiting for server to start...${NC}"
    while ! nc -z localhost 5173 >/dev/null 2>&1; do
        sleep 1
    done
    
    # Give the server a moment to fully initialize
    sleep 5
    
    STARTED_SERVER=true
else
    echo -e "${YELLOW}Development server already running, using existing server.${NC}"
    STARTED_SERVER=false
fi

# Run Cypress tests
npm run cy:run
E2E_STATUS=$?

# Kill the server if we started it
if [ "$STARTED_SERVER" = true ]; then
    echo -e "${YELLOW}Stopping development server...${NC}"
    kill $SERVER_PID
fi

if [ $E2E_STATUS -eq 0 ]; then
    echo -e "${GREEN}✓ E2E tests passed!${NC}"
    E2E_RESULT="✅ PASSED"
else
    echo -e "${RED}✗ E2E tests failed!${NC}"
    E2E_RESULT="❌ FAILED"
fi

# Create final report
cat >> $REPORT_FILE << EOF
| Test Type | Status | Coverage |
|-----------|--------|----------|
| Backend Unit Tests | $BACKEND_RESULT | $BACKEND_COVERAGE% |
| Security Tests | $SECURITY_RESULT | N/A |
| Frontend Unit Tests | $FRONTEND_RESULT | $FRONTEND_COVERAGE% |
| Frontend Coverage | $FRONTEND_COV_RESULT | See detailed report |
| Linting | $LINT_RESULT | N/A |
| End-to-End Tests | $E2E_RESULT | N/A |

## Test Details

### Backend Test Results
\`\`\`
$(cat $BACKEND_OUTPUT_FILE)
\`\`\`

### Frontend Test Results
\`\`\`
$(cat $FRONTEND_OUTPUT_FILE)
\`\`\`

## Coverage Reports

- Backend Coverage Report: file://$PROJECT_ROOT/server/coverage_html/index.html
- Frontend Coverage Report: file://$PROJECT_ROOT/client/coverage/index.html
- E2E Test Report: file://$PROJECT_ROOT/client/cypress/videos

## Next Steps

$(if [ $BACKEND_STATUS -ne 0 ] || [ $SECURITY_STATUS -ne 0 ] || [ $FRONTEND_STATUS -ne 0 ] || [ $FRONTEND_COV_STATUS -ne 0 ] || [ $LINT_STATUS -ne 0 ] || [ $E2E_STATUS -ne 0 ]; then
    echo "- Fix failing tests"
fi)
$(if [ $(echo "$BACKEND_COVERAGE < 70" | bc -l) -eq 1 ]; then
    echo "- Improve backend test coverage (currently $BACKEND_COVERAGE%, target is 70%)"
fi)
$(if [ $(echo "$FRONTEND_COVERAGE < 70" | bc -l) -eq 1 ]; then
    echo "- Improve frontend test coverage (currently $FRONTEND_COVERAGE%, target is 70%)"
fi)
EOF

# Clean up temp files
rm $BACKEND_OUTPUT_FILE $FRONTEND_OUTPUT_FILE

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}Test suite execution completed!${NC}"
echo -e "${BLUE}Test report saved to:${NC} $REPORT_FILE"
echo -e "${BLUE}========================================${NC}"

# Return overall status
if [ $BACKEND_STATUS -eq 0 ] && [ $SECURITY_STATUS -eq 0 ] && [ $FRONTEND_STATUS -eq 0 ] && [ $FRONTEND_COV_STATUS -eq 0 ] && [ $LINT_STATUS -eq 0 ] && [ $E2E_STATUS -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Check the report for details.${NC}"
    exit 1
fi