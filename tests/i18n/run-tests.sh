#!/bin/bash

# BDC i18n Test Runner
# Comprehensive test runner for all internationalization tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test directories
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$TEST_DIR/../.." && pwd)"
CLIENT_DIR="$PROJECT_ROOT/client"
SERVER_DIR="$PROJECT_ROOT/server"

# Default options
RUN_FRONTEND=true
RUN_BACKEND=true
RUN_E2E=true
COVERAGE=false
WATCH=false
VERBOSE=false
PARALLEL=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --frontend-only)
            RUN_FRONTEND=true
            RUN_BACKEND=false
            RUN_E2E=false
            shift
            ;;
        --backend-only)
            RUN_FRONTEND=false
            RUN_BACKEND=true
            RUN_E2E=false
            shift
            ;;
        --e2e-only)
            RUN_FRONTEND=false
            RUN_BACKEND=false
            RUN_E2E=true
            shift
            ;;
        --coverage)
            COVERAGE=true
            shift
            ;;
        --watch)
            WATCH=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --help)
            echo "BDC i18n Test Runner"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --frontend-only    Run only frontend tests"
            echo "  --backend-only     Run only backend tests"
            echo "  --e2e-only         Run only E2E tests"
            echo "  --coverage         Generate coverage reports"
            echo "  --watch            Run tests in watch mode"
            echo "  --verbose          Verbose output"
            echo "  --parallel         Run tests in parallel"
            echo "  --help             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                 # Run all tests"
            echo "  $0 --frontend-only --coverage  # Frontend tests with coverage"
            echo "  $0 --e2e-only --verbose       # E2E tests with verbose output"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Function to print section headers
print_section() {
    echo -e "\n${BLUE}===================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}===================================================${NC}\n"
}

# Function to print success message
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error message
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to print warning message
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    local missing_deps=()
    
    if $RUN_FRONTEND; then
        if ! command_exists npm; then
            missing_deps+=("npm")
        fi
        if ! command_exists node; then
            missing_deps+=("node")
        fi
    fi
    
    if $RUN_BACKEND; then
        if ! command_exists python; then
            missing_deps+=("python")
        fi
        if ! command_exists pytest; then
            missing_deps+=("pytest")
        fi
    fi
    
    if $RUN_E2E; then
        if ! command_exists npx; then
            missing_deps+=("npx")
        fi
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Function to setup test environment
setup_environment() {
    print_section "Setting Up Test Environment"
    
    # Set environment variables
    export NODE_ENV=test
    export PYTHONPATH="$SERVER_DIR:$PYTHONPATH"
    
    if $RUN_FRONTEND; then
        if [ ! -d "$CLIENT_DIR/node_modules" ]; then
            print_warning "Installing frontend dependencies..."
            cd "$CLIENT_DIR"
            npm install
        fi
    fi
    
    if $RUN_BACKEND; then
        if [ ! -f "$SERVER_DIR/venv/bin/activate" ]; then
            print_warning "Setting up Python virtual environment..."
            cd "$SERVER_DIR"
            python -m venv venv
            source venv/bin/activate
            pip install -r requirements-test.txt
        else
            cd "$SERVER_DIR"
            source venv/bin/activate
        fi
    fi
    
    print_success "Environment setup complete"
}

# Function to run frontend tests
run_frontend_tests() {
    if ! $RUN_FRONTEND; then
        return 0
    fi
    
    print_section "Running Frontend i18n Tests"
    
    cd "$CLIENT_DIR"
    
    local jest_args=()
    jest_args+=("--config" "$TEST_DIR/jest.config.js")
    jest_args+=("$TEST_DIR/component-tests.jsx")
    
    if $COVERAGE; then
        jest_args+=("--coverage")
    fi
    
    if $WATCH; then
        jest_args+=("--watch")
    fi
    
    if $VERBOSE; then
        jest_args+=("--verbose")
    fi
    
    if $PARALLEL; then
        jest_args+=("--maxWorkers=4")
    fi
    
    echo "Running: npm test -- ${jest_args[*]}"
    
    if npm test -- "${jest_args[@]}"; then
        print_success "Frontend tests passed"
        return 0
    else
        print_error "Frontend tests failed"
        return 1
    fi
}

# Function to run backend tests
run_backend_tests() {
    if ! $RUN_BACKEND; then
        return 0
    fi
    
    print_section "Running Backend i18n Tests"
    
    cd "$SERVER_DIR"
    source venv/bin/activate
    
    local pytest_args=()
    pytest_args+=("-c" "$TEST_DIR/pytest.ini")
    pytest_args+=("$TEST_DIR/api-tests.py")
    
    if $COVERAGE; then
        pytest_args+=("--cov=app/i18n")
        pytest_args+=("--cov-report=html:$TEST_DIR/htmlcov")
        pytest_args+=("--cov-report=term-missing")
    fi
    
    if $VERBOSE; then
        pytest_args+=("-v")
    fi
    
    if $PARALLEL; then
        pytest_args+=("-n" "4")
    fi
    
    echo "Running: pytest ${pytest_args[*]}"
    
    if pytest "${pytest_args[@]}"; then
        print_success "Backend tests passed"
        return 0
    else
        print_error "Backend tests failed"
        return 1
    fi
}

