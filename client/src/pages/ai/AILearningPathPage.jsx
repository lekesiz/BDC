import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import {
  Loader2,
  Map,
  Target,
  Clock,
  CheckCircle,
  AlertCircle,
  ChevronRight,
  Play,
  Pause,
  RotateCcw,
  Download,
  Share2,
  BookOpen,
  Lock
} from 'lucide-react';
const AILearningPathPage = () => {
  const { user, hasRole } = useAuth();
  const { toast } = useToast();
  // AI Learning Path is restricted to admin and trainer roles only
  const canAccessLearningPath = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  // If user doesn't have permission, show access denied
  if (!canAccessLearningPath) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="p-8 text-center max-w-md">
          <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Restricted</h2>
          <p className="text-gray-600 mb-4">
            AI Learning Path Optimization is only available to administrators and trainers.
          </p>
          <p className="text-sm text-gray-500">
            Current role: <span className="font-medium">{user?.role}</span>
          </p>
        </Card>
      </div>
    );
  }
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [learningPaths, setLearningPaths] = useState([]);
  const [selectedPath, setSelectedPath] = useState(null);
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [selectedBeneficiary, setSelectedBeneficiary] = useState('');
  const [pathSettings, setPathSettings] = useState({
    duration: '3_months',
    intensity: 'moderate',
    focus_areas: [],
    learning_style: 'balanced'
  });
  const focusAreas = [
    'technical_skills',
    'soft_skills',
    'leadership',
    'communication',
    'problem_solving',
    'creativity',
    'time_management',
    'teamwork'
  ];
  const learningStyles = [
    { value: 'visual', label: 'Visual Learning' },
    { value: 'auditory', label: 'Auditory Learning' },
    { value: 'kinesthetic', label: 'Hands-on Learning' },
    { value: 'reading', label: 'Reading/Writing' },
    { value: 'balanced', label: 'Balanced Approach' }
  ];
  useEffect(() => {
    fetchBeneficiaries();
    fetchLearningPaths();
  }, []);
  const fetchBeneficiaries = async () => {
    try {
      const res = await fetch('/api/beneficiaries', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch beneficiaries');
      const data = await res.json();
      setBeneficiaries(data);
    } catch (error) {
      console.error('Error fetching beneficiaries:', error);
    }
  };
  const fetchLearningPaths = async () => {
    try {
      const res = await fetch('/api/ai/learning-paths', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch learning paths');
      const data = await res.json();
      setLearningPaths(data);
    } catch (error) {
      console.error('Error fetching learning paths:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch learning paths',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleGeneratePath = async () => {
    // Additional permission check for path generation
    if (!hasRole(['super_admin', 'tenant_admin', 'trainer'])) {
      toast({
        title: 'Access Denied',
        description: 'Learning path generation is restricted to administrators and trainers only',
        variant: 'destructive'
      });
      return;
    }
    if (!selectedBeneficiary) {
      toast({
        title: 'Error',
        description: 'Please select a beneficiary',
        variant: 'destructive'
      });
      return;
    }
    setGenerating(true);
    try {
      const res = await fetch('/api/ai/learning-paths/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          beneficiary_id: selectedBeneficiary,
          settings: pathSettings
        })
      });
      if (!res.ok) throw new Error('Failed to generate learning path');
      const data = await res.json();
      setSelectedPath(data);
      fetchLearningPaths();
      toast({
        title: 'Success',
        description: 'Learning path generated successfully'
      });
    } catch (error) {
      console.error('Error generating learning path:', error);
      toast({
        title: 'Error',
        description: 'Failed to generate learning path',
        variant: 'destructive'
      });
    } finally {
      setGenerating(false);
    }
  };
  const handleStartPath = async (pathId) => {
    // Additional permission check for starting paths
    if (!hasRole(['super_admin', 'tenant_admin', 'trainer'])) {
      toast({
        title: 'Access Denied',
        description: 'Starting learning paths is restricted to administrators and trainers only',
        variant: 'destructive'
      });
      return;
    }
    try {
      const res = await fetch(`/api/ai/learning-paths/${pathId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to start learning path');
      toast({
        title: 'Success',
        description: 'Learning path started'
      });
      fetchLearningPaths();
    } catch (error) {
      console.error('Error starting path:', error);
      toast({
        title: 'Error',
        description: 'Failed to start learning path',
        variant: 'destructive'
      });
    }
  };
  const handleExportPath = async (pathId) => {
    // Additional permission check for export functionality
    if (!hasRole(['super_admin', 'tenant_admin', 'trainer'])) {
      toast({
        title: 'Access Denied',
        description: 'Export functionality is restricted to administrators and trainers only',
        variant: 'destructive'
      });
      return;
    }
    try {
      const res = await fetch(`/api/ai/learning-paths/${pathId}/export`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to export path');
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `learning_path_${pathId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error exporting path:', error);
      toast({
        title: 'Error',
        description: 'Failed to export learning path',
        variant: 'destructive'
      });
    }
  };
  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'overdue':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
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
        <div className="flex items-center gap-3">
          <Map className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">AI Learning Path Optimization</h1>
        </div>
      </div>
      {/* Generate New Path */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Generate New Learning Path</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Beneficiary
            </label>
            <select
              value={selectedBeneficiary}
              onChange={(e) => setSelectedBeneficiary(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select beneficiary</option>
              {beneficiaries.map((beneficiary) => (
                <option key={beneficiary.id} value={beneficiary.id}>
                  {beneficiary.full_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Duration
            </label>
            <select
              value={pathSettings.duration}
              onChange={(e) => setPathSettings({ ...pathSettings, duration: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="1_month">1 Month</option>
              <option value="3_months">3 Months</option>
              <option value="6_months">6 Months</option>
              <option value="1_year">1 Year</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Intensity
            </label>
            <select
              value={pathSettings.intensity}
              onChange={(e) => setPathSettings({ ...pathSettings, intensity: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="light">Light (2-3 hrs/week)</option>
              <option value="moderate">Moderate (5-8 hrs/week)</option>
              <option value="intensive">Intensive (10+ hrs/week)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Learning Style
            </label>
            <select
              value={pathSettings.learning_style}
              onChange={(e) => setPathSettings({ ...pathSettings, learning_style: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              {learningStyles.map((style) => (
                <option key={style.value} value={style.value}>
                  {style.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Focus Areas
          </label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {focusAreas.map((area) => (
              <label key={area} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={pathSettings.focus_areas.includes(area)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setPathSettings({
                        ...pathSettings,
                        focus_areas: [...pathSettings.focus_areas, area]
                      });
                    } else {
                      setPathSettings({
                        ...pathSettings,
                        focus_areas: pathSettings.focus_areas.filter(a => a !== area)
                      });
                    }
                  }}
                  className="rounded text-primary"
                />
                <span className="text-sm">
                  {area.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                </span>
              </label>
            ))}
          </div>
        </div>
        <Button
          onClick={handleGeneratePath}
          disabled={generating || !selectedBeneficiary}
          className="w-full md:w-auto"
        >
          {generating ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Map className="h-4 w-4 mr-2" />
              Generate Learning Path
            </>
          )}
        </Button>
      </Card>
      {/* Selected Path Details */}
      {selectedPath && (
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-semibold">{selectedPath.title}</h2>
              <p className="text-sm text-gray-600">{selectedPath.description}</p>
            </div>
            <div className="flex gap-2">
              {hasRole(['super_admin', 'tenant_admin', 'trainer']) && (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportPath(selectedPath.id)}
                  >
                    <Download className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => handleStartPath(selectedPath.id)}
                  >
                    <Play className="h-4 w-4 mr-1" />
                    Start Path
                  </Button>
                </>
              )}
            </div>
          </div>
          {/* Learning Milestones */}
          <div className="space-y-4">
            <h3 className="font-medium text-gray-900">Learning Milestones</h3>
            <div className="relative">
              {selectedPath.milestones.map((milestone, index) => (
                <div key={index} className="flex gap-4 mb-6 last:mb-0">
                  <div className="relative">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                      milestone.status === 'completed' ? 'bg-green-500 text-white' :
                      milestone.status === 'in_progress' ? 'bg-blue-500 text-white' :
                      'bg-gray-300 text-gray-600'
                    }`}>
                      {milestone.status === 'completed' ? (
                        <CheckCircle className="h-5 w-5" />
                      ) : (
                        <span className="font-semibold">{index + 1}</span>
                      )}
                    </div>
                    {index < selectedPath.milestones.length - 1 && (
                      <div className="absolute top-10 left-1/2 w-0.5 h-16 bg-gray-300 -translate-x-1/2" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{milestone.title}</h4>
                        <Badge className={getStatusColor(milestone.status)}>
                          {milestone.status}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{milestone.description}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          <span>{milestone.estimated_duration}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Target className="h-4 w-4" />
                          <span>{milestone.skills.length} skills</span>
                        </div>
                        <Badge className={getDifficultyColor(milestone.difficulty)}>
                          {milestone.difficulty}
                        </Badge>
                      </div>
                      {milestone.resources && milestone.resources.length > 0 && (
                        <div className="mt-3 pt-3 border-t">
                          <p className="text-sm font-medium text-gray-700 mb-2">Resources:</p>
                          <div className="space-y-1">
                            {milestone.resources.map((resource, rIndex) => (
                              <a
                                key={rIndex}
                                href={resource.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-2 text-sm text-blue-600 hover:underline"
                              >
                                <BookOpen className="h-3 w-3" />
                                {resource.title}
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Card>
      )}
      {/* Existing Learning Paths */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Active Learning Paths</h2>
        {learningPaths.length === 0 ? (
          <div className="text-center py-8">
            <Map className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">No active learning paths</p>
          </div>
        ) : (
          <div className="space-y-4">
            {learningPaths.map((path) => (
              <div
                key={path.id}
                className="border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => setSelectedPath(path)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-gray-900">{path.title}</h3>
                      <Badge className={getStatusColor(path.status)}>
                        {path.status}
                      </Badge>
                      <Badge variant="secondary">
                        {path.beneficiary_name}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{path.description}</p>
                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${path.progress}%` }}
                      />
                    </div>
                    <div className="flex items-center justify-between mt-3">
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span>{path.completed_milestones}/{path.total_milestones} milestones</span>
                        <span>{path.duration}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {path.status === 'in_progress' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              // Pause logic
                            }}
                          >
                            <Pause className="h-4 w-4" />
                          </Button>
                        )}
                        {path.status === 'paused' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStartPath(path.id);
                            }}
                          >
                            <Play className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleExportPath(path.id);
                          }}
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-gray-400 ml-4" />
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};
export default AILearningPathPage;