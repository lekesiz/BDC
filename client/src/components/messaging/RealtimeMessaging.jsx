import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';
import { Card } from '../ui/card';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import {
  Send,
  Loader2,
  Users,
  Circle,
  CheckCheck,
  Paperclip,
  Image,
  FileText,
  MoreVertical
} from 'lucide-react';
import io from 'socket.io-client';
const RealtimeMessaging = ({ conversationId, recipientId, groupId = null }) => {
  const { user } = useAuth();
  const { toast } = useToast();
  const [socket, setSocket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [typing, setTyping] = useState(false);
  const [typingUsers, setTypingUsers] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  useEffect(() => {
    // Initialize socket connection
    const socketConnection = io(process.env.REACT_APP_SOCKET_URL || 'http://localhost:5001', {
      auth: {
        token: localStorage.getItem('token')
      }
    });
    setSocket(socketConnection);
    // Join conversation room
    socketConnection.emit('join_conversation', {
      conversationId,
      userId: user.id
    });
    // Socket event listeners
    socketConnection.on('message_received', handleMessageReceived);
    socketConnection.on('user_typing', handleUserTyping);
    socketConnection.on('user_stopped_typing', handleUserStoppedTyping);
    socketConnection.on('users_online', handleUsersOnline);
    socketConnection.on('message_delivered', handleMessageDelivered);
    socketConnection.on('message_read', handleMessageRead);
    socketConnection.on('error', handleSocketError);
    return () => {
      if (socketConnection) {
        socketConnection.emit('leave_conversation', {
          conversationId,
          userId: user.id
        });
        socketConnection.disconnect();
      }
    };
  }, [conversationId, user.id]);
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  const handleMessageReceived = (message) => {
    setMessages(prev => [...prev, message]);
    // Mark message as delivered if not sender
    if (message.sender_id !== user.id && socket) {
      socket.emit('mark_delivered', {
        messageId: message.id,
        userId: user.id
      });
    }
  };
  const handleUserTyping = ({ userId, userName }) => {
    if (userId !== user.id) {
      setTypingUsers(prev => {
        if (!prev.find(u => u.userId === userId)) {
          return [...prev, { userId, userName }];
        }
        return prev;
      });
    }
  };
  const handleUserStoppedTyping = ({ userId }) => {
    setTypingUsers(prev => prev.filter(u => u.userId !== userId));
  };
  const handleUsersOnline = (users) => {
    setOnlineUsers(users);
  };
  const handleMessageDelivered = ({ messageId, userId }) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, delivered_to: [...(msg.delivered_to || []), userId] }
        : msg
    ));
  };
  const handleMessageRead = ({ messageId, userId }) => {
    setMessages(prev => prev.map(msg => 
      msg.id === messageId 
        ? { ...msg, read_by: [...(msg.read_by || []), userId] }
        : msg
    ));
  };
  const handleSocketError = (error) => {
    console.error('Socket error:', error);
    toast({
      title: 'Connection Error',
      description: 'Failed to connect to messaging server',
      variant: 'destructive'
    });
  };
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !socket || sending) return;
    setSending(true);
    const messageData = {
      conversationId,
      recipientId,
      groupId,
      content: newMessage.trim(),
      sender_id: user.id,
      sender_name: user.full_name,
      timestamp: new Date().toISOString()
    };
    try {
      // Emit message through socket
      socket.emit('send_message', messageData);
      // Add message to local state immediately
      setMessages(prev => [...prev, {
        ...messageData,
        id: Date.now(), // Temporary ID
        status: 'sending'
      }]);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        title: 'Error',
        description: 'Failed to send message',
        variant: 'destructive'
      });
    } finally {
      setSending(false);
    }
  };
  const handleTyping = (e) => {
    setNewMessage(e.target.value);
    if (!socket) return;
    // Emit typing event
    if (!typing) {
      setTyping(true);
      socket.emit('start_typing', {
        conversationId,
        userId: user.id,
        userName: user.full_name
      });
    }
    // Clear existing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    // Set new timeout
    typingTimeoutRef.current = setTimeout(() => {
      setTyping(false);
      socket.emit('stop_typing', {
        conversationId,
        userId: user.id
      });
    }, 1000);
  };
  const markMessageAsRead = (messageId) => {
    if (socket) {
      socket.emit('mark_read', {
        messageId,
        userId: user.id
      });
    }
  };
  const getMessageStatus = (message) => {
    if (message.status === 'sending') return 'sending';
    if (message.read_by?.length > 0) return 'read';
    if (message.delivered_to?.length > 0) return 'delivered';
    return 'sent';
  };
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      minute: '2-digit',
      hour12: true 
    });
  };
  const isUserOnline = (userId) => {
    return onlineUsers.includes(userId);
  };
  return (
    <div className="flex flex-col h-full">
      {/* Online Status Bar */}
      <div className="px-4 py-2 border-b bg-gray-50">
        <div className="flex items-center gap-2">
          {onlineUsers.length > 0 && (
            <>
              <Circle className="h-3 w-3 fill-green-500 text-green-500" />
              <span className="text-sm text-gray-600">
                {onlineUsers.length} online
              </span>
            </>
          )}
        </div>
      </div>
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((message, index) => {
          const isOwnMessage = message.sender_id === user.id;
          const showAvatar = index === 0 || 
            messages[index - 1].sender_id !== message.sender_id;
          return (
            <div
              key={message.id || index}
              className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-[70%] ${isOwnMessage ? 'text-right' : 'text-left'}`}>
                {!isOwnMessage && showAvatar && (
                  <p className="text-xs text-gray-500 mb-1">{message.sender_name}</p>
                )}
                <div
                  className={`inline-block px-4 py-2 rounded-lg ${
                    isOwnMessage
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="whitespace-pre-wrap break-words">{message.content}</p>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-400">
                    {formatTime(message.timestamp)}
                  </span>
                  {isOwnMessage && (
                    <span className="text-xs text-gray-400">
                      {getMessageStatus(message) === 'read' && (
                        <CheckCheck className="h-3 w-3 inline text-blue-500" />
                      )}
                      {getMessageStatus(message) === 'delivered' && (
                        <CheckCheck className="h-3 w-3 inline" />
                      )}
                      {getMessageStatus(message) === 'sending' && (
                        <Loader2 className="h-3 w-3 inline animate-spin" />
                      )}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
        {/* Typing Indicator */}
        {typingUsers.length > 0 && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
            </div>
            <span>
              {typingUsers.map(u => u.userName).join(', ')} {typingUsers.length === 1 ? 'is' : 'are'} typing...
            </span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      {/* Message Input */}
      <form onSubmit={handleSendMessage} className="p-4 border-t">
        <div className="flex gap-2">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            className="text-gray-500"
          >
            <Paperclip className="h-4 w-4" />
          </Button>
          <Input
            type="text"
            value={newMessage}
            onChange={handleTyping}
            placeholder="Type a message..."
            className="flex-1"
            disabled={sending}
          />
          <Button
            type="submit"
            disabled={!newMessage.trim() || sending}
          >
            {sending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </form>
    </div>
  );
};
export default RealtimeMessaging;