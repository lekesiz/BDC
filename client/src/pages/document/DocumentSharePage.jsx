import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaShare, FaLink, FaCopy, FaEnvelope, FaUsers, FaUser, FaLock, FaEye, FaDownload, FaEdit, FaTrash, FaCheck, FaTimes, FaSearch, FaClock, FaGlobe } from 'react-icons/fa';
import { toast } from 'react-toastify';
const DocumentSharePageV2 = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [document, setDocument] = useState(null);
  const [sharedUsers, setSharedUsers] = useState([]);
  const [sharedGroups, setSharedGroups] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState({ users: [], groups: [] });
  const [shareLink, setShareLink] = useState(null);
  const [linkSettings, setLinkSettings] = useState({
    enabled: false,
    expiration: null,
    password: '',
    max_views: null,
    allow_download: true,
    require_login: false
  });
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [selectedGroups, setSelectedGroups] = useState([]);
  const [permissions, setPermissions] = useState('view');
  const [showLinkModal, setShowLinkModal] = useState(false);
  const [emailData, setEmailData] = useState({
    recipients: '',
    subject: '',
    message: ''
  });
  const [showEmailModal, setShowEmailModal] = useState(false);
  const [shareHistory, setShareHistory] = useState([]);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  useEffect(() => {
    fetchDocument();
    fetchSharedUsers();
    fetchShareLink();
    fetchShareHistory();
  }, [id]);
  const fetchDocument = async () => {
    try {
      const response = await axios.get(`/api/documents/${id}`);
      setDocument(response.data);
    } catch (error) {
      toast.error('Doküman yüklenemedi');
      navigate('/documents');
    }
  };
  const fetchSharedUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/documents/${id}/shares`);
      setSharedUsers(response.data.users || []);
      setSharedGroups(response.data.groups || []);
    } catch (error) {
      console.error('Paylaşımlar yüklenemedi:', error);
    } finally {
      setLoading(false);
    }
  };
  const fetchShareLink = async () => {
    try {
      const response = await axios.get(`/api/documents/${id}/share-link`);
      setShareLink(response.data.link);
      setLinkSettings(response.data.settings || linkSettings);
    } catch (error) {
      console.error('Paylaşım linki yüklenemedi:', error);
    }
  };
  const fetchShareHistory = async () => {
    try {
      const response = await axios.get(`/api/documents/${id}/share-history`);
      setShareHistory(response.data);
    } catch (error) {
      console.error('Paylaşım geçmişi yüklenemedi:', error);
    }
  };
  const searchUsersAndGroups = async (term) => {
    if (!term || term.length < 2) {
      setSearchResults({ users: [], groups: [] });
      return;
    }
    try {
      const response = await axios.get('/api/search/users-groups', {
        params: { q: term }
      });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Arama başarısız:', error);
    }
  };
  const handleShare = async () => {
    try {
      const data = {
        user_ids: selectedUsers.map(u => u.id),
        group_ids: selectedGroups.map(g => g.id),
        permissions
      };
      await axios.post(`/api/documents/${id}/share`, data);
      toast.success('Doküman paylaşıldı');
      fetchSharedUsers();
      setSelectedUsers([]);
      setSelectedGroups([]);
      setSearchTerm('');
      setSearchResults({ users: [], groups: [] });
    } catch (error) {
      toast.error('Paylaşım başarısız');
    }
  };
  const handleRemoveShare = async (shareId, type) => {
    if (window.confirm('Bu paylaşımı kaldırmak istediğinizden emin misiniz?')) {
      try {
        await axios.delete(`/api/documents/${id}/shares/${shareId}`, {
          params: { type }
        });
        toast.success('Paylaşım kaldırıldı');
        fetchSharedUsers();
      } catch (error) {
        toast.error('İşlem başarısız');
      }
    }
  };
  const handleUpdatePermission = async (shareId, newPermission, type) => {
    try {
      await axios.put(`/api/documents/${id}/shares/${shareId}`, {
        permissions: newPermission,
        type
      });
      toast.success('İzinler güncellendi');
      fetchSharedUsers();
    } catch (error) {
      toast.error('Güncelleme başarısız');
    }
  };
  const handleGenerateLink = async () => {
    try {
      const response = await axios.post(`/api/documents/${id}/share-link`, linkSettings);
      setShareLink(response.data.link);
      toast.success('Paylaşım linki oluşturuldu');
    } catch (error) {
      toast.error('Link oluşturulamadı');
    }
  };
  const handleRevokeLink = async () => {
    if (window.confirm('Paylaşım linkini iptal etmek istediğinizden emin misiniz?')) {
      try {
        await axios.delete(`/api/documents/${id}/share-link`);
        setShareLink(null);
        toast.success('Paylaşım linki iptal edildi');
      } catch (error) {
        toast.error('İşlem başarısız');
      }
    }
  };
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Kopyalandı');
  };
  const handleSendEmail = async () => {
    try {
      await axios.post(`/api/documents/${id}/share-email`, {
        ...emailData,
        link: shareLink
      });
      toast.success('E-posta gönderildi');
      setShowEmailModal(false);
      setEmailData({ recipients: '', subject: '', message: '' });
    } catch (error) {
      toast.error('E-posta gönderilemedi');
    }
  };
  const renderPermissionBadge = (permission) => {
    const badges = {
      view: { color: 'bg-green-100 text-green-800', icon: FaEye },
      download: { color: 'bg-blue-100 text-blue-800', icon: FaDownload },
      edit: { color: 'bg-yellow-100 text-yellow-800', icon: FaEdit }
    };
    const badge = badges[permission] || badges.view;
    const Icon = badge.icon;
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        <Icon className="mr-1" />
        {permission === 'view' ? 'Görüntüleme' : permission === 'download' ? 'İndirme' : 'Düzenleme'}
      </span>
    );
  };
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate(`/documents/${id}`)}
            className="text-gray-600 hover:text-gray-800 mb-4"
          >
            ← Doküman Detayına Dön
          </button>
          <h1 className="text-2xl font-bold mb-2">{document?.name} - Paylaşım Ayarları</h1>
          <p className="text-gray-600">Bu dokümanı diğer kullanıcılarla paylaşın</p>
        </div>
        {/* Share with Users/Groups */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">
            <FaUsers className="inline mr-2" />
            Kullanıcı ve Gruplarla Paylaş
          </h3>
          <div className="mb-4">
            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  searchUsersAndGroups(e.target.value);
                }}
                placeholder="Kullanıcı veya grup ara..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg"
              />
              <FaSearch className="absolute left-3 top-3 text-gray-400" />
            </div>
            {/* Search Results */}
            {(searchResults.users.length > 0 || searchResults.groups.length > 0) && (
              <div className="mt-2 border rounded-lg max-h-60 overflow-y-auto">
                {searchResults.users.length > 0 && (
                  <div>
                    <p className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50">Kullanıcılar</p>
                    {searchResults.users.map(user => (
                      <div
                        key={user.id}
                        className="px-3 py-2 hover:bg-gray-50 cursor-pointer flex items-center justify-between"
                        onClick={() => {
                          if (!selectedUsers.find(u => u.id === user.id)) {
                            setSelectedUsers([...selectedUsers, user]);
                          }
                        }}
                      >
                        <div className="flex items-center">
                          <FaUser className="text-gray-400 mr-2" />
                          <div>
                            <p className="font-medium">{user.name}</p>
                            <p className="text-sm text-gray-600">{user.email}</p>
                          </div>
                        </div>
                        {selectedUsers.find(u => u.id === user.id) && (
                          <FaCheck className="text-green-500" />
                        )}
                      </div>
                    ))}
                  </div>
                )}
                {searchResults.groups.length > 0 && (
                  <div>
                    <p className="px-3 py-2 text-sm font-medium text-gray-700 bg-gray-50">Gruplar</p>
                    {searchResults.groups.map(group => (
                      <div
                        key={group.id}
                        className="px-3 py-2 hover:bg-gray-50 cursor-pointer flex items-center justify-between"
                        onClick={() => {
                          if (!selectedGroups.find(g => g.id === group.id)) {
                            setSelectedGroups([...selectedGroups, group]);
                          }
                        }}
                      >
                        <div className="flex items-center">
                          <FaUsers className="text-gray-400 mr-2" />
                          <div>
                            <p className="font-medium">{group.name}</p>
                            <p className="text-sm text-gray-600">{group.member_count} üye</p>
                          </div>
                        </div>
                        {selectedGroups.find(g => g.id === group.id) && (
                          <FaCheck className="text-green-500" />
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
          {/* Selected Users and Groups */}
          {(selectedUsers.length > 0 || selectedGroups.length > 0) && (
            <div className="mb-4">
              <p className="text-sm font-medium mb-2">Seçilenler:</p>
              <div className="flex flex-wrap gap-2">
                {selectedUsers.map(user => (
                  <span
                    key={user.id}
                    className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center"
                  >
                    <FaUser className="mr-1" />
                    {user.name}
                    <button
                      onClick={() => setSelectedUsers(selectedUsers.filter(u => u.id !== user.id))}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      <FaTimes />
                    </button>
                  </span>
                ))}
                {selectedGroups.map(group => (
                  <span
                    key={group.id}
                    className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm flex items-center"
                  >
                    <FaUsers className="mr-1" />
                    {group.name}
                    <button
                      onClick={() => setSelectedGroups(selectedGroups.filter(g => g.id !== group.id))}
                      className="ml-2 text-green-600 hover:text-green-800"
                    >
                      <FaTimes />
                    </button>
                  </span>
                ))}
              </div>
            </div>
          )}
          {/* Permission Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2">İzinler</label>
            <select
              value={permissions}
              onChange={(e) => setPermissions(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
            >
              <option value="view">Sadece Görüntüleme</option>
              <option value="download">Görüntüleme ve İndirme</option>
              <option value="edit">Tam Yetki (Görüntüleme, İndirme, Düzenleme)</option>
            </select>
          </div>
          <button
            onClick={handleShare}
            disabled={selectedUsers.length === 0 && selectedGroups.length === 0}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
          >
            <FaShare className="inline mr-2" />
            Paylaş
          </button>
        </div>
        {/* Current Shares */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">Mevcut Paylaşımlar</h3>
          {sharedUsers.length === 0 && sharedGroups.length === 0 ? (
            <p className="text-gray-600">Bu doküman henüz kimseyle paylaşılmamış</p>
          ) : (
            <div className="space-y-3">
              {sharedUsers.map(share => (
                <div key={share.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <FaUser className="text-gray-400 mr-3" />
                    <div>
                      <p className="font-medium">{share.user_name}</p>
                      <p className="text-sm text-gray-600">{share.user_email}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    {renderPermissionBadge(share.permissions)}
                    <select
                      value={share.permissions}
                      onChange={(e) => handleUpdatePermission(share.id, e.target.value, 'user')}
                      className="px-2 py-1 border rounded text-sm"
                    >
                      <option value="view">Görüntüleme</option>
                      <option value="download">İndirme</option>
                      <option value="edit">Düzenleme</option>
                    </select>
                    <button
                      onClick={() => handleRemoveShare(share.id, 'user')}
                      className="text-red-500 hover:text-red-600"
                    >
                      <FaTrash />
                    </button>
                  </div>
                </div>
              ))}
              {sharedGroups.map(share => (
                <div key={share.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center">
                    <FaUsers className="text-gray-400 mr-3" />
                    <div>
                      <p className="font-medium">{share.group_name}</p>
                      <p className="text-sm text-gray-600">{share.member_count} üye</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    {renderPermissionBadge(share.permissions)}
                    <select
                      value={share.permissions}
                      onChange={(e) => handleUpdatePermission(share.id, e.target.value, 'group')}
                      className="px-2 py-1 border rounded text-sm"
                    >
                      <option value="view">Görüntüleme</option>
                      <option value="download">İndirme</option>
                      <option value="edit">Düzenleme</option>
                    </select>
                    <button
                      onClick={() => handleRemoveShare(share.id, 'group')}
                      className="text-red-500 hover:text-red-600"
                    >
                      <FaTrash />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        {/* Share Link */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h3 className="text-lg font-semibold mb-4">
            <FaLink className="inline mr-2" />
            Paylaşım Linki
          </h3>
          {shareLink ? (
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <input
                  type="text"
                  value={shareLink}
                  readOnly
                  className="flex-1 px-3 py-2 border rounded-lg bg-gray-50"
                />
                <button
                  onClick={() => copyToClipboard(shareLink)}
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  <FaCopy className="inline mr-2" />
                  Kopyala
                </button>
                <button
                  onClick={() => setShowEmailModal(true)}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                >
                  <FaEnvelope className="inline mr-2" />
                  E-posta Gönder
                </button>
              </div>
              <div className="text-sm text-gray-600">
                {linkSettings.expiration && (
                  <p>• Geçerlilik: {new Date(linkSettings.expiration).toLocaleDateString('tr-TR')}</p>
                )}
                {linkSettings.password && <p>• Şifre korumalı</p>}
                {linkSettings.max_views && <p>• Maksimum görüntüleme: {linkSettings.max_views}</p>}
                {!linkSettings.allow_download && <p>• İndirme devre dışı</p>}
                {linkSettings.require_login && <p>• Giriş gerekli</p>}
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setShowLinkModal(true)}
                  className="text-blue-500 hover:text-blue-600"
                >
                  Ayarları Düzenle
                </button>
                <button
                  onClick={handleRevokeLink}
                  className="text-red-500 hover:text-red-600"
                >
                  Linki İptal Et
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-gray-600 mb-4">Henüz paylaşım linki oluşturulmamış</p>
              <button
                onClick={() => setShowLinkModal(true)}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              >
                Link Oluştur
              </button>
            </div>
          )}
        </div>
        {/* Additional Actions */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Ek İşlemler</h3>
          <button
            onClick={() => setShowHistoryModal(true)}
            className="text-blue-500 hover:text-blue-600"
          >
            <FaClock className="inline mr-2" />
            Paylaşım Geçmişini Görüntüle
          </button>
        </div>
      </div>
      {/* Link Settings Modal */}
      {showLinkModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">Paylaşım Linki Ayarları</h3>
              <button
                onClick={() => setShowLinkModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <FaTimes />
              </button>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={linkSettings.require_login}
                    onChange={(e) => setLinkSettings({ ...linkSettings, require_login: e.target.checked })}
                    className="mr-2"
                  />
                  <span>Giriş yapma zorunluluğu</span>
                </label>
              </div>
              <div className="mb-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={linkSettings.allow_download}
                    onChange={(e) => setLinkSettings({ ...linkSettings, allow_download: e.target.checked })}
                    className="mr-2"
                  />
                  <span>İndirmeye izin ver</span>
                </label>
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Geçerlilik Tarihi</label>
                <input
                  type="datetime-local"
                  value={linkSettings.expiration || ''}
                  onChange={(e) => setLinkSettings({ ...linkSettings, expiration: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Şifre (Opsiyonel)</label>
                <input
                  type="text"
                  value={linkSettings.password}
                  onChange={(e) => setLinkSettings({ ...linkSettings, password: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Şifre belirleyin"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Maksimum Görüntüleme</label>
                <input
                  type="number"
                  value={linkSettings.max_views || ''}
                  onChange={(e) => setLinkSettings({ ...linkSettings, max_views: e.target.value ? parseInt(e.target.value) : null })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="Sınırsız için boş bırakın"
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowLinkModal(false)}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  İptal
                </button>
                <button
                  onClick={() => {
                    handleGenerateLink();
                    setShowLinkModal(false);
                  }}
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  {shareLink ? 'Güncelle' : 'Oluştur'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Email Modal */}
      {showEmailModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">E-posta ile Paylaş</h3>
              <button
                onClick={() => setShowEmailModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <FaTimes />
              </button>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Alıcılar</label>
                <input
                  type="text"
                  value={emailData.recipients}
                  onChange={(e) => setEmailData({ ...emailData, recipients: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="E-posta adreslerini virgülle ayırın"
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Konu</label>
                <input
                  type="text"
                  value={emailData.subject}
                  onChange={(e) => setEmailData({ ...emailData, subject: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder={`${document?.name} sizinle paylaşıldı`}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Mesaj</label>
                <textarea
                  value={emailData.message}
                  onChange={(e) => setEmailData({ ...emailData, message: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows="4"
                  placeholder="İsteğe bağlı mesaj..."
                />
              </div>
              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowEmailModal(false)}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  İptal
                </button>
                <button
                  onClick={handleSendEmail}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
                >
                  <FaEnvelope className="inline mr-2" />
                  Gönder
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      {/* Share History Modal */}
      {showHistoryModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[80vh] overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">Paylaşım Geçmişi</h3>
              <button
                onClick={() => setShowHistoryModal(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <FaTimes />
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              {shareHistory.length === 0 ? (
                <p className="text-gray-600 text-center py-8">Henüz paylaşım geçmişi yok</p>
              ) : (
                <div className="space-y-3">
                  {shareHistory.map((item) => (
                    <div key={item.id} className="border rounded-lg p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium">
                            {item.action === 'share' ? 'Paylaşıldı' :
                             item.action === 'view' ? 'Görüntülendi' :
                             item.action === 'download' ? 'İndirildi' :
                             item.action === 'revoke' ? 'İptal edildi' : item.action}
                          </p>
                          <p className="text-sm text-gray-600">
                            {item.user_name} • {new Date(item.created_at).toLocaleString('tr-TR')}
                          </p>
                          {item.details && (
                            <p className="text-sm text-gray-500 mt-1">{item.details}</p>
                          )}
                        </div>
                        <div>
                          {item.method === 'link' ? (
                            <FaLink className="text-gray-400" />
                          ) : item.method === 'email' ? (
                            <FaEnvelope className="text-gray-400" />
                          ) : (
                            <FaShare className="text-gray-400" />
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
      )}
    </div>
  );
};
export default DocumentSharePageV2;