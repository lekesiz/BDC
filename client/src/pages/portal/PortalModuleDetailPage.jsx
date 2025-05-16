import { useState, useEffect, useRef } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { 
  BookOpen, 
  ArrowLeft, 
  CheckCircle, 
  Clock, 
  Play,
  Pause,
  FileText,
  MessageSquare,
  Download,
  Users,
  CheckSquare,
  Paperclip,
  ChevronRight,
  ChevronLeft,
  Loader,
  BookOpenCheck,
  AlertTriangle
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';

/**
 * PortalModuleDetailPage displays a specific module with its lessons and resources
 */
const PortalModuleDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [moduleData, setModuleData] = useState(null);
  const [currentLessonIndex, setCurrentLessonIndex] = useState(0);
  const [isCompleting, setIsCompleting] = useState(false);
  const videoRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  
  // Fetch module data
  useEffect(() => {
    const fetchModuleData = async () => {
      try {
        setIsLoading(true);
        const response = await api.get(`/api/portal/modules/${id}`);
        setModuleData(response.data);
        
        // Set current lesson to the first incomplete lesson or the first lesson
        const incompleteIndex = response.data.lessons.findIndex(lesson => lesson.status !== 'completed');
        setCurrentLessonIndex(incompleteIndex !== -1 ? incompleteIndex : 0);
      } catch (error) {
        console.error('Error fetching module data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load module data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchModuleData();
  }, [id, toast]);
  
  // Format duration
  const formatDuration = (minutes) => {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    
    if (remainingMinutes === 0) {
      return `${hours} hr`;
    }
    
    return `${hours} hr ${remainingMinutes} min`;
  };
  
  // Toggle video playback
  const togglePlayback = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };
  
  // Mark lesson as completed
  const completeLesson = async (lessonId) => {
    try {
      setIsCompleting(true);
      await api.post(`/api/portal/lessons/${lessonId}/complete`);
      
      // Update the lesson's status locally
      setModuleData(prevData => ({
        ...prevData,
        lessons: prevData.lessons.map(lesson => 
          lesson.id === lessonId ? { ...lesson, status: 'completed' } : lesson
        )
      }));
      
      toast({
        title: 'Success',
        description: 'Lesson marked as completed',
        type: 'success',
      });
      
      // Move to the next lesson if available
      if (currentLessonIndex < moduleData.lessons.length - 1) {
        setCurrentLessonIndex(currentLessonIndex + 1);
      }
    } catch (error) {
      console.error('Error completing lesson:', error);
      toast({
        title: 'Error',
        description: 'Failed to mark lesson as completed',
        type: 'error',
      });
    } finally {
      setIsCompleting(false);
    }
  };
  
  // Download resource
  const downloadResource = async (resourceId, resourceName) => {
    try {
      const response = await api.get(`/api/portal/resources/${resourceId}/download`, {
        responseType: 'blob'
      });
      
      // Create a URL for the blob
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', resourceName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Success',
        description: 'Resource downloaded successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error downloading resource:', error);
      toast({
        title: 'Error',
        description: 'Failed to download resource',
        type: 'error',
      });
    }
  };
  
  // Navigate to previous lesson
  const goToPreviousLesson = () => {
    if (currentLessonIndex > 0) {
      setCurrentLessonIndex(currentLessonIndex - 1);
    }
  };
  
  // Navigate to next lesson
  const goToNextLesson = () => {
    if (currentLessonIndex < moduleData.lessons.length - 1) {
      setCurrentLessonIndex(currentLessonIndex + 1);
    }
  };
  
  // Calculate module completion percentage
  const calculateCompletion = () => {
    if (!moduleData || !moduleData.lessons.length) return 0;
    
    const completedLessons = moduleData.lessons.filter(lesson => lesson.status === 'completed').length;
    return Math.round((completedLessons / moduleData.lessons.length) * 100);
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  
  if (!moduleData) {
    return (
      <div className="container mx-auto py-6">
        <Card className="p-6 text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Module Not Found</h2>
          <p className="text-gray-500 mb-4">The module you're looking for doesn't exist or you don't have access to it.</p>
          <Button onClick={() => navigate('/portal/courses')}>
            Back to Courses
          </Button>
        </Card>
      </div>
    );
  }
  
  const currentLesson = moduleData.lessons[currentLessonIndex];
  
  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <button
          className="mr-4 p-2 rounded-full hover:bg-gray-100"
          onClick={() => navigate(`/portal/courses/${moduleData.courseId}`)}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        
        <div>
          <div className="flex items-center">
            <h1 className="text-2xl font-bold">{moduleData.title}</h1>
            {moduleData.status === 'completed' && (
              <span className="ml-3 bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
                <CheckCircle className="w-3 h-3 mr-1" />
                Completed
              </span>
            )}
          </div>
          <p className="text-gray-500">
            {moduleData.course} • {formatDuration(moduleData.duration)} • {moduleData.lessons.length} lessons
          </p>
        </div>
      </div>
      
      {/* Module content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content area */}
        <div className="lg:col-span-2 space-y-6">
          {/* Video/content area */}
          <Card className="overflow-hidden">
            <div className="aspect-video bg-gray-900 relative">
              {currentLesson.type === 'video' ? (
                <>
                  <video
                    ref={videoRef}
                    src={currentLesson.videoUrl}
                    className="w-full h-full"
                    controls
                    onPlay={() => setIsPlaying(true)}
                    onPause={() => setIsPlaying(false)}
                  />
                  
                  {!isPlaying && (
                    <button
                      className="absolute inset-0 flex items-center justify-center bg-black/30"
                      onClick={togglePlayback}
                    >
                      <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
                        <Play className="w-8 h-8 text-white" fill="white" />
                      </div>
                    </button>
                  )}
                </>
              ) : currentLesson.type === 'presentation' ? (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center">
                    <FileText className="w-16 h-16 text-white/50 mx-auto mb-3" />
                    <p className="text-white/70">Presentation content</p>
                  </div>
                </div>
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center">
                    <BookOpen className="w-16 h-16 text-white/50 mx-auto mb-3" />
                    <p className="text-white/70">Lesson content</p>
                  </div>
                </div>
              )}
            </div>
            
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h2 className="text-xl font-medium">{currentLesson.title}</h2>
                  <p className="text-sm text-gray-500">
                    {currentLesson.type.charAt(0).toUpperCase() + currentLesson.type.slice(1)} • {formatDuration(currentLesson.duration)}
                  </p>
                </div>
                
                {currentLesson.status === 'completed' ? (
                  <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Completed
                  </span>
                ) : (
                  <Button
                    onClick={() => completeLesson(currentLesson.id)}
                    disabled={isCompleting}
                    className="flex items-center"
                  >
                    {isCompleting ? (
                      <>
                        <Loader className="w-4 h-4 mr-2 animate-spin" />
                        Completing...
                      </>
                    ) : (
                      <>
                        <CheckSquare className="w-4 h-4 mr-2" />
                        Mark as Completed
                      </>
                    )}
                  </Button>
                )}
              </div>
              
              <div className="prose max-w-none">
                <p>{currentLesson.description}</p>
                
                {currentLesson.content && (
                  <div className="mt-4"
                    dangerouslySetInnerHTML={{ __html: currentLesson.content }}
                  />
                )}
              </div>
              
              {/* Lesson resources */}
              {currentLesson.resources && currentLesson.resources.length > 0 && (
                <div className="mt-8">
                  <h3 className="text-lg font-medium mb-4">Lesson Resources</h3>
                  
                  <div className="space-y-3">
                    {currentLesson.resources.map(resource => (
                      <div key={resource.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center">
                          <div className="p-2 bg-gray-100 rounded-lg mr-3">
                            <FileText className="w-4 h-4 text-gray-500" />
                          </div>
                          <div>
                            <h4 className="font-medium text-sm">{resource.name}</h4>
                            <p className="text-xs text-gray-500">{resource.type} • {resource.size}</p>
                          </div>
                        </div>
                        
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => downloadResource(resource.id, resource.name)}
                          className="flex items-center"
                        >
                          <Download className="w-4 h-4 mr-1" />
                          Download
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Navigation buttons */}
              <div className="flex justify-between mt-8 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={goToPreviousLesson}
                  disabled={currentLessonIndex === 0}
                  className="flex items-center"
                >
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Previous Lesson
                </Button>
                
                <Button
                  variant={currentLessonIndex === moduleData.lessons.length - 1 ? "outline" : "default"}
                  onClick={goToNextLesson}
                  disabled={currentLessonIndex === moduleData.lessons.length - 1}
                  className="flex items-center"
                >
                  Next Lesson
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          </Card>
          
          {/* Discussion area */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-lg font-medium">Discussion</h2>
            </div>
            
            <div className="p-6">
              <div className="flex items-start space-x-4 mb-6">
                <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                  <span className="text-primary font-medium">{user?.name?.charAt(0) || 'U'}</span>
                </div>
                
                <div className="flex-1">
                  <textarea
                    placeholder="Ask a question or share your thoughts..."
                    className="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                    rows={3}
                  />
                  
                  <div className="flex justify-between mt-2">
                    <div className="flex items-center">
                      <button className="text-gray-500 hover:text-gray-700">
                        <Paperclip className="w-4 h-4" />
                      </button>
                    </div>
                    
                    <Button>
                      Post Comment
                    </Button>
                  </div>
                </div>
              </div>
              
              {moduleData.discussions && moduleData.discussions.length > 0 ? (
                <div className="space-y-6">
                  {moduleData.discussions.map(discussion => (
                    <div key={discussion.id} className="border-t pt-6">
                      <div className="flex items-start space-x-4">
                        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                          <span className="text-gray-600 font-medium">{discussion.author.charAt(0)}</span>
                        </div>
                        
                        <div>
                          <div className="flex items-center">
                            <h4 className="font-medium">{discussion.author}</h4>
                            <span className="mx-2 text-gray-300">•</span>
                            <span className="text-sm text-gray-500">
                              {new Date(discussion.timestamp).toLocaleDateString()}
                            </span>
                          </div>
                          
                          <div className="mt-1">
                            <p>{discussion.message}</p>
                          </div>
                          
                          <div className="mt-2 flex space-x-3">
                            <button className="text-sm text-gray-500 hover:text-primary">
                              Reply
                            </button>
                            <button className="text-sm text-gray-500 hover:text-primary">
                              Like
                            </button>
                          </div>
                          
                          {/* Replies */}
                          {discussion.replies && discussion.replies.length > 0 && (
                            <div className="mt-4 space-y-4 pl-6 border-l">
                              {discussion.replies.map(reply => (
                                <div key={reply.id} className="flex items-start space-x-3">
                                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                                    <span className="text-gray-600 font-medium text-xs">{reply.author.charAt(0)}</span>
                                  </div>
                                  
                                  <div>
                                    <div className="flex items-center">
                                      <h5 className="font-medium text-sm">{reply.author}</h5>
                                      <span className="mx-2 text-gray-300 text-xs">•</span>
                                      <span className="text-xs text-gray-500">
                                        {new Date(reply.timestamp).toLocaleDateString()}
                                      </span>
                                    </div>
                                    
                                    <div className="mt-1">
                                      <p className="text-sm">{reply.message}</p>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No discussions yet</p>
                  <p className="text-sm text-gray-400 mt-1">Be the first to start a discussion</p>
                </div>
              )}
            </div>
          </Card>
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          {/* Module progress */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-lg font-medium">Module Progress</h2>
            </div>
            
            <div className="p-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-500">Your Progress</span>
                <span className="font-medium">{calculateCompletion()}%</span>
              </div>
              
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
                <div 
                  className="bg-primary h-2.5 rounded-full" 
                  style={{ width: `${calculateCompletion()}%` }}
                ></div>
              </div>
              
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">
                  {moduleData.lessons.filter(lesson => lesson.status === 'completed').length} of {moduleData.lessons.length} lessons completed
                </span>
              </div>
            </div>
          </Card>
          
          {/* Module content */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-lg font-medium">Module Content</h2>
            </div>
            
            <div className="divide-y max-h-[500px] overflow-y-auto">
              {moduleData.lessons.map((lesson, index) => (
                <div 
                  key={lesson.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${index === currentLessonIndex ? 'bg-gray-50' : ''}`}
                  onClick={() => setCurrentLessonIndex(index)}
                >
                  <div className="flex items-start">
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                      lesson.status === 'completed' 
                        ? 'bg-green-100 text-green-600' 
                        : index === currentLessonIndex
                        ? 'bg-blue-100 text-blue-600'
                        : 'bg-gray-100 text-gray-600'
                    }`}>
                      {lesson.status === 'completed' ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <span>{index + 1}</span>
                      )}
                    </div>
                    
                    <div>
                      <h3 className={`font-medium text-sm ${index === currentLessonIndex ? 'text-primary' : ''}`}>
                        {lesson.title}
                      </h3>
                      <div className="flex items-center text-xs text-gray-500 mt-1">
                        <span className="capitalize">{lesson.type}</span>
                        <span className="mx-1">•</span>
                        <span>{formatDuration(lesson.duration)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
          
          {/* Module Info */}
          <Card className="overflow-hidden">
            <div className="p-6 border-b">
              <h2 className="text-lg font-medium">Module Information</h2>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <h3 className="text-sm font-medium mb-2">Description</h3>
                <p className="text-sm text-gray-500">
                  {moduleData.description}
                </p>
              </div>
              
              {moduleData.objectives && moduleData.objectives.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-2">Learning Objectives</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {moduleData.objectives.map((objective, index) => (
                      <li key={index} className="text-sm text-gray-500">
                        {objective}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div>
                <h3 className="text-sm font-medium mb-2">About the Instructor</h3>
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center mr-3">
                    <span className="text-gray-600 font-medium">
                      {moduleData.instructor ? moduleData.instructor.charAt(0) : 'I'}
                    </span>
                  </div>
                  <div>
                    <p className="font-medium text-sm">
                      {moduleData.instructor || 'Unknown Instructor'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {moduleData.instructorRole || 'Instructor'}
                    </p>
                  </div>
                </div>
              </div>
              
              {moduleData.prerequisites && moduleData.prerequisites.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium mb-2">Prerequisites</h3>
                  <ul className="list-disc pl-5 space-y-1">
                    {moduleData.prerequisites.map((prerequisite, index) => (
                      <li key={index} className="text-sm text-gray-500">
                        {prerequisite}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default PortalModuleDetailPage;