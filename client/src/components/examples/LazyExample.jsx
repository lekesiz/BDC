import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
const LazyExample = () => {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Lazy Loaded Component</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-gray-600">
          This component was loaded lazily using React.lazy and Suspense.
        </p>
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <code className="text-sm">const LazyComponent = lazy(() =&gt; import('./LazyExample'));</code>
        </div>
      </CardContent>
    </Card>
  );
};
export default LazyExample;