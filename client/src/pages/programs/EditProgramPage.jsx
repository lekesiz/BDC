import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Textarea } from '../../components/ui/textarea';
import { Select } from '../../components/ui/select';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Loader2, Save, X } from 'lucide-react';

const EditProgramPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    category: '',
    level: 'beginner',
    duration_weeks: 1,
    status: 'draft',
    max_participants: 20,
    objectives: '',
    requirements: '',
    price: 0,
    currency: 'EUR',
  });

  const [modules, setModules] = useState([]);

  useEffect(() => {
    fetchProgramDetails();
  }, [id]);

  const fetchProgramDetails = async () => {
    try {
      const res = await fetch(`/api/programs/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch program');

      const data = await res.json();
      setFormData({
        name: data.name || '',
        description: data.description || '',
        category: data.category || '',
        level: data.level || 'beginner',
        duration_weeks: data.duration_weeks || 1,
        status: data.status || 'draft',
        max_participants: data.max_participants || 20,
        objectives: data.objectives || '',
        requirements: data.requirements || '',
        price: data.price || 0,
        currency: data.currency || 'EUR',
      });
      
      setModules(data.modules || []);
    } catch (error) {
      console.error('Error fetching program:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch program details',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleAddModule = () => {
    setModules([
      ...modules,
      {
        name: '',
        description: '',
        duration_hours: 1,
        order_index: modules.length
      }
    ]);
  };

  const handleModuleChange = (index, field, value) => {
    const updatedModules = [...modules];
    updatedModules[index][field] = value;
    setModules(updatedModules);
  };

  const handleRemoveModule = (index) => {
    const updatedModules = modules.filter((_, i) => i !== index);
    // Update order indices
    updatedModules.forEach((module, i) => {
      module.order_index = i;
    });
    setModules(updatedModules);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);

    try {
      const res = await fetch(`/api/programs/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          ...formData,
          modules
        })
      });

      if (!res.ok) throw new Error('Failed to update program');

      toast({
        title: 'Success',
        description: 'Program updated successfully'
      });

      navigate('/programs');
    } catch (error) {
      console.error('Error updating program:', error);
      toast({
        title: 'Error',
        description: 'Failed to update program',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Edit Program</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <div className="p-6 space-y-6">
            <h2 className="text-lg font-semibold text-gray-800">Basic Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Program Name *
                </label>
                <Input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="Enter program name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category *
                </label>
                <Input
                  type="text"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                  placeholder="e.g., Web Development, Data Science"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Level
                </label>
                <Select
                  name="level"
                  value={formData.level}
                  onChange={handleChange}
                >
                  <option value="beginner">Beginner</option>
                  <option value="intermediate">Intermediate</option>
                  <option value="advanced">Advanced</option>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <Select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="draft">Draft</option>
                  <option value="published">Published</option>
                  <option value="active">Active</option>
                  <option value="archived">Archived</option>
                </Select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Duration (weeks)
                </label>
                <Input
                  type="number"
                  name="duration_weeks"
                  value={formData.duration_weeks}
                  onChange={handleChange}
                  min="1"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Participants
                </label>
                <Input
                  type="number"
                  name="max_participants"
                  value={formData.max_participants}
                  onChange={handleChange}
                  min="1"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Price
                </label>
                <div className="relative">
                  <Input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleChange}
                    min="0"
                    step="0.01"
                  />
                  <div className="absolute inset-y-0 right-0 flex items-center pr-3">
                    <span className="text-sm text-gray-500">{formData.currency}</span>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <Textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                placeholder="Enter program description"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Learning Objectives
                </label>
                <Textarea
                  name="objectives"
                  value={formData.objectives}
                  onChange={handleChange}
                  rows={3}
                  placeholder="Enter learning objectives"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Prerequisites
                </label>
                <Textarea
                  name="requirements"
                  value={formData.requirements}
                  onChange={handleChange}
                  rows={3}
                  placeholder="Enter prerequisites"
                />
              </div>
            </div>
          </div>
        </Card>

        {/* Modules Section */}
        <Card>
          <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">Program Modules</h2>
              <Button
                type="button"
                variant="outline"
                onClick={handleAddModule}
              >
                Add Module
              </Button>
            </div>

            {modules.length === 0 ? (
              <p className="text-sm text-gray-500">No modules added yet</p>
            ) : (
              <div className="space-y-4">
                {modules.map((module, index) => (
                  <div key={index} className="border rounded-lg p-4 space-y-3">
                    <div className="flex items-center justify-between">
                      <Badge>Module {index + 1}</Badge>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemoveModule(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Module Name
                        </label>
                        <Input
                          type="text"
                          value={module.name}
                          onChange={(e) => handleModuleChange(index, 'name', e.target.value)}
                          placeholder="Enter module name"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Duration (hours)
                        </label>
                        <Input
                          type="number"
                          value={module.duration_hours}
                          onChange={(e) => handleModuleChange(index, 'duration_hours', parseInt(e.target.value))}
                          min="1"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <Textarea
                        value={module.description}
                        onChange={(e) => handleModuleChange(index, 'description', e.target.value)}
                        rows={2}
                        placeholder="Enter module description"
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        <div className="flex items-center justify-end gap-3">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate('/programs')}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            disabled={saving}
          >
            {saving ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Changes
              </>
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};

export default EditProgramPage;