import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../components/ui/use-toast';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Input } from '../../components/ui/input';
import {
  Loader2,
  Sparkles,
  BookOpen,
  Target,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  RefreshCw,
  Search,
  Filter,
  SlidersHorizontal
} from 'lucide-react';

const AIRecommendationsPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [recommendations, setRecommendations] = useState([]);
  const [filteredRecommendations, setFilteredRecommendations] = useState([]);
  const [selectedBeneficiary, setSelectedBeneficiary] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    autoApprove: false,
    priorityThreshold: 'high',
    maxRecommendations: 10
  });

  useEffect(() => {
    fetchBeneficiaries();
    fetchRecommendations();
  }, []);

  useEffect(() => {
    filterRecommendations();
  }, [recommendations, selectedBeneficiary, selectedType, searchTerm]);

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

  const fetchRecommendations = async () => {
    try {
      const res = await fetch('/api/ai/recommendations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch recommendations');

      const data = await res.json();
      setRecommendations(data);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch AI recommendations',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchRecommendations();
  };

  const filterRecommendations = () => {
    let filtered = [...recommendations];

    if (selectedBeneficiary !== 'all') {
      filtered = filtered.filter(rec => rec.beneficiary_id === selectedBeneficiary);
    }

    if (selectedType !== 'all') {
      filtered = filtered.filter(rec => rec.type === selectedType);
    }

    if (searchTerm) {
      filtered = filtered.filter(rec => 
        rec.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        rec.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    setFilteredRecommendations(filtered);
  };

  const handleApproveRecommendation = async (recommendationId) => {
    try {
      const res = await fetch(`/api/ai/recommendations/${recommendationId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to approve recommendation');

      toast({
        title: 'Success',
        description: 'Recommendation approved successfully'
      });

      fetchRecommendations();
    } catch (error) {
      console.error('Error approving recommendation:', error);
      toast({
        title: 'Error',
        description: 'Failed to approve recommendation',
        variant: 'destructive'
      });
    }
  };

  const handleRejectRecommendation = async (recommendationId) => {
    try {
      const res = await fetch(`/api/ai/recommendations/${recommendationId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to reject recommendation');

      toast({
        title: 'Success',
        description: 'Recommendation rejected'
      });

      fetchRecommendations();
    } catch (error) {
      console.error('Error rejecting recommendation:', error);
      toast({
        title: 'Error',
        description: 'Failed to reject recommendation',
        variant: 'destructive'
      });
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'learning_path':
        return <BookOpen className="h-4 w-4" />;
      case 'skill_improvement':
        return <Target className="h-4 w-4" />;
      case 'performance_boost':
        return <TrendingUp className="h-4 w-4" />;
      default:
        return <Sparkles className="h-4 w-4" />;
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
          <Sparkles className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">AI Recommendations</h1>
          <Badge variant="secondary">
            {filteredRecommendations.filter(r => r.status === 'pending').length} pending
          </Badge>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={() => setShowSettings(!showSettings)}
          >
            <SlidersHorizontal className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Recommendation Settings</h2>
          <div className="space-y-4">
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={settings.autoApprove}
                onChange={(e) => setSettings({ ...settings, autoApprove: e.target.checked })}
                className="rounded text-primary"
              />
              <div>
                <p className="font-medium">Auto-approve recommendations</p>
                <p className="text-sm text-gray-600">
                  Automatically approve low-risk recommendations
                </p>
              </div>
            </label>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority Threshold
              </label>
              <select
                value={settings.priorityThreshold}
                onChange={(e) => setSettings({ ...settings, priorityThreshold: e.target.value })}
                className="w-48 px-3 py-2 border border-gray-300 rounded-md"
              >
                <option value="high">High priority only</option>
                <option value="medium">Medium and above</option>
                <option value="low">All priorities</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max recommendations per beneficiary
              </label>
              <Input
                type="number"
                value={settings.maxRecommendations}
                onChange={(e) => setSettings({ ...settings, maxRecommendations: parseInt(e.target.value) })}
                min="1"
                max="50"
                className="w-32"
              />
            </div>
          </div>
        </Card>
      )}

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              type="text"
              placeholder="Search recommendations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
          
          <select
            value={selectedBeneficiary}
            onChange={(e) => setSelectedBeneficiary(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="all">All Beneficiaries</option>
            {beneficiaries.map((beneficiary) => (
              <option key={beneficiary.id} value={beneficiary.id}>
                {beneficiary.full_name}
              </option>
            ))}
          </select>

          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="all">All Types</option>
            <option value="learning_path">Learning Path</option>
            <option value="skill_improvement">Skill Improvement</option>
            <option value="performance_boost">Performance Boost</option>
            <option value="content_suggestion">Content Suggestion</option>
          </select>
        </div>
      </Card>

      {/* Recommendations List */}
      {filteredRecommendations.length === 0 ? (
        <Card className="p-8 text-center">
          <Sparkles className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations found</h3>
          <p className="text-gray-500">Try adjusting your filters or refresh to get new recommendations</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredRecommendations.map((recommendation) => (
            <Card key={recommendation.id} className="p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="p-2 bg-primary/10 text-primary rounded-lg">
                      {getTypeIcon(recommendation.type)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{recommendation.title}</h3>
                      <p className="text-sm text-gray-500">
                        For: {recommendation.beneficiary_name}
                      </p>
                    </div>
                    <Badge className={getPriorityColor(recommendation.priority)}>
                      {recommendation.priority} priority
                    </Badge>
                    {recommendation.status === 'approved' && (
                      <Badge variant="success">Approved</Badge>
                    )}
                    {recommendation.status === 'rejected' && (
                      <Badge variant="destructive">Rejected</Badge>
                    )}
                  </div>
                  
                  <p className="text-gray-600 mb-4">{recommendation.description}</p>

                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      <span>{recommendation.estimated_duration}</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Target className="h-4 w-4" />
                      <span>{recommendation.impact_score}% impact</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <TrendingUp className="h-4 w-4" />
                      <span>{recommendation.confidence}% confidence</span>
                    </div>
                  </div>

                  {recommendation.reasoning && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-800">
                        <strong>AI Reasoning:</strong> {recommendation.reasoning}
                      </p>
                    </div>
                  )}
                </div>

                {recommendation.status === 'pending' && (
                  <div className="flex gap-2 ml-4">
                    <Button
                      size="sm"
                      onClick={() => handleApproveRecommendation(recommendation.id)}
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Approve
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleRejectRecommendation(recommendation.id)}
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Reject
                    </Button>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default AIRecommendationsPage;