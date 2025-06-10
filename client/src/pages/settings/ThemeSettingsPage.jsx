// TODO: i18n - processed
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../../contexts/ThemeContext';
import { FaMoon, FaSun, FaDesktop, FaPalette, FaTextHeight, FaCheck } from 'react-icons/fa';import { useTranslation } from "react-i18next";
const ThemeSettingsPage = () => {const { t } = useTranslation();
  const navigate = useNavigate();
  const { theme, accentColor, fontSize, changeTheme, changeAccentColor, changeFontSize } = useTheme();
  const themeOptions = [
  { id: 'light', name: 'Açık', icon: FaSun, description: 'Açık tema' },
  { id: 'dark', name: 'Koyu', icon: FaMoon, description: 'Koyu tema' },
  { id: 'system', name: 'Sistem', icon: FaDesktop, description: 'Sistem temasını takip et' }];

  const colorOptions = [
  { id: 'blue', name: 'Mavi', color: '#3b82f6' },
  { id: 'green', name: 'Yeşil', color: '#22c55e' },
  { id: 'purple', name: 'Mor', color: '#a855f7' },
  { id: 'red', name: 'Kırmızı', color: '#ef4444' }];

  const fontOptions = [
  { id: 'small', name: 'Küçük', size: '14px' },
  { id: 'medium', name: 'Orta', size: '16px' },
  { id: 'large', name: 'Büyük', size: '18px' }];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/settings')}
            className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 mb-4">{t("pages._ayarlara_geri_dn")}


          </button>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t("pages.tema_ayarlar")}</h1>
          <p className="text-gray-600 dark:text-gray-400">{t("pages.uygulamann_grnmn_zelletirin")}</p>
        </div>
        {/* Theme Selection */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            <FaPalette className="inline mr-2" />{t("pages.tema")}

          </h3>
          <div className="grid grid-cols-3 gap-4">
            {themeOptions.map((option) =>
            <button
              key={option.id}
              onClick={() => changeTheme(option.id)}
              className={`p-4 rounded-lg border transition-all ${
              theme === option.id ?
              'border-blue-500 bg-blue-50 dark:bg-blue-900' :
              'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'}`
              }>

                <option.icon className={`text-3xl mb-2 mx-auto ${
              theme === option.id ? 'text-blue-500' : 'text-gray-600 dark:text-gray-400'}`
              } />
                <p className={`font-medium ${
              theme === option.id ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-white'}`
              }>
                  {option.name}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {option.description}
                </p>
                {theme === option.id &&
              <FaCheck className="text-green-500 mt-2 mx-auto" />
              }
              </button>
            )}
          </div>
        </div>
        {/* Accent Color */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            <FaPalette className="inline mr-2" />{t("pages.vurgu_rengi")}

          </h3>
          <div className="grid grid-cols-4 gap-4">
            {colorOptions.map((option) =>
            <button
              key={option.id}
              onClick={() => changeAccentColor(option.id)}
              className={`p-4 rounded-lg border transition-all ${
              accentColor === option.id ?
              'border-blue-500 ring-2 ring-blue-500' :
              'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'}`
              }>

                <div
                className="w-16 h-16 rounded-full mx-auto mb-2"
                style={{ backgroundColor: option.color }} />

                <p className={`text-sm font-medium ${
              accentColor === option.id ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-white'}`
              }>
                  {option.name}
                </p>
                {accentColor === option.id &&
              <FaCheck className="text-green-500 mt-2 mx-auto" />
              }
              </button>
            )}
          </div>
        </div>
        {/* Font Size */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">
            <FaTextHeight className="inline mr-2" />{t("pages.yaz_boyutu")}

          </h3>
          <div className="grid grid-cols-3 gap-4">
            {fontOptions.map((option) =>
            <button
              key={option.id}
              onClick={() => changeFontSize(option.id)}
              className={`p-4 rounded-lg border transition-all ${
              fontSize === option.id ?
              'border-blue-500 bg-blue-50 dark:bg-blue-900' :
              'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'}`
              }>

                <p
                className={`mb-2 ${
                fontSize === option.id ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-white'}`
                }
                style={{ fontSize: option.size }}>{t("pages.aa")}


              </p>
                <p className={`font-medium ${
              fontSize === option.id ? 'text-blue-900 dark:text-blue-100' : 'text-gray-900 dark:text-white'}`
              }>
                  {option.name}
                </p>
                {fontSize === option.id &&
              <FaCheck className="text-green-500 mt-2 mx-auto" />
              }
              </button>
            )}
          </div>
        </div>
        {/* Preview */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Önizleme</h3>
          <div className="space-y-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded">
              <h4 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">{t("pages.rnek_balk")}</h4>
              <p className="text-gray-600 dark:text-gray-300">{t("pages.bu_bir_rnek_metindir_setiiniz_tema_ve_ayarlarn_grn")}

              </p>
              <div className="mt-4 space-x-2">
                <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">{t("pages.birincil_buton")}

                </button>
                <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-50 dark:hover:bg-gray-700">{t("pages.ikincil_buton")}

                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>);

};
export default ThemeSettingsPage;