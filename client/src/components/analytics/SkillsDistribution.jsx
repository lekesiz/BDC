import React from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend, ResponsiveContainer, Tooltip } from 'recharts';

/**
 * SkillsDistribution component displays the distribution of skills among beneficiaries
 * @param {Object} props - Component props
 * @param {Array} props.data - The data for the chart
 */
export const SkillsDistribution = ({ data = [] }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <p>No skills data available</p>
      </div>
    );
  }
  
  // Format data for radar chart if needed
  const chartData = data.map(item => ({
    skill: item.name,
    preTraining: item.preTraining,
    postTraining: item.postTraining,
    industryAverage: item.industryAverage
  }));
  
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart outerRadius={90} data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="skill" />
          <PolarRadiusAxis angle={30} domain={[0, 5]} />
          <Radar 
            name="Pre-Training" 
            dataKey="preTraining" 
            stroke="#ef4444" 
            fill="#ef4444" 
            fillOpacity={0.2} 
          />
          <Radar 
            name="Post-Training" 
            dataKey="postTraining" 
            stroke="#4f46e5" 
            fill="#4f46e5" 
            fillOpacity={0.2} 
          />
          <Radar 
            name="Industry Avg." 
            dataKey="industryAverage" 
            stroke="#10b981" 
            fill="#10b981" 
            fillOpacity={0.2} 
          />
          <Tooltip formatter={(value) => `${value}/5`} />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SkillsDistribution;