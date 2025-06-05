import React from 'react';
import { useTranslation } from 'react-i18next';
/**
 * Example component showing how to use translations in the BDC application
 * This demonstrates the usage of the Turkish translations we've added
 */
const LanguageExample = () => {
  const { t, i18n } = useTranslation();
  return (
    <div className="p-4 space-y-4">
      <h1 className="text-2xl font-bold">{t('common.welcome')}</h1>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h2 className="text-lg font-semibold mb-2">{t('navigation.dashboard')}</h2>
          <ul className="space-y-1">
            <li>{t('navigation.beneficiaries')}</li>
            <li>{t('navigation.programs')}</li>
            <li>{t('navigation.evaluations')}</li>
            <li>{t('navigation.calendar')}</li>
          </ul>
        </div>
        <div>
          <h2 className="text-lg font-semibold mb-2">{t('common.actions')}</h2>
          <div className="space-x-2">
            <button className="px-3 py-1 bg-blue-500 text-white rounded">
              {t('common.save')}
            </button>
            <button className="px-3 py-1 bg-gray-500 text-white rounded">
              {t('common.cancel')}
            </button>
            <button className="px-3 py-1 bg-red-500 text-white rounded">
              {t('common.delete')}
            </button>
          </div>
        </div>
      </div>
      <div>
        <h2 className="text-lg font-semibold mb-2">{t('auth.loginTitle')}</h2>
        <form className="space-y-2 max-w-sm">
          <input 
            type="email" 
            placeholder={t('auth.email')}
            className="w-full px-3 py-2 border rounded"
          />
          <input 
            type="password" 
            placeholder={t('auth.password')}
            className="w-full px-3 py-2 border rounded"
          />
          <button className="w-full px-3 py-2 bg-blue-500 text-white rounded">
            {t('auth.signIn')}
          </button>
        </form>
      </div>
      <div>
        <p className="text-sm text-gray-600">
          Current language: {i18n.language}
        </p>
      </div>
    </div>
  );
};
export default LanguageExample;