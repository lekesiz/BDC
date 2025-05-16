import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import io from 'socket.io-client';
import { useAuth } from '../hooks/useAuth';
import { toast } from 'react-toastify';

const SocketContext = createContext();

export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};

export const SocketProvider = ({ children }) => {
  const { user, isAuthenticated } = useAuth();
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const socketRef = useRef(null);

  useEffect(() => {
    // Temporarily disable Socket.IO
    console.log('Socket.IO temporarily disabled');
    return;
    
    if (user && isAuthenticated) {
      // Create socket connection
      const token = localStorage.getItem('access_token');
      const newSocket = io('http://localhost:5001', {
        transports: ['polling'],
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
      });

      socketRef.current = newSocket;

      // Connection handlers
      newSocket.on('connect', () => {
        console.log('Connected to server');
        setConnected(true);
      });

      newSocket.on('disconnect', () => {
        console.log('Disconnected from server');
        setConnected(false);
      });

      newSocket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        setConnected(false);
      });

      // Global event handlers
      newSocket.on('notification', (data) => {
        console.log('Notification received:', data);
        toast.info(data.message);
      });

      newSocket.on('user_joined', (data) => {
        console.log('User joined:', data);
        if (data.users) {
          setOnlineUsers(data.users);
        }
      });

      newSocket.on('user_left', (data) => {
        console.log('User left:', data);
        if (data.users) {
          setOnlineUsers(data.users);
        }
      });

      newSocket.on('message', (data) => {
        console.log('Message received:', data);
        // Handle chat messages
      });

      setSocket(newSocket);

      // Join user room
      newSocket.emit('join_room', { room: `user_${user.id}` });

      // Cleanup on unmount
      return () => {
        if (socketRef.current) {
          socketRef.current.disconnect();
          socketRef.current = null;
        }
      };
    } else {
      // Disconnect if no user
      if (socketRef.current) {
        socketRef.current.disconnect();
        socketRef.current = null;
        setSocket(null);
        setConnected(false);
      }
    }
  }, [user, isAuthenticated]);

  // Emit event helper
  const emit = (event, data, callback) => {
    if (socketRef.current && connected) {
      console.log('Emitting event:', event, data);
      if (callback) {
        socketRef.current.emit(event, data, callback);
      } else {
        socketRef.current.emit(event, data);
      }
    } else {
      console.warn('Socket not connected. Cannot emit event:', event);
    }
  };

  // Subscribe to event helper
  const on = (event, handler) => {
    if (socketRef.current) {
      socketRef.current.on(event, handler);
      return () => {
        if (socketRef.current) {
          socketRef.current.off(event, handler);
        }
      };
    }
    return () => {};
  };

  // Unsubscribe from event helper
  const off = (event, handler) => {
    if (socketRef.current) {
      socketRef.current.off(event, handler);
    }
  };

  // Join a room
  const joinRoom = (room) => {
    emit('join_room', { room });
  };

  // Leave a room
  const leaveRoom = (room) => {
    emit('leave_room', { room });
  };

  // Send a message
  const sendMessage = (room, message) => {
    emit('send_message', { room, message }, (response) => {
      if (!response.success) {
        toast.error(response.error || 'Failed to send message');
      }
    });
  };

  // Mark messages as read
  const markAsRead = (messageIds) => {
    emit('mark_as_read', { message_ids: messageIds });
  };

  const value = {
    socket,
    connected,
    onlineUsers,
    emit,
    on,
    off,
    joinRoom,
    leaveRoom,
    sendMessage,
    markAsRead
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};