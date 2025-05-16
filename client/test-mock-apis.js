// Test mock APIs
import axios from 'axios';

const baseURL = 'http://localhost:5001';

async function testMockAPIs() {
  try {
    console.log('Testing portal dashboard...');
    const dashboardResponse = await axios.get(`${baseURL}/api/portal/dashboard`);
    console.log('Portal dashboard:', dashboardResponse.status === 200 ? 'SUCCESS' : 'FAILED');
  } catch (error) {
    console.error('Portal dashboard error:', error.message);
  }

  try {
    console.log('\nTesting portal courses...');
    const coursesResponse = await axios.get(`${baseURL}/api/portal/courses`);
    console.log('Portal courses:', coursesResponse.status === 200 ? 'SUCCESS' : 'FAILED');
  } catch (error) {
    console.error('Portal courses error:', error.message);
  }

  try {
    console.log('\nTesting portal assessments...');
    const assessmentsResponse = await axios.get(`${baseURL}/api/portal/assessments`);
    console.log('Portal assessments:', assessmentsResponse.status === 200 ? 'SUCCESS' : 'FAILED');
  } catch (error) {
    console.error('Portal assessments error:', error.message);
  }

  try {
    console.log('\nTesting trainer assessments...');
    const trainerAssessmentsResponse = await axios.get(`${baseURL}/api/assessment/templates`);
    console.log('Trainer assessments:', trainerAssessmentsResponse.status === 200 ? 'SUCCESS' : 'FAILED');
  } catch (error) {
    console.error('Trainer assessments error:', error.message);
  }
}

testMockAPIs();