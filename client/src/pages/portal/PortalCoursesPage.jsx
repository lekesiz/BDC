import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  Search, 
  CheckCircle, 
  Clock, 
  Calendar,
  ChevronRight,
  Filter,
  ChevronDown,
  Loader,
  BookOpenCheck,
  ArrowUpRight
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';

/**
 * PortalCoursesPage displays all courses and modules available to the student
 */
const PortalCoursesPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOpen, setFilterOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Fetch courses data
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/portal/courses');
        setCourses(response.data);
        setFilteredCourses(response.data);
      } catch (error) {
        console.error('Error fetching course data:', error);
        toast({
          title: 'Error',
          description: 'Failed to load course data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchCourses();
  }, [toast]);
  
  // Apply filters and search
  useEffect(() => {
    let results = [...courses];
    
    // Apply status filter
    if (statusFilter !== 'all') {
      results = results.filter(course => course.status === statusFilter);
    }
    
    // Apply search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      results = results.filter(
        course => 
          course.title.toLowerCase().includes(searchLower) ||
          course.description.toLowerCase().includes(searchLower) ||
          course.modules.some(module => 
            module.title.toLowerCase().includes(searchLower) ||
            (module.description && module.description.toLowerCase().includes(searchLower))
          )
      );
    }
    
    setFilteredCourses(results);
  }, [courses, statusFilter, searchTerm]);
  
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
  
  // Calculate course completion percentage
  const calculateCompletion = (modules) => {
    if (!modules.length) return 0;
    
    const completedModules = modules.filter(module => module.status === 'completed').length;
    return Math.round((completedModules / modules.length) * 100);
  };
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader className="w-10 h-10 text-primary animate-spin" />
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">My Courses</h1>
        
        <div className="flex space-x-2">
          <div className="relative">
            <Button
              variant="outline"
              onClick={() => setFilterOpen(!filterOpen)}
              className="flex items-center"
            >
              <Filter className="w-4 h-4 mr-2" />
              Filter
              <ChevronDown className="w-4 h-4 ml-2" />
            </Button>
            
            {filterOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border p-4">
                <h3 className="text-sm font-medium mb-2">Status</h3>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="filter-all"
                      name="status-filter"
                      checked={statusFilter === 'all'}
                      onChange={() => setStatusFilter('all')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="filter-all" className="ml-2 block text-sm text-gray-700">
                      All Courses
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="filter-in-progress"
                      name="status-filter"
                      checked={statusFilter === 'in_progress'}
                      onChange={() => setStatusFilter('in_progress')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="filter-in-progress" className="ml-2 block text-sm text-gray-700">
                      In Progress
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="filter-completed"
                      name="status-filter"
                      checked={statusFilter === 'completed'}
                      onChange={() => setStatusFilter('completed')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="filter-completed" className="ml-2 block text-sm text-gray-700">
                      Completed
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="radio"
                      id="filter-not-started"
                      name="status-filter"
                      checked={statusFilter === 'not_started'}
                      onChange={() => setStatusFilter('not_started')}
                      className="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
                    />
                    <label htmlFor="filter-not-started" className="ml-2 block text-sm text-gray-700">
                      Not Started
                    </label>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Search bar */}
      <div className="relative max-w-md mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
        <Input
          type="text"
          placeholder="Search courses and modules..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="pl-10"
        />
      </div>
      
      {/* Course grid */}
      {filteredCourses.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-300 mx-auto mb-3" />
          <h3 className="text-lg font-medium">No courses found</h3>
          <p className="text-gray-500 mt-1">Try adjusting your search or filters</p>
        </div>
      ) : (
        <div className="space-y-8">
          {filteredCourses.map(course => (
            <Card key={course.id} className="overflow-hidden">
              <div className="p-6 flex justify-between items-center border-b">
                <div className="flex items-center">
                  <div className={`p-3 rounded-lg mr-4 ${
                    course.status === 'completed' 
                      ? 'bg-green-50' 
                      : course.status === 'in_progress'
                      ? 'bg-blue-50'
                      : 'bg-gray-50'
                  }`}>
                    <BookOpen className={`h-6 w-6 ${
                      course.status === 'completed' 
                        ? 'text-green-500' 
                        : course.status === 'in_progress'
                        ? 'text-blue-500'
                        : 'text-gray-500'
                    }`} />
                  </div>
                  <div>
                    <h2 className="text-lg font-medium">{course.title}</h2>
                    <p className="text-sm text-gray-500">{course.description}</p>
                  </div>
                </div>
                
                <div className="flex items-center">
                  {course.status === 'completed' ? (
                    <span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Completed
                    </span>
                  ) : course.status === 'in_progress' ? (
                    <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      In Progress
                    </span>
                  ) : (
                    <span className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded-full flex items-center">
                      <Calendar className="w-3 h-3 mr-1" />
                      Not Started
                    </span>
                  )}
                </div>
              </div>
              
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex-1 pr-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-500">Course Progress</span>
                      <span className="font-medium">{calculateCompletion(course.modules)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${
                          course.status === 'completed' 
                            ? 'bg-green-500' 
                            : 'bg-primary'
                        }`}
                        style={{ width: `${calculateCompletion(course.modules)}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-4 text-sm">
                    <div className="text-center">
                      <p className="text-gray-500">Duration</p>
                      <p className="font-medium">{formatDuration(course.totalDuration)}</p>
                    </div>
                    <div className="text-center">
                      <p className="text-gray-500">Modules</p>
                      <p className="font-medium">{course.modules.length}</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-3 mt-6">
                  <h3 className="font-medium">Modules</h3>
                  
                  <div className="space-y-2">
                    {course.modules.map(module => (
                      <div 
                        key={module.id}
                        className={`border rounded-lg p-3 flex justify-between items-center hover:bg-gray-50 cursor-pointer ${
                          module.status === 'completed' ? 'border-green-200 bg-green-50/30' : ''
                        }`}
                        onClick={() => navigate(`/portal/modules/${module.id}`)}
                      >
                        <div className="flex items-center">
                          <div className={`p-2 rounded-full mr-3 ${
                            module.status === 'completed' 
                              ? 'bg-green-100 text-green-600' 
                              : module.status === 'in_progress'
                              ? 'bg-blue-100 text-blue-600'
                              : 'bg-gray-100 text-gray-600'
                          }`}>
                            {module.status === 'completed' ? (
                              <CheckCircle className="w-4 h-4" />
                            ) : (
                              <BookOpen className="w-4 h-4" />
                            )}
                          </div>
                          <div>
                            <h4 className="font-medium text-sm">{module.title}</h4>
                            <p className="text-xs text-gray-500">
                              {formatDuration(module.duration)} • {module.lessonCount} lessons
                            </p>
                          </div>
                        </div>
                        
                        <div className="flex items-center">
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-xs"
                          >
                            {module.status === 'completed' 
                              ? 'Review' 
                              : module.status === 'in_progress'
                              ? 'Continue'
                              : 'Start'
                            }
                            <ChevronRight className="w-4 h-4 ml-1" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-50 p-4 border-t flex justify-between items-center">
                <div className="flex items-center text-sm">
                  <BookOpenCheck className="w-4 h-4 text-gray-500 mr-2" />
                  <span>
                    {course.modules.filter(m => m.status === 'completed').length} of {course.modules.length} modules completed
                  </span>
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigate(`/portal/courses/${course.id}`)}
                  className="flex items-center"
                >
                  View Course
                  <ArrowUpRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default PortalCoursesPage;