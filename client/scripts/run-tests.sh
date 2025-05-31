#!/bin/bash

# Comprehensive test runner script for BDC application
# Usage: ./scripts/run-tests.sh [test-type] [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
TEST_TYPE="${1:-all}"
BROWSER="${CYPRESS_BROWSER:-chrome}"
HEADLESS="${CYPRESS_HEADLESS:-true}"
RECORD="${CYPRESS_RECORD:-false}"
PARALLEL="${CYPRESS_PARALLEL:-false}"
API_URL="${CYPRESS_apiUrl:-http://localhost:5001/api}"
BASE_URL="${CYPRESS_baseUrl:-http://localhost:5173}"
SPEC_PATTERN="${2:-cypress/e2e/**/*.cy.js}"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if services are running
check_services() {
    print_status "Checking if services are running..."
    
    # Check frontend
    if ! curl -s "$BASE_URL" > /dev/null; then
        print_error "Frontend server is not running at $BASE_URL"
        print_status "Starting frontend server..."
        npm run dev &
        FRONTEND_PID=$!
        npx wait-on "$BASE_URL" --timeout 60000 || {
            print_error "Failed to start frontend server"
            exit 1
        }
    else
        print_success "Frontend server is running at $BASE_URL"
    fi
    
    # Check backend
    if ! curl -s "$API_URL/health" > /dev/null; then
        print_error "Backend server is not running at $API_URL"
        print_status "Please start the backend server manually"
        exit 1
    else
        print_success "Backend server is running at $API_URL"
    fi
}

# Function to seed database
seed_database() {
    print_status "Seeding test database..."
    npx cypress run --spec "cypress/support/seed-only.cy.js" --headless || {
        print_warning "Database seeding failed, continuing with existing data..."
    }
}

# Function to run specific test suites
run_authentication_tests() {
    print_status "Running authentication tests..."
    npx cypress run \
        --spec "cypress/e2e/auth*.cy.js" \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=true,screenshotOnRunFailure=true"
}

run_admin_tests() {
    print_status "Running admin dashboard tests..."
    npx cypress run \
        --spec "cypress/e2e/admin*.cy.js" \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=true,screenshotOnRunFailure=true"
}

run_beneficiary_tests() {
    print_status "Running beneficiary management tests..."
    npx cypress run \
        --spec "cypress/e2e/beneficiary*.cy.js" \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=true,screenshotOnRunFailure=true"
}

run_evaluation_tests() {
    print_status "Running evaluation system tests..."
    npx cypress run \
        --spec "cypress/e2e/evaluation*.cy.js" \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=true,screenshotOnRunFailure=true"
}

run_calendar_tests() {
    print_status "Running calendar system tests..."
    npx cypress run \
        --spec "cypress/e2e/calendar*.cy.js" \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=true,screenshotOnRunFailure=true"
}

run_accessibility_tests() {
    print_status "Running accessibility tests..."
    npx cypress run \
        --spec "cypress/e2e/accessibility*.cy.js" \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=true,screenshotOnRunFailure=true"
}

run_smoke_tests() {
    print_status "Running smoke tests (critical user journeys)..."
    npx cypress run \
        --spec "cypress/e2e/auth-comprehensive.cy.js,cypress/e2e/complete-flow.cy.js" \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=false,screenshotOnRunFailure=true"
}

run_regression_tests() {
    print_status "Running full regression test suite..."
    
    local cypress_args="--browser $BROWSER --headless=$HEADLESS"
    
    if [ "$RECORD" = "true" ]; then
        cypress_args="$cypress_args --record"
    fi
    
    if [ "$PARALLEL" = "true" ]; then
        cypress_args="$cypress_args --parallel"
    fi
    
    npx cypress run $cypress_args \
        --config "video=true,screenshotOnRunFailure=true,defaultCommandTimeout=10000"
}

