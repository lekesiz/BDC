import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

const TestCreationPageSimple = () => {
  const navigate = useNavigate();

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/evaluations')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Evaluations
        </Button>
        
        <h1 className="text-3xl font-bold">Create New Test</h1>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Test Details</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Test creation form will go here</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default TestCreationPageSimple;