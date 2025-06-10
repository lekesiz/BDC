// TODO: i18n - processed
import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import io from 'socket.io-client';
import { useAuth } from '../hooks/useAuth';
import { toast } from 'react-toastify';import { useTranslation } from "react-i18next";
const SocketContext = createContext();
export const useSocket = () => {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};
export const SocketProvider = ({ children }) => {const { t } = useTranslation();
  const { user, isAuthenticated } = useAuth();
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const socketRef = useRef(null);
  useEffect(() => {
    // Temporarily disable Socket.IO connection
    return;
    // Enable Socket.IO connection when user is authenticated
    if (user && isAuthenticated) {
      // Create socket connection
      const token = localStorage.getItem('access_token');
      const newSocket = io('http://localhost:5001', {
        auth: { token },
        query: { token }, // Also pass token as query parameter
        transports: ['polling', 'websocket'],
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
        timeout: 20000
      });
      socketRef.current = newSocket;
      // Connection handlers
      newSocket.on('connect', () => {
        setConnected(true);
      });
      newSocket.on('disconnect', () => {
        setConnected(false);
      });
      newSocket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        setConnected(false);
      });
      // Global event handlers
      newSocket.on('notification', (data) => {
        toast.info(data.message);
      });
      newSocket.on('user_joined', (data) => {
        if (data.users) {
          setOnlineUsers(data.users);
        }
      });
      newSocket.on('user_left', (data) => {
        if (data.users) {
          setOnlineUsers(data.users);
        }
      });
      newSocket.on('message', (data) => {

        // Handle chat messages
      }); // Program real-time events
      newSocket.on('program_created', (data) => {
        toast.success(`New program created: ${data.program?.name}`);
        // Trigger program list refresh
        window.dispatchEvent(new CustomEvent('programCreated', { detail: data.program }));
      });
      newSocket.on('program_updated', (data) => {
        toast.info(`Program updated: ${data.program?.name}`);
        // Trigger program list/detail refresh
        window.dispatchEvent(new CustomEvent('programUpdated', { detail: data.program }));
      });
      newSocket.on('program_deleted', (data) => {
        toast.warning(`Program deleted: ${data.program?.name}`);
        // Trigger program list refresh
        window.dispatchEvent(new CustomEvent('programDeleted', { detail: data.program }));
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
      if (callback) {
        socketRef.current.emit(event, data, callback);
      } else {
        socketRef.current.emit(event, data);
      }
    } else {}
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
    </SocketContext.Provider>);

};