import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Plus, X, Save, Settings, Eye, Upload, Download, Copy, Trash2, ArrowUp, ArrowDown } from 'lucide-react';
import axios from '../../lib/api';
import { toast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Input } from '../../components/ui/input';
import { Select } from '../../components/ui/select';
import { Textarea } from '../../components/ui';
import { Tabs } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
const TrainerRubricBuilderPage = () => {
  const navigate = useNavigate();
  const { rubricId } = useParams();
  const isEditMode = !!rubricId;
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [rubric, setRubric] = useState({
    title: '',
    description: '',
    type: 'analytic', // analytic or holistic
    criteria: [],
    settings: {
      pointsScale: 'percentage', // percentage, points, custom
      maxPoints: 100,
      passingScore: 70,
      allowPartialPoints: true,
      showFeedback: true,
      autoCalculate: true
    },
    status: 'draft' // draft, published, archived
  });
  const [activeTab, setActiveTab] = useState('criteria');
  const [showPreview, setShowPreview] = useState(false);
  const [templates, setTemplates] = useState([]);
  useEffect(() => {
    if (isEditMode) {
      fetchRubric();
    } else {
      fetchTemplates();
      setLoading(false);
    }
  }, [rubricId]);
  const fetchRubric = async () => {
    try {
      const response = await axios.get(`/api/rubrics/${rubricId}`);
      setRubric(response.data);
    } catch (error) {
      console.error('Error fetching rubric:', error);
      toast({
        title: 'Error',
        description: 'Failed to load rubric',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };
  const fetchTemplates = async () => {
    try {
      const response = await axios.get('/api/rubrics/templates');
      setTemplates(response.data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };
  const handleAddCriterion = () => {
    const newCriterion = {
      id: Date.now().toString(),
      name: 'New Criterion',
      description: '',
      weight: 25,
      levels: [
        { id: '1', name: 'Excellent', description: '', points: 100 },
        { id: '2', name: 'Good', description: '', points: 75 },
        { id: '3', name: 'Satisfactory', description: '', points: 50 },
        { id: '4', name: 'Needs Improvement', description: '', points: 25 }
      ]
    };
    setRubric({
      ...rubric,
      criteria: [...rubric.criteria, newCriterion]
    });
  };
  const handleUpdateCriterion = (criterionId, updates) => {
    setRubric({
      ...rubric,
      criteria: rubric.criteria.map(criterion =>
        criterion.id === criterionId ? { ...criterion, ...updates } : criterion
      )
    });
  };
  const handleRemoveCriterion = (criterionId) => {
    setRubric({
      ...rubric,
      criteria: rubric.criteria.filter(criterion => criterion.id !== criterionId)
    });
  };
  const handleAddLevel = (criterionId) => {
    const criterion = rubric.criteria.find(c => c.id === criterionId);
    const newLevel = {
      id: Date.now().toString(),
      name: 'New Level',
      description: '',
      points: 0
    };
    handleUpdateCriterion(criterionId, {
      levels: [...criterion.levels, newLevel]
    });
  };
  const handleUpdateLevel = (criterionId, levelId, updates) => {
    const criterion = rubric.criteria.find(c => c.id === criterionId);
    const updatedLevels = criterion.levels.map(level =>
      level.id === levelId ? { ...level, ...updates } : level
    );
    handleUpdateCriterion(criterionId, { levels: updatedLevels });
  };
  const handleRemoveLevel = (criterionId, levelId) => {
    const criterion = rubric.criteria.find(c => c.id === criterionId);
    const updatedLevels = criterion.levels.filter(level => level.id !== levelId);
    handleUpdateCriterion(criterionId, { levels: updatedLevels });
  };
  const handleMoveCriterion = (index, direction) => {
    const newCriteria = [...rubric.criteria];
    const item = newCriteria[index];
    newCriteria.splice(index, 1);
    newCriteria.splice(index + direction, 0, item);
    setRubric({
      ...rubric,
      criteria: newCriteria
    });
  };
  const handleSaveRubric = async () => {
    if (!rubric.title.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a rubric title',
        variant: 'error'
      });
      return;
    }
    if (rubric.criteria.length === 0) {
      toast({
        title: 'Error',
        description: 'Please add at least one criterion',
        variant: 'error'
      });
      return;
    }
    setSaving(true);
    try {
      if (isEditMode) {
        await axios.put(`/api/rubrics/${rubricId}`, rubric);
        toast({
          title: 'Success',
          description: 'Rubric updated successfully',
          variant: 'success'
        });
      } else {
        const response = await axios.post('/api/rubrics', rubric);
        toast({
          title: 'Success',
          description: 'Rubric created successfully',
          variant: 'success'
        });
        navigate(`/assessment/rubrics/${response.data.id}/edit`);
      }
    } catch (error) {
      console.error('Error saving rubric:', error);
      toast({
        title: 'Error',
        description: 'Failed to save rubric',
        variant: 'error'
      });
    } finally {
      setSaving(false);
    }
  };
  const handleApplyTemplate = (template) => {
    setRubric({
      ...rubric,
      ...template,
      id: rubric.id // Keep the current ID if editing
    });
    toast({
      title: 'Success',
      description: 'Template applied successfully',
      variant: 'success'
    });
  };
  const handleExportRubric = () => {
    const dataStr = JSON.stringify(rubric, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `${rubric.title.replace(/\s+/g, '-')}-rubric.json`;
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };
  const handleImportRubric = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedRubric = JSON.parse(e.target.result);
        setRubric({
          ...importedRubric,
          id: rubric.id // Keep the current ID if editing
        });
        toast({
          title: 'Success',
          description: 'Rubric imported successfully',
          variant: 'success'
        });
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Invalid rubric file',
          variant: 'error'
        });
      }
    };
    reader.readAsText(file);
  };
  const calculateTotalWeight = () => {
    return rubric.criteria.reduce((sum, criterion) => sum + (criterion.weight || 0), 0);
  };
  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="h-64 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">
            {isEditMode ? 'Edit Rubric' : 'Create Rubric'}
          </h1>
          <div className="flex gap-2">
            <label htmlFor="import-file" className="cursor-pointer">
              <Button variant="outline" as="span">
                <Upload className="h-4 w-4 mr-2" />
                Import
              </Button>
              <input
                id="import-file"
                type="file"
                accept=".json"
                className="hidden"
                onChange={handleImportRubric}
              />
            </label>
            <Button onClick={handleExportRubric} variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button
              onClick={() => setShowPreview(!showPreview)}
              variant="outline"
            >
              <Eye className="h-4 w-4 mr-2" />
              {showPreview ? 'Hide' : 'Show'} Preview
            </Button>
            <Button
              onClick={handleSaveRubric}
              disabled={saving}
            >
              <Save className="h-4 w-4 mr-2" />
              Save Rubric
            </Button>
          </div>
        </div>
      </div>
      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
        <Tabs.TabsList>
          <Tabs.TabTrigger value="basic">Basic Information</Tabs.TabTrigger>
          <Tabs.TabTrigger value="criteria">Criteria & Levels</Tabs.TabTrigger>
          <Tabs.TabTrigger value="settings">Settings</Tabs.TabTrigger>
          <Tabs.TabTrigger value="templates">Templates</Tabs.TabTrigger>
        </Tabs.TabsList>
        {/* Basic Information Tab */}
        <Tabs.TabContent value="basic">
          <Card className="p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rubric Title *
                </label>
                <Input
                  value={rubric.title}
                  onChange={(e) => setRubric({ ...rubric, title: e.target.value })}
                  placeholder="Enter rubric title"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <Textarea
                  value={rubric.description}
                  onChange={(e) => setRubric({ ...rubric, description: e.target.value })}
                  placeholder="Enter rubric description"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rubric Type
                </label>
                <Select
                  value={rubric.type}
                  onValueChange={(value) => setRubric({ ...rubric, type: value })}
                >
                  <Select.Option value="analytic">Analytic Rubric</Select.Option>
                  <Select.Option value="holistic">Holistic Rubric</Select.Option>
                </Select>
                <p className="text-sm text-gray-600 mt-1">
                  {rubric.type === 'analytic' 
                    ? 'Breaks down assessment into multiple criteria with individual scores'
                    : 'Provides a single overall score based on general performance levels'
                  }
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status
                </label>
                <Select
                  value={rubric.status}
                  onValueChange={(value) => setRubric({ ...rubric, status: value })}
                >
                  <Select.Option value="draft">Draft</Select.Option>
                  <Select.Option value="published">Published</Select.Option>
                  <Select.Option value="archived">Archived</Select.Option>
                </Select>
              </div>
            </div>
          </Card>
        </Tabs.TabContent>
        {/* Criteria & Levels Tab */}
        <Tabs.TabContent value="criteria">
          <Card className="p-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Criteria</h3>
                <p className="text-sm text-gray-600">
                  Total Weight: {calculateTotalWeight()}%
                  {calculateTotalWeight() !== 100 && (
                    <span className="text-yellow-600 ml-2">
                      (Should equal 100%)
                    </span>
                  )}
                </p>
              </div>
              <Button onClick={handleAddCriterion}>
                <Plus className="h-4 w-4 mr-2" />
                Add Criterion
              </Button>
            </div>
            <div className="space-y-4">
              {rubric.criteria.map((criterion, index) => (
                <Card key={criterion.id} className="p-4">
                  <div className="flex items-start gap-3">
                    <div className="flex flex-col gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleMoveCriterion(index, -1)}
                        disabled={index === 0}
                      >
                        <ArrowUp className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleMoveCriterion(index, 1)}
                        disabled={index === rubric.criteria.length - 1}
                      >
                        <ArrowDown className="h-4 w-4" />
                      </Button>
                    </div>
                    <div className="flex-1 space-y-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-3">
                          <div className="flex items-center gap-3">
                            <Input
                              value={criterion.name}
                              onChange={(e) => handleUpdateCriterion(criterion.id, { name: e.target.value })}
                              placeholder="Criterion name"
                              className="font-medium"
                            />
                            <Input
                              type="number"
                              value={criterion.weight}
                              onChange={(e) => handleUpdateCriterion(criterion.id, { weight: parseInt(e.target.value) || 0 })}
                              placeholder="Weight"
                              className="w-24"
                              min="0"
                              max="100"
                            />
                            <span className="text-gray-600">%</span>
                          </div>
                          <Textarea
                            value={criterion.description}
                            onChange={(e) => handleUpdateCriterion(criterion.id, { description: e.target.value })}
                            placeholder="Criterion description"
                            rows={2}
                          />
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveCriterion(criterion.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                      {/* Performance Levels */}
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="font-medium text-sm">Performance Levels</h4>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAddLevel(criterion.id)}
                          >
                            <Plus className="h-3 w-3 mr-1" />
                            Add Level
                          </Button>
                        </div>
                        <div className="space-y-2">
                          {criterion.levels.map((level, levelIndex) => (
                            <div key={level.id} className="flex items-start gap-2">
                              <div className="flex-1 grid grid-cols-12 gap-2">
                                <Input
                                  value={level.name}
                                  onChange={(e) => handleUpdateLevel(criterion.id, level.id, { name: e.target.value })}
                                  placeholder="Level name"
                                  className="col-span-3"
                                />
                                <Textarea
                                  value={level.description}
                                  onChange={(e) => handleUpdateLevel(criterion.id, level.id, { description: e.target.value })}
                                  placeholder="Level description"
                                  className="col-span-7"
                                  rows={1}
                                />
                                <Input
                                  type="number"
                                  value={level.points}
                                  onChange={(e) => handleUpdateLevel(criterion.id, level.id, { points: parseInt(e.target.value) || 0 })}
                                  placeholder="Points"
                                  className="col-span-2"
                                  min="0"
                                  max="100"
                                />
                              </div>
                              {criterion.levels.length > 1 && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => handleRemoveLevel(criterion.id, level.id)}
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </Card>
        </Tabs.TabContent>
        {/* Settings Tab */}
        <Tabs.TabContent value="settings">
          <Card className="p-6">
            <div className="space-y-4 max-w-2xl">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Points Scale
                </label>
                <Select
                  value={rubric.settings.pointsScale}
                  onValueChange={(value) => setRubric({
                    ...rubric,
                    settings: { ...rubric.settings, pointsScale: value }
                  })}
                >
                  <Select.Option value="percentage">Percentage (0-100%)</Select.Option>
                  <Select.Option value="points">Points</Select.Option>
                  <Select.Option value="custom">Custom Scale</Select.Option>
                </Select>
              </div>
              {rubric.settings.pointsScale === 'points' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Maximum Points
                  </label>
                  <Input
                    type="number"
                    value={rubric.settings.maxPoints}
                    onChange={(e) => setRubric({
                      ...rubric,
                      settings: { ...rubric.settings, maxPoints: parseInt(e.target.value) || 0 }
                    })}
                    min="1"
                  />
                </div>
              )}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Passing Score
                </label>
                <div className="flex items-center gap-2">
                  <Input
                    type="number"
                    value={rubric.settings.passingScore}
                    onChange={(e) => setRubric({
                      ...rubric,
                      settings: { ...rubric.settings, passingScore: parseInt(e.target.value) || 0 }
                    })}
                    min="0"
                    max="100"
                    className="w-24"
                  />
                  <span className="text-gray-600">%</span>
                </div>
              </div>
              <div className="space-y-3">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={rubric.settings.allowPartialPoints}
                    onChange={(e) => setRubric({
                      ...rubric,
                      settings: { ...rubric.settings, allowPartialPoints: e.target.checked }
                    })}
                    className="rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Allow partial points between levels
                  </span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={rubric.settings.showFeedback}
                    onChange={(e) => setRubric({
                      ...rubric,
                      settings: { ...rubric.settings, showFeedback: e.target.checked }
                    })}
                    className="rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Show level descriptions as feedback
                  </span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={rubric.settings.autoCalculate}
                    onChange={(e) => setRubric({
                      ...rubric,
                      settings: { ...rubric.settings, autoCalculate: e.target.checked }
                    })}
                    className="rounded"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Auto-calculate total score
                  </span>
                </label>
              </div>
            </div>
          </Card>
        </Tabs.TabContent>
        {/* Templates Tab */}
        <Tabs.TabContent value="templates">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Rubric Templates</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map(template => (
                <Card key={template.id} className="p-4">
                  <h4 className="font-medium mb-2">{template.title}</h4>
                  <p className="text-sm text-gray-600 mb-3">{template.description}</p>
                  <div className="flex items-center justify-between">
                    <Badge variant="secondary">{template.type}</Badge>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleApplyTemplate(template)}
                    >
                      <Copy className="h-3 w-3 mr-1" />
                      Use Template
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </Card>
        </Tabs.TabContent>
      </Tabs>
      {/* Preview Panel */}
      {showPreview && (
        <Card className="mt-6 p-6">
          <h3 className="text-lg font-semibold mb-4">Rubric Preview</h3>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-gray-900">
                    Criteria ({calculateTotalWeight()}%)
                  </th>
                  {rubric.criteria[0]?.levels.map(level => (
                    <th key={level.id} className="px-4 py-3 text-center font-medium text-gray-900 border-l">
                      {level.name}
                      <div className="text-sm font-normal text-gray-600">
                        {level.points} {rubric.settings.pointsScale === 'percentage' ? '%' : 'pts'}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rubric.criteria.map((criterion, index) => (
                  <tr key={criterion.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                    <td className="px-4 py-3">
                      <div className="font-medium">{criterion.name}</div>
                      <div className="text-sm text-gray-600">{criterion.description}</div>
                      <div className="text-sm text-gray-500 mt-1">Weight: {criterion.weight}%</div>
                    </td>
                    {criterion.levels.map(level => (
                      <td key={level.id} className="px-4 py-3 text-sm border-l">
                        {level.description}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};
export default TrainerRubricBuilderPage;