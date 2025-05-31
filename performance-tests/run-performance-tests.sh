#!/bin/bash

# Performance Testing Suite for BDC Application
# This script runs various performance tests and generates reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${BASE_URL:-http://localhost:5000}"
RESULTS_DIR="./results/$(date +%Y%m%d_%H%M%S)"
K6_CLOUD_TOKEN="${K6_CLOUD_TOKEN:-}"

# Create results directory
mkdir -p "$RESULTS_DIR"

echo -e "${GREEN}BDC Performance Testing Suite${NC}"
echo "================================"
echo "Base URL: $BASE_URL"
echo "Results will be saved to: $RESULTS_DIR"
echo ""

# Function to run a test
run_test() {
    local test_name=$1
    local test_file=$2
    local description=$3
    
    echo -e "${YELLOW}Running $test_name...${NC}"
    echo "$description"
    echo ""
    
    # Run the test
    if k6 run \
        --out json="$RESULTS_DIR/${test_name}.json" \
        --summary-export="$RESULTS_DIR/${test_name}_summary.json" \
        -e BASE_URL="$BASE_URL" \
        "$test_file"; then
        echo -e "${GREEN}✓ $test_name completed successfully${NC}"
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        return 1
    fi
    
    echo ""
}

# Function to generate HTML report
generate_html_report() {
    local test_name=$1
    
    echo "Generating HTML report for $test_name..."
    
    # Convert k6 JSON output to HTML report
    k6-to-html "$RESULTS_DIR/${test_name}.json" "$RESULTS_DIR/${test_name}_report.html" || true
}

# 1. Smoke Test
echo -e "${YELLOW}1. SMOKE TEST${NC}"
echo "Quick test to verify the system is working"
cat > "$RESULTS_DIR/smoke-test.js" << 'EOF'
import http from 'k6/http';
import { check } from 'k6';

