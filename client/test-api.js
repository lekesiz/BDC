// Simple test script to check if API is working
import axios from 'axios';

const baseURL = 'http://localhost:5001';

async function testAPI() {
  try {
    // Test backend
    console.log('Testing backend API...');
    const backendResponse = await axios.get(`${baseURL}/api/health`);
    console.log('Backend response:', backendResponse.data);
  } catch (error) {
    console.error('Backend error:', error.message);
  }

  try {
    // Test frontend proxy
    console.log('\nTesting frontend proxy...');
    const frontendResponse = await axios.get('http://localhost:5174/api/health');
    console.log('Frontend proxy response:', frontendResponse.data);
  } catch (error) {
    console.error('Frontend proxy error:', error.message);
  }
}

testAPI();