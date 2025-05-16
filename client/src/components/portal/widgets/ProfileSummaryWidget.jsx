import { useNavigate } from 'react-router-dom';
import { User, Mail, Award, Calendar, Clock, Target, Loader } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

/**
 * Displays a summary of the student's profile information
 */
const ProfileSummaryWidget = ({ data, isLoading, error }) => {
  const navigate = useNavigate();
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  if (isLoading) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-center items-center">
          <Loader className="h-8 w-8 text-primary animate-spin" />
        </div>
      </Card>
    );
  }
  
  if (error) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 text-center text-red-500">
          Failed to load profile data
        </div>
      </Card>
    );
  }
  
  if (!data) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 text-center text-gray-500">
          No profile data available
        </div>
      </Card>
    );
  }
  
  return (
    <Card className="overflow-hidden h-full">
      <div className="p-6 flex items-center border-b">
        <div className="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mr-4">
          {data.avatar ? (
            <img 
              src={data.avatar} 
              alt={data.name}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            <User className="w-7 h-7 text-primary" />
          )}
        </div>
        <div>
          <h2 className="font-medium">{data.name}</h2>
          <p className="text-sm text-gray-500">{data.email}</p>
        </div>
      </div>
      
      <div className="p-4 divide-y">
        <div className="py-2 flex justify-between">
          <span className="text-sm text-gray-500">Program</span>
          <span className="text-sm font-medium">{data.program?.name}</span>
        </div>
        <div className="py-2 flex justify-between">
          <span className="text-sm text-gray-500">Start Date</span>
          <span className="text-sm font-medium">
            {formatDate(data.program?.startDate)}
          </span>
        </div>
        <div className="py-2 flex justify-between">
          <span className="text-sm text-gray-500">Expected Completion</span>
          <span className="text-sm font-medium">
            {formatDate(data.program?.expectedEndDate)}
          </span>
        </div>
        <div className="py-2 flex justify-between">
          <span className="text-sm text-gray-500">Primary Trainer</span>
          <span className="text-sm font-medium">{data.primaryTrainer?.name || 'N/A'}</span>
        </div>
      </div>
      
      <div className="bg-gray-50 p-4 text-center">
        <Button
          variant="link"
          onClick={() => navigate('/portal/profile')}
        >
          View Full Profile
        </Button>
      </div>
    </Card>
  );
};

export default ProfileSummaryWidget;