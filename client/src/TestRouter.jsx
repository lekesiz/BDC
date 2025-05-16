import React from 'react';
import { BrowserRouter } from 'react-router-dom';

function TestRouter() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true
      }}
    >
      <div>
        <h1>Router Test - The warnings should be gone!</h1>
      </div>
    </BrowserRouter>
  );
}

export default TestRouter;