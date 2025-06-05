import React from 'react';
import ApiDebugPanel from '@/components/debug/ApiDebugPanel';
const DebugPage = () => {
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">System Debug Panel</h1>
      <ApiDebugPanel />
    </div>
  );
};
export default DebugPage;