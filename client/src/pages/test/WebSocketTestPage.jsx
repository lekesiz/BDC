import React, { useState, useEffect } from 'react';
import { useSocket } from '../../contexts/SocketContext';
import { useAuth } from '../../hooks/useAuth';
const WebSocketTestPage = () => {
  const { connected, emit, on, off } = useSocket();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [room, setRoom] = useState('test_room');
  const [message, setMessage] = useState('');
  const [customEvent, setCustomEvent] = useState('test_event');
  const [customData, setCustomData] = useState('');
  useEffect(() => {
    // Subscribe to messages
    const handleMessage = (data) => {
      setMessages(prev => [...prev, {
        type: 'message',
        data,
        timestamp: new Date().toISOString()
      }]);
    };
    const handleTestEvent = (data) => {
      setMessages(prev => [...prev, {
        type: 'custom',
        event: 'test_event',
        data,
        timestamp: new Date().toISOString()
      }]);
    };
    on('message', handleMessage);
    on('test_event', handleTestEvent);
    // Join test room
    emit('join_room', { room });
    return () => {
      off('message', handleMessage);
      off('test_event', handleTestEvent);
      emit('leave_room', { room });
    };
  }, [room]);
  const sendMessage = () => {
    if (message.trim()) {
      emit('send_message', {
        room,
        message,
        user: user?.username
      });
      setMessage('');
    }
  };
  const sendCustomEvent = () => {
    if (customEvent && customData) {
      emit(customEvent, customData);
    }
  };
  const joinNewRoom = () => {
    emit('leave_room', { room: room });
    const newRoom = `room_${Date.now()}`;
    setRoom(newRoom);
    emit('join_room', { room: newRoom });
  };
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">WebSocket Test Page</h1>
      <div className="mb-6 p-4 bg-gray-100 rounded">
        <p className="font-semibold">
          Connection Status: 
          <span className={connected ? "text-green-600" : "text-red-600"}>
            {connected ? " Connected" : " Disconnected"}
          </span>
        </p>
        <p>Current Room: {room}</p>
        <p>User: {user?.username || 'Unknown'}</p>
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        {/* Send Message */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-4">Send Message</h2>
          <div className="space-y-3">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Enter message"
              className="w-full px-3 py-2 border rounded"
            />
            <button
              onClick={sendMessage}
              disabled={!connected}
              className="w-full bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
            >
              Send Message
            </button>
          </div>
        </div>
        {/* Send Custom Event */}
        <div className="bg-white rounded-lg shadow p-4">
          <h2 className="text-xl font-semibold mb-4">Send Custom Event</h2>
          <div className="space-y-3">
            <input
              type="text"
              value={customEvent}
              onChange={(e) => setCustomEvent(e.target.value)}
              placeholder="Event name"
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="text"
              value={customData}
              onChange={(e) => setCustomData(e.target.value)}
              placeholder="Event data"
              className="w-full px-3 py-2 border rounded"
            />
            <button
              onClick={sendCustomEvent}
              disabled={!connected}
              className="w-full bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 disabled:bg-gray-400"
            >
              Send Event
            </button>
          </div>
        </div>
      </div>
      {/* Room Controls */}
      <div className="mt-6 bg-white rounded-lg shadow p-4">
        <h2 className="text-xl font-semibold mb-4">Room Controls</h2>
        <button
          onClick={joinNewRoom}
          disabled={!connected}
          className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 disabled:bg-gray-400"
        >
          Join New Room
        </button>
      </div>
      {/* Messages */}
      <div className="mt-6 bg-white rounded-lg shadow p-4">
        <h2 className="text-xl font-semibold mb-4">Messages</h2>
        <div className="max-h-96 overflow-y-auto space-y-2">
          {messages.length === 0 ? (
            <p className="text-gray-500">No messages yet...</p>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded">
                <div className="flex justify-between text-xs text-gray-500 mb-1">
                  <span>Type: {msg.type}</span>
                  <span>{new Date(msg.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="text-sm">
                  {msg.type === 'custom' && (
                    <span className="font-medium">Event: {msg.event}</span>
                  )}
                  <pre className="mt-1">{JSON.stringify(msg.data, null, 2)}</pre>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
export default WebSocketTestPage;