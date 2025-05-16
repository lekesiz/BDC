import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart, 
  PieChart, 
  CheckCircle, 
  Clock, 
  CalendarCheck, 
  BookOpen,
  Award,
  ArrowRight,
  ChevronRight,
  Download,
  FileText,
  TrendingUp,
  Loader,
  AlertTriangle,
  Star
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';

/**
 * PortalProgressPage shows the student's overall program progress,
 * completion status, and learning journey
 */
const PortalProgressPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [progressData, setProgressData] = useState(null);
  const [selectedModule, setSelectedModule] = useState(null);
  
  // Fetch progress data
  useEffect(() => {
    const fetchProgressData = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/progress');
        setProgressData(response.data);
        
        // Set the first module as selected by default if there are modules
        if (response.data.modules && response.data.modules.length > 0) {
          setSelectedModule(response.data.modules[0].id);
        }
      } catch (error) {
        console.error('Error fetching progress data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load progress data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchProgressData();
  }, [toast]);
  
  // Format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  // Format time duration (minutes to hours and minutes)
  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    
    if (hours === 0) {
      return `${mins} min`;
    } else if (mins === 0) {
      return `${hours} ${hours === 1 ? 'hour' : 'hours'}`;
    } else {
      return `${hours} ${hours === 1 ? 'hour' : 'hours'} ${mins} min`;
    }
  };
  
  // Get the selected module details
  const getSelectedModuleDetails = () => {
    if (!progressData || !selectedModule) return null;
    
    return progressData.modules.find(module => module.id === selectedModule);
  };
  
  // Calculate days remaining in program
  const getDaysRemaining = () => {
    if (!progressData || !progressData.program.expectedEndDate) return 0;
    
    const endDate = new Date(progressData.program.expectedEndDate);
    const today = new Date();
    const diffTime = endDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return diffDays > 0 ? diffDays : 0;
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  
  const selectedModuleDetails = getSelectedModuleDetails();
  const daysRemaining = getDaysRemaining();
  
  return (
    <div className="container mx-auto py-6">
      {/* Page header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-2">My Program Progress</h1>
        <p className="text-gray-600">
          Track your learning journey and progress in the {progressData.program.name} program
        </p>
      </div>
      
      {/* Overview metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Overall progress */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <div className="p-3 rounded-full bg-blue-50 mr-3">
              <BarChart className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Overall Progress</h3>
              <p className="text-2xl font-bold">{progressData.program.progress}%</p>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
            <div 
              className="bg-blue-500 h-2.5 rounded-full" 
              style={{ width: `${progressData.program.progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-sm text-gray-500">
            <span>Started: {formatDate(progressData.program.startDate)}</span>
            <span>Expected End: {formatDate(progressData.program.expectedEndDate)}</span>
          </div>
        </Card>
        
        {/* Modules */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <div className="p-3 rounded-full bg-green-50 mr-3">
              <BookOpen className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Modules</h3>
              <p className="text-2xl font-bold">
                {progressData.moduleStats.completed}/{progressData.moduleStats.total}
              </p>
            </div>
          </div>
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-500">Completed</span>
            <span className="text-sm font-medium">{progressData.moduleStats.completedPercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
            <div 
              className="bg-green-500 h-2.5 rounded-full" 
              style={{ width: `${progressData.moduleStats.completedPercentage}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-sm">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
              <span className="text-gray-500">Completed ({progressData.moduleStats.completed})</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
              <span className="text-gray-500">In Progress ({progressData.moduleStats.inProgress})</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded-full bg-gray-300 mr-1"></div>
              <span className="text-gray-500">Not Started ({progressData.moduleStats.notStarted})</span>
            </div>
          </div>
        </Card>
        
        {/* Estimated completion */}
        <Card className="p-6">
          <div className="flex items-center mb-4">
            <div className="p-3 rounded-full bg-purple-50 mr-3">
              <CalendarCheck className="h-6 w-6 text-purple-500" />
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Time Remaining</h3>
              <p className="text-2xl font-bold">{daysRemaining} days</p>
            </div>
          </div>
          
          <div className="space-y-2 mb-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Time spent:</span>
              <span className="font-medium">{formatDuration(progressData.timeStats.spent)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Estimated total:</span>
              <span className="font-medium">{formatDuration(progressData.timeStats.total)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Remaining:</span>
              <span className="font-medium">{formatDuration(progressData.timeStats.remaining)}</span>
            </div>
          </div>
          
          {progressData.timeStats.onTrack ? (
            <div className="flex items-center text-sm text-green-600 bg-green-50 p-2 rounded">
              <CheckCircle className="h-4 w-4 mr-2" />
              <span>You're on track to complete on time!</span>
            </div>
          ) : (
            <div className="flex items-center text-sm text-yellow-600 bg-yellow-50 p-2 rounded">
              <AlertTriangle className="h-4 w-4 mr-2" />
              <span>
                {progressData.timeStats.behindSchedule
                  ? "You're slightly behind schedule."
                  : "You're ahead of schedule!"
                }
              </span>
            </div>
          )}
        </Card>
      </div>
      
      {/* Recent achievements */}
      {progressData.recentAchievements && progressData.recentAchievements.length > 0 && (
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Recent Achievements</h2>
            <Button 
              variant="link" 
              onClick={() => navigate('/portal/achievements')}
              className="text-sm flex items-center"
            >
              View All
              <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {progressData.recentAchievements.map(achievement => (
              <Card key={achievement.id} className="overflow-hidden">
                <div className={`h-2 ${achievement.type === 'badge' ? 'bg-purple-500' : 'bg-green-500'}`}></div>
                <div className="p-4">
                  <div className="flex items-center mb-3">
                    <div className={`p-2 rounded-full mr-3 ${
                      achievement.type === 'badge' 
                        ? 'bg-purple-50 text-purple-500' 
                        : 'bg-green-50 text-green-500'
                    }`}>
                      {achievement.type === 'badge' ? (
                        <Award className="h-5 w-5" />
                      ) : (
                        <CheckCircle className="h-5 w-5" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-medium">{achievement.name}</h3>
                      <p className="text-xs text-gray-500">
                        {formatDate(achievement.dateEarned)}
                      </p>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">{achievement.description}</p>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
      
      {/* Module progress section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Module Progress</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Module list */}
          <div className="lg:col-span-1">
            <Card className="overflow-hidden">
              <div className="p-4 border-b bg-gray-50">
                <h3 className="font-medium">Modules</h3>
              </div>
              <div className="divide-y max-h-[400px] overflow-auto">
                {progressData.modules.map(module => (
                  <div
                    key={module.id}
                    className={`p-4 cursor-pointer transition-colors ${
                      selectedModule === module.id 
                        ? 'bg-primary/5 border-l-4 border-primary' 
                        : 'hover:bg-gray-50'
                    }`}
                    onClick={() => setSelectedModule(module.id)}
                  >
                    <div className="flex justify-between items-center mb-2">
                      <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full mr-2 ${
                          module.status === 'completed' 
                            ? 'bg-green-500' 
                            : module.status === 'in_progress'
                            ? 'bg-blue-500'
                            : 'bg-gray-300'
                        }`}></div>
                        <h4 className="font-medium truncate pr-4">
                          {module.name}
                        </h4>
                      </div>
                      {selectedModule === module.id && (
                        <ChevronRight className="h-4 w-4 text-primary" />
                      )}
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div 
                        className={`h-1.5 rounded-full ${
                          module.status === 'completed' 
                            ? 'bg-green-500' 
                            : module.status === 'in_progress'
                            ? 'bg-blue-500'
                            : 'bg-gray-300'
                        }`}
                        style={{ width: `${module.progress}%` }}
                      ></div>
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-xs text-gray-500">
                        {module.lessonsCompleted}/{module.totalLessons} lessons
                      </span>
                      <span className="text-xs font-medium">
                        {module.progress}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
          
          {/* Module details */}
          <div className="lg:col-span-3">
            {selectedModuleDetails ? (
              <Card className="overflow-hidden">
                <div className="bg-gray-50 p-6 border-b">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center mb-1">
                        <h3 className="text-lg font-semibold">{selectedModuleDetails.name}</h3>
                        <span className={`ml-3 px-2 py-0.5 text-xs rounded-full ${
                          selectedModuleDetails.status === 'completed' 
                            ? 'bg-green-100 text-green-700' 
                            : selectedModuleDetails.status === 'in_progress'
                            ? 'bg-blue-100 text-blue-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                          {selectedModuleDetails.status === 'completed' 
                            ? 'Completed' 
                            : selectedModuleDetails.status === 'in_progress'
                            ? 'In Progress'
                            : 'Not Started'
                          }
                        </span>
                      </div>
                      <p className="text-gray-600">{selectedModuleDetails.description}</p>
                    </div>
                    <Button
                      onClick={() => navigate(`/portal/modules/${selectedModuleDetails.id}`)}
                      className="shrink-0"
                    >
                      {selectedModuleDetails.status === 'completed' 
                        ? 'Review Module' 
                        : selectedModuleDetails.status === 'in_progress'
                        ? 'Continue Module'
                        : 'Start Module'
                      }
                    </Button>
                  </div>
                </div>
                
                <div className="p-6">
                  {/* Module stats */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm text-gray-500 mb-1">Progress</h4>
                      <div className="flex items-center">
                        <div className="text-2xl font-bold mr-2">{selectedModuleDetails.progress}%</div>
                        <div className="w-full bg-gray-200 rounded-full h-2.5">
                          <div 
                            className={`h-2.5 rounded-full ${
                              selectedModuleDetails.status === 'completed' 
                                ? 'bg-green-500' 
                                : 'bg-blue-500'
                            }`}
                            style={{ width: `${selectedModuleDetails.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm text-gray-500 mb-1">Lessons Completed</h4>
                      <div className="text-2xl font-bold">
                        {selectedModuleDetails.lessonsCompleted}/{selectedModuleDetails.totalLessons}
                      </div>
                    </div>
                    
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="text-sm text-gray-500 mb-1">Time Spent</h4>
                      <div className="text-2xl font-bold">
                        {formatDuration(selectedModuleDetails.timeSpent)}
                      </div>
                    </div>
                  </div>
                  
                  {/* Lesson progress */}
                  <h4 className="font-medium mb-3">Lesson Progress</h4>
                  <div className="space-y-4 mb-6">
                    {selectedModuleDetails.lessons.map(lesson => (
                      <div 
                        key={lesson.id} 
                        className={`border rounded-lg p-4 ${
                          lesson.status === 'completed' && 'bg-green-50 border-green-100'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start">
                            <div className="mt-0.5 mr-3">
                              {lesson.status === 'completed' ? (
                                <CheckCircle className="h-5 w-5 text-green-500" />
                              ) : (
                                <Clock className="h-5 w-5 text-gray-400" />
                              )}
                            </div>
                            <div>
                              <h5 className="font-medium">{lesson.title}</h5>
                              <p className="text-sm text-gray-600">{lesson.description}</p>
                              
                              <div className="flex items-center mt-2 space-x-4 text-xs">
                                <span className="text-gray-500">
                                  Duration: {formatDuration(lesson.duration)}
                                </span>
                                
                                {lesson.lastAccessed && (
                                  <span className="text-gray-500">
                                    Last accessed: {formatDate(lesson.lastAccessed)}
                                  </span>
                                )}
                                
                                {lesson.completedDate && (
                                  <span className="text-green-600">
                                    Completed: {formatDate(lesson.completedDate)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          <Button
                            variant={lesson.status === 'completed' ? 'outline' : 'default'}
                            size="sm"
                            onClick={() => navigate(`/portal/modules/${selectedModuleDetails.id}`)}
                          >
                            {lesson.status === 'completed' ? 'Review' : 'Start'}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* Resources */}
                  {selectedModuleDetails.resources && selectedModuleDetails.resources.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-3">Module Resources</h4>
                      <Card className="overflow-hidden border">
                        <div className="divide-y">
                          {selectedModuleDetails.resources.map(resource => (
                            <div key={resource.id} className="p-4 hover:bg-gray-50">
                              <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                  <div className="p-2 mr-3">
                                    <FileText className="h-5 w-5 text-gray-400" />
                                  </div>
                                  <div>
                                    <h5 className="font-medium">{resource.name}</h5>
                                    <p className="text-xs text-gray-500">{resource.type} • {resource.size}</p>
                                  </div>
                                </div>
                                
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => navigate('/portal/resources')}
                                >
                                  <Download className="h-4 w-4 mr-1" />
                                  Download
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </Card>
                    </div>
                  )}
                </div>
              </Card>
            ) : (
              <Card className="p-8 text-center">
                <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-1">No module selected</h3>
                <p className="text-gray-500">
                  Please select a module from the list to view detailed progress
                </p>
              </Card>
            )}
          </div>
        </div>
      </div>
      
      {/* Program certificate */}
      {progressData.programCertificate && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">Program Certificate</h2>
          
          <Card className="p-6">
            <div className="md:flex items-center justify-between">
              <div className="mb-4 md:mb-0">
                <div className="flex items-center mb-2">
                  <Award className="h-6 w-6 text-yellow-500 mr-2" />
                  <h3 className="text-lg font-medium">{progressData.program.name} Certificate</h3>
                </div>
                <p className="text-gray-600 mb-4">
                  {progressData.programCertificate.isEarned 
                    ? "Congratulations! You've earned your program certificate."
                    : `Complete ${progressData.programCertificate.requiredCompletion - progressData.programCertificate.currentCompletion} more modules to earn your certificate.`
                  }
                </p>
                
                <div className="flex items-center">
                  <div className="flex -space-x-2 mr-3">
                    {[...Array(3)].map((_, index) => (
                      <div 
                        key={index}
                        className="w-8 h-8 rounded-full bg-yellow-100 flex items-center justify-center ring-2 ring-white"
                      >
                        <Star className="h-4 w-4 text-yellow-500" />
                      </div>
                    ))}
                  </div>
                  <div>
                    <div className="text-sm font-medium">Certificate Progress</div>
                    <div className="text-xs text-gray-500">
                      {progressData.programCertificate.currentCompletion} of {progressData.programCertificate.requiredCompletion} required modules
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="text-center">
                <div className="inline-block relative mb-4">
                  <div className="w-24 h-24 rounded-full bg-blue-50 flex items-center justify-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {progressData.programCertificate.completionPercentage}%
                    </div>
                  </div>
                  {/* Progress circle indicator could be added here */}
                </div>
                
                <Button
                  disabled={!progressData.programCertificate.isEarned}
                  onClick={() => progressData.programCertificate.isEarned && 
                    window.open(`/api/portal/certificates/program/download`, '_blank')
                  }
                >
                  <Award className="h-4 w-4 mr-2" />
                  {progressData.programCertificate.isEarned 
                    ? "View Certificate" 
                    : "Certificate Locked"
                  }
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
      
      {/* Learning recommendations */}
      {progressData.recommendations && progressData.recommendations.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold mb-4">Learning Recommendations</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {progressData.recommendations.map(recommendation => (
              <Card key={recommendation.id} className="overflow-hidden">
                <div className={`h-2 ${
                  recommendation.type === 'module' 
                    ? 'bg-blue-500' 
                    : recommendation.type === 'resource'
                    ? 'bg-purple-500'
                    : 'bg-green-500'
                }`}></div>
                <div className="p-6">
                  <div className="flex items-center mb-3">
                    <div className={`p-2 rounded-full mr-3 ${
                      recommendation.type === 'module' 
                        ? 'bg-blue-50 text-blue-500' 
                        : recommendation.type === 'resource'
                        ? 'bg-purple-50 text-purple-500'
                        : 'bg-green-50 text-green-500'
                    }`}>
                      {recommendation.type === 'module' ? (
                        <BookOpen className="h-5 w-5" />
                      ) : recommendation.type === 'resource' ? (
                        <FileText className="h-5 w-5" />
                      ) : (
                        <TrendingUp className="h-5 w-5" />
                      )}
                    </div>
                    <h3 className="font-medium">{recommendation.title}</h3>
                  </div>
                  
                  <p className="text-gray-600 mb-4">{recommendation.description}</p>
                  
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => {
                      if (recommendation.type === 'module') {
                        navigate(`/portal/modules/${recommendation.moduleId}`);
                      } else if (recommendation.type === 'resource') {
                        navigate('/portal/resources');
                      } else if (recommendation.type === 'skill') {
                        navigate('/portal/skills');
                      }
                    }}
                  >
                    {recommendation.type === 'module' 
                      ? 'Go to Module' 
                      : recommendation.type === 'resource'
                      ? 'View Resource'
                      : 'Develop Skill'
                    }
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortalProgressPage;