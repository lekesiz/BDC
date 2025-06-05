import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Modal } from '../../components/ui/modal';
import {
  Loader2,
  FileText,
  Plus,
  Search,
  Download,
  Upload,
  Edit,
  Trash2,
  Copy,
  Files
} from 'lucide-react';
const DocumentTemplatesPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [templates, setTemplates] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [templateForm, setTemplateForm] = useState({
    name: '',
    description: '',
    category: 'general'
  });
  const templateCategories = [
    'all',
    'contracts', 
    'certificates',
    'reports',
    'evaluations',
    'general'
  ];
  useEffect(() => {
    fetchTemplates();
  }, []);
  const fetchTemplates = async () => {
    try {
      const res = await fetch('/api/documents/templates', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch templates');
      const data = await res.json();
      setTemplates(data);
    } catch (error) {
      console.error('Error fetching templates:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch document templates',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleUploadTemplate = async () => {
    if (!uploadFile || !templateForm.name) {
      toast({
        title: 'Error',
        description: 'Please provide a template name and file',
        variant: 'destructive'
      });
      return;
    }
    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('name', templateForm.name);
    formData.append('description', templateForm.description);
    formData.append('category', templateForm.category);
    try {
      const res = await fetch('/api/documents/templates', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });
      if (!res.ok) throw new Error('Failed to upload template');
      toast({
        title: 'Success',
        description: 'Template uploaded successfully'
      });
      fetchTemplates();
      setShowUploadModal(false);
      resetUploadForm();
    } catch (error) {
      console.error('Error uploading template:', error);
      toast({
        title: 'Error',
        description: 'Failed to upload template',
        variant: 'destructive'
      });
    } finally {
      setUploading(false);
    }
  };
  const handleDeleteTemplate = async (templateId) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    try {
      const res = await fetch(`/api/documents/templates/${templateId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to delete template');
      toast({
        title: 'Success',
        description: 'Template deleted successfully'
      });
      fetchTemplates();
    } catch (error) {
      console.error('Error deleting template:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete template',
        variant: 'destructive'
      });
    }
  };
  const handleDuplicateTemplate = async (templateId) => {
    try {
      const res = await fetch(`/api/documents/templates/${templateId}/duplicate`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to duplicate template');
      toast({
        title: 'Success',
        description: 'Template duplicated successfully'
      });
      fetchTemplates();
    } catch (error) {
      console.error('Error duplicating template:', error);
      toast({
        title: 'Error',
        description: 'Failed to duplicate template',
        variant: 'destructive'
      });
    }
  };
  const resetUploadForm = () => {
    setTemplateForm({
      name: '',
      description: '',
      category: 'general'
    });
    setUploadFile(null);
  };
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });
  const getCategoryIcon = (category) => {
    switch (category) {
      case 'contracts':
        return '📑';
      case 'certificates':
        return '🏆';
      case 'reports':
        return '📊';
      case 'evaluations':
        return '📋';
      default:
        return '📄';
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
        <h1 className="text-2xl font-bold text-gray-900">Document Templates</h1>
        <Button onClick={() => setShowUploadModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          New Template
        </Button>
      </div>
      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
          <Input
            type="text"
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        <div className="flex gap-2">
          {templateCategories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(category)}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </Button>
          ))}
        </div>
      </div>
      {/* Templates Grid */}
      {filteredTemplates.length === 0 ? (
        <Card className="p-8 text-center">
          <Files className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No templates found</h3>
          <p className="text-gray-500">
            {searchTerm || selectedCategory !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Upload your first template to get started'}
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredTemplates.map((template) => (
            <Card key={template.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{getCategoryIcon(template.category)}</span>
                      <h3 className="font-semibold text-gray-900">{template.name}</h3>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                  </div>
                  <Badge variant="secondary">
                    {template.category}
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <div>
                    <p>Format: {template.file_type?.toUpperCase()}</p>
                    <p>Size: {(template.file_size / 1024).toFixed(1)} KB</p>
                  </div>
                  <div>
                    <p>Created: {new Date(template.created_at).toLocaleDateString()}</p>
                    <p>Used: {template.usage_count} times</p>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open(`/api/documents/templates/${template.id}/download`)}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => navigate(`/documents/create-from-template/${template.id}`)}
                  >
                    <FileText className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDuplicateTemplate(template.id)}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                  {(user.role === 'super_admin' || user.role === 'tenant_admin') && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/documents/templates/${template.id}/edit`)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDeleteTemplate(template.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
      {/* Upload Modal */}
      <Modal
        isOpen={showUploadModal}
        onClose={() => {
          setShowUploadModal(false);
          resetUploadForm();
        }}
        title="Upload New Template"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Template Name *
            </label>
            <Input
              type="text"
              value={templateForm.name}
              onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
              placeholder="Enter template name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <Input
              type="text"
              value={templateForm.description}
              onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
              placeholder="Enter template description"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category
            </label>
            <select
              value={templateForm.category}
              onChange={(e) => setTemplateForm({ ...templateForm, category: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="general">General</option>
              <option value="contracts">Contracts</option>
              <option value="certificates">Certificates</option>
              <option value="reports">Reports</option>
              <option value="evaluations">Evaluations</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Template File *
            </label>
            <input
              type="file"
              onChange={(e) => setUploadFile(e.target.files[0])}
              accept=".doc,.docx,.pdf,.xls,.xlsx"
              className="w-full"
            />
            <p className="text-sm text-gray-500 mt-1">
              Accepted formats: DOC, DOCX, PDF, XLS, XLSX
            </p>
          </div>
          <div className="flex justify-end gap-3">
            <Button
              variant="outline"
              onClick={() => {
                setShowUploadModal(false);
                resetUploadForm();
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleUploadTemplate}
              disabled={uploading || !uploadFile || !templateForm.name}
            >
              {uploading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Template
                </>
              )}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
export default DocumentTemplatesPage;