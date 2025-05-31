import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const successRate = new Rate('success');

// Stress test configuration - push system to its limits
export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up to 100 users
    { duration: '5m', target: 100 },   // Stay at 100 users
    { duration: '2m', target: 300 },   // Ramp up to 300 users
    { duration: '5m', target: 300 },   // Stay at 300 users
    { duration: '2m', target: 500 },   // Ramp up to 500 users
    { duration: '5m', target: 500 },   // Stay at 500 users
    { duration: '2m', target: 800 },   // Ramp up to 800 users
    { duration: '5m', target: 800 },   // Stay at 800 users
    { duration: '2m', target: 1000 },  // Ramp up to 1000 users
    { duration: '5m', target: 1000 },  // Stay at 1000 users
    { duration: '10m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(99)<5000'], // 99% of requests must complete below 5s
    http_req_failed: ['rate<0.1'],     // Error rate must be below 10%
    errors: ['rate<0.1'],              // Custom error rate below 10%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

export default function() {
  // Simulate different types of load
  const scenario = Math.random();
  
  if (scenario < 0.4) {
    // 40% - Heavy read operations
    heavyReadScenario();
  } else if (scenario < 0.7) {
    // 30% - Write operations
    writeScenario();
  } else if (scenario < 0.9) {
    // 20% - Mixed operations
    mixedScenario();
  } else {
    // 10% - API abuse scenario
    abuseScenario();
  }
}

function heavyReadScenario() {
  // Simulate users browsing through multiple pages rapidly
  const endpoints = [
    '/api/beneficiaries?page=1&per_page=50',
    '/api/beneficiaries?page=2&per_page=50',
    '/api/beneficiaries?page=3&per_page=50',
    '/api/programs?page=1&per_page=100',
    '/api/documents?page=1&per_page=100',
    '/api/dashboard/stats',
    '/api/analytics/overview',
  ];

  // Login first
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    email: 'loadtest@bdc.com',
    password: 'LoadTest123!'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });

  if (loginRes.status !== 200) {
    errorRate.add(1);
    return;
  }

  const token = loginRes.json('token');
  const headers = { 'Authorization': `Bearer ${token}` };

  // Rapid fire requests
  endpoints.forEach(endpoint => {
    const res = http.get(`${BASE_URL}${endpoint}`, { headers });
    
    check(res, {
      'status is 200': (r) => r.status === 200,
    }) ? successRate.add(1) : errorRate.add(1);
    
    sleep(0.1); // Very short delay between requests
  });
}

function writeScenario() {
  // Simulate heavy write operations
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    email: 'trainer@bdc.com',
    password: 'Trainer123!'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });

  if (loginRes.status !== 200) {
    errorRate.add(1);
    return;
  }

  const token = loginRes.json('token');
  const headers = { 
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  // Create multiple beneficiaries
  for (let i = 0; i < 5; i++) {
    const payload = JSON.stringify({
      first_name: `Stress${Math.random().toString(36).substring(7)}`,
      last_name: 'Test',
      email: `stress${Date.now()}${i}@test.com`,
      phone: '+1234567890',
      date_of_birth: '1990-01-01',
      address: '123 Stress Test St',
      city: 'Load City',
      country: 'Test Country',
      status: 'active'
    });

    const res = http.post(`${BASE_URL}/api/beneficiaries`, payload, { headers });
    
    check(res, {
      'beneficiary created': (r) => r.status === 201,
    }) ? successRate.add(1) : errorRate.add(1);
    
    sleep(0.5);
  }
}

function mixedScenario() {
  // Simulate realistic mixed usage
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    email: 'admin@bdc.com',
    password: 'Admin123!'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });

  if (loginRes.status !== 200) {
    errorRate.add(1);
    return;
  }

  const token = loginRes.json('token');
  const headers = { 'Authorization': `Bearer ${token}` };

  // Dashboard
  const dashRes = http.get(`${BASE_URL}/api/dashboard/stats`, { headers });
  check(dashRes, { 'dashboard loaded': (r) => r.status === 200 }) 
    ? successRate.add(1) : errorRate.add(1);

  sleep(1);

  // Search
  const searchRes = http.get(`${BASE_URL}/api/beneficiaries/search?q=test`, { headers });
  check(searchRes, { 'search completed': (r) => r.status === 200 }) 
    ? successRate.add(1) : errorRate.add(1);

  sleep(0.5);

  // Update profile
  const updateRes = http.patch(`${BASE_URL}/api/users/profile`, 
    JSON.stringify({ bio: 'Stress test update' }), 
    { headers: { ...headers, 'Content-Type': 'application/json' } }
  );
  check(updateRes, { 'profile updated': (r) => r.status === 200 }) 
    ? successRate.add(1) : errorRate.add(1);
}

function abuseScenario() {
  // Simulate potential abuse patterns
  
  // Rapid login attempts
  for (let i = 0; i < 10; i++) {
    const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
      email: `abuse${i}@test.com`,
      password: 'wrongpassword'
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
    
    // We expect these to fail or be rate limited
    if (res.status === 429) {
      successRate.add(1); // Rate limiting is working
    } else {
      errorRate.add(1);
    }
    
    sleep(0.1);
  }
  
  // Large payload attempts
  const largePayload = JSON.stringify({
    data: 'x'.repeat(1000000) // 1MB of data
  });
  
  const res = http.post(`${BASE_URL}/api/test/large`, largePayload, {
    headers: { 'Content-Type': 'application/json' }
  });
  
  // Should be rejected
  if (res.status === 413) {
    successRate.add(1); // Payload size limit working
  } else {
    errorRate.add(1);
  }
}