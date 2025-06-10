// TODO: i18n - processed
import React from 'react';
import ApiDebugPanel from '@/components/debug/ApiDebugPanel';import { useTranslation } from "react-i18next";
const DebugPage = () => {const { t } = useTranslation();
  return (
    <div className="container mx-auto py-8">
      <h1 className="text-2xl font-bold mb-6">{t("pages.system_debug_panel")}</h1>
      <ApiDebugPanel />
    </div>);

};
export default DebugPage;