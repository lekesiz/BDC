// TODO: i18n - processed
import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
/**
 * BeneficiaryStatistics component displays key statistics about beneficiaries
 * @param {Object} props - Component props
 * @param {Array} props.data - The data for the chart
 */import { useTranslation } from "react-i18next";
export const BeneficiaryStatistics = ({ data = [] }) => {const { t } = useTranslation();
  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-gray-500">
        <p>{t("components.no_beneficiary_data_available")}</p>
      </div>);

  }
  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5
          }}>

          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip
            formatter={(value, name) => [value, name === 'enrollment' ? 'Enrollment' : 'Graduation']}
            labelFormatter={(value) => `Period: ${value}`} />

          <Legend />
          <Bar dataKey="enrollment" name="Enrollment" fill="#4f46e5" />
          <Bar dataKey="graduation" name="Graduation" fill="#10b981" />
        </BarChart>
      </ResponsiveContainer>
    </div>);

};
export default BeneficiaryStatistics;