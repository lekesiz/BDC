import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Search, 
  Filter, 
  ChevronDown,
  Calendar,
  Users,
  Clock,
  Edit,
  Trash2,
  BookOpen,
  Award,
  Star
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { useSocket } from '@/contexts/SocketContext';
/**
 * ProgramsListPage displays all training programs
 */
const ProgramsListPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const { on } = useSocket();
  const [programs, setPrograms] = useState([]);
  const [filteredPrograms, setFilteredPrograms] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterOpen, setFilterOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  // Fetch programs
  useEffect(() => {
    const fetchPrograms = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/programs');
        setPrograms(response.data);
        setFilteredPrograms(response.data);
      } catch (error) {
        console.error('Error fetching programs:', error);
        toast({
          title: 'Error',
          description: 'Failed to load programs',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchPrograms();
  }, []); // Remove toast dependency to prevent infinite loop
  // Real-time program updates
  useEffect(() => {
    const handleProgramCreated = (event) => {
      const newProgram = event.detail;
      if (newProgram) {
        setPrograms(prev => [newProgram, ...prev]);
      }
    };
    const handleProgramUpdated = (event) => {
      const updatedProgram = event.detail;
      if (updatedProgram) {
        setPrograms(prev => prev.map(p => 
          p.id === updatedProgram.id ? updatedProgram : p
        ));
      }
    };
    const handleProgramDeleted = (event) => {
      const deletedProgram = event.detail;
      if (deletedProgram) {
        setPrograms(prev => prev.filter(p => p.id !== deletedProgram.id));
      }
    };
    // Listen to custom events from Socket context
    window.addEventListener('programCreated', handleProgramCreated);
    window.addEventListener('programUpdated', handleProgramUpdated);
    window.addEventListener('programDeleted', handleProgramDeleted);
    return () => {
      window.removeEventListener('programCreated', handleProgramCreated);
      window.removeEventListener('programUpdated', handleProgramUpdated);
      window.removeEventListener('programDeleted', handleProgramDeleted);
    };
  }, []);
  // Filter programs based on search and filters
  useEffect(() => {
    let filtered = [...programs];
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(program => 
        program.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        program.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        program.code?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(program => program.category === selectedCategory);
    }
    // Level filter
    if (selectedLevel !== 'all') {
      filtered = filtered.filter(program => program.level === selectedLevel);
    }
    // Status filter
    if (selectedStatus !== 'all') {
      filtered = filtered.filter(program => program.status === selectedStatus);
    }
    setFilteredPrograms(filtered);
  }, [searchTerm, selectedCategory, selectedLevel, selectedStatus, programs]);
  // Delete program
  const handleDeleteProgram = async (programId) => {
    if (!window.confirm('Are you sure you want to delete this program?')) {
      return;
    }
    try {
      await api.delete(`/api/programs/${programId}`);
      toast({
        title: 'Success',
        description: 'Program deleted successfully',
        type: 'success',
      });
      // Remove from list
      setPrograms(programs.filter(p => p.id !== programId));
    } catch (error) {
      console.error('Error deleting program:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete program',
        type: 'error',
      });
    }
  };
  // Get status badge color
  const getStatusColor = (status) => {
    switch(status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      case 'draft':
        return 'bg-yellow-100 text-yellow-800';
      case 'archived':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  // Get level icon
  const getLevelIcon = (level) => {
    switch(level) {
      case 'beginner':
        return <Star className="w-4 h-4 text-green-500" />;
      case 'intermediate':
        return <><Star className="w-4 h-4 text-yellow-500" /><Star className="w-4 h-4 text-yellow-500" /></>;
      case 'advanced':
        return <><Star className="w-4 h-4 text-orange-500" /><Star className="w-4 h-4 text-orange-500" /><Star className="w-4 h-4 text-orange-500" /></>;
      default:
        return null;
    }
  };
  // Real-time program events
  useEffect(() => {
    const offCreated = on('program_created', ({ program }) => {
      setPrograms(prev => [program, ...prev]);
      setFilteredPrograms(prev => [program, ...prev]);
    });
    const offUpdated = on('program_updated', ({ program }) => {
      setPrograms(prev => prev.map(p => (p.id === program.id ? program : p)));
      setFilteredPrograms(prev => prev.map(p => (p.id === program.id ? program : p)));
    });
    const offDeleted = on('program_deleted', ({ program_id }) => {
      setPrograms(prev => prev.filter(p => p.id !== program_id));
      setFilteredPrograms(prev => prev.filter(p => p.id !== program_id));
    });
    // Cleanup
    return () => {
      offCreated && offCreated();
      offUpdated && offUpdated();
      offDeleted && offDeleted();
    };
  }, [on]);
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-500">Loading programs...</p>
        </div>
      </div>
    );
  }
  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Training Programs</h1>
        {(user.role === 'super_admin' || user.role === 'tenant_admin') && (
          <Button
            onClick={() => navigate('/programs/new')}
            className="flex items-center"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Program
          </Button>
        )}
      </div>
      <div className="mb-6 flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <Input
            type="text"
            placeholder="Search programs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
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
            <div className="absolute right-0 mt-2 w-64 bg-white rounded-md shadow-lg z-10 border p-4">
              <h3 className="font-medium mb-3">Filter Programs</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                  <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="all">All Categories</option>
                    <option value="technical">Technical Skills</option>
                    <option value="soft_skills">Soft Skills</option>
                    <option value="leadership">Leadership</option>
                    <option value="communication">Communication</option>
                    <option value="management">Management</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Level</label>
                  <select
                    value={selectedLevel}
                    onChange={(e) => setSelectedLevel(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="all">All Levels</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                  <select
                    value={selectedStatus}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                  >
                    <option value="all">All Status</option>
                    <option value="draft">Draft</option>
                    <option value="active">Active</option>
                    <option value="completed">Completed</option>
                    <option value="archived">Archived</option>
                  </select>
                </div>
              </div>
              <div className="flex justify-end mt-4 space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedCategory('all');
                    setSelectedLevel('all');
                    setSelectedStatus('all');
                  }}
                >
                  Clear
                </Button>
                <Button
                  size="sm"
                  onClick={() => setFilterOpen(false)}
                >
                  Apply
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
      {filteredPrograms.length === 0 ? (
        <Card className="p-8 text-center">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No programs found</h3>
          <p className="text-gray-500">
            {searchTerm || selectedCategory !== 'all' || selectedLevel !== 'all' || selectedStatus !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Create your first training program to get started'}
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {(filteredPrograms || []).map((program) => (
            <Card key={program.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">{program.name}</h3>
                    {program.code && (
                      <p className="text-sm text-gray-500">Code: {program.code}</p>
                    )}
                  </div>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(program.status)}`}>
                    {program.status?.charAt(0).toUpperCase() + program.status?.slice(1)}
                  </span>
                </div>
                <p className="text-gray-600 mb-4 line-clamp-2">{program.description}</p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center text-gray-600">
                    <Clock className="w-4 h-4 mr-2" />
                    Duration: {program.duration || 'N/A'} days
                  </div>
                  <div className="flex items-center text-gray-600">
                    <Users className="w-4 h-4 mr-2" />
                    Enrolled: {program.enrolled_count || 0} / {program.max_participants || '∞'}
                  </div>
                  <div className="flex items-center text-gray-600">
                    <BookOpen className="w-4 h-4 mr-2" />
                    Modules: {program.module_count || 0}
                  </div>
                  {program.start_date && (
                    <div className="flex items-center text-gray-600">
                      <Calendar className="w-4 h-4 mr-2" />
                      Starts: {new Date(program.start_date).toLocaleDateString()}
                    </div>
                  )}
                  <div className="flex items-center text-gray-600">
                    <div className="flex items-center mr-2">
                      Level: 
                    </div>
                    <div className="flex items-center">
                      {getLevelIcon(program.level)}
                      <span className="ml-1">{program.level?.charAt(0).toUpperCase() + program.level?.slice(1) || 'N/A'}</span>
                    </div>
                  </div>
                </div>
                <div className="flex justify-between items-center mt-6">
                  <div className="flex items-center text-sm text-gray-500">
                    <Award className="w-4 h-4 mr-1" />
                    {program.category?.charAt(0).toUpperCase() + program.category?.slice(1).replace('_', ' ')}
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/programs/${program.id}`)}
                    >
                      View
                    </Button>
                    {(user.role === 'super_admin' || user.role === 'tenant_admin') && (
                      <>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => navigate(`/programs/${program.id}/edit`)}
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteProgram(program.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
export default ProgramsListPage;