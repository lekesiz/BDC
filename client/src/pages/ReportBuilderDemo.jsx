// TODO: i18n - processed
import React from 'react';
import { ReportBuilder } from '../components/reports';import { useTranslation } from "react-i18next";
const ReportBuilderDemo = () => {const { t } = useTranslation();
  return (
    <div className="min-h-screen bg-gray-50">
      <ReportBuilder />
    </div>);

};
export default ReportBuilderDemo;