run_performance_tests() {
    print_status "Running performance tests..."
    
    # Build application for production testing
    print_status "Building application for performance testing..."
    npm run build
    
    # Start preview server
    print_status "Starting preview server..."
    npm run preview &
    PREVIEW_PID=$!
    npx wait-on "http://localhost:4173" --timeout 60000
    
    # Run Lighthouse tests
    print_status "Running Lighthouse performance tests..."
    npm run lighthouse
    
    # Cleanup
    if [ ! -z "$PREVIEW_PID" ]; then
        kill $PREVIEW_PID
    fi
}

run_visual_tests() {
    print_status "Running visual regression tests..."
    npx cypress run \
        --spec "cypress/e2e/*visual*.cy.js" \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=false,screenshotOnRunFailure=true"
}

run_mobile_tests() {
    print_status "Running mobile-specific tests..."
    CYPRESS_viewportWidth=375 CYPRESS_viewportHeight=667 \
    npx cypress run \
        --browser "$BROWSER" \
        --headless="$HEADLESS" \
        --config "video=true,screenshotOnRunFailure=true"
}

# Function to generate test reports
generate_reports() {
    print_status "Generating test reports..."
    
    # Merge Cypress reports if they exist
    if [ -d "cypress/reports" ]; then
        npx mochawesome-merge cypress/reports/*.json > cypress/reports/merged-report.json
        npx marge cypress/reports/merged-report.json --reportDir cypress/reports --inline
        print_success "Test reports generated in cypress/reports/"
    fi
    
    # Generate coverage report if available
    if [ -f "coverage/cypress/coverage-final.json" ]; then
        npx nyc report --reporter html --report-dir coverage/html
        print_success "Coverage report generated in coverage/html/"
    fi
}

# Function to cleanup processes
cleanup() {
    print_status "Cleaning up..."
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$PREVIEW_PID" ]; then
        kill $PREVIEW_PID 2>/dev/null || true
    fi
}

# Trap cleanup function
trap cleanup EXIT

# Main execution logic
print_status "Starting BDC E2E Test Suite"
print_status "Test Type: $TEST_TYPE"
print_status "Browser: $BROWSER"
print_status "Headless: $HEADLESS"

# Check prerequisites
if ! command -v npx &> /dev/null; then
    print_error "npx is not installed. Please install Node.js and npm."
    exit 1
fi

if [ ! -f "cypress.config.js" ]; then
    print_error "cypress.config.js not found. Please run this script from the project root."
    exit 1
fi

# Check services
check_services

# Seed database if needed
if [ "$TEST_TYPE" != "smoke" ] && [ "$TEST_TYPE" != "performance" ]; then
    seed_database
fi

# Run tests based on type
case $TEST_TYPE in
    "auth"|"authentication")
        run_authentication_tests
        ;;
    "admin")
        run_admin_tests
        ;;
    "beneficiary"|"beneficiaries")
        run_beneficiary_tests
        ;;
    "evaluation"|"evaluations")
        run_evaluation_tests
        ;;
    "calendar")
        run_calendar_tests
        ;;
    "accessibility"|"a11y")
        run_accessibility_tests
        ;;
    "smoke")
        run_smoke_tests
        ;;
    "regression")
        run_regression_tests
        ;;
    "performance"|"perf")
        run_performance_tests
        ;;
    "visual")
        run_visual_tests
        ;;
    "mobile")
        run_mobile_tests
        ;;
    "all")
        print_status "Running complete test suite..."
        run_smoke_tests
        run_authentication_tests
        run_admin_tests
        run_beneficiary_tests
        run_evaluation_tests
        run_calendar_tests
        run_accessibility_tests
        ;;
    *)
        print_status "Running custom test spec: $TEST_TYPE"
        npx cypress run \
            --spec "$TEST_TYPE" \
            --browser "$BROWSER" \
            --headless="$HEADLESS" \
            --config "video=true,screenshotOnRunFailure=true"
        ;;
esac

# Generate reports
generate_reports

print_success "Test execution completed!"
print_status "Check cypress/reports/ for detailed test reports"
print_status "Check cypress/screenshots/ for failure screenshots"
print_status "Check cypress/videos/ for test recordings"