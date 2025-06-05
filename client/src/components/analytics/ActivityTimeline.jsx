import React from 'react';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';
import { 
  Users, 
  Calendar, 
  FileText, 
  Award, 
  Clipboard,
  BarChart
} from 'lucide-react';
/**
 * ActivityTimeline component displays a timeline of recent activities in the system
 * @param {Object} props - Component props
 * @param {Array} props.data - The activity data to display
 */
export const ActivityTimeline = ({ data = [] }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <p>No activity data available</p>
      </div>
    );
  }
  // Get icon based on activity type
  const getActivityIcon = (type) => {
    switch (type) {
      case 'beneficiary':
        return <Users className="w-5 h-5 text-blue-500" />;
      case 'appointment':
        return <Calendar className="w-5 h-5 text-green-500" />;
      case 'document':
        return <FileText className="w-5 h-5 text-purple-500" />;
      case 'evaluation':
        return <Clipboard className="w-5 h-5 text-red-500" />;
      case 'achievement':
        return <Award className="w-5 h-5 text-yellow-500" />;
      case 'report':
        return <BarChart className="w-5 h-5 text-indigo-500" />;
      default:
        return <Calendar className="w-5 h-5 text-gray-500" />;
    }
  };
  // Format activity date
  const formatActivityDate = (dateString) => {
    const date = new Date(dateString);
    return format(date, 'dd MMM yyyy, HH:mm', { locale: tr });
  };
  return (
    <div className="flow-root max-h-80 overflow-y-auto pr-2">
      <ul className="-mb-8">
        {data.map((activity, index) => (
          <li key={activity.id}>
            <div className="relative pb-8">
              {index !== data.length - 1 && (
                <span
                  className="absolute top-5 left-5 -ml-px h-full w-0.5 bg-gray-200"
                  aria-hidden="true"
                />
              )}
              <div className="relative flex items-start space-x-3">
                <div className="relative">
                  <div className="h-10 w-10 rounded-full bg-gray-100 flex items-center justify-center ring-8 ring-white">
                    {getActivityIcon(activity.type)}
                  </div>
                </div>
                <div className="min-w-0 flex-1">
                  <div>
                    <div className="text-sm">
                      <span className="font-medium text-gray-900">{activity.actor}</span>
                    </div>
                    <p className="mt-0.5 text-sm text-gray-500">
                      {formatActivityDate(activity.date)}
                    </p>
                  </div>
                  <div className="mt-2 text-sm text-gray-700">
                    <p>{activity.description}</p>
                  </div>
                  {activity.link && (
                    <div className="mt-2">
                      <a
                        href={activity.link}
                        className="text-sm text-primary hover:underline"
                      >
                        View details
                      </a>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};
export default ActivityTimeline;