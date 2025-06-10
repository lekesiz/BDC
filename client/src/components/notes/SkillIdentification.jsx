// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Chart as ChartJS,
  RadialLinearScale,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler } from
'chart.js';
import { Radar, Pie, Bar, Line } from 'react-chartjs-2';
// Register ChartJS components
import { useTranslation } from "react-i18next";ChartJS.register(
  RadialLinearScale,
  ArcElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);
const SkillIdentification = ({ noteId, beneficiaryId }) => {const { t } = useTranslation();
  const [skillData, setSkillData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [viewMode, setViewMode] = useState('overview'); // overview, detailed, timeline, comparison
  const [timeRange, setTimeRange] = useState('last30days');
  const [comparisonMode, setComparisonMode] = useState(false);
  const [selectedSkill, setSelectedSkill] = useState(null);
  useEffect(() => {
    fetchSkillData();
  }, [noteId, beneficiaryId, timeRange]);
  const fetchSkillData = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        noteId: noteId || '',
        beneficiaryId: beneficiaryId || '',
        timeRange,
        includeHistory: true
      });
      const response = await fetch(`/api/skills/analysis?${params}`);
      const data = await response.json();
      setSkillData(data);
    } catch (error) {
      console.error('Error fetching skill data:', error);
    } finally {
      setLoading(false);
    }
  };
  const getSkillRadarData = () => {
    if (!skillData) return null;
    const categories = selectedCategory === 'all' ?
    Object.keys(skillData.currentSkills) :
    [selectedCategory];
    const labels = [];
    const values = [];
    categories.forEach((category) => {
      if (skillData.currentSkills[category]) {
        skillData.currentSkills[category].forEach((skill) => {
          labels.push(skill.skill);
          values.push(skill.proficiency || 50);
        });
      }
    });
    return {
      labels: labels.slice(0, 8), // Limit to 8 for readability
      datasets: [{
        label: 'Current Proficiency',
        data: values.slice(0, 8),
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgb(59, 130, 246)',
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(59, 130, 246)'
      }]
    };
  };
  const getSkillDistribution = () => {
    if (!skillData) return null;
    const distribution = {};
    Object.entries(skillData.currentSkills).forEach(([category, skills]) => {
      distribution[category] = skills.length;
    });
    return {
      labels: Object.keys(distribution).map((cat) =>
      cat.replace('_', ' ').split(' ').map((word) =>
      word.charAt(0).toUpperCase() + word.slice(1)
      ).join(' ')
      ),
      datasets: [{
        data: Object.values(distribution),
        backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(34, 197, 94, 0.8)',
        'rgba(168, 85, 247, 0.8)',
        'rgba(251, 191, 36, 0.8)'],

        borderColor: [
        'rgb(59, 130, 246)',
        'rgb(34, 197, 94)',
        'rgb(168, 85, 247)',
        'rgb(251, 191, 36)'],

        borderWidth: 2
      }]
    };
  };
  const getSkillTimeline = () => {
    if (!skillData?.skillHistory) return null;
    const skillGroups = {};
    skillData.skillHistory.forEach((entry) => {
      const date = new Date(entry.date).toLocaleDateString();
      if (!skillGroups[date]) {
        skillGroups[date] = {};
      }
      entry.skills.forEach((skill) => {
        if (!skillGroups[date][skill.category]) {
          skillGroups[date][skill.category] = 0;
        }
        skillGroups[date][skill.category]++;
      });
    });
    const dates = Object.keys(skillGroups).sort();
    const categories = ['technical_skills', 'soft_skills', 'cognitive_skills', 'subject_knowledge'];
    const datasets = categories.map((category, index) => ({
      label: category.replace('_', ' ').split(' ').map((w) => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
      data: dates.map((date) => skillGroups[date][category] || 0),
      borderColor: [
      'rgb(59, 130, 246)',
      'rgb(34, 197, 94)',
      'rgb(168, 85, 247)',
      'rgb(251, 191, 36)'][
      index],
      backgroundColor: [
      'rgba(59, 130, 246, 0.1)',
      'rgba(34, 197, 94, 0.1)',
      'rgba(168, 85, 247, 0.1)',
      'rgba(251, 191, 36, 0.1)'][
      index],
      fill: true
    }));
    return {
      labels: dates,
      datasets
    };
  };
  const SkillCard = ({ skill, category }) => {const { t } = useTranslation();
    const categoryColors = {
      technical_skills: 'blue',
      soft_skills: 'green',
      cognitive_skills: 'purple',
      subject_knowledge: 'yellow'
    };
    const color = categoryColors[category] || 'gray';
    const proficiency = skill.proficiency || 50;
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        whileHover={{ scale: 1.02 }}
        className={`bg-white rounded-lg shadow-md p-4 border-2 border-${color}-200 hover:border-${color}-400 transition-all cursor-pointer`}
        onClick={() => setSelectedSkill(skill)}>

        <div className="flex justify-between items-start mb-3">
          <h4 className="font-semibold text-gray-900">{skill.skill}</h4>
          <span className={`text-xs px-2 py-1 rounded-full bg-${color}-100 text-${color}-800`}>
            {skill.confidence || 'Medium'}
          </span>
        </div>
        {skill.context &&
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">{skill.context}</p>
        }
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">{t("components.proficiency")}</span>
            <span className="font-medium">{proficiency}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`bg-${color}-500 h-2 rounded-full transition-all duration-300`}
              style={{ width: `${proficiency}%` }} />

          </div>
        </div>
        {skill.lastDemonstrated &&
        <p className="text-xs text-gray-500 mt-2">{t("components.last_demonstrated")}
          {new Date(skill.lastDemonstrated).toLocaleDateString()}
          </p>
        }
      </motion.div>);

  };
  const SkillComparisonChart = ({ skills }) => {const { t } = useTranslation();
    if (!skills || skills.length === 0) return null;
    const sortedSkills = [...skills].sort((a, b) => (b.proficiency || 0) - (a.proficiency || 0));
    const topSkills = sortedSkills.slice(0, 10);
    const data = {
      labels: topSkills.map((s) => s.skill),
      datasets: [{
        label: 'Proficiency Level',
        data: topSkills.map((s) => s.proficiency || 50),
        backgroundColor: topSkills.map((s) => {
          const p = s.proficiency || 50;
          if (p >= 80) return 'rgba(34, 197, 94, 0.8)';
          if (p >= 60) return 'rgba(59, 130, 246, 0.8)';
          if (p >= 40) return 'rgba(251, 191, 36, 0.8)';
          return 'rgba(239, 68, 68, 0.8)';
        }),
        borderColor: topSkills.map((s) => {
          const p = s.proficiency || 50;
          if (p >= 80) return 'rgb(34, 197, 94)';
          if (p >= 60) return 'rgb(59, 130, 246)';
          if (p >= 40) return 'rgb(251, 191, 36)';
          return 'rgb(239, 68, 68)';
        }),
        borderWidth: 2
      }]
    };
    return (
      <Bar
        data={data}
        options={{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              beginAtZero: true,
              max: 100,
              title: {
                display: true,
                text: 'Proficiency (%)'
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
                  return `${context.parsed.x}% proficiency`;
                }
              }
            }
          }
        }} />);


  };
  const SkillDevelopmentPlan = ({ skill }) => {const { t } = useTranslation();
    const plan = skillData?.developmentPlans?.[skill.skill] || {};
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.development_plan")}
          {skill.skill}
        </h3>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-2">{t("components.current_level")}</h4>
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-500 h-3 rounded-full"
                    style={{ width: `${skill.proficiency || 50}%` }} />

                </div>
              </div>
              <span className="text-sm font-medium">{skill.proficiency || 50}%</span>
            </div>
          </div>
          <div>
            <h4 className="font-medium text-gray-700 mb-2">{t("components.target_level")}</h4>
            <div className="flex items-center space-x-4">
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-green-500 h-3 rounded-full"
                    style={{ width: `${plan.targetLevel || 80}%` }} />

                </div>
              </div>
              <span className="text-sm font-medium">{plan.targetLevel || 80}%</span>
            </div>
          </div>
          {plan.recommendations && plan.recommendations.length > 0 &&
          <div>
              <h4 className="font-medium text-gray-700 mb-2">{t("components.recommendations")}</h4>
              <ul className="space-y-2">
                {plan.recommendations.map((rec, index) =>
              <li key={index} className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    <span className="text-sm text-gray-600">{rec}</span>
                  </li>
              )}
              </ul>
            </div>
          }
          {plan.resources && plan.resources.length > 0 &&
          <div>
              <h4 className="font-medium text-gray-700 mb-2">{t("components.learning_resources")}</h4>
              <div className="space-y-2">
                {plan.resources.map((resource, index) =>
              <a
                key={index}
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center text-sm text-blue-600 hover:text-blue-800">

                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                    {resource.title}
                  </a>
              )}
              </div>
            </div>
          }
          <div>
            <h4 className="font-medium text-gray-700 mb-2">{t("components.estimated_timeline")}</h4>
            <p className="text-sm text-gray-600">{plan.timeline || '4-6 weeks'}</p>
          </div>
        </div>
      </div>);

  };
  const SkillInsights = ({ insights }) => {const { t } = useTranslation();
    if (!insights) return null;
    return (
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.ai_insights")}</h3>
        <div className="space-y-4">
          {insights.strengths && insights.strengths.length > 0 &&
          <div>
              <h4 className="font-medium text-gray-700 mb-2">{t("components.strong_skills")}</h4>
              <div className="flex flex-wrap">
                {insights.strengths.map((skill, index) =>
              <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 mr-2 mb-2">
                    {skill}
                  </span>
              )}
              </div>
            </div>
          }
          {insights.emerging && insights.emerging.length > 0 &&
          <div>
              <h4 className="font-medium text-gray-700 mb-2">{t("components.emerging_skills")}</h4>
              <div className="flex flex-wrap">
                {insights.emerging.map((skill, index) =>
              <span key={index} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 mr-2 mb-2">
                    {skill}
                  </span>
              )}
              </div>
            </div>
          }
          {insights.recommendations && insights.recommendations.length > 0 &&
          <div>
              <h4 className="font-medium text-gray-700 mb-2">{t("components.recommendations")}</h4>
              <ul className="space-y-2">
                {insights.recommendations.map((rec, index) =>
              <li key={index} className="flex items-start">
                    <svg className="w-4 h-4 text-blue-500 mr-2 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-sm text-gray-600">{rec}</span>
                  </li>
              )}
              </ul>
            </div>
          }
          {insights.careerPaths && insights.careerPaths.length > 0 &&
          <div>
              <h4 className="font-medium text-gray-700 mb-2">{t("components.potential_career_paths")}</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {insights.careerPaths.map((path, index) =>
              <div key={index} className="bg-white rounded-lg p-3">
                    <h5 className="font-medium text-gray-900">{path.title}</h5>
                    <p className="text-sm text-gray-600">{path.match}{t("components._skill_match")}</p>
                    <div className="mt-2">
                      <span className="text-xs text-gray-500">{t("components.required_skills")}</span>
                      <span className="text-xs text-gray-700">{path.requiredSkills.join(', ')}</span>
                    </div>
                  </div>
              )}
              </div>
            </div>
          }
        </div>
      </div>);

  };
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>);

  }
  if (!skillData) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">{t("components.no_skill_data_available")}</p>
      </div>);

  }
  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex flex-wrap gap-4 items-center justify-between">
        <div className="flex gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("components.view_mode")}

            </label>
            <select
              value={viewMode}
              onChange={(e) => setViewMode(e.target.value)}
              className="block w-40 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">

              <option value="overview">{t("components.overview")}</option>
              <option value="detailed">{t("components.detailed")}</option>
              <option value="timeline">{t("components.timeline")}</option>
              <option value="comparison">{t("components.comparison")}</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t("components.category")}

            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="block w-48 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">

              <option value="all">{t("components.all_categories")}</option>
              <option value="technical_skills">{t("components.technical_skills")}</option>
              <option value="soft_skills">{t("components.soft_skills")}</option>
              <option value="cognitive_skills">{t("components.cognitive_skills")}</option>
              <option value="subject_knowledge">{t("components.subject_knowledge")}</option>
            </select>
          </div>
          {viewMode === 'timeline' &&
          <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t("components.time_range")}

            </label>
              <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="block w-40 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500">

                <option value="last7days">{t("components.last_7_days")}</option>
                <option value="last30days">{t("components.last_30_days")}</option>
                <option value="last3months">{t("components.last_3_months")}</option>
                <option value="last6months">{t("components.last_6_months")}</option>
                <option value="alltime">{t("components.all_time")}</option>
              </select>
            </div>
          }
        </div>
        <button
          onClick={() => window.print()}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">{t("components.export_report")}


        </button>
      </div>
      {/* Main Content */}
      <AnimatePresence mode="wait">
        {viewMode === 'overview' &&
        <motion.div
          key="overview"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="space-y-6">

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow-md p-6">
                <p className="text-sm font-medium text-gray-500">{t("components.total_skills")}</p>
                <p className="text-2xl font-bold text-gray-900">{skillData.totalSkills}</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <p className="text-sm font-medium text-gray-500">{t("components.new_this_month")}</p>
                <p className="text-2xl font-bold text-blue-600">{skillData.newSkills}</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <p className="text-sm font-medium text-gray-500">{t("components.average_proficiency")}</p>
                <p className="text-2xl font-bold text-green-600">{skillData.avgProficiency}%</p>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <p className="text-sm font-medium text-gray-500">{t("components.top_category")}</p>
                <p className="text-2xl font-bold text-purple-600">{skillData.topCategory}</p>
              </div>
            </div>
            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.skill_radar")}</h3>
                <div className="h-80">
                  <Radar
                  data={getSkillRadarData()}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                      r: {
                        beginAtZero: true,
                        max: 100
                      }
                    }
                  }} />

                </div>
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.skill_distribution")}</h3>
                <div className="h-80">
                  <Pie
                  data={getSkillDistribution()}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'bottom'
                      }
                    }
                  }} />

                </div>
              </div>
            </div>
            {/* AI Insights */}
            <SkillInsights insights={skillData.aiInsights} />
          </motion.div>
        }
        {viewMode === 'detailed' &&
        <motion.div
          key="detailed"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="space-y-6">

            {Object.entries(skillData.currentSkills).map(([category, skills]) =>
          selectedCategory === 'all' || selectedCategory === category ?
          <div key={category} className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {category.replace('_', ' ').split(' ').map((w) =>
              w.charAt(0).toUpperCase() + w.slice(1)
              ).join(' ')}
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {skills.map((skill, index) =>
              <SkillCard key={index} skill={skill} category={category} />
              )}
                  </div>
                </div> :
          null
          )}
          </motion.div>
        }
        {viewMode === 'timeline' &&
        <motion.div
          key="timeline"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="space-y-6">

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.skill_development_timeline")}</h3>
              <div className="h-96">
                <Line
                data={getSkillTimeline()}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      title: {
                        display: true,
                        text: 'Number of Skills'
                      }
                    }
                  },
                  plugins: {
                    legend: {
                      position: 'bottom'
                    }
                  }
                }} />

              </div>
            </div>
            {/* Milestone Events */}
            {skillData.milestones && skillData.milestones.length > 0 &&
          <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.skill_milestones")}</h3>
                <div className="space-y-4">
                  {skillData.milestones.map((milestone, index) =>
              <div key={index} className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  milestone.type === 'new_skill' ? 'bg-blue-100' :
                  milestone.type === 'proficiency_increase' ? 'bg-green-100' :
                  'bg-purple-100'}`
                  }>
                          <svg className={`w-5 h-5 ${
                    milestone.type === 'new_skill' ? 'text-blue-600' :
                    milestone.type === 'proficiency_increase' ? 'text-green-600' :
                    'text-purple-600'}`
                    } fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            {milestone.type === 'new_skill' ?
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /> :
                      milestone.type === 'proficiency_increase' ?
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /> :

                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      }
                          </svg>
                        </div>
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">{milestone.title}</p>
                        <p className="text-sm text-gray-500">{milestone.description}</p>
                      </div>
                      <div className="text-sm text-gray-400">
                        {new Date(milestone.date).toLocaleDateString()}
                      </div>
                    </div>
              )}
                </div>
              </div>
          }
          </motion.div>
        }
        {viewMode === 'comparison' &&
        <motion.div
          key="comparison"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="space-y-6">

            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.top_skills_comparison")}</h3>
              <div className="h-96">
                <SkillComparisonChart
                skills={Object.values(skillData.currentSkills).flat()} />

              </div>
            </div>
            {/* Skill Gap Analysis */}
            {skillData.skillGaps && skillData.skillGaps.length > 0 &&
          <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{t("components.skill_gap_analysis")}</h3>
                <div className="space-y-4">
                  {skillData.skillGaps.map((gap, index) =>
              <div key={index} className="border-l-4 border-yellow-400 pl-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium text-gray-900">{gap.skill}</h4>
                          <p className="text-sm text-gray-600">{gap.description}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-gray-900">Gap: {gap.gapSize}%</p>
                          <p className="text-xs text-gray-500">Priority: {gap.priority}</p>
                        </div>
                      </div>
                      <div className="mt-2 flex items-center space-x-4">
                        <div className="flex-1">
                          <div className="w-full bg-gray-200 rounded-full h-2">
                            <div
                        className="bg-yellow-500 h-2 rounded-full"
                        style={{ width: `${100 - gap.gapSize}%` }} />

                          </div>
                        </div>
                        <span className="text-sm text-gray-600">
                          Current: {100 - gap.gapSize}%
                        </span>
                      </div>
                    </div>
              )}
                </div>
              </div>
          }
          </motion.div>
        }
      </AnimatePresence>
      {/* Selected Skill Modal */}
      <AnimatePresence>
        {selectedSkill &&
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setSelectedSkill(null)}>

            <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-lg shadow-xl p-6 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}>

              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">{selectedSkill.skill}</h2>
                <button
                onClick={() => setSelectedSkill(null)}
                className="text-gray-400 hover:text-gray-600">

                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">{t("components.skill_details")}</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-500">{t("components.category")}</p>
                      <p className="font-medium">{selectedSkill.category}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Confidence Level</p>
                      <p className="font-medium">{selectedSkill.confidence || 'Medium'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">{t("components.last_demonstrated")}</p>
                      <p className="font-medium">
                        {selectedSkill.lastDemonstrated ?
                      new Date(selectedSkill.lastDemonstrated).toLocaleDateString() :
                      'N/A'}
                      </p>
                    </div>
                    {selectedSkill.context &&
                  <div>
                        <p className="text-sm text-gray-500">{t("components.context")}</p>
                        <p className="text-sm">{selectedSkill.context}</p>
                      </div>
                  }
                  </div>
                </div>
                <SkillDevelopmentPlan skill={selectedSkill} />
              </div>
              {/* Skill History */}
              {selectedSkill.history && selectedSkill.history.length > 0 &&
            <div className="mt-6">
                  <h3 className="font-semibold text-gray-700 mb-3">{t("components.skill_history")}</h3>
                  <div className="space-y-2">
                    {selectedSkill.history.map((entry, index) =>
                <div key={index} className="flex items-center justify-between py-2 border-b">
                        <div>
                          <p className="text-sm font-medium">{entry.event}</p>
                          <p className="text-xs text-gray-500">{entry.description}</p>
                        </div>
                        <p className="text-sm text-gray-400">
                          {new Date(entry.date).toLocaleDateString()}
                        </p>
                      </div>
                )}
                  </div>
                </div>
            }
              <div className="mt-6 flex justify-end space-x-4">
                <button
                onClick={() => setSelectedSkill(null)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300">{t("components.close")}


              </button>
                <button
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">{t("components.create_development_plan")}


              </button>
              </div>
            </motion.div>
          </motion.div>
        }
      </AnimatePresence>
    </div>);

};
export default SkillIdentification;