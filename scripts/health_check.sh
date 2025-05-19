#!/bin/bash
# Health check script for BDC application

set -e

# Default URL
URL=${1:-"http://localhost:5000"}

echo "Running health checks for $URL..."

# Function to check endpoint
check_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Checking $description: "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$URL$endpoint")
    
    if [ "$response" == "$expected_status" ]; then
        echo "✓ OK (HTTP $response)"
        return 0
    else
        echo "✗ FAILED (Expected $expected_status, got $response)"
        return 1
    fi
}

# Initialize error counter
errors=0

# Basic health check
check_endpoint "/api/health" "200" "API health" || ((errors++))

# Authentication check
check_endpoint "/api/auth/status" "401" "Auth endpoint (expecting 401)" || ((errors++))

# Frontend check (if applicable)
check_endpoint "/" "200" "Frontend" || ((errors++))

# Database connectivity (through API)
check_endpoint "/api/health/db" "200" "Database connectivity" || ((errors++))

# Redis connectivity (through API)
check_endpoint "/api/health/redis" "200" "Redis connectivity" || ((errors++))

# Socket.io check
check_endpoint "/socket.io/" "200" "Socket.io endpoint" || ((errors++))

# Performance check
echo -n "Checking response time: "
response_time=$(curl -s -o /dev/null -w "%{time_total}" "$URL/api/health")
if (( $(echo "$response_time < 1" | bc -l) )); then
    echo "✓ OK (${response_time}s)"
else
    echo "✗ SLOW (${response_time}s)"
    ((errors++))
fi

# Summary
echo ""
if [ $errors -eq 0 ]; then
    echo "✓ All health checks passed!"
    exit 0
else
    echo "✗ $errors health check(s) failed!"
    exit 1
fi