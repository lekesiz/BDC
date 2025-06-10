// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement } from
'chart.js';
import { Radar, Bar, Doughnut } from 'react-chartjs-2';
import { motion } from 'framer-motion';
// Register ChartJS components
import { useTranslation } from "react-i18next";ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement
);
const SkillsVisualization = ({ assessmentData, beneficiaryId }) => {const { t } = useTranslation();
  const [chartType, setChartType] = useState('radar');
  const [skillsData, setSkillsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [timeRange, setTimeRange] = useState('last30days');
  useEffect(() => {
    fetchSkillsData();
  }, [beneficiaryId, timeRange]);
  const fetchSkillsData = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/analytics/skills/${beneficiaryId}?timeRange=${timeRange}`
      );
      const data = await response.json();
      setSkillsData(data);
    } catch (error) {
      console.error('Error fetching skills data:', error);
    } finally {
      setLoading(false);
    }
  };
  const getRadarData = () => {
    if (!skillsData) return null;
    const categories = selectedCategory === 'all' ?
    skillsData.categories :
    skillsData.categories.filter((cat) => cat.id === selectedCategory);
    const labels = categories.map((cat) => cat.name);
    const currentScores = categories.map((cat) => cat.currentScore);
    const previousScores = categories.map((cat) => cat.previousScore);
    const targetScores = categories.map((cat) => cat.targetScore);
    return {
      labels,
      datasets: [
      {
        label: 'Current Performance',
        data: currentScores,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderWidth: 3,
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(59, 130, 246)'
      },
      {
        label: 'Previous Performance',
        data: previousScores,
        borderColor: 'rgb(156, 163, 175)',
        backgroundColor: 'rgba(156, 163, 175, 0.1)',
        borderWidth: 2,
        borderDash: [5, 5],
        pointBackgroundColor: 'rgb(156, 163, 175)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(156, 163, 175)'
      },
      {
        label: 'Target',
        data: targetScores,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        borderWidth: 2,
        borderDash: [10, 5],
        pointBackgroundColor: 'rgb(34, 197, 94)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(34, 197, 94)'
      }]

    };
  };
  const getBarData = () => {
    if (!skillsData) return null;
    const categories = selectedCategory === 'all' ?
    skillsData.categories :
    skillsData.categories.filter((cat) => cat.id === selectedCategory);
    const labels = categories.map((cat) => cat.name);
    const improvements = categories.map((cat) =>
    ((cat.currentScore - cat.previousScore) / cat.previousScore * 100).toFixed(1)
    );
    return {
      labels,
      datasets: [
      {
        label: 'Improvement %',
        data: improvements,
        backgroundColor: improvements.map((imp) =>
        imp >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)'
        ),
        borderColor: improvements.map((imp) =>
        imp >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'
        ),
        borderWidth: 2
      }]

    };
  };
  const getDoughnutData = () => {
    if (!skillsData) return null;
    const masteryLevels = skillsData.masteryDistribution;
    return {
      labels: ['Expert', 'Proficient', 'Developing', 'Beginner'],
      datasets: [
      {
        data: [
        masteryLevels.expert,
        masteryLevels.proficient,
        masteryLevels.developing,
        masteryLevels.beginner],

        backgroundColor: [
        'rgba(34, 197, 94, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(251, 191, 36, 0.8)',
        'rgba(239, 68, 68, 0.8)'],

        borderColor: [
        'rgb(34, 197, 94)',
        'rgb(59, 130, 246)',
        'rgb(251, 191, 36)',
        'rgb(239, 68, 68)'],

        borderWidth: 2
      }]

    };
  };
  const radarOptions = {
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: {
          stepSize: 20,
          font: {
            size: 12
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.1)'
        },
        pointLabels: {
          font: {
            size: 14,
            weight: 'bold'
          }
        }
      }
    },
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          font: {
            size: 14
          }
        }
      },
      tooltip: {
        enabled: true,
        callbacks: {
          label: function (context) {
            return context.dataset.label + ': ' + context.parsed.r + '%';
          }
        }
      }
    },
    maintainAspectRatio: false
  };
  const barOptions = {
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function (value) {
            return value + '%';
          }
        }
      }
    },
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return 'Improvement: ' + context.parsed.y + '%';
          }
        }
      }
    },
    maintainAspectRatio: false
  };
  const doughnutOptions = {
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          font: {
            size: 14
          }
        }
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = (value / total * 100).toFixed(1);
            return label + ': ' + percentage + '%';
          }
        }
      }
    },
    maintainAspectRatio: false
  };
  const SkillCard = ({ skill }) => {const { t } = useTranslation();
    const improvement = ((skill.currentScore - skill.previousScore) / skill.previousScore * 100).toFixed(1);
    const isImproving = improvement >= 0;
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-md p-6 border border-gray-200">

        <div className="flex justify-between items-start mb-4">
          <div>
            <h4 className="text-lg font-semibold text-gray-900">{skill.name}</h4>
            <p className="text-sm text-gray-500">{skill.category}</p>
          </div>
          <div className={`flex items-center ${isImproving ? 'text-green-600' : 'text-red-600'}`}>
            {isImproving ?
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg> :

            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
            }
            <span className="font-semibold">{improvement}%</span>
          </div>
        </div>
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>{t("components.current_level")}</span>
            <span>{skill.currentScore}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${skill.currentScore}%` }} />

          </div>
        </div>
        <div className="mb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>{t("components.target_level")}</span>
            <span>{skill.targetScore}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${skill.targetScore}%` }} />

          </div>
        </div>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">{t("components.last_assessment")}</p>
            <p className="font-semibold">{skill.lastAssessmentDate}</p>
          </div>
          <div>
            <p className="text-gray-500">{t("components.next_target")}</p>
            <p className="font-semibold">{skill.nextTargetDate}</p>
          </div>
        </div>
        {skill.recommendations && skill.recommendations.length > 0 &&
        <div className="mt-4 pt-4 border-t border-gray-200">
            <p className="text-sm font-semibold text-gray-700 mb-2">{t("components.recommendations")}</p>
            <ul className="text-sm text-gray-600 space-y-1">
              {skill.recommendations.map((rec, index) =>
            <li key={index} className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  {rec}
                </li>
            )}
            </ul>
          </div>
        }
      </motion.div>);

  };
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>);

  }
  if (!skillsData) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">{t("components.no_skills_data_available")}</p>
      </div>);

  }
  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{t("components.chart_type")}

          </label>
          <select
            value={chartType}
            onChange={(e) => setChartType(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">

            <option value="radar">{t("components.radar_chart")}</option>
            <option value="bar">{t("components.progress_chart")}</option>
            <option value="doughnut">{t("components.mastery_distribution")}</option>
            <option value="cards">{t("components.skill_cards")}</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{t("components.category")}

          </label>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">

            <option value="all">{t("components.all_categories")}</option>
            {skillsData.categories.map((cat) =>
            <option key={cat.id} value={cat.id}>{cat.name}</option>
            )}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">{t("components.time_range")}

          </label>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">

            <option value="last7days">{t("components.last_7_days")}</option>
            <option value="last30days">{t("components.last_30_days")}</option>
            <option value="last90days">{t("components.last_90_days")}</option>
            <option value="last6months">{t("components.last_6_months")}</option>
            <option value="lastyear">{t("components.last_year")}</option>
          </select>
        </div>
      </div>
      {/* Charts */}
      <div className="bg-white rounded-lg shadow-md p-6">
        {chartType === 'radar' &&
        <div className="h-96">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.skills_overview")}</h3>
            <Radar data={getRadarData()} options={radarOptions} />
          </div>
        }
        {chartType === 'bar' &&
        <div className="h-96">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.improvement_progress")}</h3>
            <Bar data={getBarData()} options={barOptions} />
          </div>
        }
        {chartType === 'doughnut' &&
        <div className="h-96">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.mastery_level_distribution")}</h3>
            <div className="max-w-md mx-auto">
              <Doughnut data={getDoughnutData()} options={doughnutOptions} />
            </div>
          </div>
        }
        {chartType === 'cards' &&
        <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.detailed_skills_analysis")}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {skillsData.skills.map((skill) =>
            <SkillCard key={skill.id} skill={skill} />
            )}
            </div>
          </div>
        }
      </div>
      {/* Summary Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-md p-6">

          <div className="flex items-center">
            <div className="flex-shrink-0 p-3 bg-blue-100 rounded-full">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">{t("components.overall_progress")}</p>
              <p className="text-2xl font-semibold text-gray-900">{skillsData.overallProgress}%</p>
            </div>
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-md p-6">

          <div className="flex items-center">
            <div className="flex-shrink-0 p-3 bg-green-100 rounded-full">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">{t("components.skills_mastered")}</p>
              <p className="text-2xl font-semibold text-gray-900">{skillsData.skillsMastered}</p>
            </div>
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-md p-6">

          <div className="flex items-center">
            <div className="flex-shrink-0 p-3 bg-yellow-100 rounded-full">
              <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">{t("archive-components.in_progress")}</p>
              <p className="text-2xl font-semibold text-gray-900">{skillsData.skillsInProgress}</p>
            </div>
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg shadow-md p-6">

          <div className="flex items-center">
            <div className="flex-shrink-0 p-3 bg-purple-100 rounded-full">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">{t("components.improvement_rate")}</p>
              <p className="text-2xl font-semibold text-gray-900">{skillsData.improvementRate}%</p>
            </div>
          </div>
        </motion.div>
      </div>
      {/* Insights and Recommendations */}
      {skillsData.insights && skillsData.insights.length > 0 &&
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-lg shadow-md p-6">

          <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.key_insights_recommendations")}

        </h3>
          <div className="space-y-4">
            {skillsData.insights.map((insight, index) =>
          <div key={index} className="flex items-start">
                <div className={`flex-shrink-0 w-2 h-2 mt-1.5 rounded-full ${
            insight.type === 'success' ? 'bg-green-500' :
            insight.type === 'warning' ? 'bg-yellow-500' :
            'bg-blue-500'}`
            } />
                <div className="ml-3">
                  <p className="text-sm font-medium text-gray-900">{insight.title}</p>
                  <p className="text-sm text-gray-600">{insight.description}</p>
                  {insight.action &&
              <button className="mt-2 text-sm text-blue-600 hover:text-blue-800 font-medium">
                      {insight.action} →
                    </button>
              }
                </div>
              </div>
          )}
          </div>
        </motion.div>
      }
    </div>);

};
export default SkillsVisualization;