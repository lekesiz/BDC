import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft,
  Save,
  Calendar,
  Clock,
  Users,
  BookOpen,
  Award,
  DollarSign,
  Plus,
  X
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';

/**
 * CreateProgramPage for creating new training programs
 */
const CreateProgramPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  
  const [isLoading, setIsLoading] = useState(false);
  const [categories, setCategories] = useState([]);
  const [levels, setLevels] = useState([]);
  const [trainers, setTrainers] = useState([]);
  
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    description: '',
    category: '',
    level: 'beginner',
    duration: 30,
    max_participants: 30,
    price: 0,
    minimum_attendance: 80,
    passing_score: 70,
    prerequisites: '',
    status: 'draft',
    start_date: '',
    end_date: ''
  });
  
  const [modules, setModules] = useState([]);
  const [newModule, setNewModule] = useState({
    name: '',
    description: '',
    duration: 0,
    order: 1
  });
  
  // Fetch initial data
  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [categoriesRes, levelsRes, trainersRes] = await Promise.all([
          api.get('/api/programs/categories'),
          api.get('/api/programs/levels'),
          api.get('/api/users?role=trainer')
        ]);
        
        setCategories(categoriesRes.data);
        setLevels(levelsRes.data);
        setTrainers(trainersRes.data || []);
      } catch (error) {
        console.error('Error fetching initial data:', error);
      }
    };
    
    fetchInitialData();
  }, []);
  
  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Add module
  const handleAddModule = () => {
    if (!newModule.name) {
      toast({
        title: 'Error',
        description: 'Module name is required',
        type: 'error',
      });
      return;
    }
    
    setModules([...modules, { ...newModule, id: Date.now() }]);
    setNewModule({
      name: '',
      description: '',
      duration: 0,
      order: modules.length + 2
    });
  };
  
  // Remove module
  const handleRemoveModule = (moduleId) => {
    setModules(modules.filter(m => m.id !== moduleId));
  };
  
  // Submit form
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.name || !formData.category || !formData.level) {
      toast({
        title: 'Error',
        description: 'Please fill in all required fields',
        type: 'error',
      });
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Create program
      const programResponse = await api.post('/api/programs', formData);
      const programId = programResponse.data.id;
      
      // Create modules if any
      if (modules.length > 0) {
        await Promise.all(
          modules.map(module => 
            api.post(`/api/programs/${programId}/modules`, {
              name: module.name,
              description: module.description,
              duration: module.duration,
              order: module.order,
              is_mandatory: true
            })
          )
        );
      }
      
      toast({
        title: 'Success',
        description: 'Program created successfully',
        type: 'success',
      });
      
      navigate(`/programs/${programId}`);
    } catch (error) {
      console.error('Error creating program:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.error || 'Failed to create program',
        type: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="container mx-auto py-6">
      <div className="flex items-center mb-6">
        <button
          className="mr-4 p-2 rounded-full hover:bg-gray-100"
          onClick={() => navigate('/programs')}
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        
        <div>
          <h1 className="text-2xl font-bold">Create Training Program</h1>
          <p className="text-gray-500">Set up a new training program for beneficiaries</p>
        </div>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Basic Information */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Basic Information</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Program Name *
                </label>
                <Input
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  placeholder="e.g., Leadership Development Program"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Program Code
                </label>
                <Input
                  name="code"
                  value={formData.code}
                  onChange={handleInputChange}
                  placeholder="e.g., LDP-2024"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <Textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Describe the program objectives and content..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category *
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleInputChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  <option value="">Select Category</option>
                  {categories.map(cat => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Level *
                </label>
                <select
                  name="level"
                  value={formData.level}
                  onChange={handleInputChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                >
                  {levels.map(level => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </Card>
          
          {/* Schedule & Capacity */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Schedule & Capacity</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (days)
                </label>
                <Input
                  type="number"
                  name="duration"
                  value={formData.duration}
                  onChange={handleInputChange}
                  min="1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <Input
                  type="date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleInputChange}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <Input
                  type="date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleInputChange}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Maximum Participants
                </label>
                <Input
                  type="number"
                  name="max_participants"
                  value={formData.max_participants}
                  onChange={handleInputChange}
                  min="1"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Price (€)
                </label>
                <Input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleInputChange}
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
          </Card>
          
          {/* Requirements */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Requirements</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Prerequisites
                </label>
                <Textarea
                  name="prerequisites"
                  value={formData.prerequisites}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="List any prerequisites for this program..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Minimum Attendance (%)
                </label>
                <Input
                  type="number"
                  name="minimum_attendance"
                  value={formData.minimum_attendance}
                  onChange={handleInputChange}
                  min="0"
                  max="100"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Passing Score (%)
                </label>
                <Input
                  type="number"
                  name="passing_score"
                  value={formData.passing_score}
                  onChange={handleInputChange}
                  min="0"
                  max="100"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="completed">Completed</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>
          </Card>
          
          {/* Modules */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Modules</h3>
            
            <div className="space-y-4">
              {modules.map((module, index) => (
                <div key={module.id} className="p-3 border rounded-md">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-medium">{module.name}</h4>
                      <p className="text-sm text-gray-500">{module.description}</p>
                      <div className="flex items-center mt-1 text-sm text-gray-500">
                        <Clock className="w-3 h-3 mr-1" />
                        Duration: {module.duration} hours
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => handleRemoveModule(module.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
              
              <div className="border-t pt-4">
                <h4 className="font-medium mb-3">Add Module</h4>
                <div className="space-y-3">
                  <Input
                    placeholder="Module name"
                    value={newModule.name}
                    onChange={(e) => setNewModule({ ...newModule, name: e.target.value })}
                  />
                  <Textarea
                    placeholder="Module description"
                    rows={2}
                    value={newModule.description}
                    onChange={(e) => setNewModule({ ...newModule, description: e.target.value })}
                  />
                  <Input
                    type="number"
                    placeholder="Duration (hours)"
                    value={newModule.duration}
                    onChange={(e) => setNewModule({ ...newModule, duration: Number(e.target.value) })}
                    min="0"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={handleAddModule}
                    className="w-full"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Add Module
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        </div>
        
        <div className="flex justify-end mt-6 space-x-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/programs')}
          >
            Cancel
          </Button>
          
          <Button
            type="submit"
            disabled={isLoading}
            className="flex items-center"
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Creating...
              </>
            ) : (
              <>
                <Save className="w-4 h-4 mr-2" />
                Create Program
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default CreateProgramPage;