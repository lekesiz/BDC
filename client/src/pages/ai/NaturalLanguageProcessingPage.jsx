import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Brain, 
  MessageSquare, 
  FileText, 
  Search, 
  TrendingUp,
  Sparkles,
  Gauge,
  AlertCircle,
  CheckCircle,
  ChevronRight,
  Filter,
  Download,
  Tag,
  BarChart,
  PieChart,
  Activity,
  Users,
  Globe,
  Zap,
  Lock
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../components/ui/use-toast';
const nlpFeatures = [
  {
    id: 'sentiment_analysis',
    name: 'Sentiment Analysis',
    icon: TrendingUp,
    description: 'Analyze sentiment in student feedback and responses',
    enabled: true
  },
  {
    id: 'text_summarization',
    name: 'Text Summarization',
    icon: FileText,
    description: 'Automatically summarize long texts and documents',
    enabled: true
  },
  {
    id: 'key_extraction',
    name: 'Keyword Extraction',
    icon: Tag,
    description: 'Extract key concepts and topics from text',
    enabled: true
  },
  {
    id: 'language_detection',
    name: 'Language Detection',
    icon: Globe,
    description: 'Detect and translate content in multiple languages',
    enabled: true
  },
  {
    id: 'intent_recognition',
    name: 'Intent Recognition',
    icon: Zap,
    description: 'Understand user intent for better response handling',
    enabled: true
  },
  {
    id: 'entity_extraction',
    name: 'Entity Extraction',
    icon: Users,
    description: 'Extract names, dates, and other entities from text',
    enabled: true
  }
];
const NaturalLanguageProcessingPage = () => {
  const navigate = useNavigate();
  const { user, hasRole } = useAuth();
  const { showToast } = useToast();
  // NLP features are restricted to admin and trainer roles only
  const canAccessNLP = hasRole(['super_admin', 'tenant_admin', 'trainer']);
  // If user doesn't have permission, show access denied
  if (!canAccessNLP) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="p-8 text-center max-w-md">
          <Lock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Restricted</h2>
          <p className="text-gray-600 mb-4">
            Natural Language Processing features are only available to administrators and trainers.
          </p>
          <p className="text-sm text-gray-500">
            Current role: <span className="font-medium">{user?.role}</span>
          </p>
        </Card>
      </div>
    );
  }
  const [loading, setLoading] = useState(false);
  const [inputText, setInputText] = useState('');
  const [results, setResults] = useState(null);
  const [savedAnalyses, setSavedAnalyses] = useState([]);
  const [activeTab, setActiveTab] = useState('analyze');
  const [selectedFeatures, setSelectedFeatures] = useState(['sentiment_analysis', 'key_extraction']);
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    avgSentiment: 0,
    topKeywords: [],
    languageDistribution: {}
  });
  useEffect(() => {
    fetchSavedAnalyses();
    fetchStats();
  }, []);
  const fetchSavedAnalyses = async () => {
    try {
      const response = await fetch('/api/ai/nlp/analyses', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setSavedAnalyses(data.analyses || []);
      }
    } catch (error) {
      console.error('Error fetching analyses:', error);
    }
  };
  const fetchStats = async () => {
    try {
      const response = await fetch('/api/ai/nlp/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data.stats || stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };
  const analyzeText = async () => {
    if (!inputText.trim()) {
      showToast('Please enter some text to analyze', 'error');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch('/api/ai/nlp/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          text: inputText,
          features: selectedFeatures
        })
      });
      if (response.ok) {
        const data = await response.json();
        setResults(data.results);
        showToast('Analysis completed successfully', 'success');
        fetchSavedAnalyses();
        fetchStats();
      } else {
        showToast('Failed to analyze text', 'error');
      }
    } catch (error) {
      showToast('Error analyzing text', 'error');
    } finally {
      setLoading(false);
    }
  };
  const exportResults = (format = 'json') => {
    // Additional permission check for export functionality
    if (!hasRole(['super_admin', 'tenant_admin', 'trainer'])) {
      showToast('Export functionality is restricted to administrators and trainers only', 'error');
      return;
    }
    if (!results) return;
    const dataStr = format === 'json' 
      ? JSON.stringify(results, null, 2)
      : generateCSV(results);
    const blob = new Blob([dataStr], { type: format === 'json' ? 'application/json' : 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nlp-analysis-${Date.now()}.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };
  const generateCSV = (data) => {
    // Simple CSV generation for results
    let csv = 'Feature,Result\n';
    Object.entries(data).forEach(([key, value]) => {
      csv += `"${key}","${JSON.stringify(value).replace(/"/g, '""')}"\n`;
    });
    return csv;
  };
  // Spinner component definition
  const Spinner = () => (
    <div className="flex justify-center">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
    </div>
  );
  const getSentimentIcon = (sentiment) => {
    if (sentiment > 0.6) return <CheckCircle className="w-5 h-5 text-green-500" />;
    if (sentiment < -0.6) return <XCircle className="w-5 h-5 text-red-500" />;
    return <AlertCircle className="w-5 h-5 text-yellow-500" />;
  };
  const getSentimentLabel = (sentiment) => {
    if (sentiment > 0.6) return 'Positive';
    if (sentiment > 0.2) return 'Slightly Positive';
    if (sentiment < -0.6) return 'Negative';
    if (sentiment < -0.2) return 'Slightly Negative';
    return 'Neutral';
  };
  const renderAnalyze = () => (
    <div className="space-y-6">
      {/* Input Section */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Text Analysis</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Input Text</label>
            <textarea
              className="w-full p-3 border rounded-lg"
              rows="6"
              placeholder="Enter text to analyze... (e.g., student feedback, essay, or any text content)"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Select Features</label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {nlpFeatures.map(feature => (
                <label key={feature.id} className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={selectedFeatures.includes(feature.id)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedFeatures([...selectedFeatures, feature.id]);
                      } else {
                        setSelectedFeatures(selectedFeatures.filter(f => f !== feature.id));
                      }
                    }}
                  />
                  <span className="text-sm">{feature.name}</span>
                </label>
              ))}
            </div>
          </div>
          <div className="flex space-x-2">
            <Button
              onClick={analyzeText}
              disabled={loading || !inputText.trim() || selectedFeatures.length === 0}
            >
              <Brain className="w-4 h-4 mr-2" />
              Analyze Text
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                setInputText('');
                setResults(null);
              }}
            >
              Clear
            </Button>
          </div>
        </div>
      </Card>
      {/* Results Section */}
      {results && (
        <Card>
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-semibold text-lg">Analysis Results</h3>
            {hasRole(['super_admin', 'tenant_admin', 'trainer']) && (
              <div className="space-x-2">
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => exportResults('json')}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export JSON
                </Button>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => exportResults('csv')}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export CSV
                </Button>
              </div>
            )}
          </div>
          <div className="space-y-4">
            {results.sentiment && (
              <div>
                <h4 className="font-medium mb-2">Sentiment Analysis</h4>
                <div className="flex items-center space-x-4">
                  {getSentimentIcon(results.sentiment.score)}
                  <div className="flex-1">
                    <p className="font-medium">{getSentimentLabel(results.sentiment.score)}</p>
                    <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                      <div
                        className={`h-2 rounded-full ${
                          results.sentiment.score > 0.2 ? 'bg-green-500' :
                          results.sentiment.score < -0.2 ? 'bg-red-500' :
                          'bg-yellow-500'
                        }`}
                        style={{ width: `${Math.abs(results.sentiment.score) * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-sm font-medium">
                    {(results.sentiment.score * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            )}
            {results.keywords && (
              <div>
                <h4 className="font-medium mb-2">Extracted Keywords</h4>
                <div className="flex flex-wrap gap-2">
                  {results.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
                    >
                      {keyword.text} ({keyword.score.toFixed(2)})
                    </span>
                  ))}
                </div>
              </div>
            )}
            {results.summary && (
              <div>
                <h4 className="font-medium mb-2">Summary</h4>
                <p className="text-sm bg-gray-50 p-3 rounded">{results.summary}</p>
              </div>
            )}
            {results.language && (
              <div>
                <h4 className="font-medium mb-2">Language Detection</h4>
                <div className="flex items-center space-x-2">
                  <Globe className="w-5 h-5 text-gray-600" />
                  <span className="font-medium">{results.language.name}</span>
                  <span className="text-sm text-gray-600">
                    (Confidence: {(results.language.confidence * 100).toFixed(1)}%)
                  </span>
                </div>
              </div>
            )}
            {results.entities && (
              <div>
                <h4 className="font-medium mb-2">Extracted Entities</h4>
                <div className="space-y-2">
                  {Object.entries(results.entities).map(([type, entities]) => (
                    <div key={type}>
                      <p className="text-sm font-medium text-gray-600 mb-1">
                        {type.charAt(0).toUpperCase() + type.slice(1)}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {entities.map((entity, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-gray-100 rounded text-sm"
                          >
                            {entity}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {results.intent && (
              <div>
                <h4 className="font-medium mb-2">Intent Recognition</h4>
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{results.intent.primary}</span>
                    <span className="text-sm text-gray-600">
                      {(results.intent.confidence * 100).toFixed(1)}% confidence
                    </span>
                  </div>
                  {results.intent.secondary && (
                    <p className="text-sm text-gray-600">
                      Secondary: {results.intent.secondary}
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
  const renderHistory = () => (
    <Card>
      <h3 className="font-semibold text-lg mb-4">Analysis History</h3>
      {savedAnalyses.length === 0 ? (
        <p className="text-gray-600 text-center py-8">No saved analyses yet</p>
      ) : (
        <div className="space-y-3">
          {savedAnalyses.map(analysis => (
            <div key={analysis.id} className="border rounded-lg p-4">
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <p className="font-medium mb-1">
                    {new Date(analysis.created_at).toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {analysis.text}
                  </p>
                </div>
                <Button
                  size="sm"
                  variant="secondary"
                  onClick={() => {
                    setInputText(analysis.text);
                    setResults(analysis.results);
                    setActiveTab('analyze');
                  }}
                >
                  View
                </Button>
              </div>
              <div className="flex items-center space-x-4 text-sm">
                {analysis.results.sentiment && (
                  <div className="flex items-center space-x-1">
                    {getSentimentIcon(analysis.results.sentiment.score)}
                    <span>{getSentimentLabel(analysis.results.sentiment.score)}</span>
                  </div>
                )}
                {analysis.results.language && (
                  <div className="flex items-center space-x-1">
                    <Globe className="w-4 h-4 text-gray-600" />
                    <span>{analysis.results.language.name}</span>
                  </div>
                )}
                {analysis.results.keywords && (
                  <div className="flex items-center space-x-1">
                    <Tag className="w-4 h-4 text-gray-600" />
                    <span>{analysis.results.keywords.length} keywords</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
  const renderInsights = () => (
    <div className="space-y-6">
      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Analyses</p>
              <p className="text-2xl font-bold">{stats.totalAnalyses}</p>
            </div>
            <Activity className="w-8 h-8 text-primary" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Sentiment</p>
              <p className="text-2xl font-bold">
                {stats.avgSentiment > 0 ? '+' : ''}{(stats.avgSentiment * 100).toFixed(1)}%
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Languages</p>
              <p className="text-2xl font-bold">{Object.keys(stats.languageDistribution).length}</p>
            </div>
            <Globe className="w-8 h-8 text-blue-600" />
          </div>
        </Card>
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Top Keywords</p>
              <p className="text-2xl font-bold">{stats.topKeywords.length}</p>
            </div>
            <Tag className="w-8 h-8 text-purple-600" />
          </div>
        </Card>
      </div>
      {/* Top Keywords */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Top Keywords</h3>
        {stats.topKeywords.length === 0 ? (
          <p className="text-gray-600">No keywords analyzed yet</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {stats.topKeywords.map((keyword, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
                style={{
                  fontSize: `${Math.max(12, Math.min(20, keyword.count * 2))}px`
                }}
              >
                {keyword.text} ({keyword.count})
              </span>
            ))}
          </div>
        )}
      </Card>
      {/* Language Distribution */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Language Distribution</h3>
        {Object.keys(stats.languageDistribution).length === 0 ? (
          <p className="text-gray-600">No language data yet</p>
        ) : (
          <div className="space-y-3">
            {Object.entries(stats.languageDistribution).map(([language, count]) => (
              <div key={language} className="flex items-center">
                <span className="w-20 text-sm">{language}</span>
                <div className="flex-1 mx-4">
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className="bg-primary h-4 rounded-full"
                      style={{
                        width: `${(count / stats.totalAnalyses) * 100}%`
                      }}
                    />
                  </div>
                </div>
                <span className="text-sm text-gray-600">
                  {((count / stats.totalAnalyses) * 100).toFixed(1)}%
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>
      {/* Use Cases */}
      <Card>
        <h3 className="font-semibold text-lg mb-4">Common Use Cases</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Student Feedback Analysis</h4>
            <p className="text-sm text-gray-600 mb-2">
              Analyze course feedback to understand student sentiment and extract key themes
            </p>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                setInputText("The course was excellent! The instructor explained concepts clearly and the practical exercises were very helpful. However, I felt the pace was a bit too fast in the advanced topics section.");
                setActiveTab('analyze');
              }}
            >
              Try Example
            </Button>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Essay Evaluation</h4>
            <p className="text-sm text-gray-600 mb-2">
              Summarize essays and extract key arguments for quicker evaluation
            </p>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                setInputText("Climate change is one of the most pressing issues of our time. The scientific consensus shows that human activities are the primary cause of global warming. We must take immediate action to reduce greenhouse gas emissions and transition to renewable energy sources.");
                setActiveTab('analyze');
              }}
            >
              Try Example
            </Button>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Support Ticket Classification</h4>
            <p className="text-sm text-gray-600 mb-2">
              Automatically categorize and prioritize student support requests
            </p>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                setInputText("I'm having trouble accessing my course materials. When I try to log in, I get an error message saying my account is locked. This is urgent as I have an assignment due tomorrow.");
                setActiveTab('analyze');
              }}
            >
              Try Example
            </Button>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Multi-language Support</h4>
            <p className="text-sm text-gray-600 mb-2">
              Detect languages and provide translations for international students
            </p>
            <Button
              size="sm"
              variant="secondary"
              onClick={() => {
                setInputText("Bonjour, je suis très satisfait de ce cours. Les explications sont claires et les exercices pratiques sont utiles.");
                setActiveTab('analyze');
              }}
            >
              Try Example
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Natural Language Processing</h1>
        <Button
          onClick={() => navigate('/ai/insights')}
          variant="secondary"
        >
          Back to AI Tools
        </Button>
      </div>
      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {nlpFeatures.slice(0, 3).map(feature => (
          <Card key={feature.id}>
            <div className="flex items-center space-x-3 mb-2">
              <feature.icon className="w-6 h-6 text-primary" />
              <h3 className="font-medium">{feature.name}</h3>
            </div>
            <p className="text-sm text-gray-600">{feature.description}</p>
          </Card>
        ))}
      </div>
      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex space-x-8">
          {['analyze', 'history', 'insights'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize
                ${activeTab === tab
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>
      {/* Tab Content */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Spinner />
        </div>
      ) : (
        <>
          {activeTab === 'analyze' && renderAnalyze()}
          {activeTab === 'history' && renderHistory()}
          {activeTab === 'insights' && renderInsights()}
        </>
      )}
    </div>
  );
};
export default NaturalLanguageProcessingPage;