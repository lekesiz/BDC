import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { 
  Plus, 
  Edit, 
  Trash2, 
  GripVertical, 
  Calendar,
  Clock,
  Users,
  FileText,
  ChevronRight,
  Search,
  Filter
} from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import LoadingSpinner from '../../components/ui/LoadingSpinner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';

const ProgramModulesPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [program, setProgram] = useState(null);
  const [modules, setModules] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [showModuleDialog, setShowModuleDialog] = useState(false);
  const [selectedModule, setSelectedModule] = useState(null);
  const [moduleForm, setModuleForm] = useState({
    title: '',
    description: '',
    duration: '',
    order: 0,
    status: 'draft'
  });

  useEffect(() => {
    fetchProgramAndModules();
  }, [id]);

  const fetchProgramAndModules = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setProgram({
        id,
        name: 'Professional Development Program',
        description: 'Comprehensive training program for skill development',
        total_modules: 8,
        total_duration: '120 hours'
      });

      setModules([
        {
          id: 1,
          title: 'Introduction to Leadership',
          description: 'Fundamentals of effective leadership and team management',
          duration: '15 hours',
          order: 1,
          status: 'published',
          sessions: 5,
          assignments: 3,
          participants: 24
        },
        {
          id: 2,
          title: 'Communication Skills',
          description: 'Developing effective communication strategies',
          duration: '12 hours',
          order: 2,
          status: 'published',
          sessions: 4,
          assignments: 2,
          participants: 24
        },
        {
          id: 3,
          title: 'Project Management Basics',
          description: 'Introduction to project planning and execution',
          duration: '20 hours',
          order: 3,
          status: 'draft',
          sessions: 6,
          assignments: 4,
          participants: 0
        },
        {
          id: 4,
          title: 'Time Management',
          description: 'Techniques for effective time management and productivity',
          duration: '8 hours',
          order: 4,
          status: 'published',
          sessions: 3,
          assignments: 1,
          participants: 22
        }
      ]);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load program modules",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateModule = () => {
    setSelectedModule(null);
    setModuleForm({
      title: '',
      description: '',
      duration: '',
      order: modules.length + 1,
      status: 'draft'
    });
    setShowModuleDialog(true);
  };

  const handleEditModule = (module) => {
    setSelectedModule(module);
    setModuleForm({
      title: module.title,
      description: module.description,
      duration: module.duration,
      order: module.order,
      status: module.status
    });
    setShowModuleDialog(true);
  };

  const handleSaveModule = async () => {
    try {
      // Validate form
      if (!moduleForm.title || !moduleForm.duration) {
        toast({
          title: "Validation Error",
          description: "Please fill in all required fields",
          variant: "destructive"
        });
        return;
      }

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      if (selectedModule) {
        // Update existing module
        setModules(modules.map(m => 
          m.id === selectedModule.id 
            ? { ...m, ...moduleForm }
            : m
        ));
        toast({
          title: "Success",
          description: "Module updated successfully"
        });
      } else {
        // Create new module
        const newModule = {
          id: Date.now(),
          ...moduleForm,
          sessions: 0,
          assignments: 0,
          participants: 0
        };
        setModules([...modules, newModule]);
        toast({
          title: "Success",
          description: "Module created successfully"
        });
      }

      setShowModuleDialog(false);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save module",
        variant: "destructive"
      });
    }
  };

  const handleDeleteModule = async (moduleId) => {
    if (!confirm('Are you sure you want to delete this module?')) return;

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setModules(modules.filter(m => m.id !== moduleId));
      toast({
        title: "Success",
        description: "Module deleted successfully"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete module",
        variant: "destructive"
      });
    }
  };

  const filteredModules = modules.filter(module => {
    const matchesSearch = module.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         module.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || module.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Program Modules</h1>
          <p className="text-gray-600 mt-1">{program?.name}</p>
        </div>
        <Button onClick={handleCreateModule}>
          <Plus className="h-4 w-4 mr-2" />
          Add Module
        </Button>
      </div>

      {/* Program Overview */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Modules</p>
              <p className="text-2xl font-bold">{modules.length}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Total Duration</p>
              <p className="text-2xl font-bold">{program?.total_duration}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Published</p>
              <p className="text-2xl font-bold">
                {modules.filter(m => m.status === 'published').length}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Draft</p>
              <p className="text-2xl font-bold">
                {modules.filter(m => m.status === 'draft').length}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Search and Filter */}
      <div className="flex gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Search modules..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-[180px]">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Modules</SelectItem>
            <SelectItem value="published">Published</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Modules List */}
      <div className="space-y-4">
        {filteredModules.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-gray-500">No modules found</p>
            </CardContent>
          </Card>
        ) : (
          filteredModules.map((module) => (
            <Card key={module.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4 flex-1">
                    <div className="mt-1">
                      <GripVertical className="h-5 w-5 text-gray-400 cursor-move" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold">{module.title}</h3>
                        <Badge variant={module.status === 'published' ? 'success' : 'secondary'}>
                          {module.status}
                        </Badge>
                      </div>
                      <p className="text-gray-600 mb-4">{module.description}</p>
                      <div className="flex items-center gap-6 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          <span>{module.duration}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          <span>{module.sessions} sessions</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <FileText className="h-4 w-4" />
                          <span>{module.assignments} assignments</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          <span>{module.participants} participants</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/programs/${id}/modules/${module.id}`)}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleEditModule(module)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteModule(module.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>

      {/* Module Dialog */}
      <Dialog open={showModuleDialog} onOpenChange={setShowModuleDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {selectedModule ? 'Edit Module' : 'Create New Module'}
            </DialogTitle>
            <DialogDescription>
              {selectedModule 
                ? 'Update the module information below.' 
                : 'Fill in the details to create a new module.'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Module Title *</Label>
              <Input
                id="title"
                value={moduleForm.title}
                onChange={(e) => setModuleForm({ ...moduleForm, title: e.target.value })}
                placeholder="Enter module title"
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={moduleForm.description}
                onChange={(e) => setModuleForm({ ...moduleForm, description: e.target.value })}
                placeholder="Enter module description"
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="duration">Duration *</Label>
                <Input
                  id="duration"
                  value={moduleForm.duration}
                  onChange={(e) => setModuleForm({ ...moduleForm, duration: e.target.value })}
                  placeholder="e.g., 15 hours"
                />
              </div>
              <div>
                <Label htmlFor="status">Status</Label>
                <Select 
                  value={moduleForm.status} 
                  onValueChange={(value) => setModuleForm({ ...moduleForm, status: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="published">Published</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowModuleDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveModule}>
              {selectedModule ? 'Update' : 'Create'} Module
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ProgramModulesPage;