import { useNavigate } from 'react-router-dom';
import { Award, Medal, Star, CheckCircle, Loader } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
/**
 * Displays the student's recent achievements, badges, and certificates
 */
const AchievementsWidget = ({ data, isLoading, error }) => {
  const navigate = useNavigate();
  // Format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  // Get icon based on achievement type
  const getAchievementIcon = (type, className = "h-5 w-5") => {
    switch (type) {
      case 'badge':
        return <Medal className={className} />;
      case 'certificate':
        return <Award className={className} />;
      case 'completion':
        return <CheckCircle className={className} />;
      default:
        return <Star className={className} />;
    }
  };
  // Get color class based on achievement type
  const getAchievementColorClass = (type) => {
    switch (type) {
      case 'badge':
        return 'bg-purple-50 text-purple-500';
      case 'certificate':
        return 'bg-green-50 text-green-500';
      case 'completion':
        return 'bg-blue-50 text-blue-500';
      default:
        return 'bg-gray-50 text-gray-500';
    }
  };
  if (isLoading) {
    return (
      <Card className="overflow-hidden h-full">
        <div className="p-6 flex justify-between items-center border-b">
          <h2 className="text-lg font-medium">My Achievements</h2>
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
          <h2 className="text-lg font-medium">My Achievements</h2>
        </div>
        <div className="p-6 text-center text-red-500">
          Failed to load achievements
        </div>
      </Card>
    );
  }
  // Get achievements summary stats
  const highlightMetrics = data?.highlights || [];
  // Get recent achievements to display (limit to 3)
  const recentAchievements = data?.recentAchievements?.slice(0, 3) || [];
  return (
    <Card className="overflow-hidden h-full">
      <div className="p-6 flex justify-between items-center border-b">
        <h2 className="text-lg font-medium">My Achievements</h2>
        <Button 
          variant="outline" 
          size="sm"
          onClick={() => navigate('/portal/achievements')}
        >
          View All
        </Button>
      </div>
      <div className="p-4">
        {/* Achievement stats */}
        {highlightMetrics.length > 0 && (
          <div className="grid grid-cols-2 gap-3 mb-4">
            {highlightMetrics.map(metric => (
              <div 
                key={metric.id} 
                className="bg-gray-50 rounded-lg p-3 text-center flex flex-col items-center"
              >
                <div className={`p-2 rounded-full mb-1 ${getAchievementColorClass(metric.type)}`}>
                  {getAchievementIcon(metric.type, "h-4 w-4")}
                </div>
                <div className="text-xl font-semibold">{metric.value}</div>
                <div className="text-xs text-gray-500">{metric.label}</div>
              </div>
            ))}
          </div>
        )}
        {/* Recent achievements */}
        <h3 className="text-sm font-medium text-gray-500 mb-3">Recently Earned</h3>
        {recentAchievements.length > 0 ? (
          <div className="space-y-3">
            {recentAchievements.map(achievement => (
              <div key={achievement.id} className="border rounded-lg p-3">
                <div className="flex items-center mb-1">
                  <div className={`p-2 rounded-full mr-2 ${getAchievementColorClass(achievement.type)}`}>
                    {getAchievementIcon(achievement.type, "h-4 w-4")}
                  </div>
                  <div>
                    <h4 className="font-medium text-sm">{achievement.name}</h4>
                    <p className="text-xs text-gray-500">
                      Earned on {formatDate(achievement.dateEarned)}
                    </p>
                  </div>
                </div>
                <p className="text-xs text-gray-600 pl-10">{achievement.description}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-6">
            <Award className="h-12 w-12 text-gray-300 mx-auto mb-2" />
            <p className="text-gray-500">No achievements yet</p>
            <p className="text-xs text-gray-400">Complete modules to earn achievements</p>
          </div>
        )}
      </div>
      <div className="bg-gray-50 p-4 text-center border-t">
        <Button
          variant="link"
          onClick={() => navigate('/portal/achievements')}
        >
          View All Achievements
        </Button>
      </div>
    </Card>
  );
};
export default AchievementsWidget;