export const options = {
    vus: 1,
    duration: '1m',
    thresholds: {
        http_req_duration: ['p(99)<1500'],
        http_req_failed: ['rate<0.01'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

export default function() {
    const res = http.get(`${BASE_URL}/api/health`);
    check(res, {
        'status is 200': (r) => r.status === 200,
        'response time < 500ms': (r) => r.timings.duration < 500,
    });
}
EOF

run_test "smoke-test" "$RESULTS_DIR/smoke-test.js" "Testing basic connectivity and response"

# 2. Load Test
echo -e "${YELLOW}2. LOAD TEST${NC}"
echo "Testing normal expected load"
run_test "load-test" "./k6-load-test.js" "Simulating normal user behavior with gradual ramp-up"

# 3. Stress Test
echo -e "${YELLOW}3. STRESS TEST${NC}"
echo "Testing system under stress conditions"
run_test "stress-test" "./k6-stress-test.js" "Pushing system to its limits"

# 4. Spike Test
echo -e "${YELLOW}4. SPIKE TEST${NC}"
echo "Testing sudden traffic spikes"
cat > "$RESULTS_DIR/spike-test.js" << 'EOF'
import http from 'k6/http';
import { check } from 'k6';

export const options = {
    stages: [
        { duration: '10s', target: 0 },
        { duration: '5s', target: 100 },
        { duration: '3m', target: 100 },
        { duration: '5s', target: 500 },
        { duration: '3m', target: 500 },
        { duration: '5s', target: 100 },
        { duration: '3m', target: 100 },
        { duration: '10s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(99)<3000'],
        http_req_failed: ['rate<0.1'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

export default function() {
    const res = http.get(`${BASE_URL}/api/beneficiaries?page=1&per_page=20`);
    check(res, {
        'status is 200': (r) => r.status === 200,
    });
}
EOF

run_test "spike-test" "$RESULTS_DIR/spike-test.js" "Testing system response to sudden traffic spikes"

# 5. Soak Test (optional - takes a long time)
if [ "$RUN_SOAK_TEST" = "true" ]; then
    echo -e "${YELLOW}5. SOAK TEST${NC}"
    echo "Testing system stability over extended period"
    cat > "$RESULTS_DIR/soak-test.js" << 'EOF'
import http from 'k6/http';
import { check } from 'k6';

export const options = {
    stages: [
        { duration: '5m', target: 100 },
        { duration: '2h', target: 100 },
        { duration: '5m', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(99)<2000'],
        http_req_failed: ['rate<0.01'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

export default function() {
    const res = http.get(`${BASE_URL}/api/dashboard/stats`);
    check(res, {
        'status is 200': (r) => r.status === 200,
    });
}
EOF
    
    run_test "soak-test" "$RESULTS_DIR/soak-test.js" "Testing for memory leaks and degradation over time"
fi

# 6. API Endpoint Test
echo -e "${YELLOW}6. API ENDPOINT TEST${NC}"
echo "Testing individual API endpoints"
cat > "$RESULTS_DIR/api-test.js" << 'EOF'
import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
    vus: 50,
    duration: '5m',
    thresholds: {
        'http_req_duration{endpoint:login}': ['p(95)<500'],
        'http_req_duration{endpoint:beneficiaries}': ['p(95)<800'],
        'http_req_duration{endpoint:programs}': ['p(95)<1000'],
        'http_req_duration{endpoint:documents}': ['p(95)<1200'],
    },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

export default function() {
    let token;
    
    group('Login', () => {
        const res = http.post(`${BASE_URL}/api/auth/login`, 
            JSON.stringify({ email: 'test@bdc.com', password: 'Test123!' }), 
            { headers: { 'Content-Type': 'application/json' }, tags: { endpoint: 'login' } }
        );
        check(res, { 'login successful': (r) => r.status === 200 });
        if (res.status === 200) token = res.json('token');
    });
    
    if (!token) return;
    
    const headers = { 'Authorization': `Bearer ${token}` };
    
    group('API Endpoints', () => {
        const endpoints = [
            { name: 'beneficiaries', url: '/api/beneficiaries' },
            { name: 'programs', url: '/api/programs' },
            { name: 'documents', url: '/api/documents' },
        ];
        
        endpoints.forEach(endpoint => {
            const res = http.get(`${BASE_URL}${endpoint.url}`, 
                { headers, tags: { endpoint: endpoint.name } }
            );
            check(res, { [`${endpoint.name} response OK`]: (r) => r.status === 200 });
        });
    });
}
EOF

run_test "api-test" "$RESULTS_DIR/api-test.js" "Testing individual API endpoint performance"

# Generate summary report
echo -e "${YELLOW}Generating Summary Report...${NC}"
cat > "$RESULTS_DIR/summary.md" << EOF
# BDC Performance Test Results
Date: $(date)
Base URL: $BASE_URL

## Test Results Summary

### 1. Smoke Test
Basic connectivity and response verification
- Duration: 1 minute
- Virtual Users: 1
- Target: Verify system is operational

### 2. Load Test
Normal expected load simulation
- Duration: ~26 minutes
- Virtual Users: Ramp up to 200
- Target: Test normal operating conditions

### 3. Stress Test
System under stress conditions
- Duration: ~44 minutes
- Virtual Users: Ramp up to 1000
- Target: Find system breaking point

### 4. Spike Test
Sudden traffic spike handling
- Duration: ~10 minutes
- Virtual Users: Spike from 100 to 500
- Target: Test elasticity and recovery

### 5. API Endpoint Test
Individual endpoint performance
- Duration: 5 minutes
- Virtual Users: 50 concurrent
- Target: Baseline endpoint performance

## Key Metrics
- Response Time (p95): Check individual test results
- Error Rate: Check individual test results
- Throughput: Check individual test results

## Recommendations
1. Review any failed thresholds in test results
2. Investigate endpoints with high response times
3. Check for memory leaks if soak test was run
4. Monitor database connection pool usage
5. Review error logs for any issues

EOF

# Generate comparison chart (if multiple test runs exist)
if command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Generating comparison charts...${NC}"
    python3 - << 'EOF' > "$RESULTS_DIR/generate_charts.py"
import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

# Read test results and create comparison charts
results_dir = os.environ.get('RESULTS_DIR', '.')

def load_summary(filename):
    try:
        with open(os.path.join(results_dir, filename)) as f:
            return json.load(f)
    except:
        return None

# Load test summaries
tests = ['smoke-test', 'load-test', 'stress-test', 'spike-test', 'api-test']
summaries = {}

for test in tests:
    summary = load_summary(f'{test}_summary.json')
    if summary:
        summaries[test] = summary

# Create charts
if summaries:
    # Response time comparison
    plt.figure(figsize=(10, 6))
    test_names = []
    p95_values = []
    
    for test, data in summaries.items():
        if 'metrics' in data and 'http_req_duration' in data['metrics']:
            test_names.append(test)
            p95_values.append(data['metrics']['http_req_duration']['p(95)'])
    
    plt.bar(test_names, p95_values)
    plt.title('Response Time Comparison (p95)')
    plt.xlabel('Test Type')
    plt.ylabel('Response Time (ms)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, 'response_time_comparison.png'))
    plt.close()
    
    print(f"Charts generated in {results_dir}")
EOF
    
    RESULTS_DIR="$RESULTS_DIR" python3 "$RESULTS_DIR/generate_charts.py" || true
fi

# Create index.html for easy viewing
cat > "$RESULTS_DIR/index.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>BDC Performance Test Results</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .test-section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; }
        .success { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>BDC Performance Test Results</h1>
    <p>Test execution completed at: <script>document.write(new Date().toLocaleString());</script></p>
    
    <h2>Test Reports</h2>
    <ul>
        <li><a href="smoke-test_report.html">Smoke Test Report</a></li>
        <li><a href="load-test_report.html">Load Test Report</a></li>
        <li><a href="stress-test_report.html">Stress Test Report</a></li>
        <li><a href="spike-test_report.html">Spike Test Report</a></li>
        <li><a href="api-test_report.html">API Test Report</a></li>
    </ul>
    
    <h2>Summary</h2>
    <iframe src="summary.md" width="100%" height="600px"></iframe>
    
    <h2>Charts</h2>
    <img src="response_time_comparison.png" alt="Response Time Comparison" style="max-width: 100%;">
</body>
</html>
EOF

echo ""
echo -e "${GREEN}Performance testing completed!${NC}"
echo "Results saved to: $RESULTS_DIR"
echo "Open $RESULTS_DIR/index.html to view the results"

# Open results in browser (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "$RESULTS_DIR/index.html"
fi