import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

/**
 * TrainingProgress component displays the progress of beneficiaries through training programs
 * @param {Object} props - Component props
 * @param {Array} props.data - The data for the chart
 */
export const TrainingProgress = ({ data = [] }) => {
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <p>No training progress data available</p>
      </div>
    );
  }
  
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip 
            formatter={(value, name) => [
              `${value}%`, 
              name === 'completionRate' 
                ? 'Completion Rate' 
                : name === 'retentionRate'
                ? 'Retention Rate'
                : 'Satisfaction Score'
            ]}
            labelFormatter={(value) => `Period: ${value}`}
          />
          <Legend />
          <Line type="monotone" dataKey="completionRate" name="Completion Rate" stroke="#4f46e5" activeDot={{ r: 8 }} />
          <Line type="monotone" dataKey="retentionRate" name="Retention Rate" stroke="#10b981" />
          <Line type="monotone" dataKey="satisfactionScore" name="Satisfaction Score" stroke="#f59e0b" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TrainingProgress;