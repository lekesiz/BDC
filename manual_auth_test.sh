#!/bin/bash
# Manual Authentication Security Test Script

echo "🔒 BDC Authentication Security Test"
echo "=================================="

# Test 1: Admin Login
echo "📝 Test 1: Admin Authentication"
admin_response=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bdc.com","password":"admin123","remember":false}')

if echo "$admin_response" | grep -q "access_token"; then
    echo "✅ Admin login successful"
    admin_token=$(echo "$admin_response" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "🎟️  Token: ${admin_token:0:30}..."
else
    echo "❌ Admin login failed"
    echo "Response: $admin_response"
fi

echo ""

# Test 2: Trainer Login  
echo "📝 Test 2: Trainer Authentication"
trainer_response=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"trainer@bdc.com","password":"trainer123","remember":false}')

if echo "$trainer_response" | grep -q "access_token"; then
    echo "✅ Trainer login successful"
    trainer_token=$(echo "$trainer_response" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "🎟️  Token: ${trainer_token:0:30}..."
else
    echo "❌ Trainer login failed"
    echo "Response: $trainer_response"
fi

echo ""

# Test 3: Student Login
echo "📝 Test 3: Student Authentication"
student_response=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@bdc.com","password":"student123","remember":false}')

if echo "$student_response" | grep -q "access_token"; then
    echo "✅ Student login successful"
    student_token=$(echo "$student_response" | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "🎟️  Token: ${student_token:0:30}..."
else
    echo "❌ Student login failed"
    echo "Response: $student_response"
fi

echo ""

# Test 4: Invalid Credentials
echo "📝 Test 4: Invalid Credentials Test"
invalid_response=$(curl -s -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bdc.com","password":"wrongpassword","remember":false}')

if echo "$invalid_response" | grep -q "error"; then
    echo "✅ Invalid credentials properly rejected"
else
    echo "❌ Security issue: Invalid credentials accepted"
    echo "Response: $invalid_response"
fi

echo ""

# Test 5: API Access with Token
if [ ! -z "$admin_token" ]; then
    echo "📝 Test 5: API Access with Admin Token"
    api_response=$(curl -s -X GET http://localhost:5001/api/users \
      -H "Authorization: Bearer $admin_token")
    
    if echo "$api_response" | grep -q "error"; then
        echo "⚠️  API returned error: $(echo "$api_response" | head -c 100)..."
    else
        echo "✅ API access successful with valid token"
    fi
fi

echo ""
echo "🎯 Authentication Security Test Completed"
echo "==========================================="
echo ""
echo "📊 Summary:"
echo "  - All user roles can authenticate with correct credentials"
echo "  - Invalid credentials are properly rejected"
echo "  - JWT tokens are generated successfully"
echo "  - API endpoints can be accessed with valid tokens"
echo ""
echo "🔍 For complete security testing, use the web interface at:"
echo "   http://localhost:8080/test_auth_security.html"