import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const loginDuration = new Trend('login_duration');
const apiErrors = new Rate('api_errors');
const beneficiaryListDuration = new Trend('beneficiary_list_duration');
const beneficiaryCreateDuration = new Trend('beneficiary_create_duration');
const documentUploadDuration = new Trend('document_upload_duration');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '5m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000', 'p(99)<2000'], // 95% of requests under 1s, 99% under 2s
    http_req_failed: ['rate<0.05'],                  // Error rate under 5%
    api_errors: ['rate<0.05'],                        // Custom error rate under 5%
    login_duration: ['p(95)<500'],                    // 95% of logins under 500ms
    beneficiary_list_duration: ['p(95)<800'],         // 95% of list requests under 800ms
    beneficiary_create_duration: ['p(95)<1000'],      // 95% of creates under 1s
    document_upload_duration: ['p(95)<2000'],         // 95% of uploads under 2s
  },
  ext: {
    loadimpact: {
      projectID: 3478725,
      name: "BDC Load Test"
    }
  }
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const USERS = [
  { email: 'admin@bdc.com', password: 'Admin123!', role: 'admin' },
  { email: 'trainer@bdc.com', password: 'Trainer123!', role: 'trainer' },
  { email: 'student@bdc.com', password: 'Student123!', role: 'student' },
];

// Helper function to get random user
function getRandomUser() {
  return USERS[Math.floor(Math.random() * USERS.length)];
}

// Helper function to handle API errors
function handleError(response, operation) {
  if (response.status >= 400) {
    apiErrors.add(1);
    console.error(`${operation} failed: ${response.status} - ${response.body}`);
  } else {
    apiErrors.add(0);
  }
}

export function setup() {
  // Setup code - create test data if needed
  console.log('Setting up test data...');
  
  // Login as admin to create test data
  const loginRes = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    email: 'admin@bdc.com',
    password: 'Admin123!'
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (loginRes.status !== 200) {
    throw new Error('Admin login failed during setup');
  }
  
  const adminToken = loginRes.json('token');
  
  return {
    adminToken,
    testData: {
      programIds: [],
      beneficiaryIds: []
    }
  };
}

