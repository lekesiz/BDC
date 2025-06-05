import React, { useState } from 'react';
import api from '../../lib/api';
import { toast } from 'react-toastify';
const NotificationTestPage = () => {
  const [notification, setNotification] = useState({
    title: 'Test Notification',
    message: 'This is a test notification message',
    type: 'info',
    recipient_id: null,
    data: {}
  });
  const sendNotification = async () => {
    try {
      const response = await api.post('/api/notifications/send', notification);
      toast.success('Notification sent successfully!');
    } catch (error) {
      toast.error('Failed to send notification');
      console.error('Error sending notification:', error);
    }
  };
  const sendGlobalNotification = async () => {
    try {
      const response = await api.post('/api/notifications/broadcast', {
        ...notification,
        broadcast: true
      });
      toast.success('Global notification sent!');
    } catch (error) {
      toast.error('Failed to send global notification');
      console.error('Error broadcasting:', error);
    }
  };
  const handleChange = (e) => {
    const { name, value } = e.target;
    setNotification(prev => ({
      ...prev,
      [name]: value
    }));
  };
  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Notification Test Page</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Send Test Notification</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input
              type="text"
              name="title"
              value={notification.title}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Message</label>
            <textarea
              name="message"
              value={notification.message}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Type</label>
            <select
              name="type"
              value={notification.type}
              onChange={handleChange}
              className="w-full px-3 py-2 border rounded"
            >
              <option value="info">Info</option>
              <option value="success">Success</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Recipient ID (optional)</label>
            <input
              type="number"
              name="recipient_id"
              value={notification.recipient_id || ''}
              onChange={(e) => setNotification(prev => ({
                ...prev,
                recipient_id: e.target.value ? parseInt(e.target.value) : null
              }))}
              placeholder="Leave empty for current user"
              className="w-full px-3 py-2 border rounded"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Additional Data (JSON)</label>
            <textarea
              name="data"
              value={JSON.stringify(notification.data, null, 2)}
              onChange={(e) => {
                try {
                  const data = JSON.parse(e.target.value);
                  setNotification(prev => ({ ...prev, data }));
                } catch (err) {
                  // Invalid JSON, ignore
                }
              }}
              rows={3}
              className="w-full px-3 py-2 border rounded font-mono text-sm"
            />
          </div>
          <div className="flex gap-4">
            <button
              onClick={sendNotification}
              className="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600"
            >
              Send Notification
            </button>
            <button
              onClick={sendGlobalNotification}
              className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600"
            >
              Send Global Notification
            </button>
          </div>
        </div>
      </div>
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Instructions</h2>
        <ol className="list-decimal list-inside space-y-2 text-gray-700">
          <li>Make sure you're logged in to the application</li>
          <li>Look for the notification bell icon in the header</li>
          <li>Send a test notification using the form above</li>
          <li>You should see the notification count update in real-time</li>
          <li>Click the bell icon to see and interact with notifications</li>
          <li>Try sending global notifications to all users</li>
          <li>Open multiple browser tabs to test real-time sync</li>
        </ol>
      </div>
    </div>
  );
};
export default NotificationTestPage;