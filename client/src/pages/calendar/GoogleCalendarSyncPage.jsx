// TODO: i18n - processed
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaGoogle, FaSync, FaCheck, FaTimes, FaInfoCircle, FaCalendarAlt, FaExclamationTriangle, FaTrash, FaClock, FaChartBar } from 'react-icons/fa';
import { toast } from 'react-toastify';import { useTranslation } from "react-i18next";
const GoogleCalendarSyncPageV2 = () => {const { t } = useTranslation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [accountInfo, setAccountInfo] = useState(null);
  const [syncSettings, setSyncSettings] = useState({
    enabled: false,
    auto_sync: false,
    sync_interval: 30,
    sync_direction: 'bidirectional',
    conflict_resolution: 'calendar_wins',
    sync_range_days: 365,
    selected_calendars: [],
    sync_types: {
      appointments: true,
      availability: true,
      holidays: false,
      reminders: true
    },
    notification_settings: {
      sync_success: true,
      sync_errors: true,
      conflicts: true,
      email_notifications: false
    }
  });
  const [googleCalendars, setGoogleCalendars] = useState([]);
  const [syncHistory, setSyncHistory] = useState([]);
  const [syncStats, setSyncStats] = useState({
    total_synced: 0,
    last_sync_appointments: 0,
    last_sync_errors: 0,
    next_sync_time: null
  });
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  useEffect(() => {
    fetchAccountInfo();
    fetchSyncSettings();
    fetchSyncHistory();
    fetchSyncStats();
  }, []);
  const fetchAccountInfo = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/calendar/google/account');
      setAccountInfo(response.data);
      if (response.data.connected) {
        fetchGoogleCalendars();
      }
    } catch (error) {
      console.error('Hesap bilgileri alınamadı:', error);
    } finally {
      setLoading(false);
    }
  };
  const fetchSyncSettings = async () => {
    try {
      const response = await axios.get('/api/calendar/google/settings');
      setSyncSettings(response.data);
    } catch (error) {
      console.error('Senkronizasyon ayarları alınamadı:', error);
    }
  };
  const fetchGoogleCalendars = async () => {
    try {
      const response = await axios.get('/api/calendar/google/calendars');
      setGoogleCalendars(response.data);
    } catch (error) {
      console.error('Google takvimler alınamadı:', error);
    }
  };
  const fetchSyncHistory = async () => {
    try {
      const response = await axios.get('/api/calendar/google/history');
      setSyncHistory(response.data);
    } catch (error) {
      console.error('Senkronizasyon geçmişi alınamadı:', error);
    }
  };
  const fetchSyncStats = async () => {
    try {
      const response = await axios.get('/api/calendar/google/stats');
      setSyncStats(response.data);
    } catch (error) {
      console.error('Senkronizasyon istatistikleri alınamadı:', error);
    }
  };
  const handleConnectGoogle = async () => {
    try {
      const response = await axios.get('/api/calendar/google/auth-url');
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error('Google bağlantısı başlatılamadı');
    }
  };
  const handleDisconnectGoogle = async () => {
    if (window.confirm('Google hesabı bağlantısını kesmek istediğinizden emin misiniz?')) {
      try {
        await axios.post('/api/calendar/google/disconnect');
        setAccountInfo(null);
        setGoogleCalendars([]);
        setSyncSettings({ ...syncSettings, enabled: false });
        toast.success('Google hesabı bağlantısı kesildi');
      } catch (error) {
        toast.error('Bağlantı kesilirken hata oluştu');
      }
    }
  };
  const handleSyncNow = async () => {
    setSyncing(true);
    try {
      const response = await axios.post('/api/calendar/google/sync');
      toast.success(`Senkronizasyon tamamlandı: ${response.data.synced_count} randevu senkronize edildi`);
      fetchSyncHistory();
      fetchSyncStats();
    } catch (error) {
      toast.error('Senkronizasyon sırasında hata oluştu');
    } finally {
      setSyncing(false);
    }
  };
  const handleUpdateSettings = async () => {
    try {
      await axios.put('/api/calendar/google/settings', syncSettings);
      toast.success('Ayarlar güncellendi');
    } catch (error) {
      toast.error('Ayarlar güncellenirken hata oluştu');
    }
  };
  const handleCalendarToggle = (calendarId) => {
    const updated = [...syncSettings.selected_calendars];
    const index = updated.indexOf(calendarId);
    if (index > -1) {
      updated.splice(index, 1);
    } else {
      updated.push(calendarId);
    }
    setSyncSettings({ ...syncSettings, selected_calendars: updated });
  };
  const renderConnectionStatus = () => {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FaGoogle className="mr-2 text-blue-500" />{t("pages.google_hesap_balants")}

        </h3>
        {accountInfo?.connected ?
        <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">{accountInfo.email}</p>
                <p className="text-sm text-gray-600">
                  Bağlantı: {new Date(accountInfo.connected_at).toLocaleDateString('tr-TR')}
                </p>
              </div>
              <div className="flex items-center space-x-2">
                <span className="flex items-center text-green-600">
                  <FaCheck className="mr-1" />
                  Bağlı
                </span>
                <button
                onClick={handleDisconnectGoogle}
                className="px-3 py-1 text-sm text-red-600 hover:bg-red-50 rounded">{t("pages.balanty_kes")}


              </button>
              </div>
            </div>
            <div className="pt-4 border-t">
              <label className="flex items-center">
                <input
                type="checkbox"
                checked={syncSettings.enabled}
                onChange={(e) => setSyncSettings({ ...syncSettings, enabled: e.target.checked })}
                className="mr-2" />

                <span>{t("pages.senkronizasyonu_etkinletir")}</span>
              </label>
            </div>
          </div> :

        <div className="text-center py-8">
            <FaGoogle className="text-5xl text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600 mb-4">{t("pages.google_hesabnz_bal_deil")}</p>
            <button
            onClick={handleConnectGoogle}
            className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600">{t("pages.google_ile_balan")}


          </button>
          </div>
        }
      </div>);

  };
  const renderSyncSettings = () => {
    if (!accountInfo?.connected || !syncSettings.enabled) return null;
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FaSync className="mr-2" />{t("pages.senkronizasyon_ayarlar")}

        </h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">{t("pages.senkronizasyon_yn")}</label>
            <select
              value={syncSettings.sync_direction}
              onChange={(e) => setSyncSettings({ ...syncSettings, sync_direction: e.target.value })}
              className="w-full px-3 py-2 border rounded">

              <option value="to_google">{t("pages.sadece_googlea")}</option>
              <option value="from_google">{t("pages.sadece_googledan")}</option>
              <option value="bidirectional">{t("pages.ift_ynl")}</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">{t("pages.akma_zm")}</label>
            <select
              value={syncSettings.conflict_resolution}
              onChange={(e) => setSyncSettings({ ...syncSettings, conflict_resolution: e.target.value })}
              className="w-full px-3 py-2 border rounded">

              <option value="calendar_wins">{t("pages.takvim_ncelikli")}</option>
              <option value="google_wins">{t("pages.google_ncelikli")}</option>
              <option value="ask_each_time">{t("pages.her_seferinde_sor")}</option>
            </select>
          </div>
          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={syncSettings.auto_sync}
                onChange={(e) => setSyncSettings({ ...syncSettings, auto_sync: e.target.checked })}
                className="mr-2" />

              <span>{t("pages.otomatik_senkronizasyon")}</span>
            </label>
          </div>
          {syncSettings.auto_sync &&
          <div>
              <label className="block text-sm font-medium mb-2">{t("pages.senkronizasyon_aral_dakika")}

            </label>
              <input
              type="number"
              value={syncSettings.sync_interval}
              onChange={(e) => setSyncSettings({ ...syncSettings, sync_interval: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border rounded"
              min="5"
              max="1440" />

            </div>
          }
          <div>
            <label className="block text-sm font-medium mb-2">{t("pages.senkronizasyon_aral_gn")}

            </label>
            <input
              type="number"
              value={syncSettings.sync_range_days}
              onChange={(e) => setSyncSettings({ ...syncSettings, sync_range_days: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border rounded"
              min="30"
              max="730" />

          </div>
          <div>
            <label className="block text-sm font-medium mb-2">{t("pages.veri_trleri")}</label>
            <div className="space-y-2">
              {Object.entries(syncSettings.sync_types).map(([type, enabled]) =>
              <label key={type} className="flex items-center">
                  <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(e) => setSyncSettings({
                    ...syncSettings,
                    sync_types: { ...syncSettings.sync_types, [type]: e.target.checked }
                  })}
                  className="mr-2" />

                  <span>{type === 'appointments' ? 'Randevular' :
                  type === 'availability' ? 'Uygunluk' :
                  type === 'holidays' ? 'Tatiller' : 'Hatırlatıcılar'}</span>
                </label>
              )}
            </div>
          </div>
          <button
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className="text-blue-500 hover:text-blue-600 text-sm">

            {showAdvancedSettings ? 'Gelişmiş Ayarları Gizle' : 'Gelişmiş Ayarları Göster'}
          </button>
          {showAdvancedSettings &&
          <div className="space-y-4 pt-4 border-t">
              <div>
                <label className="block text-sm font-medium mb-2">{t("components.bildirim_ayarlar")}</label>
                <div className="space-y-2">
                  {Object.entries(syncSettings.notification_settings).map(([setting, enabled]) =>
                <label key={setting} className="flex items-center">
                      <input
                    type="checkbox"
                    checked={enabled}
                    onChange={(e) => setSyncSettings({
                      ...syncSettings,
                      notification_settings: {
                        ...syncSettings.notification_settings,
                        [setting]: e.target.checked
                      }
                    })}
                    className="mr-2" />

                      <span>
                        {setting === 'sync_success' ? 'Başarılı Senkronizasyonlar' :
                    setting === 'sync_errors' ? 'Senkronizasyon Hataları' :
                    setting === 'conflicts' ? 'Çakışmalar' : 'E-posta Bildirimleri'}
                      </span>
                    </label>
                )}
                </div>
              </div>
            </div>
          }
          <div className="flex justify-end space-x-2 pt-4">
            <button
              onClick={handleUpdateSettings}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">{t("pages.ayarlar_kaydet")}


            </button>
            <button
              onClick={handleSyncNow}
              disabled={syncing}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50">

              {syncing ? 'Senkronize Ediliyor...' : 'Şimdi Senkronize Et'}
            </button>
          </div>
        </div>
      </div>);

  };
  const renderCalendarSelection = () => {
    if (!accountInfo?.connected || !syncSettings.enabled || googleCalendars.length === 0) return null;
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FaCalendarAlt className="mr-2" />{t("pages.google_takvimler")}

        </h3>
        <div className="space-y-3">
          {googleCalendars.map((calendar) =>
          <div key={calendar.id} className="flex items-center justify-between p-3 border rounded">
              <div className="flex items-center">
                <input
                type="checkbox"
                checked={syncSettings.selected_calendars.includes(calendar.id)}
                onChange={() => handleCalendarToggle(calendar.id)}
                className="mr-3" />

                <div>
                  <p className="font-medium">{calendar.name}</p>
                  {calendar.description &&
                <p className="text-sm text-gray-600">{calendar.description}</p>
                }
                </div>
              </div>
              <div
              className="w-4 h-4 rounded"
              style={{ backgroundColor: calendar.color }} />

            </div>
          )}
        </div>
      </div>);

  };
  const renderSyncStats = () => {
    if (!accountInfo?.connected || !syncSettings.enabled) return null;
    return (
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FaChartBar className="mr-2" />{t("pages.senkronizasyon_istatistikleri")}

        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded">
            <p className="text-2xl font-bold text-blue-600">{syncStats.total_synced}</p>
            <p className="text-sm text-gray-600">{t("pages.toplam_senkronize")}</p>
          </div>
          <div className="text-center p-4 bg-green-50 rounded">
            <p className="text-2xl font-bold text-green-600">{syncStats.last_sync_appointments}</p>
            <p className="text-sm text-gray-600">{t("pages.son_senkronizasyon")}</p>
          </div>
          <div className="text-center p-4 bg-red-50 rounded">
            <p className="text-2xl font-bold text-red-600">{syncStats.last_sync_errors}</p>
            <p className="text-sm text-gray-600">{t("pages.hata_says")}</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded">
            <p className="text-2xl font-bold text-purple-600">
              {syncStats.next_sync_time ? new Date(syncStats.next_sync_time).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) : '-'}
            </p>
            <p className="text-sm text-gray-600">{t("pages.sonraki_senkronizasyon")}</p>
          </div>
        </div>
      </div>);

  };
  const renderSyncHistory = () => {
    if (!accountInfo?.connected || !syncSettings.enabled || syncHistory.length === 0) return null;
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FaClock className="mr-2" />{t("pages.senkronizasyon_gemii")}

        </h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tarih/Saat
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t("pages.durum")}

                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t("pages.senkronize")}

                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{t("components.hata")}

                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Süre
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {syncHistory.map((sync) =>
              <tr key={sync.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(sync.sync_time).toLocaleString('tr-TR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {sync.status === 'success' ?
                  <span className="flex items-center text-green-600">
                        <FaCheck className="mr-1" />
                        Başarılı
                      </span> :

                  <span className="flex items-center text-red-600">
                        <FaTimes className="mr-1" />
                        Hatalı
                      </span>
                  }
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {sync.synced_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {sync.error_count}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {sync.duration}s
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>);

  };
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>);

  }
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/calendar')}
            className="text-gray-600 hover:text-gray-800 mb-4">{t("pages._takvime_geri_dn")}


          </button>
          <h1 className="text-2xl font-bold">{t("pages.google_takvim_senkronizasyonu")}</h1>
          <p className="text-gray-600">{t("pages.google_takvim_ile_otomatik_senkronizasyon_ayarlarn")}</p>
        </div>
        {renderConnectionStatus()}
        {renderSyncSettings()}
        {renderCalendarSelection()}
        {renderSyncStats()}
        {renderSyncHistory()}
      </div>
    </div>);

};
export default GoogleCalendarSyncPageV2;