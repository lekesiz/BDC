import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Search, Plus, Filter, ListFilter, Eye, Edit, Copy, Archive, 
  AlertTriangle, CheckCircle, Clock, BarChart2, Users, Calendar 
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs } from '@/components/ui/tabs';
import { Select } from '@/components/ui/select';
import { useToast } from '@/components/ui/toast';
import EmptyState from '@/components/common/EmptyState';
/**
 * TrainerAssessmentsPage displays assessment templates and assigned assessments
 * for the trainer to manage
 */
const TrainerAssessmentsPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('templates');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  // State for templates, assigned assessments, and drafts
  const [templates, setTemplates] = useState([]);
  const [assignedAssessments, setAssignedAssessments] = useState([]);
  const [draftTemplates, setDraftTemplates] = useState([]);
  // State for search and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        // Fetch assessment templates (active)
        const templatesResponse = await fetch('/api/assessment/templates?status=active');
        if (!templatesResponse.ok) throw new Error('Failed to fetch templates');
        const templatesData = await templatesResponse.json();
        setTemplates(templatesData);
        // Fetch draft templates
        const draftsResponse = await fetch('/api/assessment/templates?status=draft');
        if (!draftsResponse.ok) throw new Error('Failed to fetch draft templates');
        const draftsData = await draftsResponse.json();
        setDraftTemplates(draftsData);
        // Fetch assigned assessments
        const assignedResponse = await fetch('/api/assessment/assigned');
        if (!assignedResponse.ok) throw new Error('Failed to fetch assigned assessments');
        const assignedData = await assignedResponse.json();
        setAssignedAssessments(assignedData);
      } catch (err) {
        console.error('Error fetching assessment data:', err);
        setError(err.message);
        toast({
          title: 'Error',
          description: 'Failed to load assessment data',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, [toast]);
  // Filter templates
  const filteredTemplates = templates.filter(template => {
    const matchesSearch = 
      searchTerm === '' || 
      template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = 
      selectedType === 'all' || 
      template.type === selectedType;
    const matchesCategory = 
      selectedCategory === 'all' || 
      (template.categories && template.categories.includes(selectedCategory));
    return matchesSearch && matchesType && matchesCategory;
  });
  // Filter draft templates
  const filteredDrafts = draftTemplates.filter(template => {
    const matchesSearch = 
      searchTerm === '' || 
      template.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      template.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = 
      selectedType === 'all' || 
      template.type === selectedType;
    const matchesCategory = 
      selectedCategory === 'all' || 
      (template.categories && template.categories.includes(selectedCategory));
    return matchesSearch && matchesType && matchesCategory;
  });
  // Filter assigned assessments
  const filteredAssigned = assignedAssessments.filter(assessment => {
    const matchesSearch = 
      searchTerm === '' || 
      assessment.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      assessment.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      assessment.assigned_to.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = 
      selectedStatus === 'all' || 
      assessment.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });
  // Handle creating new assessment
  const handleCreateAssessment = () => {
    navigate('/assessment/create');
  };
  // Handle editing template
  const handleEditTemplate = (templateId) => {
    navigate(`/assessment/edit/${templateId}`);
  };
  // Handle viewing template
  const handleViewTemplate = (templateId) => {
    navigate(`/assessment/templates/${templateId}`);
  };
  // Handle duplicating template
  const handleDuplicateTemplate = async (templateId) => {
    try {
      // Fetch the template to duplicate
      const response = await fetch(`/api/assessment/templates/${templateId}`);
      if (!response.ok) throw new Error('Failed to fetch template');
      const template = await response.json();
      // Create a duplicate with a new name
      const duplicateData = {
        ...template,
        title: `${template.title} (Copy)`,
        status: 'draft'
      };
      delete duplicateData.id;
      delete duplicateData.created_at;
      delete duplicateData.updated_at;
      // Save the duplicate
      const createResponse = await fetch('/api/assessment/templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(duplicateData),
      });
      if (!createResponse.ok) throw new Error('Failed to duplicate template');
      toast({
        title: 'Success',
        description: 'Template has been duplicated',
        type: 'success',
      });
      // Refresh the data
      const draftsResponse = await fetch('/api/assessment/templates?status=draft');
      const draftsData = await draftsResponse.json();
      setDraftTemplates(draftsData);
    } catch (err) {
      console.error('Error duplicating template:', err);
      toast({
        title: 'Error',
        description: 'Failed to duplicate template',
        type: 'error',
      });
    }
  };
  // Handle archiving template
  const handleArchiveTemplate = async (templateId) => {
    try {
      const response = await fetch(`/api/assessment/templates/${templateId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'archived' }),
      });
      if (!response.ok) throw new Error('Failed to archive template');
      toast({
        title: 'Success',
        description: 'Template has been archived',
        type: 'success',
      });
      // Refresh the templates
      const templatesResponse = await fetch('/api/assessment/templates?status=active');
      const templatesData = await templatesResponse.json();
      setTemplates(templatesData);
    } catch (err) {
      console.error('Error archiving template:', err);
      toast({
        title: 'Error',
        description: 'Failed to archive template',
        type: 'error',
      });
    }
  };
  // Handle assigning assessment
  const handleAssignAssessment = (templateId) => {
    navigate(`/assessment/assign/${templateId}`);
  };
  // Handle viewing assigned assessment
  const handleViewAssignment = (assignmentId) => {
    navigate(`/assessment/assigned/${assignmentId}`);
  };
  // Handle viewing results
  const handleViewResults = (assignmentId) => {
    navigate(`/assessment/assigned/${assignmentId}/results`);
  };
  // Render loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary"></div>
      </div>
    );
  }
  return (
    <div className="container mx-auto py-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-2">Assessment Management</h1>
          <p className="text-gray-600">Create, manage, and assign assessments to track beneficiary progress</p>
        </div>
        <div className="mt-4 md:mt-0 flex gap-3">
          <Button 
            variant="outline"
            onClick={() => navigate('/assessment/statistics')} 
            className="flex items-center"
          >
            <BarChart2 className="w-4 h-4 mr-2" />
            View Statistics
          </Button>
          <Button onClick={handleCreateAssessment} className="flex items-center">
            <Plus className="w-4 h-4 mr-2" />
            Create Assessment
          </Button>
        </div>
      </div>
      {/* Tabs */}
      <Tabs
        value={activeTab}
        onValueChange={setActiveTab}
        className="mb-6"
      >
        <Tabs.TabsList>
          <Tabs.TabTrigger value="templates">
            Templates ({templates.length})
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="assigned">
            Assigned ({assignedAssessments.length})
          </Tabs.TabTrigger>
          <Tabs.TabTrigger value="drafts">
            Drafts ({draftTemplates.length})
          </Tabs.TabTrigger>
        </Tabs.TabsList>
        {/* Search and filters */}
        <div className="flex flex-col md:flex-row gap-4 items-center mt-4 mb-6">
          <div className="relative flex-grow">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={16} />
            <Input 
              type="text" 
              placeholder="Search by title, description or cohort..." 
              className="pl-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          {(activeTab === 'templates' || activeTab === 'drafts') && (
            <>
              <Select
                value={selectedType}
                onValueChange={setSelectedType}
                className="w-full md:w-40"
              >
                <Select.Trigger>
                  <div className="flex items-center">
                    <Filter className="w-4 h-4 mr-2" />
                    <span>{selectedType === 'all' ? 'All Types' : selectedType}</span>
                  </div>
                </Select.Trigger>
                <Select.Content>
                  <Select.Item value="all">All Types</Select.Item>
                  <Select.Item value="quiz">Quiz</Select.Item>
                  <Select.Item value="project">Project</Select.Item>
                </Select.Content>
              </Select>
              <Select
                value={selectedCategory}
                onValueChange={setSelectedCategory}
                className="w-full md:w-40"
              >
                <Select.Trigger>
                  <div className="flex items-center">
                    <ListFilter className="w-4 h-4 mr-2" />
                    <span>{selectedCategory === 'all' ? 'All Categories' : selectedCategory}</span>
                  </div>
                </Select.Trigger>
                <Select.Content>
                  <Select.Item value="all">All Categories</Select.Item>
                  <Select.Item value="Fundamentals">Fundamentals</Select.Item>
                  <Select.Item value="Front-end">Front-end</Select.Item>
                  <Select.Item value="Advanced">Advanced</Select.Item>
                  <Select.Item value="Frameworks">Frameworks</Select.Item>
                  <Select.Item value="Portfolio">Portfolio</Select.Item>
                </Select.Content>
              </Select>
            </>
          )}
          {activeTab === 'assigned' && (
            <Select
              value={selectedStatus}
              onValueChange={setSelectedStatus}
              className="w-full md:w-40"
            >
              <Select.Trigger>
                <div className="flex items-center">
                  <ListFilter className="w-4 h-4 mr-2" />
                  <span>{selectedStatus === 'all' ? 'All Statuses' : selectedStatus}</span>
                </div>
              </Select.Trigger>
              <Select.Content>
                <Select.Item value="all">All Statuses</Select.Item>
                <Select.Item value="active">Active</Select.Item>
                <Select.Item value="scheduled">Scheduled</Select.Item>
                <Select.Item value="completed">Completed</Select.Item>
                <Select.Item value="canceled">Canceled</Select.Item>
              </Select.Content>
            </Select>
          )}
        </div>
        {/* Templates tab content */}
        <Tabs.TabContent value="templates">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}
          {filteredTemplates.length === 0 ? (
            <EmptyState
              title="No assessment templates found"
              description="Create your first assessment template to start evaluating beneficiaries"
              icon={<AlertTriangle size={50} />}
              actionLabel="Create Assessment"
              onAction={handleCreateAssessment}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredTemplates.map((template) => (
                <Card key={template.id} className="overflow-hidden">
                  <div className={`p-2 text-xs font-medium text-white uppercase tracking-wider ${
                    template.type === 'quiz' ? 'bg-blue-600' : 'bg-purple-600'
                  }`}>
                    {template.type}
                  </div>
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-lg font-semibold">{template.title}</h3>
                      <Badge className={template.type === 'quiz' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                        {template.type}
                      </Badge>
                    </div>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">{template.description}</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {template.skills?.slice(0, 3).map((skill, index) => (
                        <Badge key={index} variant="outline" className="bg-gray-100">
                          {skill}
                        </Badge>
                      ))}
                      {template.skills?.length > 3 && (
                        <Badge variant="outline" className="bg-gray-100">
                          +{template.skills.length - 3} more
                        </Badge>
                      )}
                    </div>
                    <div className="space-y-2 mb-4">
                      {template.type === 'quiz' && (
                        <>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Questions:</span>
                            <span className="font-medium">{template.questions?.length || 0}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Time Limit:</span>
                            <span className="font-medium">{template.settings?.timeLimit || 0} minutes</span>
                          </div>
                        </>
                      )}
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Created:</span>
                        <span className="font-medium">{formatDistanceToNow(new Date(template.created_at), { addSuffix: true })}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Usage Count:</span>
                        <span className="font-medium">{template.usageCount}</span>
                      </div>
                      {template.averageScore && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Avg. Score:</span>
                          <span className="font-medium">{template.averageScore}%</span>
                        </div>
                      )}
                    </div>
                    <div className="flex flex-wrap gap-2 mt-6">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => handleViewTemplate(template.id)}
                        className="flex items-center"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        View
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => handleEditTemplate(template.id)}
                        className="flex items-center"
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Edit
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => handleDuplicateTemplate(template.id)}
                        className="flex items-center"
                      >
                        <Copy className="w-4 h-4 mr-2" />
                        Duplicate
                      </Button>
                      <Button 
                        size="sm" 
                        variant="primary" 
                        onClick={() => handleAssignAssessment(template.id)}
                        className="flex items-center mt-2 w-full"
                      >
                        <Users className="w-4 h-4 mr-2" />
                        Assign
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Tabs.TabContent>
        {/* Assigned tab content */}
        <Tabs.TabContent value="assigned">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}
          {filteredAssigned.length === 0 ? (
            <EmptyState
              title="No assigned assessments found"
              description="Assign an assessment template to a cohort or individual beneficiaries"
              icon={<Users size={50} />}
              actionLabel="Create Assignment"
              onAction={() => setActiveTab('templates')}
            />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredAssigned.map((assessment) => (
                <Card key={assessment.id} className="overflow-hidden">
                  <div className={`p-2 text-xs font-medium text-white uppercase tracking-wider ${
                    assessment.status === 'active' ? 'bg-green-600' : 
                    assessment.status === 'scheduled' ? 'bg-amber-600' : 'bg-blue-600'
                  }`}>
                    {assessment.status}
                  </div>
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-lg font-semibold">{assessment.title}</h3>
                      <div className="flex items-center">
                        {assessment.status === 'active' && <CheckCircle className="w-4 h-4 text-green-500 mr-1" />}
                        {assessment.status === 'scheduled' && <Clock className="w-4 h-4 text-amber-500 mr-1" />}
                        {assessment.status === 'completed' && <BarChart2 className="w-4 h-4 text-blue-500 mr-1" />}
                        <Badge className={
                          assessment.status === 'active' ? 'bg-green-100 text-green-800' : 
                          assessment.status === 'scheduled' ? 'bg-amber-100 text-amber-800' : 
                          'bg-blue-100 text-blue-800'
                        }>
                          {assessment.status}
                        </Badge>
                      </div>
                    </div>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">{assessment.description}</p>
                    <div className="p-3 bg-gray-50 rounded-lg mb-4">
                      <div className="flex items-center mb-2">
                        <Users className="w-4 h-4 text-gray-500 mr-2" />
                        <div>
                          <p className="text-sm font-medium">
                            {assessment.assigned_to.type === 'cohort' ? 'Cohort:' : 'Individual:'}
                          </p>
                          <p className="text-sm text-gray-600">{assessment.assigned_to.name}</p>
                        </div>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 text-gray-500 mr-2" />
                        <div>
                          <p className="text-sm font-medium">Due Date:</p>
                          <p className="text-sm text-gray-600">
                            {new Date(assessment.due_date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              year: 'numeric'
                            })}
                          </p>
                        </div>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="bg-blue-50 p-3 rounded-lg text-center">
                        <p className="text-sm text-gray-600">Total</p>
                        <p className="text-lg font-semibold text-blue-700">{assessment.submissions.total}</p>
                      </div>
                      <div className="bg-green-50 p-3 rounded-lg text-center">
                        <p className="text-sm text-gray-600">Completed</p>
                        <p className="text-lg font-semibold text-green-700">{assessment.submissions.completed}</p>
                      </div>
                      <div className="bg-amber-50 p-3 rounded-lg text-center">
                        <p className="text-sm text-gray-600">In Progress</p>
                        <p className="text-lg font-semibold text-amber-700">{assessment.submissions.inProgress}</p>
                      </div>
                    </div>
                    {assessment.submissions.averageScore !== null && (
                      <div className="p-3 bg-purple-50 rounded-lg mb-4 text-center">
                        <p className="text-sm text-gray-600">Average Score</p>
                        <p className="text-xl font-semibold text-purple-700">{assessment.submissions.averageScore}%</p>
                      </div>
                    )}
                    <div className="flex flex-wrap gap-2 mt-6">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => handleViewAssignment(assessment.id)}
                        className="flex items-center"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Details
                      </Button>
                      {assessment.submissions.completed > 0 && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => handleViewResults(assessment.id)}
                          className="flex items-center"
                        >
                          <BarChart2 className="w-4 h-4 mr-2" />
                          Results
                        </Button>
                      )}
                      {assessment.status === 'active' && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          className="flex items-center ml-auto"
                        >
                          <AlertTriangle className="w-4 h-4 mr-2" />
                          Send Reminder
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Tabs.TabContent>
        {/* Drafts tab content */}
        <Tabs.TabContent value="drafts">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}
          {filteredDrafts.length === 0 ? (
            <EmptyState
              title="No draft templates found"
              description="Draft templates are assessments you've started but haven't published yet"
              icon={<Edit size={50} />}
              actionLabel="Create Assessment"
              onAction={handleCreateAssessment}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredDrafts.map((template) => (
                <Card key={template.id} className="overflow-hidden">
                  <div className="p-2 text-xs font-medium text-white uppercase tracking-wider bg-gray-600">
                    Draft
                  </div>
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-lg font-semibold">{template.title}</h3>
                      <Badge className={template.type === 'quiz' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'}>
                        {template.type}
                      </Badge>
                    </div>
                    <p className="text-gray-600 text-sm mb-4 line-clamp-2">{template.description}</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {template.skills?.slice(0, 3).map((skill, index) => (
                        <Badge key={index} variant="outline" className="bg-gray-100">
                          {skill}
                        </Badge>
                      ))}
                      {template.skills?.length > 3 && (
                        <Badge variant="outline" className="bg-gray-100">
                          +{template.skills.length - 3} more
                        </Badge>
                      )}
                    </div>
                    <div className="space-y-2 mb-4">
                      {template.type === 'quiz' && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Questions:</span>
                          <span className="font-medium">{template.questions?.length || 0}</span>
                        </div>
                      )}
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Last Updated:</span>
                        <span className="font-medium">{formatDistanceToNow(new Date(template.updated_at || template.created_at), { addSuffix: true })}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">Created By:</span>
                        <span className="font-medium">{template.creator_name}</span>
                      </div>
                    </div>
                    <div className="flex flex-wrap gap-2 mt-6">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        onClick={() => handleViewTemplate(template.id)}
                        className="flex items-center"
                      >
                        <Eye className="w-4 h-4 mr-2" />
                        Preview
                      </Button>
                      <Button 
                        size="sm" 
                        variant="primary" 
                        onClick={() => handleEditTemplate(template.id)}
                        className="flex items-center"
                      >
                        <Edit className="w-4 h-4 mr-2" />
                        Continue Editing
                      </Button>
                      <Button 
                        size="sm" 
                        variant="destructive" 
                        onClick={() => handleArchiveTemplate(template.id)}
                        className="flex items-center mt-2"
                      >
                        <Archive className="w-4 h-4 mr-2" />
                        Archive
                      </Button>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Tabs.TabContent>
      </Tabs>
    </div>
  );
};
export default TrainerAssessmentsPage;