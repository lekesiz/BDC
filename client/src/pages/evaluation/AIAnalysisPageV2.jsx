import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Brain, RefreshCw, Download, MessageSquare, 
  Target, TrendingUp, BookOpen, Award, AlertTriangle,
  CheckCircle, XCircle, Lightbulb, BarChart2, LineChart,
  PieChart, Activity, Zap, Shield, Star, ThumbsUp
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Pie, Doughnut, Radar, PolarArea } from 'react-chartjs-2';
import axios from '../../lib/api';
import { toast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Tabs } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
import { Alert } from '../../components/ui/alert';
import { Textarea } from '../../components/ui';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
);

const AIAnalysisPageV2 = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [session, setSession] = useState(null);
  const [test, setTest] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [insights, setInsights] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [userFeedback, setUserFeedback] = useState('');
  const [showChat, setShowChat] = useState(false);
  const [chatMessages, setChatMessages] = useState([]);

  useEffect(() => {
    fetchData();
  }, [sessionId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/evaluations/sessions/${sessionId}/ai-analysis`);
      
      setSession(response.data.session);
      setTest(response.data.test);
      setAnalysis(response.data.analysis);
      setInsights(response.data.insights);
      setRecommendations(response.data.recommendations);
      
      if (response.data.chat_history) {
        setChatMessages(response.data.chat_history);
      }
    } catch (error) {
      console.error('Error fetching analysis:', error);
      toast({
        title: 'Hata',
        description: 'AI analizi yüklenemedi',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const regenerateAnalysis = async () => {
    try {
      setGenerating(true);
      const response = await axios.post(`/api/evaluations/sessions/${sessionId}/regenerate-analysis`);
      
      setAnalysis(response.data.analysis);
      setInsights(response.data.insights);
      setRecommendations(response.data.recommendations);
      
      toast({
        title: 'Başarılı',
        description: 'AI analizi güncellendi',
        variant: 'success'
      });
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Analiz güncellenemedi',
        variant: 'error'
      });
    } finally {
      setGenerating(false);
    }
  };

  const exportAnalysis = async (format = 'pdf') => {
    try {
      const response = await axios.get(
        `/api/evaluations/sessions/${sessionId}/export-analysis?format=${format}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ai-analysis-${sessionId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Başarılı',
        description: 'Analiz raporu indirildi',
        variant: 'success'
      });
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Rapor indirilemedi',
        variant: 'error'
      });
    }
  };

  const sendChatMessage = async () => {
    if (!userFeedback.trim()) return;
    
    try {
      const response = await axios.post(`/api/evaluations/sessions/${sessionId}/chat`, {
        message: userFeedback
      });
      
      setChatMessages([
        ...chatMessages,
        { role: 'user', message: userFeedback },
        { role: 'assistant', message: response.data.response }
      ]);
      
      setUserFeedback('');
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Mesaj gönderilemedi',
        variant: 'error'
      });
    }
  };

  const getInsightIcon = (type) => {
    const icons = {
      strength: <Shield className="h-5 w-5 text-green-600" />,
      weakness: <AlertTriangle className="h-5 w-5 text-red-600" />,
      opportunity: <Lightbulb className="h-5 w-5 text-yellow-600" />,
      trend: <TrendingUp className="h-5 w-5 text-blue-600" />,
      achievement: <Award className="h-5 w-5 text-purple-600" />
    };
    return icons[type] || <Brain className="h-5 w-5 text-gray-600" />;
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

  // Chart configurations
  const learningProgressChart = {
    labels: analysis?.learning_curve?.labels || [],
    datasets: [
      {
        label: 'Öğrenme Eğrisi',
        data: analysis?.learning_curve?.values || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        fill: true,
        tension: 0.4
      },
      {
        label: 'Beklenen İlerleme',
        data: analysis?.expected_curve?.values || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        fill: true,
        tension: 0.4,
        borderDash: [5, 5]
      }
    ]
  };

  const strengthWeaknessChart = {
    labels: ['Güçlü Yönler', 'Gelişim Alanları', 'Kritik Alanlar'],
    datasets: [
      {
        data: [
          analysis?.strength_areas?.length || 0,
          analysis?.improvement_areas?.length || 0,
          analysis?.critical_areas?.length || 0
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.7)',
          'rgba(251, 191, 36, 0.7)',
          'rgba(239, 68, 68, 0.7)'
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(251, 191, 36)',
          'rgb(239, 68, 68)'
        ],
        borderWidth: 1
      }
    ]
  };

  const cognitiveProfileChart = {
    labels: analysis?.cognitive_profile?.dimensions || [],
    datasets: [
      {
        label: 'Bilişsel Profil',
        data: analysis?.cognitive_profile?.scores || [],
        backgroundColor: 'rgba(147, 51, 234, 0.3)',
        borderColor: 'rgb(147, 51, 234)',
        borderWidth: 2,
        pointBackgroundColor: 'rgb(147, 51, 234)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(147, 51, 234)'
      }
    ]
  };

  const topicMasteryChart = {
    labels: analysis?.topic_mastery?.topics || [],
    datasets: [
      {
        label: 'Konu Hakimiyeti',
        data: analysis?.topic_mastery?.scores || [],
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1
      }
    ]
  };

  const performanceTrendChart = {
    labels: analysis?.performance_trend?.dates || [],
    datasets: [
      {
        label: 'Performans Trendi',
        data: analysis?.performance_trend?.scores || [],
        borderColor: 'rgb(234, 88, 12)',
        backgroundColor: 'rgba(234, 88, 12, 0.1)',
        fill: true,
        tension: 0.3
      }
    ]
  };

  const timeManagementChart = {
    datasets: [
      {
        label: 'Zaman Yönetimi',
        data: analysis?.time_management?.distribution || [],
        backgroundColor: [
          'rgba(59, 130, 246, 0.6)',
          'rgba(34, 197, 94, 0.6)',
          'rgba(251, 191, 36, 0.6)',
          'rgba(239, 68, 68, 0.6)'
        ],
        borderWidth: 1
      }
    ],
    labels: ['Hızlı', 'Normal', 'Yavaş', 'Çok Yavaş']
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b sticky top-0 z-30">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => navigate(`/evaluations/sessions/${sessionId}/results`)}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Sonuçlara Dön
              </Button>
              <div>
                <h1 className="text-xl font-semibold">AI Performans Analizi</h1>
                <p className="text-sm text-gray-600">
                  {test.title} - Detaylı Yapay Zeka Analizi
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={regenerateAnalysis}
                disabled={generating}
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${generating ? 'animate-spin' : ''}`} />
                Yeniden Analiz Et
              </Button>
              
              <Button
                variant="outline"
                onClick={() => exportAnalysis('pdf')}
              >
                <Download className="h-4 w-4 mr-2" />
                Rapor İndir
              </Button>
              
              <Button
                onClick={() => setShowChat(!showChat)}
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                AI Asistan
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 max-w-7xl mx-auto">
        {/* AI Insights Summary */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Brain className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Genel Skor</p>
                <p className="text-xl font-bold">{analysis?.overall_score}%</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-100 rounded-lg">
                <Target className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Potansiyel</p>
                <p className="text-xl font-bold">{analysis?.potential_score}%</p>
              </div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-purple-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Gelişim Hızı</p>
                <p className="text-xl font-bold">
                  {analysis?.growth_rate > 0 ? '+' : ''}{analysis?.growth_rate}%
                </p>
              </div>
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <Activity className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Tutarlılık</p>
                <p className="text-xl font-bold">{analysis?.consistency_score}%</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Key Insights */}
        <Card className="p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Önemli Bulgular</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {insights?.map((insight, index) => (
              <div key={index} className="p-4 border rounded-lg">
                <div className="flex items-start gap-3">
                  {getInsightIcon(insight.type)}
                  <div>
                    <h4 className="font-medium mb-1">{insight.title}</h4>
                    <p className="text-sm text-gray-600">{insight.description}</p>
                    {insight.action && (
                      <Button size="sm" className="mt-2" variant="outline">
                        {insight.action}
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <Tabs.TabsList>
            <Tabs.TabTrigger value="overview">Genel Bakış</Tabs.TabTrigger>
            <Tabs.TabTrigger value="cognitive">Bilişsel Analiz</Tabs.TabTrigger>
            <Tabs.TabTrigger value="learning">Öğrenme Analizi</Tabs.TabTrigger>
            <Tabs.TabTrigger value="recommendations">Öneriler</Tabs.TabTrigger>
            <Tabs.TabTrigger value="patterns">Davranış Kalıpları</Tabs.TabTrigger>
          </Tabs.TabsList>

          {/* Overview Tab */}
          <Tabs.TabContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Learning Progress */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Öğrenme İlerlemesi</h3>
                <div className="h-64">
                  <Line 
                    data={learningProgressChart}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom'
                        }
                      }
                    }}
                  />
                </div>
              </Card>
              
              {/* Strength/Weakness Distribution */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Güç Dağılımı</h3>
                <div className="h-64">
                  <Pie 
                    data={strengthWeaknessChart}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom'
                        }
                      }
                    }}
                  />
                </div>
              </Card>
              
              {/* Topic Mastery */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Konu Hakimiyeti</h3>
                <div className="h-64">
                  <Bar 
                    data={topicMasteryChart}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: false
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          max: 100
                        }
                      }
                    }}
                  />
                </div>
              </Card>
              
              {/* Performance Trend */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Performans Trendi</h3>
                <div className="h-64">
                  <Line 
                    data={performanceTrendChart}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          display: false
                        }
                      }
                    }}
                  />
                </div>
              </Card>
            </div>
          </Tabs.TabContent>

          {/* Cognitive Analysis Tab */}
          <Tabs.TabContent value="cognitive">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Cognitive Profile */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Bilişsel Profil</h3>
                <div className="h-64">
                  <Radar 
                    data={cognitiveProfileChart}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        r: {
                          beginAtZero: true,
                          max: 100
                        }
                      }
                    }}
                  />
                </div>
              </Card>
              
              {/* Time Management */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Zaman Yönetimi</h3>
                <div className="h-64">
                  <PolarArea 
                    data={timeManagementChart}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false
                    }}
                  />
                </div>
              </Card>
              
              {/* Cognitive Insights */}
              <Card className="p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4">Bilişsel Özellikler</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis?.cognitive_traits?.map((trait, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{trait.name}</h4>
                        <Badge variant={trait.level === 'high' ? 'success' : trait.level === 'low' ? 'error' : 'warning'}>
                          {trait.level}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{trait.description}</p>
                      <div className="mt-2">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              trait.score >= 70 ? 'bg-green-600' : 
                              trait.score >= 40 ? 'bg-yellow-600' : 'bg-red-600'
                            }`}
                            style={{ width: `${trait.score}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </Tabs.TabContent>

          {/* Learning Analysis Tab */}
          <Tabs.TabContent value="learning">
            <div className="space-y-6">
              {/* Learning Style */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Öğrenme Stili</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {analysis?.learning_style?.preferences?.map((pref, index) => (
                    <div key={index} className="p-4 border rounded-lg text-center">
                      <div className="inline-flex p-3 bg-blue-100 rounded-full mb-3">
                        <BookOpen className="h-6 w-6 text-blue-600" />
                      </div>
                      <h4 className="font-medium mb-1">{pref.type}</h4>
                      <p className="text-2xl font-bold mb-1">{pref.score}%</p>
                      <p className="text-sm text-gray-600">{pref.description}</p>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Learning Path */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Önerilen Öğrenme Yolu</h3>
                <div className="space-y-4">
                  {analysis?.learning_path?.steps?.map((step, index) => (
                    <div key={index} className="flex items-start gap-4">
                      <div className={`p-2 rounded-full ${
                        step.status === 'completed' ? 'bg-green-100' : 
                        step.status === 'current' ? 'bg-blue-100' : 'bg-gray-100'
                      }`}>
                        {step.status === 'completed' ? (
                          <CheckCircle className="h-5 w-5 text-green-600" />
                        ) : step.status === 'current' ? (
                          <Activity className="h-5 w-5 text-blue-600" />
                        ) : (
                          <circle className="h-5 w-5 text-gray-400" />
                        )}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium">{step.title}</h4>
                        <p className="text-sm text-gray-600">{step.description}</p>
                        {step.resources && (
                          <div className="mt-2 flex flex-wrap gap-2">
                            {step.resources.map((resource, idx) => (
                              <Badge key={idx} variant="secondary" size="sm">
                                {resource}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                      <span className="text-sm text-gray-500">{step.duration}</span>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Knowledge Gaps */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Bilgi Eksiklikleri</h3>
                <div className="space-y-3">
                  {analysis?.knowledge_gaps?.map((gap, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{gap.topic}</h4>
                        <Badge variant="error">%{gap.severity} eksik</Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{gap.description}</p>
                      <div className="flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-yellow-600" />
                        <p className="text-sm text-gray-700">{gap.suggestion}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </Tabs.TabContent>

          {/* Recommendations Tab */}
          <Tabs.TabContent value="recommendations">
            <div className="space-y-6">
              {/* Priority Recommendations */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Öncelikli Öneriler</h3>
                <div className="space-y-4">
                  {recommendations?.priority?.map((rec, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-start gap-4">
                        <div className="p-2 bg-red-100 rounded-full">
                          <AlertTriangle className="h-5 w-5 text-red-600" />
                        </div>
                        <div className="flex-1">
                          <h4 className="font-medium mb-1">{rec.title}</h4>
                          <p className="text-sm text-gray-600 mb-2">{rec.description}</p>
                          <div className="flex items-center gap-4">
                            <span className="text-sm text-gray-500">
                              Etki: {rec.impact}/5
                            </span>
                            <span className="text-sm text-gray-500">
                              Süre: {rec.time_required}
                            </span>
                            <Button size="sm" variant="outline">
                              Başla
                            </Button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Resources */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Önerilen Kaynaklar</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {recommendations?.resources?.map((resource, index) => (
                    <div key={index} className="p-4 border rounded-lg">
                      <div className="flex items-center gap-3 mb-2">
                        <BookOpen className="h-5 w-5 text-blue-600" />
                        <h4 className="font-medium">{resource.title}</h4>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{resource.description}</p>
                      <div className="flex items-center justify-between">
                        <Badge variant="secondary">{resource.type}</Badge>
                        <Button size="sm" variant="outline">
                          Görüntüle
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Action Plan */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Eylem Planı</h3>
                <div className="space-y-4">
                  {recommendations?.action_plan?.phases?.map((phase, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h4 className="font-medium">
                          Aşama {index + 1}: {phase.name}
                        </h4>
                        <span className="text-sm text-gray-600">{phase.duration}</span>
                      </div>
                      <div className="space-y-2">
                        {phase.tasks?.map((task, taskIndex) => (
                          <div key={taskIndex} className="flex items-center gap-3">
                            <input type="checkbox" className="rounded" />
                            <span className="text-sm">{task}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>
          </Tabs.TabContent>

          {/* Behavior Patterns Tab */}
          <Tabs.TabContent value="patterns">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Response Patterns */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Cevap Kalıpları</h3>
                <div className="space-y-4">
                  {analysis?.response_patterns?.map((pattern, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{pattern.type}</h4>
                        <Badge variant={pattern.sentiment === 'positive' ? 'success' : 'warning'}>
                          {pattern.frequency}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600">{pattern.description}</p>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Error Patterns */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Hata Kalıpları</h3>
                <div className="space-y-4">
                  {analysis?.error_patterns?.map((error, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">{error.type}</h4>
                        <Badge variant="error">
                          {error.count} kez
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{error.description}</p>
                      <div className="flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-yellow-600" />
                        <p className="text-sm text-gray-700">{error.solution}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
              
              {/* Time Patterns */}
              <Card className="p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4">Zaman Kullanım Kalıpları</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 border rounded-lg">
                    <Zap className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
                    <h4 className="font-medium mb-1">Hızlı Cevaplar</h4>
                    <p className="text-2xl font-bold mb-1">{analysis?.time_patterns?.fast_responses}%</p>
                    <p className="text-sm text-gray-600">10 saniyeden az</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <Clock className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <h4 className="font-medium mb-1">Normal Cevaplar</h4>
                    <p className="text-2xl font-bold mb-1">{analysis?.time_patterns?.normal_responses}%</p>
                    <p className="text-sm text-gray-600">10-60 saniye</p>
                  </div>
                  <div className="text-center p-4 border rounded-lg">
                    <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-2" />
                    <h4 className="font-medium mb-1">Yavaş Cevaplar</h4>
                    <p className="text-2xl font-bold mb-1">{analysis?.time_patterns?.slow_responses}%</p>
                    <p className="text-sm text-gray-600">60 saniyeden fazla</p>
                  </div>
                </div>
              </Card>
            </div>
          </Tabs.TabContent>
        </Tabs>
      </div>

      {/* AI Chat Assistant */}
      {showChat && (
        <div className="fixed bottom-4 right-4 w-96 h-[500px] bg-white rounded-lg shadow-xl border flex flex-col z-50">
          <div className="p-4 border-b flex items-center justify-between">
            <h3 className="font-semibold">AI Performans Asistanı</h3>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowChat(false)}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatMessages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-xs p-3 rounded-lg ${
                  message.role === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  <p className="text-sm">{message.message}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Textarea
                value={userFeedback}
                onChange={(e) => setUserFeedback(e.target.value)}
                placeholder="Sorunuzu yazın..."
                className="flex-1"
                rows={2}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendChatMessage();
                  }
                }}
              />
              <Button onClick={sendChatMessage}>
                Gönder
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAnalysisPageV2;