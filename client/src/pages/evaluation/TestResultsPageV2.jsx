import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, Download, Share2, RefreshCw, Eye, Trophy, Target,
  TrendingUp, TrendingDown, Award, Clock, CheckCircle, XCircle,
  AlertCircle, BarChart2, PieChart, LineChart, Brain, BookOpen
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale
} from 'chart.js';
import { Line, Bar, Pie, Doughnut, Radar } from 'react-chartjs-2';
import axios from '../../lib/api';
import { toast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Card } from '../../components/ui/card';
import { Tabs } from '../../components/ui/tabs';
import { Badge } from '../../components/ui/badge';
import { Alert } from '../../components/ui/alert';

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
  Legend
);

const TestResultsPageV2 = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [session, setSession] = useState(null);
  const [test, setTest] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [comparisons, setComparisons] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [shareModalOpen, setShareModalOpen] = useState(false);

  useEffect(() => {
    fetchResults();
  }, [sessionId]);

  const fetchResults = async () => {
    try {
      setLoading(true);
      const [sessionRes, historyRes, comparisonsRes] = await Promise.all([
        axios.get(`/api/evaluations/sessions/${sessionId}/detailed`),
        axios.get(`/api/evaluations/sessions/${sessionId}/history`),
        axios.get(`/api/evaluations/sessions/${sessionId}/comparisons`)
      ]);
      
      setSession(sessionRes.data.session);
      setTest(sessionRes.data.test);
      setAnalysis(sessionRes.data.analysis);
      setHistory(historyRes.data);
      setComparisons(comparisonsRes.data);
    } catch (error) {
      console.error('Error fetching results:', error);
      toast({
        title: 'Hata',
        description: 'Sonuçlar yüklenemedi',
        variant: 'error'
      });
    } finally {
      setLoading(false);
    }
  };

  const exportResults = async (format = 'pdf') => {
    try {
      const response = await axios.get(
        `/api/evaluations/sessions/${sessionId}/export?format=${format}`,
        { responseType: 'blob' }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `test-results-${sessionId}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast({
        title: 'Başarılı',
        description: 'Sonuçlar indirildi',
        variant: 'success'
      });
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Sonuçlar indirilemedi',
        variant: 'error'
      });
    }
  };

  const shareResults = async (method) => {
    try {
      await axios.post(`/api/evaluations/sessions/${sessionId}/share`, {
        method,
        includeAnalysis: true
      });
      
      toast({
        title: 'Başarılı',
        description: 'Sonuçlar paylaşıldı',
        variant: 'success'
      });
      setShareModalOpen(false);
    } catch (error) {
      toast({
        title: 'Hata',
        description: 'Sonuçlar paylaşılamadı',
        variant: 'error'
      });
    }
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      passed: { label: 'Başarılı', variant: 'success' },
      failed: { label: 'Başarısız', variant: 'error' },
      pending: { label: 'Değerlendiriliyor', variant: 'warning' }
    };
    
    const { label, variant } = statusMap[status] || statusMap.pending;
    return <Badge variant={variant}>{label}</Badge>;
  };

  const getSkillLevel = (score) => {
    if (score >= 90) return { label: 'Uzman', color: 'text-green-600' };
    if (score >= 75) return { label: 'İleri', color: 'text-blue-600' };
    if (score >= 60) return { label: 'Orta', color: 'text-yellow-600' };
    if (score >= 40) return { label: 'Başlangıç', color: 'text-orange-600' };
    return { label: 'Acemi', color: 'text-red-600' };
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
  const scoreProgressChart = {
    labels: history.map(h => new Date(h.completed_at).toLocaleDateString()),
    datasets: [
      {
        label: 'Puanlar',
        data: history.map(h => h.score),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        tension: 0.4
      }
    ]
  };

  const skillPerformanceChart = {
    labels: analysis?.skill_analysis?.map(s => s.skill_name) || [],
    datasets: [
      {
        label: 'Performans',
        data: analysis?.skill_analysis?.map(s => s.score) || [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.5)',
          'rgba(54, 162, 235, 0.5)',
          'rgba(255, 206, 86, 0.5)',
          'rgba(75, 192, 192, 0.5)',
          'rgba(153, 102, 255, 0.5)'
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)'
        ],
        borderWidth: 1
      }
    ]
  };

  const questionsOverviewChart = {
    labels: ['Doğru', 'Yanlış', 'Boş'],
    datasets: [
      {
        data: [
          session.correct_answers,
          session.wrong_answers,
          session.unanswered_questions
        ],
        backgroundColor: [
          'rgba(34, 197, 94, 0.5)',
          'rgba(239, 68, 68, 0.5)',
          'rgba(156, 163, 175, 0.5)'
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(239, 68, 68)',
          'rgb(156, 163, 175)'
        ],
        borderWidth: 1
      }
    ]
  };

  const topicPerformanceChart = {
    labels: analysis?.topic_analysis?.map(t => t.topic) || [],
    datasets: [
      {
        label: 'Konu Performansı',
        data: analysis?.topic_analysis?.map(t => t.score) || [],
        backgroundColor: 'rgba(99, 102, 241, 0.5)',
        borderColor: 'rgb(99, 102, 241)',
        borderWidth: 1
      }
    ]
  };

  const difficultyAnalysisChart = {
    labels: ['Kolay', 'Orta', 'Zor'],
    datasets: [
      {
        label: 'Başarı Oranı',
        data: [
          analysis?.difficulty_analysis?.easy || 0,
          analysis?.difficulty_analysis?.medium || 0,
          analysis?.difficulty_analysis?.hard || 0
        ],
        backgroundColor: 'rgba(34, 197, 94, 0.5)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 1
      }
    ]
  };

  const comparisonRadarChart = {
    labels: comparisons?.dimensions || [],
    datasets: [
      {
        label: 'Sizin Skorunuz',
        data: comparisons?.your_scores || [],
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
      },
      {
        label: 'Grup Ortalaması',
        data: comparisons?.average_scores || [],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
      }
    ]
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
                onClick={() => navigate('/evaluations')}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Değerlendirmeler
              </Button>
              <div>
                <h1 className="text-xl font-semibold">{test.title}</h1>
                <p className="text-sm text-gray-600">
                  Test Sonuçları - {new Date(session.completed_at).toLocaleDateString()}
                </p>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                onClick={() => setShareModalOpen(true)}
              >
                <Share2 className="h-4 w-4 mr-2" />
                Paylaş
              </Button>
              
              <div className="relative">
                <Button
                  variant="outline"
                  onClick={() => exportResults('pdf')}
                >
                  <Download className="h-4 w-4 mr-2" />
                  İndir
                </Button>
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border p-2 hidden group-hover:block">
                  <button
                    onClick={() => exportResults('pdf')}
                    className="w-full text-left px-3 py-2 rounded hover:bg-gray-100"
                  >
                    PDF olarak indir
                  </button>
                  <button
                    onClick={() => exportResults('excel')}
                    className="w-full text-left px-3 py-2 rounded hover:bg-gray-100"
                  >
                    Excel olarak indir
                  </button>
                  <button
                    onClick={() => exportResults('csv')}
                    className="w-full text-left px-3 py-2 rounded hover:bg-gray-100"
                  >
                    CSV olarak indir
                  </button>
                </div>
              </div>
              
              <Button
                onClick={() => navigate(`/evaluations/sessions/${sessionId}/analysis`)}
              >
                <Brain className="h-4 w-4 mr-2" />
                AI Analizi
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 max-w-7xl mx-auto">
        {/* Overview Section */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-100 rounded-lg">
                <Trophy className="h-6 w-6 text-blue-600" />
              </div>
              {getStatusBadge(session.status)}
            </div>
            <h3 className="text-2xl font-bold">{session.score}%</h3>
            <p className="text-gray-600">Toplam Puan</p>
            <div className="mt-2">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${
                    session.score >= test.passing_score 
                      ? 'bg-green-600' 
                      : 'bg-red-600'
                  }`}
                  style={{ width: `${session.score}%` }}
                />
              </div>
              <p className="text-sm text-gray-600 mt-1">
                Geçme notu: {test.passing_score}%
              </p>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-100 rounded-lg">
                <Target className="h-6 w-6 text-green-600" />
              </div>
              <Badge variant="secondary">
                {((session.correct_answers / test.total_questions) * 100).toFixed(0)}%
              </Badge>
            </div>
            <h3 className="text-2xl font-bold">{session.correct_answers}/{test.total_questions}</h3>
            <p className="text-gray-600">Doğru Cevap</p>
            <div className="flex items-center gap-4 mt-2 text-sm">
              <div className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>{session.correct_answers} Doğru</span>
              </div>
              <div className="flex items-center gap-1">
                <XCircle className="h-4 w-4 text-red-600" />
                <span>{session.wrong_answers} Yanlış</span>
              </div>
              <div className="flex items-center gap-1">
                <AlertCircle className="h-4 w-4 text-gray-600" />
                <span>{session.unanswered_questions} Boş</span>
              </div>
            </div>
          </Card>
          
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Clock className="h-6 w-6 text-purple-600" />
              </div>
              <Badge variant="secondary">
                {Math.round((session.time_spent / test.time_limit) * 100)}%
              </Badge>
            </div>
            <h3 className="text-2xl font-bold">{Math.floor(session.time_spent / 60)} dk</h3>
            <p className="text-gray-600">Tamamlama Süresi</p>
            <p className="text-sm text-gray-600 mt-2">
              Ayrılan süre: {test.time_limit} dk
            </p>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <Tabs.TabsList>
            <Tabs.TabTrigger value="overview">Genel Bakış</Tabs.TabTrigger>
            <Tabs.TabTrigger value="questions">Sorular</Tabs.TabTrigger>
            <Tabs.TabTrigger value="analysis">Detaylı Analiz</Tabs.TabTrigger>
            <Tabs.TabTrigger value="comparison">Karşılaştırma</Tabs.TabTrigger>
            <Tabs.TabTrigger value="history">Geçmiş</Tabs.TabTrigger>
          </Tabs.TabsList>

          {/* Overview Tab */}
          <Tabs.TabContent value="overview">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Score Progress Chart */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Puan Gelişimi</h3>
                <div className="h-64">
                  <Line 
                    data={scoreProgressChart}
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
              
              {/* Questions Overview Chart */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Cevap Dağılımı</h3>
                <div className="h-64">
                  <Doughnut 
                    data={questionsOverviewChart}
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
              
              {/* Skill Performance Chart */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Beceri Performansı</h3>
                <div className="h-64">
                  <Bar 
                    data={skillPerformanceChart}
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
              
              {/* Topic Performance Chart */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Konu Performansı</h3>
                <div className="h-64">
                  <Bar 
                    data={topicPerformanceChart}
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
            </div>
          </Tabs.TabContent>

          {/* Questions Tab */}
          <Tabs.TabContent value="questions">
            <Card className="p-6">
              <div className="space-y-4">
                {session.responses?.map((response, index) => {
                  const question = test.questions[index];
                  const isCorrect = response.is_correct;
                  
                  return (
                    <div
                      key={response.id}
                      className={`p-4 rounded-lg border ${
                        isCorrect ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-full ${
                            isCorrect ? 'bg-green-100' : 'bg-red-100'
                          }`}>
                            {isCorrect ? (
                              <CheckCircle className="h-5 w-5 text-green-600" />
                            ) : (
                              <XCircle className="h-5 w-5 text-red-600" />
                            )}
                          </div>
                          <span className="font-semibold">Soru {index + 1}</span>
                          <Badge variant="secondary">{question.points} puan</Badge>
                          <Badge variant="secondary">{question.difficulty}</Badge>
                        </div>
                        <span className={`font-semibold ${
                          isCorrect ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {isCorrect ? `+${question.points}` : '0'} puan
                        </span>
                      </div>
                      
                      <p className="mb-3">{question.question_text}</p>
                      
                      <div className="space-y-2">
                        <div>
                          <span className="font-medium">Verilen Cevap:</span>
                          <p className="text-gray-700">{response.answer}</p>
                        </div>
                        
                        {!isCorrect && (
                          <div>
                            <span className="font-medium">Doğru Cevap:</span>
                            <p className="text-green-700">{question.correct_answer}</p>
                          </div>
                        )}
                        
                        {question.explanation && (
                          <div className="mt-2 p-3 bg-blue-50 rounded">
                            <span className="font-medium text-blue-900">Açıklama:</span>
                            <p className="text-blue-800">{question.explanation}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>
          </Tabs.TabContent>

          {/* Analysis Tab */}
          <Tabs.TabContent value="analysis">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Difficulty Analysis */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Zorluk Analizi</h3>
                <div className="h-64">
                  <Bar 
                    data={difficultyAnalysisChart}
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
              
              {/* Time Analysis */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Zaman Analizi</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-600">Ortalama Soru Süresi</span>
                      <span className="font-medium">
                        {Math.floor(session.time_spent / test.total_questions)} sn
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: '60%' }}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-600">En Hızlı Cevap</span>
                      <span className="font-medium">5 sn</span>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm text-gray-600">En Yavaş Cevap</span>
                      <span className="font-medium">3 dk 45 sn</span>
                    </div>
                  </div>
                </div>
              </Card>
              
              {/* Skill Details */}
              <Card className="p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4">Beceri Detayları</h3>
                <div className="space-y-4">
                  {analysis?.skill_analysis?.map((skill, index) => {
                    const { label, color } = getSkillLevel(skill.score);
                    
                    return (
                      <div key={index} className="p-4 border rounded-lg">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="font-semibold">{skill.skill_name}</h4>
                            <p className="text-sm text-gray-600">{skill.description}</p>
                          </div>
                          <div className="text-right">
                            <p className={`font-bold text-lg ${color}`}>
                              {skill.score}%
                            </p>
                            <p className={`text-sm ${color}`}>{label}</p>
                          </div>
                        </div>
                        
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              skill.score >= 60 ? 'bg-green-600' : 'bg-red-600'
                            }`}
                            style={{ width: `${skill.score}%` }}
                          />
                        </div>
                        
                        {skill.recommendations && (
                          <div className="mt-3 p-3 bg-blue-50 rounded">
                            <p className="text-sm text-blue-900 font-medium">Öneriler:</p>
                            <ul className="text-sm text-blue-800 mt-1 list-disc list-inside">
                              {skill.recommendations.map((rec, idx) => (
                                <li key={idx}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </Card>
            </div>
          </Tabs.TabContent>

          {/* Comparison Tab */}
          <Tabs.TabContent value="comparison">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Radar Comparison */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Performans Karşılaştırması</h3>
                <div className="h-64">
                  <Radar 
                    data={comparisonRadarChart}
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
              
              {/* Group Statistics */}
              <Card className="p-6">
                <h3 className="text-lg font-semibold mb-4">Grup İstatistikleri</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Sıralama</span>
                    <span className="font-bold text-lg">
                      {comparisons?.rank} / {comparisons?.total_participants}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Grup Ortalaması</span>
                    <span className="font-bold text-lg">
                      {comparisons?.group_average}%
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">En Yüksek Puan</span>
                    <span className="font-bold text-lg">
                      {comparisons?.highest_score}%
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">En Düşük Puan</span>
                    <span className="font-bold text-lg">
                      {comparisons?.lowest_score}%
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
                    <span className="text-gray-600">Başarı Oranı</span>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-lg">
                        {comparisons?.success_rate}%
                      </span>
                      {comparisons?.success_rate > 50 ? (
                        <TrendingUp className="h-5 w-5 text-green-600" />
                      ) : (
                        <TrendingDown className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                  </div>
                </div>
              </Card>
              
              {/* Performance Badge */}
              <Card className="p-6 lg:col-span-2">
                <h3 className="text-lg font-semibold mb-4">Başarı Rozeti</h3>
                <div className="text-center">
                  <div className="inline-flex p-6 bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full mb-4">
                    <Award className="h-16 w-16 text-white" />
                  </div>
                  <h4 className="text-2xl font-bold mb-2">{comparisons?.achievement_title}</h4>
                  <p className="text-gray-600 mb-4">{comparisons?.achievement_description}</p>
                  <div className="flex items-center justify-center gap-2">
                    {comparisons?.badges?.map((badge, index) => (
                      <Badge key={index} variant="secondary" size="lg">
                        {badge}
                      </Badge>
                    ))}
                  </div>
                </div>
              </Card>
            </div>
          </Tabs.TabContent>

          {/* History Tab */}
          <Tabs.TabContent value="history">
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Test Geçmişi</h3>
              <div className="space-y-4">
                {history.map((attempt, index) => (
                  <div
                    key={attempt.id}
                    className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer"
                    onClick={() => navigate(`/evaluations/sessions/${attempt.id}/results`)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`p-2 rounded-full ${
                          attempt.status === 'passed' ? 'bg-green-100' : 'bg-red-100'
                        }`}>
                          {attempt.status === 'passed' ? (
                            <CheckCircle className="h-5 w-5 text-green-600" />
                          ) : (
                            <XCircle className="h-5 w-5 text-red-600" />
                          )}
                        </div>
                        <div>
                          <p className="font-semibold">Deneme #{index + 1}</p>
                          <p className="text-sm text-gray-600">
                            {new Date(attempt.completed_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <p className="font-bold text-lg">{attempt.score}%</p>
                        <p className="text-sm text-gray-600">
                          {attempt.correct_answers}/{attempt.total_questions} doğru
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </Tabs.TabContent>
        </Tabs>
      </div>

      {/* Share Modal */}
      {shareModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Sonuçları Paylaş</h3>
            <div className="space-y-4">
              <button
                onClick={() => shareResults('email')}
                className="w-full p-3 border rounded-lg hover:bg-gray-50 text-left"
              >
                <p className="font-medium">E-posta ile Gönder</p>
                <p className="text-sm text-gray-600">Detaylı rapor e-postanıza gönderilecek</p>
              </button>
              
              <button
                onClick={() => shareResults('link')}
                className="w-full p-3 border rounded-lg hover:bg-gray-50 text-left"
              >
                <p className="font-medium">Link Oluştur</p>
                <p className="text-sm text-gray-600">Paylaşılabilir link oluştur</p>
              </button>
              
              <button
                onClick={() => shareResults('social')}
                className="w-full p-3 border rounded-lg hover:bg-gray-50 text-left"
              >
                <p className="font-medium">Sosyal Medyada Paylaş</p>
                <p className="text-sm text-gray-600">Başarınızı paylaşın</p>
              </button>
            </div>
            
            <div className="flex justify-end mt-6 gap-2">
              <Button
                variant="outline"
                onClick={() => setShareModalOpen(false)}
              >
                İptal
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};

export default TestResultsPageV2;