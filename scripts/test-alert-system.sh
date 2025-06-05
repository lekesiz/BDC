#!/bin/bash
# ================================
# BDC Alert System Test Script
# ================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:5000}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@bdc.com}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-Admin123!}"

# Helper Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to get auth token
get_auth_token() {
    log_info "Authenticating as admin..."
    
    local response=$(curl -s -X POST \
        "${API_URL}/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"${ADMIN_EMAIL}\",
            \"password\": \"${ADMIN_PASSWORD}\"
        }")
    
    local token=$(echo "$response" | jq -r '.access_token // empty')
    
    if [[ -z "$token" || "$token" == "null" ]]; then
        log_error "Failed to authenticate. Response: $response"
        exit 1
    fi
    
    echo "$token"
}

# Function to test alert system health
test_alert_health() {
    log_info "Testing alert system health..."
    
    local response=$(curl -s "${API_URL}/api/alerts/health")
    local status=$(echo "$response" | jq -r '.data.status // empty')
    
    if [[ "$status" == "healthy" ]]; then
        log_success "Alert system is healthy"
        local channels=$(echo "$response" | jq -r '.data.enabled_channels[]' | paste -sd, -)
        log_info "Enabled channels: $channels"
        return 0
    else
        log_error "Alert system health check failed: $response"
        return 1
    fi
}

# Function to get alert statistics
get_alert_stats() {
    local token="$1"
    log_info "Getting alert statistics..."
    
    local response=$(curl -s \
        -H "Authorization: Bearer $token" \
        "${API_URL}/api/alerts/stats")
    
    local success=$(echo "$response" | jq -r '.success // false')
    
    if [[ "$success" == "true" ]]; then
        log_success "Alert statistics retrieved"
        echo "$response" | jq '.data'
        return 0
    else
        log_error "Failed to get alert statistics: $response"
        return 1
    fi
}

# Function to send test alert
send_test_alert() {
    local token="$1"
    local severity="$2"
    local title="$3"
    local message="$4"
    
    log_info "Sending test alert (severity: $severity)..."
    
    local response=$(curl -s -X POST \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        "${API_URL}/api/alerts/test" \
        -d "{
            \"title\": \"$title\",
            \"message\": \"$message\",
            \"severity\": \"$severity\",
            \"metadata\": {
                \"test_script\": true,
                \"test_time\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
            }
        }")
    
    local success=$(echo "$response" | jq -r '.success // false')
    
    if [[ "$success" == "true" ]]; then
        local alert_id=$(echo "$response" | jq -r '.data.alert_id')
        log_success "Test alert sent successfully (ID: $alert_id)"
        return 0
    else
        log_error "Failed to send test alert: $response"
        return 1
    fi
}

# Function to send manual alert
send_manual_alert() {
    local token="$1"
    local severity="$2"
    local title="$3"
    local message="$4"
    local event_type="$5"
    
    log_info "Sending manual alert (severity: $severity)..."
    
    local response=$(curl -s -X POST \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        "${API_URL}/api/alerts/send" \
        -d "{
            \"title\": \"$title\",
            \"message\": \"$message\",
            \"severity\": \"$severity\",
            \"event_type\": \"$event_type\",
            \"source\": \"test-script\",
            \"metadata\": {
                \"script_test\": true,
                \"test_timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
                \"test_environment\": \"${ENVIRONMENT:-development}\"
            }
        }")
    
    local success=$(echo "$response" | jq -r '.success // false')
    
    if [[ "$success" == "true" ]]; then
        local alert_id=$(echo "$response" | jq -r '.data.alert_id')
        log_success "Manual alert sent successfully (ID: $alert_id)"
        return 0
    else
        log_error "Failed to send manual alert: $response"
        return 1
    fi
}

# Function to get alert configuration
get_alert_config() {
    local token="$1"
    log_info "Getting alert configuration..."
    
    local response=$(curl -s \
        -H "Authorization: Bearer $token" \
        "${API_URL}/api/alerts/config")
    
    local success=$(echo "$response" | jq -r '.success // false')
    
    if [[ "$success" == "true" ]]; then
        log_success "Alert configuration retrieved"
        echo "$response" | jq '.data'
        return 0
    else
        log_error "Failed to get alert configuration: $response"
        return 1
    fi
}

# Function to test webhook endpoint
test_webhook() {
    log_info "Testing webhook endpoint..."
    
    local webhook_response=$(curl -s -X POST \
        "${API_URL}/api/alerts/webhook" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer demo-key" \
        -d "{
            \"title\": \"Webhook Test Alert\",
            \"message\": \"This is a test alert sent via webhook\",
            \"severity\": \"low\",
            \"source\": \"webhook-test\",
            \"event_type\": \"webhook\",
            \"metadata\": {
                \"webhook_test\": true,
                \"test_time\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
            }
        }")
    
    local success=$(echo "$webhook_response" | jq -r '.success // false')
    
    if [[ "$success" == "true" ]]; then
        log_success "Webhook test successful"
        return 0
    else
        log_error "Webhook test failed: $webhook_response"
        return 1
    fi
}

# Function to test alert history
test_alert_history() {
    local token="$1"
    log_info "Testing alert history retrieval..."
    
    local response=$(curl -s \
        -H "Authorization: Bearer $token" \
        "${API_URL}/api/alerts/history?per_page=5")
    
    local success=$(echo "$response" | jq -r '.success // false')
    
    if [[ "$success" == "true" ]]; then
        local count=$(echo "$response" | jq -r '.data.alerts | length')
        log_success "Alert history retrieved ($count alerts)"
        return 0
    else
        log_error "Failed to get alert history: $response"
        return 1
    fi
}

