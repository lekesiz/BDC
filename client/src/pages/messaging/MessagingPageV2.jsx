import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaSearch, FaPaperPlane, FaSmile, FaPaperclip, FaVideo, FaPhone, FaEllipsisV, FaCheck, FaCheckDouble, FaTimes, FaPlus, FaUser, FaUsers, FaStar, FaTrash, FaArchive, FaTag } from 'react-icons/fa';
import { toast } from 'react-toastify';

const MessagingPageV2 = () => {
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewConversation, setShowNewConversation] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [groupName, setGroupName] = useState('');
  const [typing, setTyping] = useState(false);
  const [userTyping, setUserTyping] = useState({});
  const [attachments, setAttachments] = useState([]);
  const [showAttachments, setShowAttachments] = useState(false);
  const [filterTag, setFilterTag] = useState('all');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [unreadCounts, setUnreadCounts] = useState({});
  
  const tags = [
    { id: 'all', name: 'Tüm Mesajlar', icon: FaEllipsisV },
    { id: 'unread', name: 'Okunmamış', icon: FaCheckDouble },
    { id: 'starred', name: 'Yıldızlı', icon: FaStar },
    { id: 'archived', name: 'Arşivlenmiş', icon: FaArchive }
  ];

  const emojis = ['😀', '😁', '😂', '😊', '😍', '🤔', '😎', '😔', '😡', '👍', '👎', '❤️', '💔', '🎉', '🔥'];

  useEffect(() => {
    fetchConversations();
    connectWebSocket();
    return () => disconnectWebSocket();
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      fetchMessages(selectedConversation.id);
      markAsRead(selectedConversation.id);
    }
  }, [selectedConversation]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = () => {
    // WebSocket connection for real-time messaging
    const ws = new WebSocket('ws://localhost:8000/ws/messaging');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    window.ws = ws;
  };

  const disconnectWebSocket = () => {
    if (window.ws) {
      window.ws.close();
    }
  };

  const handleWebSocketMessage = (data) => {
    switch (data.type) {
      case 'new_message':
        if (selectedConversation?.id === data.conversation_id) {
          setMessages(prev => [...prev, data.message]);
        }
        updateConversationLastMessage(data.conversation_id, data.message);
        break;
      
      case 'typing':
        setUserTyping(prev => ({ ...prev, [data.user_id]: data.is_typing }));
        break;
      
      case 'read_receipt':
        updateMessageReadStatus(data.message_id);
        break;
      
      case 'online_status':
        setOnlineUsers(data.online_users);
        break;
    }
  };

  const fetchConversations = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/messaging/conversations');
      setConversations(response.data);
      
      // Calculate unread counts
      const counts = {};
      response.data.forEach(conv => {
        counts[conv.id] = conv.unread_count || 0;
      });
      setUnreadCounts(counts);
    } catch (error) {
      toast.error('Konuşmalar yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (conversationId) => {
    try {
      const response = await axios.get(`/api/messaging/conversations/${conversationId}/messages`);
      setMessages(response.data);
    } catch (error) {
      toast.error('Mesajlar yüklenemedi');
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() && attachments.length === 0) return;

    const formData = new FormData();
    formData.append('content', newMessage);
    formData.append('conversation_id', selectedConversation.id);
    
    attachments.forEach((file, index) => {
      formData.append(`attachments[${index}]`, file);
    });

    try {
      const response = await axios.post('/api/messaging/messages', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setMessages([...messages, response.data]);
      setNewMessage('');
      setAttachments([]);
      updateConversationLastMessage(selectedConversation.id, response.data);
      scrollToBottom();
    } catch (error) {
      toast.error('Mesaj gönderilemedi');
    }
  };

  const createConversation = async () => {
    if (selectedUsers.length === 0) return;

    try {
      const data = {
        participants: selectedUsers.map(u => u.id),
        is_group: selectedUsers.length > 1,
        name: groupName || null
      };

      const response = await axios.post('/api/messaging/conversations', data);
      setConversations([response.data, ...conversations]);
      setSelectedConversation(response.data);
      setShowNewConversation(false);
      setSelectedUsers([]);
      setGroupName('');
    } catch (error) {
      toast.error('Konuşma oluşturulamadı');
    }
  };

  const searchUsers = async (term) => {
    if (!term || term.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await axios.get('/api/users/search', { params: { q: term } });
      setSearchResults(response.data);
    } catch (error) {
      console.error('Kullanıcı araması başarısız:', error);
    }
  };

  const markAsRead = async (conversationId) => {
    try {
      await axios.put(`/api/messaging/conversations/${conversationId}/read`);
      setUnreadCounts(prev => ({ ...prev, [conversationId]: 0 }));
    } catch (error) {
      console.error('Okundu işareti başarısız:', error);
    }
  };

  const deleteConversation = async (conversationId) => {
    if (window.confirm('Bu konuşmayı silmek istediğinizden emin misiniz?')) {
      try {
        await axios.delete(`/api/messaging/conversations/${conversationId}`);
        setConversations(conversations.filter(c => c.id !== conversationId));
        if (selectedConversation?.id === conversationId) {
          setSelectedConversation(null);
          setMessages([]);
        }
        toast.success('Konuşma silindi');
      } catch (error) {
        toast.error('Silme işlemi başarısız');
      }
    }
  };

  const archiveConversation = async (conversationId) => {
    try {
      await axios.put(`/api/messaging/conversations/${conversationId}/archive`);
      const conversation = conversations.find(c => c.id === conversationId);
      conversation.is_archived = !conversation.is_archived;
      setConversations([...conversations]);
      toast.success(conversation.is_archived ? 'Arşivlendi' : 'Arşivden çıkarıldı');
    } catch (error) {
      toast.error('İşlem başarısız');
    }
  };

  const starConversation = async (conversationId) => {
    try {
      await axios.put(`/api/messaging/conversations/${conversationId}/star`);
      const conversation = conversations.find(c => c.id === conversationId);
      conversation.is_starred = !conversation.is_starred;
      setConversations([...conversations]);
    } catch (error) {
      console.error('Yıldızlama başarısız:', error);
    }
  };

  const handleTyping = (isTyping) => {
    if (window.ws && selectedConversation) {
      window.ws.send(JSON.stringify({
        type: 'typing',
        conversation_id: selectedConversation.id,
        is_typing: isTyping
      }));
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setAttachments([...attachments, ...files]);
  };

  const removeAttachment = (index) => {
    setAttachments(attachments.filter((_, i) => i !== index));
  };

  const updateConversationLastMessage = (conversationId, message) => {
    setConversations(prevConversations => 
      prevConversations.map(conv => 
        conv.id === conversationId
          ? { ...conv, last_message: message, updated_at: message.created_at }
          : conv
      ).sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    );
  };

  const updateMessageReadStatus = (messageId) => {
    setMessages(prevMessages =>
      prevMessages.map(msg =>
        msg.id === messageId ? { ...msg, is_read: true } : msg
      )
    );
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const filteredConversations = conversations.filter(conv => {
    if (filterTag === 'unread' && !conv.unread_count) return false;
    if (filterTag === 'starred' && !conv.is_starred) return false;
    if (filterTag === 'archived' && !conv.is_archived) return false;
    
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return conv.name?.toLowerCase().includes(searchLower) ||
             conv.participants?.some(p => p.name.toLowerCase().includes(searchLower));
    }
    
    return true;
  });

  const renderMessage = (message, index) => {
    const isOwn = message.sender_id === 'current_user_id'; // Replace with actual user ID
    const showAvatar = index === 0 || messages[index - 1]?.sender_id !== message.sender_id;
    
    return (
      <div key={message.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`}>
        {!isOwn && showAvatar && (
          <img
            src={message.sender_avatar || '/assets/avatar-placeholder.png'}
            alt={message.sender_name}
            className="w-8 h-8 rounded-full mr-3"
          />
        )}
        {!isOwn && !showAvatar && <div className="w-8 mr-3" />}
        
        <div className={`max-w-xs lg:max-w-md ${isOwn ? 'items-end' : 'items-start'}`}>
          {!isOwn && showAvatar && (
            <p className="text-xs text-gray-600 mb-1">{message.sender_name}</p>
          )}
          
          <div className={`rounded-lg px-4 py-2 ${
            isOwn ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
          }`}>
            <p className="text-sm">{message.content}</p>
            
            {message.attachments?.length > 0 && (
              <div className="mt-2 space-y-1">
                {message.attachments.map((attachment, idx) => (
                  <a
                    key={idx}
                    href={attachment.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center text-sm underline"
                  >
                    <FaPaperclip className="mr-1" />
                    {attachment.name}
                  </a>
                ))}
              </div>
            )}
          </div>
          
          <div className="flex items-center mt-1 text-xs text-gray-500">
            <span>{new Date(message.created_at).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}</span>
            {isOwn && (
              <span className="ml-2">
                {message.is_read ? <FaCheckDouble className="text-blue-500" /> : <FaCheck />}
              </span>
            )}
          </div>
        </div>
      </div>
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
    <div className="h-screen bg-gray-50 flex">
      {/* Conversations Sidebar */}
      <div className="w-80 bg-white border-r flex flex-col">
        {/* Header */}
        <div className="p-4 border-b">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold">Mesajlar</h1>
            <button
              onClick={() => setShowNewConversation(true)}
              className="bg-blue-500 text-white p-2 rounded-full hover:bg-blue-600"
            >
              <FaPlus />
            </button>
          </div>
          
          {/* Search */}
          <div className="relative">
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Konuşma ara..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg"
            />
            <FaSearch className="absolute left-3 top-3 text-gray-400" />
          </div>
          
          {/* Filter Tags */}
          <div className="flex space-x-2 mt-3 overflow-x-auto">
            {tags.map(tag => (
              <button
                key={tag.id}
                onClick={() => setFilterTag(tag.id)}
                className={`flex items-center px-3 py-1 rounded-full text-sm whitespace-nowrap ${
                  filterTag === tag.id
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <tag.icon className="mr-1" />
                {tag.name}
              </button>
            ))}
          </div>
        </div>
        
        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto">
          {filteredConversations.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-600">Konuşma bulunamadı</p>
            </div>
          ) : (
            filteredConversations.map(conversation => (
              <div
                key={conversation.id}
                onClick={() => setSelectedConversation(conversation)}
                className={`p-4 hover:bg-gray-50 cursor-pointer border-b ${
                  selectedConversation?.id === conversation.id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex items-start">
                  <div className="relative">
                    <img
                      src={conversation.avatar || '/assets/avatar-placeholder.png'}
                      alt={conversation.name}
                      className="w-12 h-12 rounded-full"
                    />
                    {onlineUsers.includes(conversation.participants?.[0]?.id) && (
                      <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                    )}
                  </div>
                  
                  <div className="ml-3 flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium">{conversation.name}</h3>
                      <span className="text-xs text-gray-500">
                        {new Date(conversation.updated_at).toLocaleDateString('tr-TR')}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 truncate">
                      {conversation.last_message?.content || 'Henüz mesaj yok'}
                    </p>
                    
                    <div className="flex items-center mt-1">
                      {conversation.is_starred && <FaStar className="text-yellow-500 mr-2" />}
                      {unreadCounts[conversation.id] > 0 && (
                        <span className="bg-blue-500 text-white text-xs px-2 py-0.5 rounded-full">
                          {unreadCounts[conversation.id]}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Chat Area */}
      {selectedConversation ? (
        <div className="flex-1 flex flex-col">
          {/* Chat Header */}
          <div className="bg-white border-b px-6 py-4 flex items-center justify-between">
            <div className="flex items-center">
              <img
                src={selectedConversation.avatar || '/assets/avatar-placeholder.png'}
                alt={selectedConversation.name}
                className="w-10 h-10 rounded-full mr-3"
              />
              <div>
                <h2 className="font-semibold">{selectedConversation.name}</h2>
                {Object.values(userTyping).some(t => t) && (
                  <p className="text-sm text-gray-600">yazıyor...</p>
                )}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => starConversation(selectedConversation.id)}
                className={`text-gray-600 hover:text-gray-800 ${
                  selectedConversation.is_starred ? 'text-yellow-500' : ''
                }`}
              >
                <FaStar />
              </button>
              <button className="text-gray-600 hover:text-gray-800">
                <FaPhone />
              </button>
              <button className="text-gray-600 hover:text-gray-800">
                <FaVideo />
              </button>
              <div className="relative">
                <button className="text-gray-600 hover:text-gray-800">
                  <FaEllipsisV />
                </button>
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg hidden">
                  <button
                    onClick={() => archiveConversation(selectedConversation.id)}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-50"
                  >
                    <FaArchive className="inline mr-2" />
                    {selectedConversation.is_archived ? 'Arşivden Çıkar' : 'Arşivle'}
                  </button>
                  <button
                    onClick={() => deleteConversation(selectedConversation.id)}
                    className="block w-full text-left px-4 py-2 hover:bg-gray-50 text-red-600"
                  >
                    <FaTrash className="inline mr-2" />
                    Sil
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
            {messages.map((message, index) => renderMessage(message, index))}
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="bg-white border-t p-4">
            {attachments.length > 0 && (
              <div className="mb-3 flex flex-wrap gap-2">
                {attachments.map((file, index) => (
                  <div key={index} className="bg-gray-100 rounded-lg px-3 py-2 flex items-center">
                    <FaPaperclip className="mr-2 text-gray-600" />
                    <span className="text-sm">{file.name}</span>
                    <button
                      onClick={() => removeAttachment(index)}
                      className="ml-2 text-red-500 hover:text-red-600"
                    >
                      <FaTimes />
                    </button>
                  </div>
                ))}
              </div>
            )}
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-gray-600 hover:text-gray-800"
              >
                <FaPaperclip />
              </button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                onChange={handleFileSelect}
                className="hidden"
              />
              
              <div className="relative">
                <button
                  onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                  className="text-gray-600 hover:text-gray-800"
                >
                  <FaSmile />
                </button>
                
                {showEmojiPicker && (
                  <div className="absolute bottom-10 left-0 bg-white border rounded-lg shadow-lg p-2 grid grid-cols-5 gap-2">
                    {emojis.map(emoji => (
                      <button
                        key={emoji}
                        onClick={() => {
                          setNewMessage(newMessage + emoji);
                          setShowEmojiPicker(false);
                        }}
                        className="text-xl hover:bg-gray-100 p-1 rounded"
                      >
                        {emoji}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              
              <input
                type="text"
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onFocus={() => handleTyping(true)}
                onBlur={() => handleTyping(false)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Mesajınızı yazın..."
                className="flex-1 px-4 py-2 border rounded-lg"
              />
              
              <button
                onClick={sendMessage}
                className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
              >
                <FaPaperPlane />
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 flex items-center justify-center bg-gray-50">
          <div className="text-center">
            <p className="text-xl text-gray-600 mb-4">Bir konuşma seçin</p>
            <button
              onClick={() => setShowNewConversation(true)}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            >
              Yeni Konuşma Başlat
            </button>
          </div>
        </div>
      )}

      {/* New Conversation Modal */}
      {showNewConversation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-md w-full">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">Yeni Konuşma</h3>
              <button
                onClick={() => setShowNewConversation(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <FaTimes />
              </button>
            </div>

            <div className="p-6">
              <div className="mb-4">
                <input
                  type="text"
                  placeholder="Kullanıcı ara..."
                  onChange={(e) => searchUsers(e.target.value)}
                  className="w-full px-4 py-2 border rounded-lg"
                />
              </div>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="mb-4 max-h-48 overflow-y-auto">
                  {searchResults.map(user => (
                    <div
                      key={user.id}
                      onClick={() => {
                        if (!selectedUsers.find(u => u.id === user.id)) {
                          setSelectedUsers([...selectedUsers, user]);
                        }
                      }}
                      className="p-3 hover:bg-gray-50 cursor-pointer flex items-center justify-between"
                    >
                      <div className="flex items-center">
                        <img
                          src={user.avatar || '/assets/avatar-placeholder.png'}
                          alt={user.name}
                          className="w-10 h-10 rounded-full mr-3"
                        />
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

              {/* Selected Users */}
              {selectedUsers.length > 0 && (
                <div className="mb-4">
                  <p className="text-sm font-medium mb-2">Seçilen Kullanıcılar:</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedUsers.map(user => (
                      <span
                        key={user.id}
                        className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm flex items-center"
                      >
                        {user.name}
                        <button
                          onClick={() => setSelectedUsers(selectedUsers.filter(u => u.id !== user.id))}
                          className="ml-2 text-blue-600 hover:text-blue-800"
                        >
                          <FaTimes />
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Group Name */}
              {selectedUsers.length > 1 && (
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Grup Adı</label>
                  <input
                    type="text"
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                    placeholder="Grup adı (opsiyonel)"
                    className="w-full px-4 py-2 border rounded-lg"
                  />
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <button
                  onClick={() => setShowNewConversation(false)}
                  className="px-4 py-2 border rounded hover:bg-gray-50"
                >
                  İptal
                </button>
                <button
                  onClick={createConversation}
                  disabled={selectedUsers.length === 0}
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:opacity-50"
                >
                  Başlat
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessagingPageV2;