# Function to run E2E tests
run_e2e_tests() {
    if ! $RUN_E2E; then
        return 0
    fi
    
    print_section "Running E2E i18n Tests"
    
    cd "$PROJECT_ROOT"
    
    # Check if application is running
    if ! curl -s http://localhost:3000 > /dev/null; then
        print_warning "Application not running. Starting development server..."
        # Start application in background
        npm run dev &
        APP_PID=$!
        
        # Wait for application to start
        echo "Waiting for application to start..."
        for i in {1..30}; do
            if curl -s http://localhost:3000 > /dev/null; then
                break
            fi
            sleep 2
        done
        
        if ! curl -s http://localhost:3000 > /dev/null; then
            print_error "Failed to start application"
            return 1
        fi
    fi
    
    local cypress_args=()
    
    if $VERBOSE; then
        cypress_args+=("--reporter" "spec")
    fi
    
    # Run language switching tests
    print_section "Running Language Switching Tests"
    if npx cypress run --spec "$TEST_DIR/language-switching-tests.js" "${cypress_args[@]}"; then
        print_success "Language switching tests passed"
    else
        print_error "Language switching tests failed"
        if [ ! -z "$APP_PID" ]; then
            kill $APP_PID
        fi
        return 1
    fi
    
    # Run RTL layout tests
    print_section "Running RTL Layout Tests"
    if npx cypress run --spec "$TEST_DIR/rtl-layout-tests.js" "${cypress_args[@]}"; then
        print_success "RTL layout tests passed"
    else
        print_error "RTL layout tests failed"
        if [ ! -z "$APP_PID" ]; then
            kill $APP_PID
        fi
        return 1
    fi
    
    # Clean up background process
    if [ ! -z "$APP_PID" ]; then
        kill $APP_PID
    fi
    
    print_success "All E2E tests passed"
    return 0
}

# Function to generate test report
generate_report() {
    print_section "Generating Test Report"
    
    local report_file="$TEST_DIR/test-report.md"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    
    cat > "$report_file" << EOF
# BDC i18n Test Report

**Generated:** $timestamp

## Test Summary

EOF
    
    if $RUN_FRONTEND; then
        echo "- ✓ Frontend component tests" >> "$report_file"
    fi
    
    if $RUN_BACKEND; then
        echo "- ✓ Backend API tests" >> "$report_file"
    fi
    
    if $RUN_E2E; then
        echo "- ✓ E2E language switching tests" >> "$report_file"
        echo "- ✓ E2E RTL layout tests" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF

## Coverage Reports

EOF
    
    if $COVERAGE; then
        if $RUN_FRONTEND; then
            echo "- Frontend coverage: \`client/coverage/index.html\`" >> "$report_file"
        fi
        
        if $RUN_BACKEND; then
            echo "- Backend coverage: \`tests/i18n/htmlcov/index.html\`" >> "$report_file"
        fi
    fi
    
    cat >> "$report_file" << EOF

## Test Files

- Component tests: \`tests/i18n/component-tests.jsx\`
- API tests: \`tests/i18n/api-tests.py\`
- Language switching tests: \`tests/i18n/language-switching-tests.js\`
- RTL layout tests: \`tests/i18n/rtl-layout-tests.js\`

## Supported Languages

- English (en) - LTR
- Spanish (es) - LTR
- French (fr) - LTR
- German (de) - LTR
- Turkish (tr) - LTR
- Russian (ru) - LTR
- Arabic (ar) - RTL
- Hebrew (he) - RTL

EOF
    
    print_success "Test report generated: $report_file"
}

# Main execution
main() {
    echo -e "${BLUE}BDC i18n Test Runner${NC}"
    echo -e "${BLUE}=====================${NC}\n"
    
    local start_time=$(date +%s)
    local failed_tests=()
    
    check_prerequisites
    setup_environment
    
    # Run tests
    if ! run_frontend_tests; then
        failed_tests+=("frontend")
    fi
    
    if ! run_backend_tests; then
        failed_tests+=("backend")
    fi
    
    if ! run_e2e_tests; then
        failed_tests+=("e2e")
    fi
    
    # Generate report
    generate_report
    
    # Calculate execution time
    local end_time=$(date +%s)
    local execution_time=$((end_time - start_time))
    
    # Print summary
    print_section "Test Summary"
    
    if [ ${#failed_tests[@]} -eq 0 ]; then
        print_success "All tests passed! 🎉"
        echo -e "${GREEN}Execution time: ${execution_time}s${NC}"
        exit 0
    else
        print_error "Some tests failed: ${failed_tests[*]}"
        echo -e "${RED}Execution time: ${execution_time}s${NC}"
        exit 1
    fi
}

# Handle interruption
trap 'echo -e "\n${YELLOW}Test execution interrupted${NC}"; exit 130' INT

# Run main function
main "$@"