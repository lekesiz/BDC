import React, { useEffect } from 'react';
import api from '@/lib/api';

function TestAPI() {
  useEffect(() => {
    console.log('API Base URL:', api.defaults.baseURL);
    console.log('Environment variable:', import.meta.env.VITE_API_URL);
  }, []);

  const testLogin = async () => {
    try {
      const response = await api.post('/api/auth/login', {
        email: 'admin@bdc.com',
        password: 'Admin123!'
      });
      console.log('Login successful:', response.data);
    } catch (error) {
      console.error('Login error:', error);
    }
  };

  return (
    <div>
      <h1>API Test</h1>
      <button onClick={testLogin}>Test Login</button>
    </div>
  );
}

export default TestAPI;