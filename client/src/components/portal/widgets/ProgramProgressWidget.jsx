import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, CheckCircle, ArrowRight, Loader } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

/**
 * Displays the student's progress in their program
 */
const ProgramProgressWidget = ({ data, isLoading, error }) => {
  const navigate = useNavigate();
  
  if (isLoading) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">My Program Progress</h2>
        </div>
        <div className="flex justify-center items-center p-12">
          <Loader className="h-8 w-8 text-primary animate-spin" />
        </div>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">My Program Progress</h2>
        </div>
        <div className="p-6 text-center text-red-500">
          Failed to load program progress
        </div>
      </Card>
    );
  }
  
  return (
    <Card className="overflow-hidden h-full">
      <div className="p-6 flex justify-between items-center border-b">
        <h2 className="text-lg font-medium">My Program Progress</h2>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate('/portal/progress')}
        >
          View Details
        </Button>
      </div>
      
      <div className="p-6">
        <div className="flex items-center mb-4">
          <div className="mr-3">
            <BookOpen className="h-8 w-8 text-primary" />
          </div>
          <div className="flex-1">
            <div className="flex justify-between mb-1">
              <h3 className="font-medium">{data?.program?.name}</h3>
              <span className="text-sm text-gray-500">
                {data?.program?.progress || 0}% Complete
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div 
                className="bg-primary h-2.5 rounded-full" 
                style={{ width: `${data?.program?.progress || 0}%` }}
              ></div>
            </div>
          </div>
        </div>
        
        <div className="space-y-4 mt-6">
          {data?.modules?.map((module, index) => (
            <div key={module.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center mr-3 ${
                    module.status === 'completed' 
                      ? 'bg-green-100 text-green-600' 
                      : module.status === 'in_progress'
                      ? 'bg-blue-100 text-blue-600'
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {module.status === 'completed' ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : (
                      <span>{index + 1}</span>
                    )}
                  </div>
                  <h4 className="font-medium">{module.name}</h4>
                </div>
                <span className="text-sm text-gray-500">
                  {module.completion}% Complete
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    module.status === 'completed' 
                      ? 'bg-green-500' 
                      : module.status === 'in_progress'
                      ? 'bg-blue-500'
                      : 'bg-gray-400'
                  }`}
                  style={{ width: `${module.completion}%` }}
                ></div>
              </div>
              
              <Button
                variant="link"
                size="sm"
                className="mt-2 p-0 h-auto"
                onClick={() => navigate(`/portal/modules/${module.id}`)}
              >
                {module.status === 'completed' 
                  ? 'Review Module' 
                  : module.status === 'in_progress'
                  ? 'Continue Module'
                  : 'Start Module'
                }
              </Button>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
};

export default ProgramProgressWidget;