import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaBell, FaCheck, FaTrash, FaCog, FaFilter, FaEnvelope, FaCalendar, FaGraduationCap, FaUserFriends, FaFile, FaChartBar, FaExclamationCircle, FaInfoCircle, FaCheckCircle, FaTimes } from 'react-icons/fa';
import { toast } from 'react-toastify';
const NotificationCenterV2 = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [filteredNotifications, setFilteredNotifications] = useState([]);
  const [categories, setCategories] = useState([
    { id: 'all', name: 'Tümü', icon: FaBell, count: 0 },
    { id: 'message', name: 'Mesajlar', icon: FaEnvelope, count: 0 },
    { id: 'appointment', name: 'Randevular', icon: FaCalendar, count: 0 },
    { id: 'assessment', name: 'Değerlendirmeler', icon: FaGraduationCap, count: 0 },
    { id: 'system', name: 'Sistem', icon: FaCog, count: 0 },
    { id: 'document', name: 'Dokümanlar', icon: FaFile, count: 0 },
    { id: 'analytics', name: 'Raporlar', icon: FaChartBar, count: 0 }
  ]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [timeFilter, setTimeFilter] = useState('all');
  const [readFilter, setReadFilter] = useState('all');
  const [selectedNotifications, setSelectedNotifications] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState({});
  const [stats, setStats] = useState({
    total: 0,
    unread: 0,
    today: 0,
    thisWeek: 0
  });
  useEffect(() => {
    fetchNotifications();
    fetchPreferences();
    connectWebSocket();
    return () => disconnectWebSocket();
  }, []);
  useEffect(() => {
    filterNotifications();
    calculateStats();
  }, [notifications, selectedCategory, timeFilter, readFilter]);
  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/notifications');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'new_notification') {
        setNotifications(prev => [data.notification, ...prev]);
        showBrowserNotification(data.notification);
      }
    };
    window.notificationWs = ws;
  };
  const disconnectWebSocket = () => {
    if (window.notificationWs) {
      window.notificationWs.close();
    }
  };
  const showBrowserNotification = (notification) => {
    if (Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        badge: '/badge.png'
      });
    }
  };
  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/notifications');
      setNotifications(response.data);
      updateCategoryCounts(response.data);
    } catch (error) {
      toast.error('Bildirimler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };
  const fetchPreferences = async () => {
    try {
      const response = await axios.get('/api/notifications/preferences');
      setPreferences(response.data);
    } catch (error) {
      console.error('Tercihler yüklenemedi:', error);
    }
  };
  const updateCategoryCounts = (notificationList) => {
    const counts = {};
    notificationList.forEach(notif => {
      counts[notif.category] = (counts[notif.category] || 0) + 1;
    });
    setCategories(prevCategories => 
      prevCategories.map(cat => ({
        ...cat,
        count: cat.id === 'all' ? notificationList.length : (counts[cat.id] || 0)
      }))
    );
  };
  const filterNotifications = () => {
    let filtered = [...notifications];
    // Category filter
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(notif => notif.category === selectedCategory);
    }
    // Read status filter
    if (readFilter === 'unread') {
      filtered = filtered.filter(notif => !notif.is_read);
    } else if (readFilter === 'read') {
      filtered = filtered.filter(notif => notif.is_read);
    }
    // Time filter
    const now = new Date();
    if (timeFilter === 'today') {
      filtered = filtered.filter(notif => {
        const notifDate = new Date(notif.created_at);
        return notifDate.toDateString() === now.toDateString();
      });
    } else if (timeFilter === 'week') {
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      filtered = filtered.filter(notif => new Date(notif.created_at) >= weekAgo);
    } else if (timeFilter === 'month') {
      const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      filtered = filtered.filter(notif => new Date(notif.created_at) >= monthAgo);
    }
    setFilteredNotifications(filtered);
  };
  const calculateStats = () => {
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    setStats({
      total: notifications.length,
      unread: notifications.filter(n => !n.is_read).length,
      today: notifications.filter(n => new Date(n.created_at) >= today).length,
      thisWeek: notifications.filter(n => new Date(n.created_at) >= weekAgo).length
    });
  };
  const markAsRead = async (notificationIds) => {
    try {
      await axios.put('/api/notifications/read', { notification_ids: notificationIds });
      setNotifications(prevNotifications =>
        prevNotifications.map(notif =>
          notificationIds.includes(notif.id) ? { ...notif, is_read: true } : notif
        )
      );
      toast.success('Bildirimler okundu olarak işaretlendi');
    } catch (error) {
      toast.error('İşlem başarısız');
    }
  };
  const deleteNotifications = async (notificationIds) => {
    if (window.confirm('Seçili bildirimleri silmek istediğinizden emin misiniz?')) {
      try {
        await axios.delete('/api/notifications', { data: { notification_ids: notificationIds } });
        setNotifications(prevNotifications =>
          prevNotifications.filter(notif => !notificationIds.includes(notif.id))
        );
        setSelectedNotifications([]);
        toast.success('Bildirimler silindi');
      } catch (error) {
        toast.error('Silme işlemi başarısız');
      }
    }
  };
  const updatePreferences = async (newPreferences) => {
    try {
      await axios.put('/api/notifications/preferences', newPreferences);
      setPreferences(newPreferences);
      toast.success('Tercihler güncellendi');
    } catch (error) {
      toast.error('Güncelleme başarısız');
    }
  };
  const handleSelectNotification = (notificationId) => {
    if (selectedNotifications.includes(notificationId)) {
      setSelectedNotifications(selectedNotifications.filter(id => id !== notificationId));
    } else {
      setSelectedNotifications([...selectedNotifications, notificationId]);
    }
  };
  const handleSelectAll = () => {
    if (selectedNotifications.length === filteredNotifications.length) {
      setSelectedNotifications([]);
    } else {
      setSelectedNotifications(filteredNotifications.map(notif => notif.id));
    }
  };
  const handleNotificationClick = async (notification) => {
    if (!notification.is_read) {
      await markAsRead([notification.id]);
    }
    if (notification.action_url) {
      navigate(notification.action_url);
    }
  };
  const getNotificationIcon = (notification) => {
    const icons = {
      message: FaEnvelope,
      appointment: FaCalendar,
      assessment: FaGraduationCap,
      system: FaCog,
      document: FaFile,
      analytics: FaChartBar,
      error: FaExclamationCircle,
      warning: FaExclamationCircle,
      info: FaInfoCircle,
      success: FaCheckCircle
    };
    const Icon = icons[notification.category] || icons[notification.type] || FaBell;
    return <Icon />;
  };
  const getTypeColor = (type) => {
    const colors = {
      error: 'text-red-500',
      warning: 'text-yellow-500',
      info: 'text-blue-500',
      success: 'text-green-500'
    };
    return colors[type] || 'text-gray-500';
  };
  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    if (diffMins < 1) return 'Şimdi';
    if (diffMins < 60) return `${diffMins} dk önce`;
    if (diffHours < 24) return `${diffHours} saat önce`;
    if (diffDays < 7) return `${diffDays} gün önce`;
    return date.toLocaleDateString('tr-TR');
  };
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto p-6">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Bildirim Merkezi</h1>
          <p className="text-gray-600">Tüm bildirimlerinizi tek bir yerden yönetin</p>
        </div>
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Toplam</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <FaBell className="text-3xl text-gray-400" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Okunmamış</p>
                <p className="text-2xl font-bold text-blue-600">{stats.unread}</p>
              </div>
              <div className="relative">
                <FaBell className="text-3xl text-blue-400" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Bugün</p>
                <p className="text-2xl font-bold">{stats.today}</p>
              </div>
              <FaCalendar className="text-3xl text-gray-400" />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Bu Hafta</p>
                <p className="text-2xl font-bold">{stats.thisWeek}</p>
              </div>
              <FaChartBar className="text-3xl text-gray-400" />
            </div>
          </div>
        </div>
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Sidebar */}
          <div className="lg:w-64">
            {/* Categories */}
            <div className="bg-white rounded-lg shadow-md p-4 mb-4">
              <h3 className="font-semibold mb-3">Kategoriler</h3>
              <div className="space-y-2">
                {categories.map(category => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`w-full flex items-center justify-between p-2 rounded hover:bg-gray-50 ${
                      selectedCategory === category.id ? 'bg-blue-50 text-blue-600' : ''
                    }`}
                  >
                    <div className="flex items-center">
                      <category.icon className="mr-2" />
                      <span>{category.name}</span>
                    </div>
                    <span className="text-sm">{category.count}</span>
                  </button>
                ))}
              </div>
            </div>
            {/* Filters */}
            <div className="bg-white rounded-lg shadow-md p-4">
              <h3 className="font-semibold mb-3 flex items-center">
                <FaFilter className="mr-2" />
                Filtreler
              </h3>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Okunma Durumu</label>
                <select
                  value={readFilter}
                  onChange={(e) => setReadFilter(e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                >
                  <option value="all">Tümü</option>
                  <option value="unread">Okunmamış</option>
                  <option value="read">Okunmuş</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Zaman Aralığı</label>
                <select
                  value={timeFilter}
                  onChange={(e) => setTimeFilter(e.target.value)}
                  className="w-full px-3 py-2 border rounded"
                >
                  <option value="all">Tümü</option>
                  <option value="today">Bugün</option>
                  <option value="week">Bu Hafta</option>
                  <option value="month">Bu Ay</option>
                </select>
              </div>
            </div>
          </div>
          {/* Main Content */}
          <div className="flex-1">
            {/* Actions Bar */}
            <div className="bg-white rounded-lg shadow-md p-4 mb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <input
                    type="checkbox"
                    checked={selectedNotifications.length === filteredNotifications.length && filteredNotifications.length > 0}
                    onChange={handleSelectAll}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-600">
                    {selectedNotifications.length} seçili
                  </span>
                  {selectedNotifications.length > 0 && (
                    <>
                      <button
                        onClick={() => markAsRead(selectedNotifications)}
                        className="text-blue-500 hover:text-blue-600 text-sm"
                      >
                        <FaCheck className="inline mr-1" />
                        Okundu İşaretle
                      </button>
                      <button
                        onClick={() => deleteNotifications(selectedNotifications)}
                        className="text-red-500 hover:text-red-600 text-sm"
                      >
                        <FaTrash className="inline mr-1" />
                        Sil
                      </button>
                    </>
                  )}
                </div>
                <button
                  onClick={() => setShowSettings(true)}
                  className="text-gray-600 hover:text-gray-800"
                >
                  <FaCog />
                </button>
              </div>
            </div>
            {/* Notifications List */}
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : filteredNotifications.length === 0 ? (
              <div className="bg-white rounded-lg shadow-md p-8 text-center">
                <FaBell className="text-5xl text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">Bildirim bulunamadı</p>
              </div>
            ) : (
              <div className="space-y-2">
                {filteredNotifications.map(notification => (
                  <div
                    key={notification.id}
                    className={`bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow cursor-pointer ${
                      !notification.is_read ? 'border-l-4 border-blue-500' : ''
                    }`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="flex items-start">
                      <input
                        type="checkbox"
                        checked={selectedNotifications.includes(notification.id)}
                        onChange={(e) => {
                          e.stopPropagation();
                          handleSelectNotification(notification.id);
                        }}
                        className="mr-3 mt-1"
                      />
                      <div className={`text-2xl mr-3 ${getTypeColor(notification.type)}`}>
                        {getNotificationIcon(notification)}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-semibold">{notification.title}</h4>
                            <p className="text-gray-600 text-sm mt-1">{notification.message}</p>
                          </div>
                          <span className="text-sm text-gray-500 ml-4">
                            {formatTime(notification.created_at)}
                          </span>
                        </div>
                        {notification.action_text && (
                          <button className="text-blue-500 hover:text-blue-600 text-sm mt-2">
                            {notification.action_text}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">Bildirim Tercihleri</h3>
              <button
                onClick={() => setShowSettings(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <FaTimes />
              </button>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {Object.entries(preferences).map(([key, value]) => (
                  <label key={key} className="flex items-center justify-between">
                    <span className="text-sm">
                      {key === 'email' ? 'E-posta Bildirimleri' :
                       key === 'push' ? 'Push Bildirimleri' :
                       key === 'sms' ? 'SMS Bildirimleri' :
                       key === 'inApp' ? 'Uygulama İçi Bildirimler' : key}
                    </span>
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={(e) => setPreferences({ ...preferences, [key]: e.target.checked })}
                      className="ml-3"
                    />
                  </label>
                ))}
              </div>
              <div className="mt-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Bildirim Sıklığı</label>
                  <select className="w-full px-3 py-2 border rounded">
                    <option value="realtime">Gerçek Zamanlı</option>
                    <option value="hourly">Saatlik Özet</option>
                    <option value="daily">Günlük Özet</option>
                    <option value="weekly">Haftalık Özet</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Sessiz Saatler</label>
                  <div className="flex space-x-2">
                    <input type="time" className="px-3 py-2 border rounded" />
                    <span className="self-center">-</span>
                    <input type="time" className="px-3 py-2 border rounded" />
                  </div>
                </div>
              </div>
              <div className="flex justify-end space-x-2 mt-6">
                <button
                  onClick={() => setShowSettings(false)}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  İptal
                </button>
                <button
                  onClick={() => {
                    updatePreferences(preferences);
                    setShowSettings(false);
                  }}
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  Kaydet
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
export default NotificationCenterV2;