import { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Select } from '../../components/ui/select';
import {
  Loader2,
  Brain,
  TrendingUp,
  Users,
  Target,
  AlertTriangle,
  CheckCircle,
  ArrowUp,
  ArrowDown,
  RefreshCw,
  Download
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';

const AIInsightsPage = () => {
  const { user } = useAuth();
  const { toast } = useToast();
  
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [insights, setInsights] = useState(null);
  const [timeRange, setTimeRange] = useState('last_30_days');
  const [category, setCategory] = useState('all');

  useEffect(() => {
    fetchAIInsights();
  }, [timeRange, category]);

  const fetchAIInsights = async () => {
    try {
      const res = await fetch(`/api/ai/insights?time_range=${timeRange}&category=${category}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to fetch insights');

      const data = await res.json();
      setInsights(data);
    } catch (error) {
      console.error('Error fetching insights:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch AI insights',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchAIInsights();
  };

  const handleExport = async () => {
    try {
      const res = await fetch(`/api/ai/insights/export?time_range=${timeRange}&category=${category}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!res.ok) throw new Error('Failed to export insights');

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ai_insights_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'Success',
        description: 'Insights exported successfully'
      });
    } catch (error) {
      console.error('Error exporting insights:', error);
      toast({
        title: 'Error',
        description: 'Failed to export insights',
        variant: 'destructive'
      });
    }
  };

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!insights) {
    return (
      <div className="text-center py-12">
        <Brain className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No insights available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Brain className="h-6 w-6 text-primary" />
          <h1 className="text-2xl font-bold text-gray-900">AI Insights</h1>
        </div>
        
        <div className="flex items-center gap-3">
          <Select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="w-40"
          >
            <option value="last_7_days">Last 7 days</option>
            <option value="last_30_days">Last 30 days</option>
            <option value="last_90_days">Last 90 days</option>
            <option value="all_time">All time</option>
          </Select>
          
          <Select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="w-40"
          >
            <option value="all">All Categories</option>
            <option value="performance">Performance</option>
            <option value="engagement">Engagement</option>
            <option value="learning">Learning</option>
            <option value="trends">Trends</option>
          </Select>
          
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button onClick={handleExport}>
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card className="p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Overall Performance</p>
            <TrendingUp className="h-4 w-4 text-green-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{insights.metrics.overall_performance}%</p>
          <p className="text-sm text-green-600 flex items-center mt-1">
            <ArrowUp className="h-3 w-3 mr-1" />
            {insights.metrics.performance_change}% from last period
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Active Learners</p>
            <Users className="h-4 w-4 text-blue-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{insights.metrics.active_learners}</p>
          <p className="text-sm text-gray-500 mt-1">
            {insights.metrics.total_learners} total
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Completion Rate</p>
            <Target className="h-4 w-4 text-purple-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{insights.metrics.completion_rate}%</p>
          <p className="text-sm text-purple-600 flex items-center mt-1">
            <ArrowUp className="h-3 w-3 mr-1" />
            {insights.metrics.completion_change}% improvement
          </p>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-gray-600">Risk Assessment</p>
            <AlertTriangle className="h-4 w-4 text-amber-600" />
          </div>
          <p className="text-2xl font-bold text-gray-900">{insights.metrics.at_risk_count}</p>
          <p className="text-sm text-gray-500 mt-1">
            learners need attention
          </p>
        </Card>
      </div>

      {/* AI Predictions */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">AI Predictions</h2>
        <div className="space-y-4">
          {insights.predictions.map((prediction, index) => (
            <div key={index} className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
              <Brain className="h-5 w-5 text-primary mt-0.5" />
              <div className="flex-1">
                <p className="font-medium text-gray-900">{prediction.title}</p>
                <p className="text-sm text-gray-600 mt-1">{prediction.description}</p>
                <div className="flex items-center gap-2 mt-2">
                  <Badge variant={prediction.confidence > 80 ? 'success' : 'warning'}>
                    {prediction.confidence}% confidence
                  </Badge>
                  <Badge variant="secondary">{prediction.impact} impact</Badge>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Performance Trends */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Performance Trends</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={insights.trends.performance}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="average_score" 
                stroke="#0088FE" 
                name="Average Score"
                strokeWidth={2}
              />
              <Line 
                type="monotone" 
                dataKey="completion_rate" 
                stroke="#00C49F" 
                name="Completion Rate"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </Card>

      {/* Learning Categories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Performance by Category</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={insights.categories.performance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#0088FE" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Time Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={insights.categories.time_spent}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {insights.categories.time_spent.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Recommendations */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">AI Recommendations</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.recommendations.map((rec, index) => (
            <div key={index} className="border rounded-lg p-4">
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-gray-900">{rec.title}</h3>
                  <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
                  <p className="text-sm text-gray-500 mt-2">
                    Estimated impact: {rec.estimated_impact}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Anomalies Detection */}
      {insights.anomalies && insights.anomalies.length > 0 && (
        <Card className="p-6 border-amber-200 bg-amber-50">
          <div className="flex items-center gap-3 mb-4">
            <AlertTriangle className="h-5 w-5 text-amber-600" />
            <h2 className="text-lg font-semibold text-gray-900">Anomalies Detected</h2>
          </div>
          <div className="space-y-3">
            {insights.anomalies.map((anomaly, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className="w-1.5 h-1.5 bg-amber-600 rounded-full mt-2" />
                <div>
                  <p className="font-medium text-gray-900">{anomaly.title}</p>
                  <p className="text-sm text-gray-600">{anomaly.description}</p>
                  <p className="text-sm text-amber-600 mt-1">
                    Action required: {anomaly.action}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default AIInsightsPage;