import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Progress } from '../ui/progress';
import { Brain, Zap, BookOpen, Target, TrendingUp, Award, AlertCircle } from 'lucide-react';
import { useToast } from '../../hooks/useToast';
import LoadingSpinner from '../ui/LoadingSpinner';
import { Badge } from '../ui/badge';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import api from '../../lib/api';
const AIContentAnalyzer = ({ content, type = 'general' }) => {
  const [text, setText] = useState(content || '');
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const { toast } = useToast();
  const handleAnalyze = async () => {
    if (!text.trim()) {
      toast({
        title: "Error",
        description: "Please enter content to analyze",
        variant: "destructive"
      });
      return;
    }
    setLoading(true);
    try {
      const response = await api.post('/ai/analyze-content', {
        content: text.trim(),
        analysis_type: type,
        include_suggestions: true,
        include_metrics: true
      });
      setAnalysis(response.data);
      toast({
        title: "Analysis Complete",
        description: "Content has been analyzed successfully"
      });
    } catch (error) {
      console.error('Error analyzing content:', error);
      toast({
        title: "Error",
        description: error.response?.data?.message || "Failed to analyze content",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };
  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };
  const getScoreBadgeVariant = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'destructive';
  };
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-purple-600" />
            AI Content Analyzer
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="content-input">Content to Analyze</Label>
            <Textarea
              id="content-input"
              placeholder="Enter the content you want to analyze..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={8}
              className="font-mono text-sm"
            />
            <p className="text-sm text-gray-500">
              {text.split(' ').filter(word => word.length > 0).length} words • 
              {text.length} characters
            </p>
          </div>
          <Button
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
            className="w-full"
          >
            {loading ? (
              <>
                <LoadingSpinner size="sm" className="mr-2" />
                Analyzing...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4 mr-2" />
                Analyze Content
              </>
            )}
          </Button>
        </CardContent>
      </Card>
      {analysis && (
        <div className="space-y-4">
          {/* Overall Score */}
          <Card>
            <CardHeader>
              <CardTitle>Overall Analysis</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="text-center">
                  <div className="text-5xl font-bold mb-2 {getScoreColor(analysis.overall_score)}">
                    {analysis.overall_score || 0}%
                  </div>
                  <Badge variant={getScoreBadgeVariant(analysis.overall_score)}>
                    {analysis.overall_rating || 'Good'}
                  </Badge>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                  <div className="text-center">
                    <BookOpen className="h-8 w-8 mx-auto mb-2 text-blue-600" />
                    <p className="text-sm text-gray-600">Readability</p>
                    <p className="font-bold">{analysis.readability_score || 0}%</p>
                  </div>
                  <div className="text-center">
                    <Target className="h-8 w-8 mx-auto mb-2 text-green-600" />
                    <p className="text-sm text-gray-600">Clarity</p>
                    <p className="font-bold">{analysis.clarity_score || 0}%</p>
                  </div>
                  <div className="text-center">
                    <TrendingUp className="h-8 w-8 mx-auto mb-2 text-purple-600" />
                    <p className="text-sm text-gray-600">Engagement</p>
                    <p className="font-bold">{analysis.engagement_score || 0}%</p>
                  </div>
                  <div className="text-center">
                    <Award className="h-8 w-8 mx-auto mb-2 text-yellow-600" />
                    <p className="text-sm text-gray-600">Quality</p>
                    <p className="font-bold">{analysis.quality_score || 0}%</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          {/* Detailed Metrics */}
          {analysis.metrics && (
            <Card>
              <CardHeader>
                <CardTitle>Detailed Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Radar Chart */}
                  {analysis.metrics.dimensions && (
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <RadarChart data={analysis.metrics.dimensions}>
                          <PolarGrid />
                          <PolarAngleAxis dataKey="metric" />
                          <PolarRadiusAxis angle={90} domain={[0, 100]} />
                          <Radar 
                            name="Score" 
                            dataKey="score" 
                            stroke="#8884d8" 
                            fill="#8884d8" 
                            fillOpacity={0.6} 
                          />
                          <Tooltip />
                        </RadarChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                  {/* Individual Metrics */}
                  <div className="space-y-3">
                    {Object.entries(analysis.metrics).map(([key, value]) => {
                      if (key === 'dimensions') return null;
                      return (
                        <div key={key} className="space-y-1">
                          <div className="flex justify-between items-center">
                            <span className="text-sm font-medium capitalize">
                              {key.replace(/_/g, ' ')}
                            </span>
                            <span className="text-sm text-gray-600">
                              {typeof value === 'number' ? `${value}%` : value}
                            </span>
                          </div>
                          {typeof value === 'number' && (
                            <Progress value={value} className="h-2" />
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
          {/* Suggestions */}
          {analysis.suggestions && analysis.suggestions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Improvement Suggestions</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analysis.suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                      <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                      <div className="flex-1">
                        <p className="font-medium text-sm">{suggestion.title}</p>
                        <p className="text-sm text-gray-600 mt-1">{suggestion.description}</p>
                        {suggestion.impact && (
                          <Badge variant="outline" className="mt-2" size="sm">
                            Impact: {suggestion.impact}
                          </Badge>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
          {/* Key Insights */}
          {analysis.insights && (
            <Card>
              <CardHeader>
                <CardTitle>Key Insights</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(analysis.insights).map(([key, value]) => (
                    <div key={key} className="border-l-4 border-purple-500 pl-4">
                      <h4 className="font-medium text-sm capitalize">
                        {key.replace(/_/g, ' ')}
                      </h4>
                      <p className="text-sm text-gray-600 mt-1">{value}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};
export default AIContentAnalyzer;