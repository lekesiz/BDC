import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Send, 
  Search, 
  Plus, 
  MoreVertical, 
  Paperclip, 
  Image, 
  User, 
  Check, 
  ArrowLeft,
  Clock,
  Users,
  ChevronDown,
  Phone,
  Video
} from 'lucide-react';
import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { useToast } from '@/components/ui/toast';
import { useAuth } from '@/hooks/useAuth';
import { format, formatDistanceToNow } from 'date-fns';
import { tr } from 'date-fns/locale';

/**
 * MessagingPage displays a messaging interface for communicating with other users
 */
const MessagingPage = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { user } = useAuth();
  const messagesEndRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [conversations, setConversations] = useState([]);
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewConversation, setShowNewConversation] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedUsers, setSelectedUsers] = useState([]);
  const [userSearchTerm, setUserSearchTerm] = useState('');
  const [isCreatingConversation, setIsCreatingConversation] = useState(false);
  const [showMobileConversation, setShowMobileConversation] = useState(false);

  // Fetch conversations
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setIsLoading(true);
        const response = await api.get('/api/messages/threads');
        setConversations(response.data.threads || []);
        setFilteredConversations(response.data.threads || []);
      } catch (error) {
        console.error('Error fetching conversations:', error);
        toast({
          title: 'Error',
          description: 'Failed to load conversations',
          type: 'error',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchConversations();
  }, [toast]);

  // Filter conversations based on search term
  useEffect(() => {
    if (!searchTerm.trim()) {
      setFilteredConversations(conversations);
      return;
    }
    
    const filtered = conversations.filter(
      conversation => 
        conversation.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        conversation.participants.some(
          p => p.name.toLowerCase().includes(searchTerm.toLowerCase())
        )
    );
    
    setFilteredConversations(filtered);
  }, [conversations, searchTerm]);

  // Fetch messages for selected conversation
  useEffect(() => {
    const fetchMessages = async () => {
      if (!selectedConversation) return;
      
      try {
        const response = await api.get(`/api/messages/threads/${selectedConversation.id}/messages`);
        setMessages(response.data.messages || []);
        
        // Mark messages as read
        if (selectedConversation.unread_count > 0) {
          await api.post(`/api/conversations/${selectedConversation.id}/mark-read`);
          
          // Update conversation in the list
          setConversations(prev => 
            prev.map(conv => 
              conv.id === selectedConversation.id 
                ? { ...conv, unread_count: 0 } 
                : conv
            )
          );
        }
      } catch (error) {
        console.error('Error fetching messages:', error);
        toast({
          title: 'Error',
          description: 'Failed to load messages',
          type: 'error',
        });
      }
    };
    
    fetchMessages();
  }, [selectedConversation, toast]);

  // Scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Search for users when creating a new conversation
  useEffect(() => {
    const searchUsers = async () => {
      if (!userSearchTerm || userSearchTerm.length < 2) {
        setSearchResults([]);
        return;
      }
      
      try {
        const response = await api.get('/api/users/search', {
          params: { query: userSearchTerm }
        });
        
        // Filter out already selected users
        const filteredResults = response.data.filter(
          user => !selectedUsers.some(selectedUser => selectedUser.id === user.id)
        );
        
        setSearchResults(filteredResults);
      } catch (error) {
        console.error('Error searching users:', error);
      }
    };
    
    const debounceTimeout = setTimeout(searchUsers, 300);
    
    return () => clearTimeout(debounceTimeout);
  }, [userSearchTerm, selectedUsers]);

  // Add user to selected list
  const addUser = (userToAdd) => {
    setSelectedUsers([...selectedUsers, userToAdd]);
    setUserSearchTerm('');
    setSearchResults([]);
  };

  // Remove user from selected list
  const removeUser = (userId) => {
    setSelectedUsers(selectedUsers.filter(u => u.id !== userId));
  };

  // Send a message
  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;
    
    try {
      const response = await api.post(`/api/conversations/${selectedConversation.id}/messages`, {
        content: newMessage
      });
      
      // Add new message to the list
      setMessages([...messages, response.data]);
      
      // Update conversation in the list
      setConversations(prev => {
        const updatedConversations = prev.map(conv => {
          if (conv.id === selectedConversation.id) {
            return {
              ...conv,
              last_message: {
                content: newMessage,
                created_at: new Date().toISOString(),
                sender_id: user.id,
                sender_name: user.name
              },
              updated_at: new Date().toISOString()
            };
          }
          return conv;
        });
        
        // Sort conversations by updated_at
        return [...updatedConversations].sort((a, b) => 
          new Date(b.updated_at) - new Date(a.updated_at)
        );
      });
      
      // Clear the input field
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        title: 'Error',
        description: 'Failed to send message',
        type: 'error',
      });
    }
  };

  // Create new conversation
  const createConversation = async () => {
    if (selectedUsers.length === 0) {
      toast({
        title: 'Error',
        description: 'Please select at least one user',
        type: 'error',
      });
      return;
    }
    
    try {
      setIsCreatingConversation(true);
      
      const response = await api.post('/api/conversations', {
        participant_ids: selectedUsers.map(u => u.id)
      });
      
      // Add new conversation to the list
      setConversations([response.data, ...conversations]);
      
      // Select the new conversation
      setSelectedConversation(response.data);
      
      // Reset state
      setSelectedUsers([]);
      setShowNewConversation(false);
      setShowMobileConversation(true);
      
      toast({
        title: 'Success',
        description: 'Conversation created successfully',
        type: 'success',
      });
    } catch (error) {
      console.error('Error creating conversation:', error);
      toast({
        title: 'Error',
        description: 'Failed to create conversation',
        type: 'error',
      });
    } finally {
      setIsCreatingConversation(false);
    }
  };

  // Handle conversation selection
  const handleSelectConversation = (conversation) => {
    setSelectedConversation(conversation);
    setShowMobileConversation(true);
  };

  // Format the conversation title
  const getConversationTitle = (conversation) => {
    if (conversation.title) return conversation.title;
    
    return conversation.participants
      .filter(p => p.id !== user?.id)
      .map(p => p.name)
      .join(', ');
  };

  // Render conversation list
  const renderConversationList = () => {
    if (showNewConversation) {
      return (
        <div className="h-full flex flex-col">
          <div className="px-4 py-3 border-b flex items-center">
            <button
              className="mr-3 p-1 rounded-full hover:bg-gray-100"
              onClick={() => setShowNewConversation(false)}
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <h2 className="text-lg font-medium">New Conversation</h2>
          </div>
          
          <div className="p-4">
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Add Participants
              </label>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <Input
                  type="text"
                  placeholder="Search users by name or email..."
                  value={userSearchTerm}
                  onChange={(e) => setUserSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              
              {searchResults.length > 0 && (
                <div className="mt-2 border rounded-md overflow-hidden max-h-60 overflow-y-auto">
                  {searchResults.map(userResult => (
                    <div 
                      key={userResult.id}
                      className="p-3 hover:bg-gray-50 cursor-pointer flex items-center justify-between border-b last:border-b-0"
                      onClick={() => addUser(userResult)}
                    >
                      <div className="flex items-center">
                        <div className="w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center mr-2 text-xs">
                          {userResult.name?.charAt(0) || 'U'}
                        </div>
                        <div>
                          <div className="font-medium">{userResult.name}</div>
                          <div className="text-xs text-gray-500">{userResult.email}</div>
                        </div>
                      </div>
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-gray-500"
                      >
                        <Plus className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {selectedUsers.length > 0 && (
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Selected Participants
                </label>
                
                <div className="flex flex-wrap gap-2">
                  {selectedUsers.map(selectedUser => (
                    <div 
                      key={selectedUser.id}
                      className="flex items-center bg-gray-100 rounded-full px-3 py-1"
                    >
                      <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center mr-2 text-xs">
                        {selectedUser.name?.charAt(0) || 'U'}
                      </div>
                      <span className="mr-2">{selectedUser.name}</span>
                      <button
                        className="text-gray-500 hover:text-gray-700"
                        onClick={() => removeUser(selectedUser.id)}
                      >
                        <span className="sr-only">Remove</span>
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <Button
              onClick={createConversation}
              disabled={selectedUsers.length === 0 || isCreatingConversation}
              className="w-full"
            >
              {isCreatingConversation ? 'Creating...' : 'Start Conversation'}
            </Button>
          </div>
        </div>
      );
    }
    
    return (
      <div className="h-full flex flex-col">
        <div className="px-4 py-3 border-b flex justify-between items-center">
          <h2 className="text-lg font-medium">Messages</h2>
          <Button 
            variant="ghost" 
            size="icon"
            onClick={() => setShowNewConversation(true)}
          >
            <Plus className="h-5 w-5" />
          </Button>
        </div>
        
        <div className="p-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
            <Input
              type="text"
              placeholder="Search conversations..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex justify-center items-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredConversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center p-4">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Send className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-1">No conversations</h3>
              <p className="text-gray-500 mb-4">
                Start a new conversation by clicking the plus button.
              </p>
              <Button 
                onClick={() => setShowNewConversation(true)}
                className="flex items-center"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Conversation
              </Button>
            </div>
          ) : (
            <div className="divide-y">
              {filteredConversations.map(conversation => (
                <div
                  key={conversation.id}
                  className={`flex p-3 cursor-pointer hover:bg-gray-50 ${
                    selectedConversation?.id === conversation.id ? 'bg-gray-50' : ''
                  }`}
                  onClick={() => handleSelectConversation(conversation)}
                >
                  <div className="flex-shrink-0 mr-3">
                    {conversation.is_group ? (
                      <div className="w-12 h-12 bg-gray-200 rounded-full flex items-center justify-center text-gray-600">
                        <Users className="w-6 h-6" />
                      </div>
                    ) : (
                      <div className="w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center text-lg">
                        {conversation.participants.find(p => p.id !== user?.id)?.name?.charAt(0) || 'G'}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-baseline">
                      <h3 className={`text-sm font-medium truncate ${conversation.unread_count > 0 ? 'text-gray-900' : 'text-gray-700'}`}>
                        {getConversationTitle(conversation)}
                      </h3>
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(conversation.updated_at), {
                          addSuffix: false,
                          locale: tr
                        })}
                      </span>
                    </div>
                    
                    <div className="flex items-center">
                      <p className={`text-sm truncate mr-2 ${conversation.unread_count > 0 ? 'text-gray-900 font-medium' : 'text-gray-500'}`}>
                        {conversation.last_message?.sender_id === user?.id ? (
                          <span className="text-xs text-gray-500 mr-1">You:</span>
                        ) : (
                          conversation.last_message?.sender_name && (
                            <span className="text-xs text-gray-500 mr-1">{conversation.last_message.sender_name.split(' ')[0]}:</span>
                          )
                        )}
                        {conversation.last_message?.content || 'No messages yet'}
                      </p>
                      
                      {conversation.unread_count > 0 && (
                        <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-medium text-white bg-primary rounded-full">
                          {conversation.unread_count}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render conversation detail
  const renderConversationDetail = () => {
    if (!selectedConversation) {
      return (
        <div className="flex flex-col items-center justify-center h-full text-center p-4 text-gray-500">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <Send className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-1">No conversation selected</h3>
          <p>Select a conversation from the list or start a new one.</p>
        </div>
      );
    }
    
    return (
      <div className="flex flex-col h-full">
        {/* Conversation header */}
        <div className="px-4 py-3 border-b flex items-center justify-between">
          <div className="flex items-center">
            {/* Show back button in mobile view */}
            <div className="md:hidden mr-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setShowMobileConversation(false)}
              >
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="flex items-center">
              <div className="flex-shrink-0 mr-3">
                {selectedConversation.is_group ? (
                  <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-gray-600">
                    <Users className="w-5 h-5" />
                  </div>
                ) : (
                  <div className="w-10 h-10 bg-primary text-white rounded-full flex items-center justify-center">
                    {selectedConversation.participants.find(p => p.id !== user?.id)?.name?.charAt(0) || 'G'}
                  </div>
                )}
              </div>
              
              <div>
                <h3 className="font-medium">
                  {getConversationTitle(selectedConversation)}
                </h3>
                <p className="text-xs text-gray-500">
                  {selectedConversation.is_group 
                    ? `${selectedConversation.participants.length} participants`
                    : 'Online'}
                </p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="icon">
              <Phone className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <Video className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon">
              <MoreVertical className="h-5 w-5" />
            </Button>
          </div>
        </div>
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Send className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-1">No messages yet</h3>
              <p>Start the conversation by sending a message.</p>
            </div>
          ) : (
            <>
              {messages.map((message, index) => {
                const isCurrentUser = message.sender_id === user?.id;
                const showSender = index === 0 || messages[index - 1].sender_id !== message.sender_id;
                
                return (
                  <div 
                    key={message.id}
                    className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[75%] ${showSender ? 'mt-4' : 'mt-1'}`}>
                      {!isCurrentUser && showSender && (
                        <div className="flex items-center mb-1">
                          <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center text-xs mr-2">
                            {message.sender_name?.charAt(0) || 'U'}
                          </div>
                          <span className="text-sm font-medium">{message.sender_name}</span>
                        </div>
                      )}
                      
                      <div
                        className={`rounded-lg p-3 text-sm ${
                          isCurrentUser 
                            ? 'bg-primary text-white rounded-tr-none' 
                            : 'bg-gray-100 text-gray-900 rounded-tl-none'
                        }`}
                      >
                        {message.content}
                      </div>
                      
                      <div className={`text-xs text-gray-500 mt-1 ${isCurrentUser ? 'text-right' : ''}`}>
                        {format(new Date(message.created_at), 'HH:mm')}
                        {isCurrentUser && (
                          <span className="ml-1">
                            <Check className="w-3 h-3 inline text-gray-500" />
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>
        
        {/* Message input */}
        <div className="border-t p-3">
          <div className="flex items-end">
            <Button variant="ghost" size="icon" className="flex-shrink-0 mr-2">
              <Paperclip className="h-5 w-5" />
            </Button>
            
            <div className="flex-1 rounded-lg border border-gray-300 bg-white relative">
              <textarea
                className="block w-full p-3 resize-none focus:outline-none rounded-lg"
                rows={2}
                placeholder="Type a message..."
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
              />
              
              <div className="absolute bottom-2 right-2 flex space-x-1">
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <Image className="h-5 w-5" />
                </Button>
              </div>
            </div>
            
            <Button 
              variant="primary" 
              size="icon" 
              className="ml-2 flex-shrink-0"
              disabled={!newMessage.trim()}
              onClick={sendMessage}
            >
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="container mx-auto py-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Messaging</h1>
      </div>
      
      <Card className="h-[calc(100vh-10rem)]">
        <div className="flex h-full">
          {/* Conversation list - hidden on mobile when a conversation is selected */}
          <div className={`w-full md:w-1/3 border-r 
                           ${showMobileConversation ? 'hidden md:block' : 'block'}`}>
            {renderConversationList()}
          </div>
          
          {/* Conversation detail - shown on mobile only when a conversation is selected */}
          <div className={`w-full md:w-2/3 
                           ${showMobileConversation ? 'block' : 'hidden md:block'}`}>
            {renderConversationDetail()}
          </div>
        </div>
      </Card>
    </div>
  );
};

export default MessagingPage;