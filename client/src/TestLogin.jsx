import React, { useState } from 'react';
import axios from 'axios';

function TestLogin() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const testDirectLogin = async () => {
    try {
      setError(null);
      setResult(null);
      
      const response = await axios.post('http://localhost:5001/api/auth/login', {
        email: 'admin@bdc.com',
        password: 'Admin123!',
        remember_me: false
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
        withCredentials: true
      });
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data || err.message);
    }
  };

  const testApiLogin = async () => {
    try {
      setError(null);
      setResult(null);
      
      // Use the configured API instance
      const { default: api } = await import('@/lib/api');
      
      const response = await api.post('/api/auth/login', {
        email: 'admin@bdc.com',
        password: 'Admin123!',
        remember_me: false
      });
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data || err.message);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Test Login</h1>
      
      <button onClick={testDirectLogin} style={{ marginRight: '10px' }}>
        Test Direct Login
      </button>
      
      <button onClick={testApiLogin}>
        Test API Login
      </button>
      
      {result && (
        <div>
          <h3>Success:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
      
      {error && (
        <div>
          <h3>Error:</h3>
          <pre>{JSON.stringify(error, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default TestLogin;