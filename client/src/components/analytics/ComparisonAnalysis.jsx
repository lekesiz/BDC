import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar, Radar, Scatter } from 'react-chartjs-2';
import { motion } from 'framer-motion';
import { useAuth } from '../../contexts/AuthContext';
// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);
const ComparisonAnalysis = ({ beneficiaryId, assessmentId }) => {
  const { user } = useAuth();
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [comparisonType, setComparisonType] = useState('peer');
  const [timeRange, setTimeRange] = useState('last6months');
  const [selectedMetrics, setSelectedMetrics] = useState([
    'accuracy',
    'speed',
    'consistency',
    'improvement'
  ]);
  const [viewMode, setViewMode] = useState('overview'); // overview, detailed, timeline
  useEffect(() => {
    fetchComparisonData();
  }, [beneficiaryId, assessmentId, comparisonType, timeRange]);
  const fetchComparisonData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        comparisonType,
        timeRange,
        assessmentId: assessmentId || '',
        includeMetrics: selectedMetrics.join(',')
      });
      const response = await fetch(
        `/api/analytics/comparison/${beneficiaryId}?${params}`
      );
      const data = await response.json();
      setComparisonData(data);
    } catch (error) {
      console.error('Error fetching comparison data:', error);
    } finally {
      setLoading(false);
    }
  };
  const getPeerComparisonChart = () => {
    if (!comparisonData?.peerComparison) return null;
    const { userMetrics, peerMetrics, percentile } = comparisonData.peerComparison;
    const labels = Object.keys(userMetrics);
    const userData = Object.values(userMetrics);
    const peerAvgData = Object.values(peerMetrics.average);
    const peerBestData = Object.values(peerMetrics.best);
    return {
      labels,
      datasets: [
        {
          label: 'Your Performance',
          data: userData,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderWidth: 3,
          pointBackgroundColor: 'rgb(59, 130, 246)',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: 'rgb(59, 130, 246)',
        },
        {
          label: 'Peer Average',
          data: peerAvgData,
          borderColor: 'rgb(156, 163, 175)',
          backgroundColor: 'rgba(156, 163, 175, 0.3)',
          borderWidth: 2,
          borderDash: [5, 5],
        },
        {
          label: 'Top Performers',
          data: peerBestData,
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.3)',
          borderWidth: 2,
          borderDash: [10, 5],
        }
      ]
    };
  };
  const getTimelineComparisonChart = () => {
    if (!comparisonData?.timeline) return null;
    const { userProgress, peerProgress } = comparisonData.timeline;
    const labels = userProgress.map(point => 
      new Date(point.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    );
    const userData = userProgress.map(point => point.score);
    const peerData = peerProgress.map(point => point.avgScore);
    return {
      labels,
      datasets: [
        {
          label: 'Your Progress',
          data: userData,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4,
        },
        {
          label: 'Peer Average',
          data: peerData,
          borderColor: 'rgb(156, 163, 175)',
          backgroundColor: 'rgba(156, 163, 175, 0.1)',
          fill: true,
          tension: 0.4,
        }
      ]
    };
  };
  const getCategoryComparisonChart = () => {
    if (!comparisonData?.categoryComparison) return null;
    const categories = comparisonData.categoryComparison;
    const labels = Object.keys(categories);
    const userScores = labels.map(cat => categories[cat].userScore);
    const peerScores = labels.map(cat => categories[cat].peerAverage);
    const gaps = labels.map(cat => categories[cat].gap);
    return {
      labels,
      datasets: [
        {
          label: 'Your Score',
          data: userScores,
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 2,
        },
        {
          label: 'Peer Average',
          data: peerScores,
          backgroundColor: 'rgba(156, 163, 175, 0.8)',
          borderColor: 'rgb(156, 163, 175)',
          borderWidth: 2,
        },
        {
          label: 'Gap',
          data: gaps,
          backgroundColor: gaps.map(gap => 
            gap >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)'
          ),
          borderColor: gaps.map(gap => 
            gap >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'
          ),
          borderWidth: 2,
          type: 'line',
          yAxisID: 'y1',
        }
      ]
    };
  };
  const getDistributionChart = () => {
    if (!comparisonData?.distribution) return null;
    const { bins, userPosition, frequencies } = comparisonData.distribution;
    const backgroundColor = bins.map((bin, index) => {
      if (index === userPosition) {
        return 'rgba(59, 130, 246, 0.8)';
      }
      return 'rgba(156, 163, 175, 0.6)';
    });
    return {
      labels: bins.map(bin => `${bin.min}-${bin.max}%`),
      datasets: [
        {
          label: 'Score Distribution',
          data: frequencies,
          backgroundColor,
          borderColor: backgroundColor.map(color => 
            color.replace('0.8', '1').replace('0.6', '1')
          ),
          borderWidth: 2,
        }
      ]
    };
  };
  const MetricCard = ({ title, value, comparison, trend, percentile }) => {
    const isPositive = comparison >= 0;
    const trendIcon = trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→';
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-md p-6"
      >
        <h3 className="text-sm font-medium text-gray-500 mb-2">{title}</h3>
        <div className="flex items-baseline justify-between">
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          <div className="text-right">
            <p className={`text-sm font-medium ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {isPositive ? '+' : ''}{comparison}%
            </p>
            <p className="text-xs text-gray-500">
              {trendIcon} {percentile ? `${percentile}th percentile` : ''}
            </p>
          </div>
        </div>
      </motion.div>
    );
  };
  const DetailedComparisonTable = ({ data }) => {
    if (!data) return null;
    return (
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Metric
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Your Score
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Peer Average
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Difference
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Percentile
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {Object.entries(data).map(([metric, values]) => {
              const difference = values.userScore - values.peerAverage;
              const isPositive = difference >= 0;
              return (
                <tr key={metric}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {metric}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {values.userScore.toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {values.peerAverage.toFixed(1)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                    isPositive ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {isPositive ? '+' : ''}{difference.toFixed(1)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <span>{values.percentile}th</span>
                      <div className="ml-2 w-20 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${values.percentile}%` }}
                        />
                      </div>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    );
  };
  const InsightsPanel = ({ insights }) => {
    if (!insights || insights.length === 0) return null;
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-md p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Key Insights & Recommendations
        </h3>
        <div className="space-y-4">
          {insights.map((insight, index) => (
            <div key={index} className="flex items-start">
              <div className={`flex-shrink-0 w-2 h-2 mt-1.5 rounded-full ${
                insight.type === 'strength' ? 'bg-green-500' :
                insight.type === 'opportunity' ? 'bg-yellow-500' :
                insight.type === 'challenge' ? 'bg-red-500' :
                'bg-blue-500'
              }`} />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">{insight.title}</p>
                <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                {insight.recommendation && (
                  <p className="text-sm text-blue-600 mt-2 font-medium">
                    Recommendation: {insight.recommendation}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </motion.div>
    );
  };
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  if (!comparisonData) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No comparison data available</p>
      </div>
    );
  }
  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Comparison Type
            </label>
            <select
              value={comparisonType}
              onChange={(e) => setComparisonType(e.target.value)}
              className="block w-40 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="peer">Peer Group</option>
              <option value="cohort">Same Cohort</option>
              <option value="age">Age Group</option>
              <option value="skill">Skill Level</option>
              <option value="historical">Past Performance</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Time Range
            </label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="block w-40 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="last30days">Last 30 Days</option>
              <option value="last3months">Last 3 Months</option>
              <option value="last6months">Last 6 Months</option>
              <option value="lastyear">Last Year</option>
              <option value="alltime">All Time</option>
            </select>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('overview')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              viewMode === 'overview'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setViewMode('detailed')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              viewMode === 'detailed'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Detailed
          </button>
          <button
            onClick={() => setViewMode('timeline')}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              viewMode === 'timeline'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Timeline
          </button>
        </div>
      </div>
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Overall Percentile"
          value={`${comparisonData.summary.overallPercentile}th`}
          comparison={comparisonData.summary.percentileChange}
          trend={comparisonData.summary.trend}
          percentile={comparisonData.summary.overallPercentile}
        />
        <MetricCard
          title="Average Score"
          value={`${comparisonData.summary.averageScore}%`}
          comparison={comparisonData.summary.scoreComparison}
          trend={comparisonData.summary.scoreTrend}
        />
        <MetricCard
          title="Improvement Rate"
          value={`${comparisonData.summary.improvementRate}%`}
          comparison={comparisonData.summary.improvementComparison}
          trend="up"
        />
        <MetricCard
          title="Consistency Score"
          value={comparisonData.summary.consistencyScore}
          comparison={comparisonData.summary.consistencyComparison}
          trend={comparisonData.summary.consistencyTrend}
        />
      </div>
      {/* Main Content based on View Mode */}
      {viewMode === 'overview' && (
        <>
          {/* Peer Comparison Radar */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Performance Comparison
              </h3>
              <div className="h-80">
                <Radar
                  data={getPeerComparisonChart()}
                  options={{
                    scales: {
                      r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                          stepSize: 20
                        }
                      }
                    },
                    plugins: {
                      legend: {
                        position: 'bottom'
                      }
                    },
                    maintainAspectRatio: false
                  }}
                />
              </div>
            </div>
            {/* Distribution Chart */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Score Distribution
              </h3>
              <div className="h-80">
                <Bar
                  data={getDistributionChart()}
                  options={{
                    scales: {
                      y: {
                        beginAtZero: true,
                        title: {
                          display: true,
                          text: 'Number of Students'
                        }
                      },
                      x: {
                        title: {
                          display: true,
                          text: 'Score Range'
                        }
                      }
                    },
                    plugins: {
                      legend: {
                        display: false
                      },
                      tooltip: {
                        callbacks: {
                          afterLabel: function(context) {
                            if (context.dataIndex === comparisonData.distribution.userPosition) {
                              return 'Your Score Range';
                            }
                            return '';
                          }
                        }
                      }
                    },
                    maintainAspectRatio: false
                  }}
                />
              </div>
            </div>
          </div>
          {/* Category Comparison */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Category Comparison
            </h3>
            <div className="h-80">
              <Bar
                data={getCategoryComparisonChart()}
                options={{
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                      title: {
                        display: true,
                        text: 'Score (%)'
                      }
                    },
                    y1: {
                      beginAtZero: true,
                      position: 'right',
                      title: {
                        display: true,
                        text: 'Gap (%)'
                      },
                      grid: {
                        drawOnChartArea: false
                      }
                    }
                  },
                  plugins: {
                    legend: {
                      position: 'bottom'
                    }
                  },
                  maintainAspectRatio: false
                }}
              />
            </div>
          </div>
        </>
      )}
      {viewMode === 'detailed' && (
        <>
          {/* Detailed Comparison Table */}
          <DetailedComparisonTable data={comparisonData.detailedMetrics} />
          {/* Strengths and Weaknesses */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Comparative Strengths
              </h3>
              <ul className="space-y-3">
                {comparisonData.analysis.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="flex-shrink-0 w-5 h-5 text-green-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{strength.area}</p>
                      <p className="text-sm text-gray-600">
                        {strength.percentile}th percentile • {strength.comparison}% above average
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Areas for Improvement
              </h3>
              <ul className="space-y-3">
                {comparisonData.analysis.improvements.map((improvement, index) => (
                  <li key={index} className="flex items-start">
                    <svg className="flex-shrink-0 w-5 h-5 text-yellow-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{improvement.area}</p>
                      <p className="text-sm text-gray-600">
                        {improvement.percentile}th percentile • {Math.abs(improvement.comparison)}% below average
                      </p>
                      <p className="text-sm text-blue-600 mt-1">
                        Target: Reach {improvement.target}th percentile
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </>
      )}
      {viewMode === 'timeline' && (
        <>
          {/* Timeline Progress Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Progress Timeline Comparison
            </h3>
            <div className="h-96">
              <Line
                data={getTimelineComparisonChart()}
                options={{
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 100,
                      title: {
                        display: true,
                        text: 'Score (%)'
                      }
                    },
                    x: {
                      title: {
                        display: true,
                        text: 'Date'
                      }
                    }
                  },
                  plugins: {
                    legend: {
                      position: 'bottom'
                    },
                    tooltip: {
                      mode: 'index',
                      intersect: false
                    }
                  },
                  interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                  },
                  maintainAspectRatio: false
                }}
              />
            </div>
          </div>
          {/* Growth Rate Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Growth Rate Analysis
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Your Growth Rate</span>
                    <span className="text-sm font-bold text-blue-600">
                      {comparisonData.growth.userRate}% per month
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: `${Math.min(comparisonData.growth.userRate * 10, 100)}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Peer Average</span>
                    <span className="text-sm font-bold text-gray-600">
                      {comparisonData.growth.peerRate}% per month
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-gray-600 h-2 rounded-full"
                      style={{ width: `${Math.min(comparisonData.growth.peerRate * 10, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Milestone Achievements
              </h3>
              <div className="space-y-3">
                {comparisonData.milestones.map((milestone, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className={`w-4 h-4 rounded-full ${
                        milestone.achieved ? 'bg-green-500' : 'bg-gray-300'
                      }`} />
                      <span className="ml-3 text-sm font-medium text-gray-700">
                        {milestone.name}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-gray-900">
                        {milestone.userDays} days
                      </p>
                      <p className="text-xs text-gray-500">
                        Avg: {milestone.peerDays} days
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
      {/* Insights Panel */}
      <InsightsPanel insights={comparisonData.insights} />
      {/* Action Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Recommended Actions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {comparisonData.recommendations.map((recommendation, index) => (
            <div key={index} className="bg-white rounded-lg p-4">
              <div className="flex items-center mb-2">
                <div className={`w-2 h-2 rounded-full ${
                  recommendation.priority === 'high' ? 'bg-red-500' :
                  recommendation.priority === 'medium' ? 'bg-yellow-500' :
                  'bg-green-500'
                }`} />
                <span className="ml-2 text-sm font-medium text-gray-900">
                  {recommendation.title}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">
                {recommendation.description}
              </p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-gray-500">
                  Est. impact: {recommendation.impact}
                </span>
                <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
                  Start →
                </button>
              </div>
            </div>
          ))}
        </div>
      </motion.div>
      {/* Export Options */}
      <div className="flex justify-end gap-4">
        <button className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
          Export Report
        </button>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700">
          Share Analysis
        </button>
      </div>
    </div>
  );
};
export default ComparisonAnalysis;