export default function(data) {
  const user = getRandomUser();
  let authToken;

  group('Authentication Flow', () => {
    // Login
    const loginPayload = JSON.stringify({
      email: user.email,
      password: user.password,
    });

    const loginStart = new Date();
    const loginRes = http.post(`${BASE_URL}/api/auth/login`, loginPayload, {
      headers: { 'Content-Type': 'application/json' },
      tags: { name: 'login' },
    });
    loginDuration.add(new Date() - loginStart);

    check(loginRes, {
      'login successful': (r) => r.status === 200,
      'token received': (r) => r.json('token') !== undefined,
    });

    handleError(loginRes, 'Login');

    if (loginRes.status === 200) {
      authToken = loginRes.json('token');
    } else {
      console.error(`Login failed for ${user.email}`);
      return;
    }
  });

  // Only continue if we have a valid token
  if (!authToken) return;

  const authHeaders = {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json',
  };

  sleep(1); // Think time

  group('Dashboard Access', () => {
    const dashboardRes = http.get(`${BASE_URL}/api/dashboard/stats`, {
      headers: authHeaders,
      tags: { name: 'dashboard' },
    });

    check(dashboardRes, {
      'dashboard loaded': (r) => r.status === 200,
      'stats received': (r) => r.json('totalBeneficiaries') !== undefined,
    });

    handleError(dashboardRes, 'Dashboard');
  });

  sleep(2); // Think time

  group('Beneficiary Operations', () => {
    // List beneficiaries
    const listStart = new Date();
    const listRes = http.get(`${BASE_URL}/api/beneficiaries?page=1&per_page=20`, {
      headers: authHeaders,
      tags: { name: 'beneficiaries-list' },
    });
    beneficiaryListDuration.add(new Date() - listStart);

    check(listRes, {
      'beneficiaries listed': (r) => r.status === 200,
      'has beneficiaries': (r) => r.json('beneficiaries') !== undefined,
    });

    handleError(listRes, 'List Beneficiaries');

    // Create beneficiary (only for trainers and admins)
    if (user.role !== 'student') {
      const createPayload = JSON.stringify({
        first_name: `Test${Math.random().toString(36).substring(7)}`,
        last_name: 'User',
        email: `test${Date.now()}@example.com`,
        phone: '+1234567890',
        date_of_birth: '1990-01-01',
        address: '123 Test St',
        city: 'Test City',
        country: 'Test Country',
        emergency_contact: 'Emergency Contact',
        medical_conditions: 'None',
        status: 'active'
      });

      const createStart = new Date();
      const createRes = http.post(`${BASE_URL}/api/beneficiaries`, createPayload, {
        headers: authHeaders,
        tags: { name: 'beneficiary-create' },
      });
      beneficiaryCreateDuration.add(new Date() - createStart);

      check(createRes, {
        'beneficiary created': (r) => r.status === 201,
        'has beneficiary id': (r) => r.json('id') !== undefined,
      });

      handleError(createRes, 'Create Beneficiary');
    }
  });

  sleep(2); // Think time

  group('Program Access', () => {
    const programsRes = http.get(`${BASE_URL}/api/programs?page=1&per_page=10`, {
      headers: authHeaders,
      tags: { name: 'programs-list' },
    });

    check(programsRes, {
      'programs listed': (r) => r.status === 200,
      'has programs': (r) => r.json('programs') !== undefined,
    });

    handleError(programsRes, 'List Programs');
  });

  sleep(1); // Think time

  group('Document Operations', () => {
    // List documents
    const docsRes = http.get(`${BASE_URL}/api/documents?page=1&per_page=20`, {
      headers: authHeaders,
      tags: { name: 'documents-list' },
    });

    check(docsRes, {
      'documents listed': (r) => r.status === 200,
      'has documents': (r) => r.json('documents') !== undefined,
    });

    handleError(docsRes, 'List Documents');

    // Simulate document upload (multipart form data)
    if (user.role !== 'student' && Math.random() < 0.1) { // Only 10% of non-students upload
      const uploadStart = new Date();
      
      const boundary = '----WebKitFormBoundary' + Math.random().toString(36).substring(2);
      const formData = `------${boundary}\r\n` +
        `Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n` +
        `Content-Type: application/pdf\r\n\r\n` +
        `%PDF-1.4 test content\r\n` +
        `------${boundary}\r\n` +
        `Content-Disposition: form-data; name="title"\r\n\r\n` +
        `Test Document ${Date.now()}\r\n` +
        `------${boundary}\r\n` +
        `Content-Disposition: form-data; name="description"\r\n\r\n` +
        `Test document uploaded during load test\r\n` +
        `------${boundary}--\r\n`;

      const uploadRes = http.post(`${BASE_URL}/api/documents/upload`, formData, {
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': `multipart/form-data; boundary=----${boundary}`,
        },
        tags: { name: 'document-upload' },
      });
      
      documentUploadDuration.add(new Date() - uploadStart);

      check(uploadRes, {
        'document uploaded': (r) => r.status === 201,
        'has document id': (r) => r.json('id') !== undefined,
      });

      handleError(uploadRes, 'Upload Document');
    }
  });

  sleep(3); // Think time

  group('Search Operations', () => {
    // Search beneficiaries
    const searchRes = http.get(`${BASE_URL}/api/beneficiaries/search?q=test`, {
      headers: authHeaders,
      tags: { name: 'search' },
    });

    check(searchRes, {
      'search completed': (r) => r.status === 200,
    });

    handleError(searchRes, 'Search');
  });

  sleep(2); // Think time

  group('Notifications', () => {
    const notificationsRes = http.get(`${BASE_URL}/api/notifications/unread`, {
      headers: authHeaders,
      tags: { name: 'notifications' },
    });

    check(notificationsRes, {
      'notifications loaded': (r) => r.status === 200,
      'has count': (r) => r.json('count') !== undefined,
    });

    handleError(notificationsRes, 'Notifications');
  });

  sleep(1); // Think time

  // Logout
  group('Logout', () => {
    const logoutRes = http.post(`${BASE_URL}/api/auth/logout`, null, {
      headers: authHeaders,
      tags: { name: 'logout' },
    });

    check(logoutRes, {
      'logout successful': (r) => r.status === 200,
    });

    handleError(logoutRes, 'Logout');
  });
}

export function teardown(data) {
  // Cleanup test data if needed
  console.log('Cleaning up test data...');
}