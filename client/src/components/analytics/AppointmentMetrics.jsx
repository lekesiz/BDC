// TODO: i18n - processed
import React from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';import { useTranslation } from "react-i18next";
const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
/**
 * AppointmentMetrics component displays a breakdown of appointments by type and status
 * @param {Object} props - Component props
 * @param {Object} props.data - The data for the chart
 */
export const AppointmentMetrics = ({ data = {} }) => {const { t } = useTranslation();
  if (!data || Object.keys(data).length === 0 || !data.byType || !data.byStatus) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <p>{t("components.no_appointment_data_available")}</p>
      </div>);

  }
  const { byType, byStatus } = data;
  const typeData = Object.entries(byType).map(([name, value]) => ({
    name,
    value
  }));
  const statusData = Object.entries(byStatus).map(([name, value]) => ({
    name,
    value
  }));
  const CustomTooltip = ({ active, payload, label }) => {const { t } = useTranslation();
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 border rounded shadow-md">
          <p className="font-medium">{`${payload[0].name}`}</p>
          <p className="text-sm">{`Count: ${payload[0].value}`}</p>
        </div>);

    }
    return null;
  };
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <h3 className="text-base font-medium mb-4 text-center">{t("components.by_type")}</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={typeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value">

                {typeData.map((entry, index) =>
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                )}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div>
        <h3 className="text-base font-medium mb-4 text-center">{t("components.by_status")}</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={statusData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value">

                {statusData.map((entry, index) =>
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                )}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="md:col-span-2">
        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="text-base font-medium mb-2">{t("components.key_insights")}</h3>
          <ul className="text-sm space-y-1 list-disc pl-4">
            <li>
              {data.insights?.mostCommonType ?
              `Most common appointment type: ${data.insights.mostCommonType}` :
              'No appointment type data available'}
            </li>
            <li>
              {data.insights?.completionRate !== undefined ?
              `Appointment completion rate: ${data.insights.completionRate}%` :
              'No completion rate data available'}
            </li>
            <li>
              {data.insights?.avgDuration ?
              `Average appointment duration: ${data.insights.avgDuration} minutes` :
              'No duration data available'}
            </li>
            <li>
              {data.insights?.cancellationRate !== undefined ?
              `Cancellation rate: ${data.insights.cancellationRate}%` :
              'No cancellation rate data available'}
            </li>
          </ul>
        </div>
      </div>
    </div>);

};
export default AppointmentMetrics;