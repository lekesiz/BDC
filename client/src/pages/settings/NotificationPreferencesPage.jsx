// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaBell, FaEnvelope, FaMobile, FaDesktop, FaCalendar, FaGraduationCap, FaFile, FaUsers, FaChartBar, FaCheck, FaTimes, FaSave, FaInfoCircle } from 'react-icons/fa';
import { toast } from 'react-toastify';import { useTranslation } from "react-i18next";
const NotificationPreferencesPageV2 = () => {const { t } = useTranslation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [preferences, setPreferences] = useState({
    channels: {
      email: true,
      push: true,
      sms: false,
      inApp: true
    },
    categories: {
      messages: {
        email: true,
        push: true,
        sms: false,
        inApp: true
      },
      appointments: {
        email: true,
        push: true,
        sms: true,
        inApp: true
      },
      assessments: {
        email: true,
        push: false,
        sms: false,
        inApp: true
      },
      documents: {
        email: false,
        push: false,
        sms: false,
        inApp: true
      },
      analytics: {
        email: true,
        push: false,
        sms: false,
        inApp: true
      },
      system: {
        email: true,
        push: true,
        sms: false,
        inApp: true
      }
    },
    timing: {
      immediate: true,
      hourly: false,
      daily: false,
      weekly: false
    },
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00',
      timezone: 'Europe/Istanbul'
    },
    frequency: {
      maxEmailsPerDay: 10,
      maxPushPerDay: 20,
      maxSmsPerDay: 5
    },
    digest: {
      enabled: false,
      time: '09:00',
      frequency: 'daily',
      categories: ['messages', 'appointments', 'assessments']
    }
  });
  const categoryInfo = {
    messages: { name: 'Mesajlar', icon: FaEnvelope, description: 'Özel mesajlar ve grup konuşmaları' },
    appointments: { name: 'Randevular', icon: FaCalendar, description: 'Randevu hatırlatıcıları ve güncellemeleri' },
    assessments: { name: 'Değerlendirmeler', icon: FaGraduationCap, description: 'Test ve değerlendirme bildirimleri' },
    documents: { name: 'Dokümanlar', icon: FaFile, description: 'Doküman paylaşımları ve güncellemeleri' },
    analytics: { name: 'Raporlar', icon: FaChartBar, description: 'Analiz ve rapor bildirimleri' },
    system: { name: 'Sistem', icon: FaBell, description: 'Sistem güncellemeleri ve önemli duyurular' }
  };
  const channelInfo = {
    email: { name: 'E-posta', icon: FaEnvelope },
    push: { name: 'Push Bildirim', icon: FaDesktop },
    sms: { name: 'SMS', icon: FaMobile },
    inApp: { name: 'Uygulama İçi', icon: FaBell }
  };
  useEffect(() => {
    fetchPreferences();
  }, []);
  const fetchPreferences = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/notifications/preferences');
      setPreferences(response.data);
    } catch (error) {
      toast.error('Tercihler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };
  const savePreferences = async () => {
    setSaving(true);
    try {
      await axios.put('/api/notifications/preferences', preferences);
      toast.success('Tercihler kaydedildi');
    } catch (error) {
      toast.error('Kaydetme başarısız');
    } finally {
      setSaving(false);
    }
  };
  const handleChannelToggle = (channel) => {
    setPreferences({
      ...preferences,
      channels: {
        ...preferences.channels,
        [channel]: !preferences.channels[channel]
      }
    });
  };
  const handleCategoryChannelToggle = (category, channel) => {
    setPreferences({
      ...preferences,
      categories: {
        ...preferences.categories,
        [category]: {
          ...preferences.categories[category],
          [channel]: !preferences.categories[category][channel]
        }
      }
    });
  };
  const handleQuietHoursToggle = () => {
    setPreferences({
      ...preferences,
      quietHours: {
        ...preferences.quietHours,
        enabled: !preferences.quietHours.enabled
      }
    });
  };
  const handleTimingChange = (timing) => {
    setPreferences({
      ...preferences,
      timing: {
        immediate: false,
        hourly: false,
        daily: false,
        weekly: false,
        [timing]: true
      }
    });
  };
  const handleDigestToggle = () => {
    setPreferences({
      ...preferences,
      digest: {
        ...preferences.digest,
        enabled: !preferences.digest.enabled
      }
    });
  };
  const handleDigestCategoryToggle = (category) => {
    const categories = preferences.digest.categories.includes(category) ?
    preferences.digest.categories.filter((c) => c !== category) :
    [...preferences.digest.categories, category];
    setPreferences({
      ...preferences,
      digest: {
        ...preferences.digest,
        categories
      }
    });
  };
  const testNotification = async (channel) => {
    try {
      await axios.post('/api/notifications/test', { channel });
      toast.success(`Test bildirimi gönderildi: ${channelInfo[channel].name}`);
    } catch (error) {
      toast.error('Test bildirimi gönderilemedi');
    }
  };
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>);

  }
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/settings')}
            className="text-gray-600 hover:text-gray-800 mb-4">{t("pages._ayarlara_geri_dn")}


          </button>
          <h1 className="text-2xl font-bold mb-2">{t("pages.bildirim_tercihleri")}</h1>
          <p className="text-gray-600">{t("pages.bildirimlerin_nasl_ve_ne_zaman_alacanz_yaplandrn")}</p>
        </div>
        {/* Master Channel Switches */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">{t("pages.bildirim_kanallar")}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(preferences.channels).map(([channel, enabled]) =>
            <div key={channel} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center">
                  {React.createElement(channelInfo[channel].icon, { className: "text-2xl mr-3 text-gray-600" })}
                  <div>
                    <p className="font-medium">{channelInfo[channel].name}</p>
                    <p className="text-sm text-gray-600">
                      {channel === 'email' && 'E-posta adresinize bildirim gönder'}
                      {channel === 'push' && 'Tarayıcı bildirimleri göster'}
                      {channel === 'sms' && 'Telefon numaranıza SMS gönder'}
                      {channel === 'inApp' && 'Uygulama içinde bildirim göster'}
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                  onClick={() => testNotification(channel)}
                  className="text-blue-500 hover:text-blue-600 text-sm">{t("components.test")}


                </button>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                    type="checkbox"
                    checked={enabled}
                    onChange={() => handleChannelToggle(channel)}
                    className="sr-only peer" />

                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            )}
          </div>
        </div>
        {/* Category Preferences */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">{t("pages.kategori_bazl_tercihler")}</h3>
          <div className="space-y-6">
            {Object.entries(preferences.categories).map(([category, channels]) =>
            <div key={category} className="border rounded-lg p-4">
                <div className="flex items-center mb-3">
                  {React.createElement(categoryInfo[category].icon, { className: "text-xl mr-3 text-gray-600" })}
                  <div className="flex-1">
                    <h4 className="font-medium">{categoryInfo[category].name}</h4>
                    <p className="text-sm text-gray-600">{categoryInfo[category].description}</p>
                  </div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {Object.entries(channels).map(([channel, enabled]) =>
                <label key={channel} className="flex items-center">
                      <input
                    type="checkbox"
                    checked={enabled}
                    onChange={() => handleCategoryChannelToggle(category, channel)}
                    disabled={!preferences.channels[channel]}
                    className="mr-2" />

                      <span className={`text-sm ${!preferences.channels[channel] ? 'text-gray-400' : ''}`}>
                        {channelInfo[channel].name}
                      </span>
                    </label>
                )}
                </div>
              </div>
            )}
          </div>
        </div>
        {/* Timing Preferences */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">{t("pages.bildirim_zamanlamas")}</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="font-medium mb-3">{t("pages.bildirim_skl")}</p>
              <div className="space-y-2">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="timing"
                    checked={preferences.timing.immediate}
                    onChange={() => handleTimingChange('immediate')}
                    className="mr-2" />

                  <span>Anında</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="timing"
                    checked={preferences.timing.hourly}
                    onChange={() => handleTimingChange('hourly')}
                    className="mr-2" />

                  <span>{t("pages.saatlik_zet")}</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="timing"
                    checked={preferences.timing.daily}
                    onChange={() => handleTimingChange('daily')}
                    className="mr-2" />

                  <span>{t("pages.gnlk_zet")}</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="timing"
                    checked={preferences.timing.weekly}
                    onChange={() => handleTimingChange('weekly')}
                    className="mr-2" />

                  <span>{t("pages.haftalk_zet")}</span>
                </label>
              </div>
            </div>
            <div>
              <p className="font-medium mb-3">{t("pages.sessiz_saatler")}</p>
              <label className="flex items-center mb-3">
                <input
                  type="checkbox"
                  checked={preferences.quietHours.enabled}
                  onChange={handleQuietHoursToggle}
                  className="mr-2" />

                <span>{t("pages.sessiz_saatleri_etkinletir")}</span>
              </label>
              {preferences.quietHours.enabled &&
              <div className="space-y-2 ml-6">
                  <div className="flex items-center space-x-2">
                    <label>Başlangıç:</label>
                    <input
                    type="time"
                    value={preferences.quietHours.start}
                    onChange={(e) => setPreferences({
                      ...preferences,
                      quietHours: { ...preferences.quietHours, start: e.target.value }
                    })}
                    className="px-3 py-1 border rounded" />

                  </div>
                  <div className="flex items-center space-x-2">
                    <label>Bitiş:</label>
                    <input
                    type="time"
                    value={preferences.quietHours.end}
                    onChange={(e) => setPreferences({
                      ...preferences,
                      quietHours: { ...preferences.quietHours, end: e.target.value }
                    })}
                    className="px-3 py-1 border rounded" />

                  </div>
                </div>
              }
            </div>
          </div>
        </div>
        {/* Digest Settings */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">{t("pages.zet_bildirimleri")}</h3>
          <label className="flex items-center mb-4">
            <input
              type="checkbox"
              checked={preferences.digest.enabled}
              onChange={handleDigestToggle}
              className="mr-2" />

            <span>{t("pages.zet_bildirimleri_al")}</span>
          </label>
          {preferences.digest.enabled &&
          <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">{t("pages.zet_zaman")}</label>
                  <input
                  type="time"
                  value={preferences.digest.time}
                  onChange={(e) => setPreferences({
                    ...preferences,
                    digest: { ...preferences.digest, time: e.target.value }
                  })}
                  className="w-full px-3 py-2 border rounded" />

                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">{t("pages.zet_skl")}</label>
                  <select
                  value={preferences.digest.frequency}
                  onChange={(e) => setPreferences({
                    ...preferences,
                    digest: { ...preferences.digest, frequency: e.target.value }
                  })}
                  className="w-full px-3 py-2 border rounded">

                    <option value="daily">Günlük</option>
                    <option value="weekly">Haftalık</option>
                    <option value="monthly">Aylık</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">{t("pages.zete_dahil_edilecek_kategoriler")}</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {Object.keys(categoryInfo).map((category) =>
                <label key={category} className="flex items-center">
                      <input
                    type="checkbox"
                    checked={preferences.digest.categories.includes(category)}
                    onChange={() => handleDigestCategoryToggle(category)}
                    className="mr-2" />

                      <span className="text-sm">{categoryInfo[category].name}</span>
                    </label>
                )}
                </div>
              </div>
            </div>
          }
        </div>
        {/* Frequency Limits */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">{t("pages.frekans_limitleri")}</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">{t("pages.gnlk_eposta_limiti")}

              </label>
              <input
                type="number"
                value={preferences.frequency.maxEmailsPerDay}
                onChange={(e) => setPreferences({
                  ...preferences,
                  frequency: { ...preferences.frequency, maxEmailsPerDay: parseInt(e.target.value) }
                })}
                className="w-full px-3 py-2 border rounded"
                min="0"
                max="100" />

            </div>
            <div>
              <label className="block text-sm font-medium mb-2">{t("pages.gnlk_push_limiti")}

              </label>
              <input
                type="number"
                value={preferences.frequency.maxPushPerDay}
                onChange={(e) => setPreferences({
                  ...preferences,
                  frequency: { ...preferences.frequency, maxPushPerDay: parseInt(e.target.value) }
                })}
                className="w-full px-3 py-2 border rounded"
                min="0"
                max="100" />

            </div>
            <div>
              <label className="block text-sm font-medium mb-2">{t("pages.gnlk_sms_limiti")}

              </label>
              <input
                type="number"
                value={preferences.frequency.maxSmsPerDay}
                onChange={(e) => setPreferences({
                  ...preferences,
                  frequency: { ...preferences.frequency, maxSmsPerDay: parseInt(e.target.value) }
                })}
                className="w-full px-3 py-2 border rounded"
                min="0"
                max="100" />

            </div>
          </div>
        </div>
        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={savePreferences}
            disabled={saving}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 disabled:opacity-50 flex items-center">

            {saving ?
            <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>{t("pages.kaydediliyor")}

            </> :

            <>
                <FaSave className="mr-2" />{t("pages.tercihleri_kaydet")}

            </>
            }
          </button>
        </div>
        {/* Info Box */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <FaInfoCircle className="text-blue-500 mt-1 mr-3" />
            <div>
              <p className="font-medium text-blue-900">{t("pages.bildirim_ipular")}</p>
              <ul className="text-sm text-blue-800 mt-2 space-y-1">
                <li>{t("pages._nemli_bildirimleri_karmamak_iin_en_az_bir_kanal_a")}</li>
                <li>{t("pages._sessiz_saatler_acil_bildirimler_iin_geerli_olmaya")}</li>
                <li>{t("pages._sms_bildirimleri_ek_crete_tabi_olabilir")}</li>
                <li>• Push bildirimleri için tarayıcı izni gereklidir</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>);

};
export default NotificationPreferencesPageV2;