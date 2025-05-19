#!/bin/bash
# Smoke test script for BDC application

set -e

# Configuration
URL=${PROD_URL:-"https://api.bdc.com"}
TEST_EMAIL="smoketest@bdc.com"
TEST_PASSWORD="SmokeTest123!"

echo "Running smoke tests for $URL..."

# Function to make API request
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    
    if [ -n "$token" ]; then
        curl -s -X $method \
             -H "Content-Type: application/json" \
             -H "Authorization: Bearer $token" \
             ${data:+-d "$data"} \
             "$URL$endpoint"
    else
        curl -s -X $method \
             -H "Content-Type: application/json" \
             ${data:+-d "$data"} \
             "$URL$endpoint"
    fi
}

# Test 1: Health endpoint
echo -n "1. Health check: "
health_response=$(api_call GET "/api/health")
if echo "$health_response" | grep -q "healthy"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

# Test 2: Authentication flow
echo -n "2. Authentication flow: "
login_response=$(api_call POST "/api/auth/login" "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

if echo "$login_response" | grep -q "access_token"; then
    echo "✓ PASS"
    ACCESS_TOKEN=$(echo "$login_response" | grep -o '"access_token":"[^"]*"' | grep -o '"[^"]*"$' | tr -d '"')
else
    echo "✗ FAIL (Login failed)"
    exit 1
fi

# Test 3: Protected endpoint access
echo -n "3. Protected endpoint: "
user_response=$(api_call GET "/api/users/me" "" "$ACCESS_TOKEN")
if echo "$user_response" | grep -q "email"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

# Test 4: Multi-tenancy check
echo -n "4. Multi-tenancy: "
tenants_response=$(api_call GET "/api/tenants" "" "$ACCESS_TOKEN")
if echo "$tenants_response" | grep -q "tenant"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

# Test 5: Real-time connection (Socket.io)
echo -n "5. Real-time connectivity: "
socket_response=$(curl -s -o /dev/null -w "%{http_code}" "$URL/socket.io/")
if [ "$socket_response" == "200" ]; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

# Test 6: File upload capability
echo -n "6. File upload: "
upload_response=$(curl -s -X POST \
    -H "Authorization: Bearer $ACCESS_TOKEN" \
    -F "file=@/tmp/test_upload.txt" \
    "$URL/api/files/upload")

if echo "$upload_response" | grep -q "file_id"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

# Test 7: API rate limiting
echo -n "7. Rate limiting: "
rate_limit_hit=false
for i in {1..20}; do
    rate_response=$(api_call GET "/api/health")
    if echo "$rate_response" | grep -q "429"; then
        rate_limit_hit=true
        break
    fi
done

if [ "$rate_limit_hit" = true ]; then
    echo "✓ PASS"
else
    echo "⚠ WARNING (Rate limiting may not be configured)"
fi

# Test 8: Error handling
echo -n "8. Error handling: "
error_response=$(api_call GET "/api/nonexistent" "" "$ACCESS_TOKEN")
if echo "$error_response" | grep -q "404"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

# Test 9: CORS headers
echo -n "9. CORS configuration: "
cors_response=$(curl -s -I -X OPTIONS \
    -H "Origin: https://app.bdc.com" \
    -H "Access-Control-Request-Method: GET" \
    "$URL/api/health")

if echo "$cors_response" | grep -q "Access-Control-Allow-Origin"; then
    echo "✓ PASS"
else
    echo "✗ FAIL"
    exit 1
fi

# Test 10: SSL/TLS configuration
echo -n "10. SSL/TLS: "
if [[ "$URL" =~ ^https ]]; then
    ssl_response=$(curl -s -o /dev/null -w "%{http_code}" --ssl-protocols TLSv1.2 "$URL/api/health")
    if [ "$ssl_response" == "200" ]; then
        echo "✓ PASS"
    else
        echo "✗ FAIL"
        exit 1
    fi
else
    echo "⚠ SKIPPED (Not HTTPS)"
fi

echo ""
echo "✓ All smoke tests passed!"
echo ""

# Performance metrics
echo "Performance Report:"
echo -n "- API response time: "
response_time=$(curl -s -o /dev/null -w "%{time_total}" "$URL/api/health")
echo "${response_time}s"

echo -n "- Authentication time: "
auth_time=$(curl -s -o /dev/null -w "%{time_total}" -X POST \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}" \
    "$URL/api/auth/login")
echo "${auth_time}s"

exit 0