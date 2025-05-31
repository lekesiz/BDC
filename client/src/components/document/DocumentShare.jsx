import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { FaEnvelope, FaLink, FaCopy, FaCheck, FaTimes, FaCalendarAlt, FaLock, FaShieldAlt } from 'react-icons/fa';
import axios from 'axios';
import { toast } from 'react-toastify';
import DocumentService from './DocumentService';

/**
 * DocumentShare - Component for sharing documents with other users
 */
const DocumentShare = ({
  documentId,
  initialShares = [],
  onShareComplete,
  onClose,
  className = ''
}) => {
  const [document, setDocument] = useState(null);
  const [shares, setShares] = useState(initialShares);
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [permission, setPermission] = useState('view');
  const [expirationDate, setExpirationDate] = useState('');
  const [publicLink, setPublicLink] = useState('');
  const [publicLinkPermission, setPublicLinkPermission] = useState('view');
  const [publicLinkExpiration, setPublicLinkExpiration] = useState('');
  const [linkCopied, setLinkCopied] = useState(false);
  const [enablePublicLink, setEnablePublicLink] = useState(false);

  // Fetch document details
  useEffect(() => {
    const fetchDocument = async () => {
      try {
        const response = await axios.get(`/api/documents/${documentId}`);
        setDocument(response.data);
        
        // Check if public link exists
        if (response.data.public_link) {
          setPublicLink(response.data.public_link);
          setPublicLinkPermission(response.data.public_link_permission || 'view');
          setPublicLinkExpiration(response.data.public_link_expiration || '');
          setEnablePublicLink(true);
        }
      } catch (error) {
        toast.error('Doküman bilgileri yüklenemedi');
      }
    };
    
    const fetchShares = async () => {
      if (initialShares.length === 0) {
        try {
          const response = await axios.get(`/api/documents/${documentId}/shares`);
          setShares(response.data);
        } catch (error) {
          toast.error('Paylaşım bilgileri yüklenemedi');
        }
      }
    };
    
    fetchDocument();
    fetchShares();
  }, [documentId, initialShares]);

  // Search users
  const searchUsers = async (query) => {
    if (!query || query.length < 2) {
      setSearchResults([]);
      return;
    }
    
    try {
      const response = await axios.get(`/api/users/search?q=${query}`);
      
      // Filter out users who already have access
      const existingUserIds = shares.map(share => share.user_id);
      const filteredResults = response.data.filter(user => 
        !existingUserIds.includes(user.id) && 
        !selectedUsers.some(selectedUser => selectedUser.id === user.id)
      );
      
      setSearchResults(filteredResults);
    } catch (error) {
      console.error('User search failed:', error);
    }
  };

  // Handle search input change
  const handleSearchChange = (e) => {
    const value = e.target.value;
    setSearchTerm(value);
    searchUsers(value);
  };

  // Select a user from search results
  const selectUser = (user) => {
    setSelectedUsers([...selectedUsers, user]);
    setSearchResults(searchResults.filter(u => u.id !== user.id));
    setSearchTerm('');
  };

  // Remove a selected user
  const removeSelectedUser = (userId) => {
    setSelectedUsers(selectedUsers.filter(user => user.id !== userId));
  };

  // Create public link
  const generatePublicLink = async () => {
    setLoading(true);
    
    try {
      const response = await axios.post(`/api/documents/${documentId}/public-link`, {
        permission: publicLinkPermission,
        expiration_date: publicLinkExpiration || null
      });
      
      setPublicLink(response.data.link);
      setEnablePublicLink(true);
      toast.success('Paylaşım linki oluşturuldu');
    } catch (error) {
      toast.error('Link oluşturulurken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Remove public link
  const removePublicLink = async () => {
    setLoading(true);
    
    try {
      await axios.delete(`/api/documents/${documentId}/public-link`);
      setPublicLink('');
      setEnablePublicLink(false);
      toast.success('Paylaşım linki kaldırıldı');
    } catch (error) {
      toast.error('Link kaldırılırken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Copy link to clipboard
  const copyLinkToClipboard = () => {
    if (!publicLink) return;
    
    navigator.clipboard.writeText(publicLink);
    setLinkCopied(true);
    toast.success('Link panoya kopyalandı');
    
    // Reset copied state after 3 seconds
    setTimeout(() => {
      setLinkCopied(false);
    }, 3000);
  };

  // Share with selected users
  const shareWithUsers = async () => {
    if (selectedUsers.length === 0) return;
    
    setLoading(true);
    
    try {
      // Extract user IDs
      const userIds = selectedUsers.map(user => user.id);
      
      // Share document
      await DocumentService.shareDocument(
        documentId,
        userIds,
        permission
      );
      
      // Fetch updated shares
      const response = await axios.get(`/api/documents/${documentId}/shares`);
      setShares(response.data);
      
      // Clear selected users
      setSelectedUsers([]);
      
      // Callback
      if (onShareComplete) {
        onShareComplete(response.data);
      }
      
      toast.success(`Doküman ${userIds.length} kişi ile paylaşıldı`);
    } catch (error) {
      toast.error('Paylaşım sırasında bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Remove an existing share
  const removeShare = async (shareId) => {
    setLoading(true);
    
    try {
      await axios.delete(`/api/documents/shares/${shareId}`);
      
      // Update shares list
      setShares(shares.filter(share => share.id !== shareId));
      
      toast.success('Paylaşım kaldırıldı');
    } catch (error) {
      toast.error('Paylaşım kaldırılırken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  // Update share permissions
  const updateSharePermission = async (shareId, newPermission) => {
    setLoading(true);
    
    try {
      await axios.patch(`/api/documents/shares/${shareId}`, {
        permission: newPermission
      });
      
      // Update shares list
      setShares(shares.map(share => 
        share.id === shareId 
          ? { ...share, permission: newPermission } 
          : share
      ));
      
      toast.success('İzinler güncellendi');
    } catch (error) {
      toast.error('İzinler güncellenirken bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`document-share ${className}`} data-cy="document-share">
      {/* Document info section */}
      {document && (
        <div className="bg-gray-50 p-4 rounded-lg mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-1">{document.name}</h2>
          <p className="text-sm text-gray-500">
            {document.type.toUpperCase()} • {document.size_formatted}
          </p>
        </div>
      )}

      {/* Share with users section */}
      <div className="mb-6">
        <h3 className="text-md font-medium mb-2">Kullanıcılarla Paylaş</h3>
        
        {/* User search */}
        <div className="relative mb-4">
          <div className="flex items-center border rounded-lg p-2">
            {selectedUsers.map(user => (
              <div 
                key={user.id}
                className="flex items-center bg-blue-100 rounded-full px-3 py-1 text-sm mr-2"
                data-cy="selected-user"
              >
                <span className="mr-1">{user.name}</span>
                <button 
                  onClick={() => removeSelectedUser(user.id)}
                  className="text-blue-500"
                  aria-label="Remove user"
                  data-cy="remove-user"
                >
                  <FaTimes size={12} />
                </button>
              </div>
            ))}
            <input
              type="text"
              value={searchTerm}
              onChange={handleSearchChange}
              placeholder="Kullanıcı ara..."
              className="flex-1 outline-none text-sm"
              data-cy="user-search-input"
            />
          </div>
          
          {/* Search results dropdown */}
          {searchResults.length > 0 && (
            <div className="absolute z-10 w-full bg-white shadow-lg rounded-md border mt-1 max-h-48 overflow-y-auto">
              {searchResults.map(user => (
                <div
                  key={user.id}
                  className="p-2 hover:bg-gray-50 cursor-pointer flex items-center"
                  onClick={() => selectUser(user)}
                  data-cy="user-search-result"
                >
                  {user.avatar ? (
                    <img 
                      src={user.avatar} 
                      alt={user.name} 
                      className="w-6 h-6 rounded-full mr-2"
                    />
                  ) : (
                    <div className="w-6 h-6 rounded-full bg-blue-500 text-white flex items-center justify-center mr-2 text-xs">
                      {user.name.charAt(0)}
                    </div>
                  )}
                  <div>
                    <p className="text-sm font-medium">{user.name}</p>
                    <p className="text-xs text-gray-500">{user.email}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Permission and expiration settings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              İzin Seviyesi
            </label>
            <select
              value={permission}
              onChange={(e) => setPermission(e.target.value)}
              className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              data-cy="permission-select"
            >
              <option value="view">Görüntüleme</option>
              <option value="comment">Yorum Yapabilme</option>
              <option value="edit">Düzenleme</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Son Erişim Tarihi (İsteğe Bağlı)
            </label>
            <div className="relative">
              <input
                type="date"
                value={expirationDate}
                onChange={(e) => setExpirationDate(e.target.value)}
                min={new Date().toISOString().split('T')[0]}
                className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 pl-10"
                data-cy="expiration-date"
              />
              <FaCalendarAlt className="absolute left-3 top-3 text-gray-400" />
            </div>
          </div>
        </div>
        
        <button
          onClick={shareWithUsers}
          disabled={selectedUsers.length === 0 || loading}
          className={`w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 
            ${(selectedUsers.length === 0 || loading) ? 'opacity-50 cursor-not-allowed' : ''}`}
          data-cy="share-button"
        >
          <FaEnvelope className="mr-2" />
          {loading ? 'Paylaşılıyor...' : 'Paylaş'}
        </button>
      </div>

      {/* Public link section */}
      <div className="mb-6">
        <h3 className="text-md font-medium mb-2">Paylaşım Linki</h3>
        
        <div className="bg-gray-50 p-4 rounded-lg">
          <div className="flex items-center mb-4">
            <div className="relative inline-block w-12 mr-2 align-middle select-none">
              <input
                type="checkbox"
                checked={enablePublicLink}
                onChange={(e) => setEnablePublicLink(e.target.checked)}
                className="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer"
                id="enable-public-link"
                data-cy="enable-public-link"
              />
              <label
                htmlFor="enable-public-link"
                className="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer"
              ></label>
            </div>
            <label
              htmlFor="enable-public-link"
              className="text-sm font-medium text-gray-700"
            >
              {enablePublicLink ? 'Link paylaşımı aktif' : 'Link paylaşımı devre dışı'}
            </label>
          </div>
          
          {enablePublicLink && (
            <>
              {/* Link settings */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Link İzin Seviyesi
                  </label>
                  <select
                    value={publicLinkPermission}
                    onChange={(e) => setPublicLinkPermission(e.target.value)}
                    className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    data-cy="public-link-permission"
                  >
                    <option value="view">Görüntüleme</option>
                    <option value="comment">Yorum Yapabilme</option>
                    <option value="edit">Düzenleme</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Link Son Erişim Tarihi
                  </label>
                  <div className="relative">
                    <input
                      type="date"
                      value={publicLinkExpiration}
                      onChange={(e) => setPublicLinkExpiration(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                      className="w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 pl-10"
                      data-cy="public-link-expiration"
                    />
                    <FaCalendarAlt className="absolute left-3 top-3 text-gray-400" />
                  </div>
                </div>
              </div>
              
              {publicLink ? (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Paylaşım Linki
                  </label>
                  <div className="flex">
                    <input
                      type="text"
                      value={publicLink}
                      readOnly
                      className="flex-1 border rounded-l-md px-3 py-2 focus:outline-none bg-white"
                      data-cy="public-link"
                    />
                    <button
                      onClick={copyLinkToClipboard}
                      className="bg-gray-100 border-t border-r border-b rounded-r-md px-3 py-2 text-gray-600 hover:bg-gray-200"
                      title="Kopyala"
                      data-cy="copy-link"
                    >
                      {linkCopied ? <FaCheck /> : <FaCopy />}
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={generatePublicLink}
                  disabled={loading}
                  className={`w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 mb-4
                    ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  data-cy="generate-link"
                >
                  <FaLink className="mr-2" />
                  {loading ? 'Oluşturuluyor...' : 'Link Oluştur'}
                </button>
              )}
              
              {publicLink && (
                <div className="flex justify-between items-center">
                  <div className="text-xs text-gray-500 flex items-center">
                    <FaShieldAlt className="mr-1" /> 
                    Link güvenliği: {publicLinkPermission === 'view' ? 'Sadece görüntüleme' : publicLinkPermission}
                    {publicLinkExpiration && (
                      <span className="ml-3 flex items-center">
                        <FaCalendarAlt className="mr-1" />
                        Son erişim: {new Date(publicLinkExpiration).toLocaleDateString('tr-TR')}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={removePublicLink}
                    className="text-red-500 hover:text-red-700 text-sm"
                    data-cy="remove-link"
                  >
                    <FaTimes className="mr-1" />
                    Kaldır
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Current shares list */}
      {shares.length > 0 && (
        <div>
          <h3 className="text-md font-medium mb-2">Mevcut Paylaşımlar</h3>
          <div className="border rounded-lg divide-y">
            {shares.map(share => (
              <div 
                key={share.id}
                className="flex items-center justify-between p-3"
                data-cy="share-item"
              >
                <div className="flex items-center">
                  {share.user_avatar ? (
                    <img 
                      src={share.user_avatar} 
                      alt={share.user_name} 
                      className="w-8 h-8 rounded-full mr-3"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center mr-3">
                      {share.user_name.charAt(0)}
                    </div>
                  )}
                  <div>
                    <p className="text-sm font-medium">{share.user_name}</p>
                    <p className="text-xs text-gray-500">{share.user_email}</p>
                    {share.expiration_date && (
                      <p className="text-xs text-amber-600">
                        <FaCalendarAlt className="inline mr-1" />
                        Son erişim: {new Date(share.expiration_date).toLocaleDateString('tr-TR')}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex items-center">
                  <select
                    value={share.permission}
                    onChange={(e) => updateSharePermission(share.id, e.target.value)}
                    className="mr-2 text-sm border rounded p-1"
                    data-cy="share-permission"
                  >
                    <option value="view">Görüntüleme</option>
                    <option value="comment">Yorum Yapabilme</option>
                    <option value="edit">Düzenleme</option>
                  </select>
                  <button
                    onClick={() => removeShare(share.id)}
                    className="text-red-500 hover:text-red-700"
                    title="Paylaşımı kaldır"
                    data-cy="remove-share"
                  >
                    <FaTimes />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Close button */}
      {onClose && (
        <button
          onClick={onClose}
          className="mt-6 w-full inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          data-cy="close-button"
        >
          Kapat
        </button>
      )}
    </div>
  );
};

DocumentShare.propTypes = {
  /** Document ID to share */
  documentId: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  /** Initial shares to display (optional) */
  initialShares: PropTypes.array,
  /** Callback when sharing is complete */
  onShareComplete: PropTypes.func,
  /** Close button handler */
  onClose: PropTypes.func,
  /** Additional CSS classes */
  className: PropTypes.string
};

export default DocumentShare;