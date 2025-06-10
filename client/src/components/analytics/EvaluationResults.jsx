// TODO: i18n - processed
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
/**
 * EvaluationResults component displays test score distributions and evaluation results
 * @param {Object} props - Component props
 * @param {Object} props.data - The data for the chart
 */import { useTranslation } from "react-i18next";
export const EvaluationResults = ({ data = {} }) => {const { t } = useTranslation();
  if (!data || Object.keys(data).length === 0 || !data.scoreDistribution) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <p>{t("components.no_evaluation_data_available")}</p>
      </div>);

  }
  const { scoreDistribution, competencyAverages, insights } = data;
  // Prepare score distribution data
  const scoreData = Object.entries(scoreDistribution).map(([range, count]) => ({
    range,
    count
  }));
  // Prepare competency data if available
  const competencyData = competencyAverages ? Object.entries(competencyAverages).map(([name, score]) => ({
    name,
    score
  })) : [];
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-base font-medium mb-2">{t("components.score_distribution")}</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={scoreData}
              margin={{
                top: 5,
                right: 30,
                left: 20,
                bottom: 5
              }}>

              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="range" />
              <YAxis />
              <Tooltip
                formatter={(value, name) => [value, 'Count']}
                labelFormatter={(value) => `Score Range: ${value}`} />

              <Legend />
              <Bar dataKey="count" name="Number of Evaluations" fill="#4f46e5" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      {competencyData.length > 0 &&
      <div>
          <h3 className="text-base font-medium mb-2">{t("components.competency_averages")}</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
              data={competencyData}
              layout="vertical"
              margin={{
                top: 5,
                right: 30,
                left: 100,
                bottom: 5
              }}>

                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" domain={[0, 5]} />
                <YAxis type="category" dataKey="name" tick={{ fontSize: 12 }} width={100} />
                <Tooltip
                formatter={(value) => [`${value}/5`, 'Average Score']} />

                <Bar dataKey="score" name="Average Score" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      }
      {insights &&
      <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-base font-medium mb-2">{t("components.key_insights")}</h3>
          <ul className="text-sm space-y-1 list-disc pl-4">
            <li>
              {insights.passRate !== undefined ?
            `Overall pass rate: ${insights.passRate}%` :
            'No pass rate data available'}
            </li>
            <li>
              {insights.avgScore !== undefined ?
            `Average score: ${insights.avgScore}/100` :
            'No average score data available'}
            </li>
            <li>
              {insights.highestCompetency ?
            `Highest rated competency: ${insights.highestCompetency}` :
            'No competency data available'}
            </li>
            <li>
              {insights.lowestCompetency ?
            `Area for improvement: ${insights.lowestCompetency}` :
            'No competency improvement data available'}
            </li>
          </ul>
        </div>
      }
    </div>);

};
export default EvaluationResults;