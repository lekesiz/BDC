import React from 'react';

const Diagnostic = () => {
  return (
    <div style={{ padding: '20px' }}>
      <h1>Diagnostic Page</h1>
      <p>If you see this, React is working properly.</p>
      <h2>Environment:</h2>
      <ul>
        <li>Node Environment: {process.env.NODE_ENV}</li>
        <li>API URL: {import.meta.env.VITE_API_URL || 'Not configured'}</li>
      </ul>
    </div>
  );
};

export default Diagnostic;