# Function to run comprehensive alert system tests
run_comprehensive_tests() {
    log_info "Starting comprehensive alert system tests..."
    echo ""
    
    # Test 1: Health Check (no auth required)
    echo "=== Test 1: Health Check ==="
    if test_alert_health; then
        log_success "✓ Health check passed"
    else
        log_error "✗ Health check failed"
        return 1
    fi
    echo ""
    
    # Get authentication token
    echo "=== Authentication ==="
    local token
    if token=$(get_auth_token); then
        log_success "✓ Authentication successful"
    else
        log_error "✗ Authentication failed"
        return 1
    fi
    echo ""
    
    # Test 2: Alert Statistics
    echo "=== Test 2: Alert Statistics ==="
    if get_alert_stats "$token" > /dev/null; then
        log_success "✓ Alert statistics retrieved"
    else
        log_error "✗ Alert statistics failed"
    fi
    echo ""
    
    # Test 3: Alert Configuration
    echo "=== Test 3: Alert Configuration ==="
    if get_alert_config "$token" > /dev/null; then
        log_success "✓ Alert configuration retrieved"
    else
        log_error "✗ Alert configuration failed"
    fi
    echo ""
    
    # Test 4: Send Test Alerts (various severities)
    echo "=== Test 4: Test Alerts ==="
    local test_alerts=(
        "low|Low Priority Test|This is a low priority test alert"
        "medium|Medium Priority Test|This is a medium priority test alert"
        "high|High Priority Test|This is a high priority test alert"
        "critical|Critical Test Alert|This is a critical test alert"
    )
    
    for alert_data in "${test_alerts[@]}"; do
        IFS='|' read -r severity title message <<< "$alert_data"
        if send_test_alert "$token" "$severity" "$title" "$message"; then
            log_success "✓ Test alert sent (severity: $severity)"
        else
            log_error "✗ Test alert failed (severity: $severity)"
        fi
    done
    echo ""
    
    # Test 5: Send Manual Alerts
    echo "=== Test 5: Manual Alerts ==="
    local manual_alerts=(
        "medium|Manual System Alert|System maintenance notification|maintenance"
        "high|Security Alert|Potential security incident detected|security"
        "low|Performance Notice|System performance information|performance"
    )
    
    for alert_data in "${manual_alerts[@]}"; do
        IFS='|' read -r severity title message event_type <<< "$alert_data"
        if send_manual_alert "$token" "$severity" "$title" "$message" "$event_type"; then
            log_success "✓ Manual alert sent (type: $event_type)"
        else
            log_error "✗ Manual alert failed (type: $event_type)"
        fi
    done
    echo ""
    
    # Test 6: Webhook Endpoint
    echo "=== Test 6: Webhook Endpoint ==="
    if test_webhook; then
        log_success "✓ Webhook test passed"
    else
        log_error "✗ Webhook test failed"
    fi
    echo ""
    
    # Test 7: Alert History
    echo "=== Test 7: Alert History ==="
    if test_alert_history "$token"; then
        log_success "✓ Alert history test passed"
    else
        log_error "✗ Alert history test failed"
    fi
    echo ""
    
    # Final Statistics
    echo "=== Final Alert Statistics ==="
    get_alert_stats "$token"
    echo ""
    
    log_success "Comprehensive alert system testing completed!"
}

# Function to show usage
show_usage() {
    cat << EOF
BDC Alert System Test Script

USAGE:
    $0 [OPTIONS] [COMMAND]

COMMANDS:
    health          Test alert system health only
    stats           Get alert statistics
    config          Get alert configuration
    test-alert      Send a single test alert
    manual-alert    Send a single manual alert
    webhook         Test webhook endpoint
    history         Get alert history
    full            Run comprehensive tests (default)

OPTIONS:
    --api-url URL          API base URL (default: http://localhost:5000)
    --admin-email EMAIL    Admin email (default: admin@bdc.com)
    --admin-password PASS  Admin password (default: Admin123!)
    --help                 Show this help message

EXAMPLES:
    $0                                    # Run full test suite
    $0 health                            # Test health only
    $0 test-alert                        # Send single test alert
    $0 --api-url https://api.bdc.com full # Test against production API

ENVIRONMENT VARIABLES:
    API_URL           Override default API URL
    ADMIN_EMAIL       Override default admin email
    ADMIN_PASSWORD    Override default admin password
EOF
}

# Main function
main() {
    local command="full"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --api-url)
                API_URL="$2"
                shift 2
                ;;
            --admin-email)
                ADMIN_EMAIL="$2"
                shift 2
                ;;
            --admin-password)
                ADMIN_PASSWORD="$2"
                shift 2
                ;;
            --help)
                show_usage
                exit 0
                ;;
            health|stats|config|test-alert|manual-alert|webhook|history|full)
                command="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check dependencies
    if ! command -v curl &> /dev/null; then
        log_error "curl is required but not installed"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        log_error "jq is required but not installed"
        exit 1
    fi
    
    log_info "Testing BDC Alert System at $API_URL"
    echo ""
    
    # Execute command
    case $command in
        health)
            test_alert_health
            ;;
        stats)
            token=$(get_auth_token)
            get_alert_stats "$token"
            ;;
        config)
            token=$(get_auth_token)
            get_alert_config "$token"
            ;;
        test-alert)
            token=$(get_auth_token)
            send_test_alert "$token" "medium" "Manual Test Alert" "This is a manual test alert from the test script"
            ;;
        manual-alert)
            token=$(get_auth_token)
            send_manual_alert "$token" "medium" "Manual Alert" "This is a manual alert from the test script" "test"
            ;;
        webhook)
            test_webhook
            ;;
        history)
            token=$(get_auth_token)
            test_alert_history "$token"
            ;;
        full)
            run_comprehensive_tests
            ;;
        *)
            log_error "Unknown command: $command"
            show_usage
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"