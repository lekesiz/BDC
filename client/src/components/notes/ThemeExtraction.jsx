import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
} from 'chart.js';
import { Doughnut, Bar, Radar } from 'react-chartjs-2';
import { motion, AnimatePresence } from 'framer-motion';
import WordCloud from 'react-d3-cloud';

// Register ChartJS components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
);

const ThemeExtraction = ({ noteId, noteContent }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedView, setSelectedView] = useState('themes');
  const [selectedTheme, setSelectedTheme] = useState(null);
  const [compareMode, setCompareMode] = useState(false);
  const [selectedNotes, setSelectedNotes] = useState([]);

  useEffect(() => {
    if (noteId || noteContent) {
      analyzeNote();
    }
  }, [noteId, noteContent]);

  const analyzeNote = async () => {
    try {
      setLoading(true);
      const payload = noteId 
        ? { noteId } 
        : { content: noteContent };

      const response = await fetch('/api/notes/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...payload,
          analysisType: 'comprehensive'
        })
      });

      const data = await response.json();
      setAnalysis(data);
    } catch (error) {
      console.error('Error analyzing note:', error);
    } finally {
      setLoading(false);
    }
  };

  const getThemeDistribution = () => {
    if (!analysis?.themes) return null;

    const labels = analysis.themes.map(theme => theme.name);
    const data = analysis.themes.map(theme => theme.prominence || 3);
    const backgroundColors = [
      'rgba(59, 130, 246, 0.8)',
      'rgba(34, 197, 94, 0.8)',
      'rgba(251, 191, 36, 0.8)',
      'rgba(239, 68, 68, 0.8)',
      'rgba(168, 85, 247, 0.8)',
    ];

    return {
      labels,
      datasets: [{
        data,
        backgroundColor: backgroundColors,
        borderColor: backgroundColors.map(color => color.replace('0.8', '1')),
        borderWidth: 2,
      }]
    };
  };

  const getConceptRadar = () => {
    if (!analysis?.concepts) return null;

    const labels = analysis.concepts.slice(0, 8).map(c => c.name);
    const values = analysis.concepts.slice(0, 8).map(c => {
      // Calculate concept strength based on various factors
      const contextLength = c.context?.length || 0;
      const definitionLength = c.definition?.length || 0;
      return Math.min(100, (contextLength + definitionLength) / 5);
    });

    return {
      labels,
      datasets: [{
        label: 'Concept Strength',
        data: values,
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgb(59, 130, 246)',
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(59, 130, 246)',
      }]
    };
  };

  const getSkillsChart = () => {
    if (!analysis?.skills) return null;

    const categories = Object.keys(analysis.skills);
    const data = categories.map(cat => analysis.skills[cat].length);

    return {
      labels: categories.map(cat => cat.replace('_', ' ').charAt(0).toUpperCase() + cat.slice(1).replace('_', ' ')),
      datasets: [{
        label: 'Skills Identified',
        data,
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderColor: [
          'rgb(59, 130, 246)',
          'rgb(34, 197, 94)',
          'rgb(251, 191, 36)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 2,
      }]
    };
  };

  const getWordCloudData = () => {
    if (!analysis?.key_elements?.important_terms) return [];

    return analysis.key_elements.important_terms.map(term => ({
      text: term.term,
      value: term.frequency * 100
    }));
  };

  const ThemeCard = ({ theme }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className="bg-white rounded-lg shadow-md p-6 cursor-pointer border-2 border-transparent hover:border-blue-500 transition-all"
      onClick={() => setSelectedTheme(theme)}
    >
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-lg font-semibold text-gray-900">{theme.name}</h3>
        <div className="flex items-center bg-blue-100 rounded-full px-3 py-1">
          <span className="text-sm font-medium text-blue-800">Level {theme.prominence}</span>
        </div>
      </div>
      {theme.explanation && (
        <p className="text-sm text-gray-600 mb-3">{theme.explanation}</p>
      )}
      {theme.evidence && (
        <div className="text-sm text-gray-500 italic">
          <p className="font-medium mb-1">Evidence:</p>
          <p className="line-clamp-2">{theme.evidence}</p>
        </div>
      )}
    </motion.div>
  );

  const ConceptCard = ({ concept }) => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200"
    >
      <h4 className="font-semibold text-gray-900 mb-2">{concept.name}</h4>
      {concept.definition && (
        <p className="text-sm text-gray-700 mb-2">{concept.definition}</p>
      )}
      {concept.context && (
        <p className="text-xs text-gray-600 italic">Context: {concept.context}</p>
      )}
    </motion.div>
  );

  const SkillBadge = ({ skill, category }) => {
    const categoryColors = {
      technical_skills: 'blue',
      soft_skills: 'green',
      cognitive_skills: 'purple',
      subject_knowledge: 'yellow'
    };

    const color = categoryColors[category] || 'gray';

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-${color}-100 text-${color}-800 mr-2 mb-2`}>
        {typeof skill === 'string' ? skill : skill.skill}
        {skill.confidence && (
          <span className={`ml-2 text-xs text-${color}-600`}>
            ({skill.confidence})
          </span>
        )}
      </span>
    );
  };

  const SentimentIndicator = ({ sentiment }) => {
    const sentimentColors = {
      positive: 'green',
      negative: 'red',
      neutral: 'gray'
    };

    const color = sentimentColors[sentiment.sentiment_label] || 'gray';

    return (
      <div className="flex items-center space-x-4">
        <div className={`w-4 h-4 rounded-full bg-${color}-500`} />
        <div>
          <p className="text-sm font-medium text-gray-900">
            {sentiment.sentiment_label.charAt(0).toUpperCase() + sentiment.sentiment_label.slice(1)}
          </p>
          <p className="text-xs text-gray-500">
            Confidence: {(sentiment.confidence * 100).toFixed(1)}%
          </p>
        </div>
        <div className="flex-1">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Compound Score</span>
            <span>{sentiment.overall_scores.compound.toFixed(3)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`bg-${color}-500 h-2 rounded-full`}
              style={{ width: `${Math.abs(sentiment.overall_scores.compound) * 100}%` }}
            />
          </div>
        </div>
      </div>
    );
  };

  const InsightPanel = ({ insights }) => (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
      <div className="space-y-4">
        {insights.main_topics && insights.main_topics.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Main Topics</h4>
            <ul className="list-disc list-inside space-y-1">
              {insights.main_topics.map((topic, index) => (
                <li key={index} className="text-sm text-gray-600">{topic}</li>
              ))}
            </ul>
          </div>
        )}
        {insights.key_insights && insights.key_insights.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Key Insights</h4>
            <ul className="list-disc list-inside space-y-1">
              {insights.key_insights.map((insight, index) => (
                <li key={index} className="text-sm text-gray-600">{insight}</li>
              ))}
            </ul>
          </div>
        )}
        {insights.comprehension_assessment && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Comprehension Assessment</h4>
            <p className="text-sm text-gray-600">{insights.comprehension_assessment}</p>
          </div>
        )}
        {insights.next_steps && insights.next_steps.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Recommended Next Steps</h4>
            <ol className="list-decimal list-inside space-y-1">
              {insights.next_steps.map((step, index) => (
                <li key={index} className="text-sm text-gray-600">{step}</li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing note content...</p>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No analysis available</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* View Selector */}
      <div className="flex flex-wrap gap-2 justify-center mb-6">
        {['themes', 'concepts', 'skills', 'sentiment', 'summary', 'insights'].map((view) => (
          <button
            key={view}
            onClick={() => setSelectedView(view)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              selectedView === view
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {view.charAt(0).toUpperCase() + view.slice(1)}
          </button>
        ))}
      </div>

      {/* Content based on selected view */}
      <AnimatePresence mode="wait">
        {selectedView === 'themes' && analysis.themes && (
          <motion.div
            key="themes"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Theme Distribution Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Theme Distribution</h3>
                <div className="h-80">
                  <Doughnut
                    data={getThemeDistribution()}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'bottom',
                        },
                      },
                    }}
                  />
                </div>
              </div>

              {/* Theme Cards */}
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900">Identified Themes</h3>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {analysis.themes.map((theme, index) => (
                    <ThemeCard key={index} theme={theme} />
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {selectedView === 'concepts' && analysis.concepts && (
          <motion.div
            key="concepts"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Concept Radar Chart */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Concept Analysis</h3>
                <div className="h-80">
                  <Radar
                    data={getConceptRadar()}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      scales: {
                        r: {
                          beginAtZero: true,
                          max: 100,
                        },
                      },
                    }}
                  />
                </div>
              </div>

              {/* Word Cloud */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Terms</h3>
                <div className="h-80">
                  <WordCloud
                    data={getWordCloudData()}
                    width={400}
                    height={300}
                    font="Arial"
                    fontWeight="bold"
                    fontSize={(word) => Math.log(word.value) * 10}
                    rotate={0}
                    padding={5}
                    random={() => 0.5}
                  />
                </div>
              </div>
            </div>

            {/* Concept Cards */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Identified Concepts</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analysis.concepts.map((concept, index) => (
                  <ConceptCard key={index} concept={concept} />
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {selectedView === 'skills' && analysis.skills && (
          <motion.div
            key="skills"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Skills Chart */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Skills Distribution</h3>
              <div className="h-80">
                <Bar
                  data={getSkillsChart()}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      y: {
                        beginAtZero: true,
                      },
                    },
                  }}
                />
              </div>
            </div>

            {/* Skills by Category */}
            <div className="space-y-6">
              {Object.entries(analysis.skills).map(([category, skills]) => (
                <div key={category} className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    {category.replace('_', ' ').charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}
                  </h3>
                  <div className="flex flex-wrap">
                    {skills.map((skill, index) => (
                      <SkillBadge key={index} skill={skill} category={category} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {selectedView === 'sentiment' && analysis.sentiment && (
          <motion.div
            key="sentiment"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Overall Sentiment */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Sentiment</h3>
              <SentimentIndicator sentiment={analysis.sentiment} />
            </div>

            {/* Sentence-level Analysis */}
            {analysis.sentiment.sentence_analysis && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentence Analysis</h3>
                <div className="space-y-3">
                  {analysis.sentiment.sentence_analysis.map((item, index) => (
                    <div key={index} className="border-l-4 border-gray-200 pl-4 py-2">
                      <p className="text-sm text-gray-700 mb-1">{item.sentence}</p>
                      <div className="flex items-center space-x-4">
                        <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                          item.dominant === 'positive' ? 'bg-green-100 text-green-800' :
                          item.dominant === 'negative' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {item.dominant}
                        </span>
                        <span className="text-xs text-gray-500">
                          Score: {item.scores.compound.toFixed(3)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Emotion Words */}
            {analysis.sentiment.emotion_words && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Emotion Words</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {Object.entries(analysis.sentiment.emotion_words).map(([category, words]) => (
                    <div key={category} className={`p-4 rounded-lg ${
                      category === 'positive' ? 'bg-green-50' :
                      category === 'negative' ? 'bg-red-50' :
                      'bg-gray-50'
                    }`}>
                      <h4 className={`font-medium mb-2 ${
                        category === 'positive' ? 'text-green-800' :
                        category === 'negative' ? 'text-red-800' :
                        'text-gray-800'
                      }`}>
                        {category.charAt(0).toUpperCase() + category.slice(1)}
                      </h4>
                      <div className="flex flex-wrap">
                        {words.map((word, index) => (
                          <span key={index} className={`inline-block px-2 py-1 m-1 text-sm rounded ${
                            category === 'positive' ? 'bg-green-200 text-green-800' :
                            category === 'negative' ? 'bg-red-200 text-red-800' :
                            'bg-gray-200 text-gray-800'
                          }`}>
                            {word}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        )}

        {selectedView === 'summary' && analysis.summary && (
          <motion.div
            key="summary"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* One-line Summary */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">One-Line Summary</h3>
              <p className="text-lg text-gray-800 font-medium italic">
                "{analysis.summary.one_line}"
              </p>
            </div>

            {/* Abstractive Summary */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Executive Summary</h3>
              <p className="text-gray-700 leading-relaxed">
                {analysis.summary.abstractive}
              </p>
            </div>

            {/* Key Points */}
            {analysis.summary.key_points && analysis.summary.key_points.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Points</h3>
                <ul className="space-y-2">
                  {analysis.summary.key_points.map((point, index) => (
                    <li key={index} className="flex items-start">
                      <span className="text-blue-500 mr-3 mt-1">•</span>
                      <span className="text-gray-700">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Extractive Summary */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Extract Summary</h3>
              <p className="text-gray-700 leading-relaxed">
                {analysis.summary.extractive}
              </p>
            </div>
          </motion.div>
        )}

        {selectedView === 'insights' && analysis.ai_insights && (
          <motion.div
            key="insights"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
          >
            <InsightPanel insights={analysis.ai_insights} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quality Score */}
      {analysis.quality_score !== undefined && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Note Quality Score</h3>
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Overall Quality</span>
                <span>{analysis.quality_score}/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all duration-500 ${
                    analysis.quality_score >= 80 ? 'bg-green-500' :
                    analysis.quality_score >= 60 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${analysis.quality_score}%` }}
                />
              </div>
            </div>
            <div className="ml-6">
              <span className={`text-2xl font-bold ${
                analysis.quality_score >= 80 ? 'text-green-600' :
                analysis.quality_score >= 60 ? 'text-yellow-600' :
                'text-red-600'
              }`}>
                {analysis.quality_score >= 80 ? 'Excellent' :
                 analysis.quality_score >= 60 ? 'Good' :
                 'Needs Improvement'}
              </span>
            </div>
          </div>

          {/* Quality Breakdown */}
          {analysis.text_statistics && (
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Words</p>
                <p className="font-semibold">{analysis.text_statistics.word_count}</p>
              </div>
              <div>
                <p className="text-gray-500">Sentences</p>
                <p className="font-semibold">{analysis.text_statistics.sentence_count}</p>
              </div>
              <div>
                <p className="text-gray-500">Readability</p>
                <p className="font-semibold">
                  {analysis.text_statistics.readability_score?.toFixed(1) || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-gray-500">Grade Level</p>
                <p className="font-semibold">
                  {analysis.text_statistics.grade_level?.toFixed(1) || 'N/A'}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Selected Theme Modal */}
      <AnimatePresence>
        {selectedTheme && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setSelectedTheme(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">{selectedTheme.name}</h2>
                <button
                  onClick={() => setSelectedTheme(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {selectedTheme.explanation && (
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-700 mb-2">Explanation</h3>
                  <p className="text-gray-600">{selectedTheme.explanation}</p>
                </div>
              )}
              
              {selectedTheme.evidence && (
                <div className="mb-4">
                  <h3 className="font-semibold text-gray-700 mb-2">Evidence</h3>
                  <p className="text-gray-600 italic">{selectedTheme.evidence}</p>
                </div>
              )}
              
              <div className="flex items-center justify-between mt-6">
                <div className="flex items-center">
                  <span className="text-sm text-gray-500 mr-2">Prominence:</span>
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((level) => (
                      <svg
                        key={level}
                        className={`w-5 h-5 ${
                          level <= selectedTheme.prominence ? 'text-yellow-400' : 'text-gray-300'
                        }`}
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => setSelectedTheme(null)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Close
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ThemeExtraction;