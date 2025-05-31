"""Comprehensive tests for realtime and socketio functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone
import json


class TestRealtime:
    """Test cases for realtime module."""
    
    @patch('app.realtime.socketio')
    def test_emit_notification(self, mock_socketio):
        """Test emitting notification to user."""
        from app.realtime import emit_notification
        
        user_id = 123
        event = 'new_message'
        data = {'message': 'Hello', 'from': 'system'}
        
        emit_notification(user_id, event, data)
        
        mock_socketio.emit.assert_called_once_with(
            event,
            data,
            room=f'user_{user_id}',
            namespace='/'
        )
    
    @patch('app.realtime.socketio')
    def test_emit_to_tenant(self, mock_socketio):
        """Test emitting to all users in tenant."""
        from app.realtime import emit_to_tenant
        
        tenant_id = 100
        event = 'announcement'
        data = {'title': 'System Update', 'message': 'Maintenance scheduled'}
        
        emit_to_tenant(tenant_id, event, data)
        
        mock_socketio.emit.assert_called_once_with(
            event,
            data,
            room=f'tenant_{tenant_id}',
            namespace='/'
        )
    
    @patch('app.realtime.socketio')
    def test_emit_to_user(self, mock_socketio):
        """Test emitting directly to user."""
        from app.realtime import emit_to_user
        
        user_id = 456
        event = 'status_update'
        data = {'status': 'online'}
        
        emit_to_user(user_id, event, data)
        
        mock_socketio.emit.assert_called_once_with(
            event,
            data,
            room=f'user_{user_id}',
            namespace='/'
        )
    
    @patch('app.realtime.socketio')
    def test_broadcast_to_all(self, mock_socketio):
        """Test broadcasting to all connected users."""
        from app.realtime import broadcast_to_all
        
        event = 'system_alert'
        data = {'alert': 'Emergency maintenance', 'severity': 'high'}
        
        broadcast_to_all(event, data)
        
        mock_socketio.emit.assert_called_once_with(
            event,
            data,
            broadcast=True,
            namespace='/'
        )
    
    def test_get_user_room(self):
        """Test user room name generation."""
        from app.realtime import get_user_room
        
        assert get_user_room(123) == 'user_123'
        assert get_user_room(456) == 'user_456'
    
    def test_get_tenant_room(self):
        """Test tenant room name generation."""
        from app.realtime import get_tenant_room
        
        assert get_tenant_room(100) == 'tenant_100'
        assert get_tenant_room(200) == 'tenant_200'
    
    @patch('app.realtime.socketio')
    def test_notify_user_status_change(self, mock_socketio):
        """Test notifying user status change."""
        from app.realtime import notify_user_status_change
        
        user_id = 789
        status = 'active'
        
        notify_user_status_change(user_id, status)
        
        mock_socketio.emit.assert_called_with(
            'user_status_changed',
            {'user_id': user_id, 'status': status},
            room=f'user_{user_id}',
            namespace='/'
        )
    
    @patch('app.realtime.socketio')
    def test_notify_new_notification(self, mock_socketio):
        """Test notifying new notification."""
        from app.realtime import notify_new_notification
        
        user_id = 321
        notification = {
            'id': 1,
            'title': 'New Message',
            'message': 'You have a new message',
            'type': 'info'
        }
        
        notify_new_notification(user_id, notification)
        
        mock_socketio.emit.assert_called_with(
            'new_notification',
            notification,
            room=f'user_{user_id}',
            namespace='/'
        )
    
    @patch('app.realtime.socketio')
    def test_notify_data_update(self, mock_socketio):
        """Test notifying data update."""
        from app.realtime import notify_data_update
        
        tenant_id = 100
        entity_type = 'beneficiary'
        entity_id = 10
        action = 'update'
        
        notify_data_update(tenant_id, entity_type, entity_id, action)
        
        expected_data = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'action': action,
            'timestamp': Mock()  # Any timestamp
        }
        
        mock_socketio.emit.assert_called()
        call_args = mock_socketio.emit.call_args
        assert call_args[0][0] == 'data_update'
        assert call_args[1]['room'] == f'tenant_{tenant_id}'


class TestSocketIOEvents:
    """Test cases for SocketIO event handlers."""
    
    @pytest.fixture
    def mock_socket(self):
        """Create mock socket context."""
        socket = Mock()
        socket.sid = 'test-socket-id'
        return socket
    
    @patch('app.socketio_events.current_user')
    @patch('app.socketio_events.join_room')
    def test_handle_connect(self, mock_join_room, mock_current_user):
        """Test socket connection handler."""
        from app.socketio_events import handle_connect
        
        mock_current_user.id = 123
        mock_current_user.tenant_id = 100
        mock_current_user.is_authenticated = True
        
        with patch('app.socketio_events.emit') as mock_emit:
            handle_connect()
            
            # Should join user and tenant rooms
            assert mock_join_room.call_count == 2
            mock_join_room.assert_any_call('user_123')
            mock_join_room.assert_any_call('tenant_100')
            
            # Should emit connected event
            mock_emit.assert_called_with('connected', {'status': 'connected'})
    
    @patch('app.socketio_events.current_user')
    @patch('app.socketio_events.leave_room')
    def test_handle_disconnect(self, mock_leave_room, mock_current_user):
        """Test socket disconnection handler."""
        from app.socketio_events import handle_disconnect
        
        mock_current_user.id = 123
        mock_current_user.tenant_id = 100
        
        handle_disconnect()
        
        # Should leave rooms
        assert mock_leave_room.call_count == 2
        mock_leave_room.assert_any_call('user_123')
        mock_leave_room.assert_any_call('tenant_100')
    
    @patch('app.socketio_events.current_user')
    @patch('app.socketio_events.emit')
    def test_handle_ping(self, mock_emit, mock_current_user):
        """Test ping handler."""
        from app.socketio_events import handle_ping
        
        data = {'timestamp': 1234567890}
        
        handle_ping(data)
        
        mock_emit.assert_called_with('pong', {
            'timestamp': data['timestamp'],
            'server_time': Mock()  # Any server time
        })
    
    @patch('app.socketio_events.current_user')
    @patch('app.socketio_events.join_room')
    def test_handle_subscribe(self, mock_join_room, mock_current_user):
        """Test channel subscription."""
        from app.socketio_events import handle_subscribe
        
        mock_current_user.id = 123
        
        data = {'channel': 'beneficiary_updates', 'entity_id': 10}
        
        with patch('app.socketio_events.emit') as mock_emit:
            handle_subscribe(data)
            
            mock_join_room.assert_called_with('beneficiary_10')
            mock_emit.assert_called_with('subscribed', {
                'channel': 'beneficiary_updates',
                'entity_id': 10
            })
    
    @patch('app.socketio_events.current_user')
    @patch('app.socketio_events.leave_room')
    def test_handle_unsubscribe(self, mock_leave_room, mock_current_user):
        """Test channel unsubscription."""
        from app.socketio_events import handle_unsubscribe
        
        data = {'channel': 'beneficiary_updates', 'entity_id': 10}
        
        with patch('app.socketio_events.emit') as mock_emit:
            handle_unsubscribe(data)
            
            mock_leave_room.assert_called_with('beneficiary_10')
            mock_emit.assert_called_with('unsubscribed', {
                'channel': 'beneficiary_updates',
                'entity_id': 10
            })
    
    @patch('app.socketio_events.current_user')
    @patch('app.socketio_events.MessageService')
    def test_handle_send_message(self, mock_message_service, mock_current_user):
        """Test sending message via socket."""
        from app.socketio_events import handle_send_message
        
        mock_current_user.id = 123
        
        data = {
            'recipient_id': 456,
            'message': 'Hello there!',
            'type': 'direct'
        }
        
        mock_message = Mock(id=1, content='Hello there!')
        mock_message_service.send_message.return_value = mock_message
        
        with patch('app.socketio_events.emit') as mock_emit:
            handle_send_message(data)
            
            # Should emit to recipient
            mock_emit.assert_any_call(
                'new_message',
                Mock(),
                room='user_456'
            )
            
            # Should acknowledge to sender
            mock_emit.assert_any_call(
                'message_sent',
                {'message_id': 1}
            )
    
    @patch('app.socketio_events.current_user')
    def test_handle_typing_indicator(self, mock_current_user):
        """Test typing indicator."""
        from app.socketio_events import handle_typing_indicator
        
        mock_current_user.id = 123
        mock_current_user.full_name = 'John Doe'
        
        data = {
            'recipient_id': 456,
            'is_typing': True
        }
        
        with patch('app.socketio_events.emit') as mock_emit:
            handle_typing_indicator(data)
            
            mock_emit.assert_called_with(
                'typing_indicator',
                {
                    'user_id': 123,
                    'user_name': 'John Doe',
                    'is_typing': True
                },
                room='user_456'
            )
    
    @patch('app.socketio_events.current_user')
    def test_handle_presence_update(self, mock_current_user):
        """Test presence update."""
        from app.socketio_events import handle_presence_update
        
        mock_current_user.id = 123
        mock_current_user.tenant_id = 100
        
        data = {'status': 'away', 'message': 'In a meeting'}
        
        with patch('app.socketio_events.emit') as mock_emit:
            handle_presence_update(data)
            
            # Should broadcast to tenant
            mock_emit.assert_called_with(
                'presence_update',
                {
                    'user_id': 123,
                    'status': 'away',
                    'message': 'In a meeting'
                },
                room='tenant_100'
            )
    
    @patch('app.socketio_events.current_user')
    def test_handle_notification_read(self, mock_current_user):
        """Test marking notification as read."""
        from app.socketio_events import handle_notification_read
        
        mock_current_user.id = 123
        
        data = {'notification_id': 10}
        
        with patch('app.socketio_events.NotificationService') as mock_service:
            with patch('app.socketio_events.emit') as mock_emit:
                handle_notification_read(data)
                
                mock_service.mark_as_read.assert_called_with(10, 123)
                mock_emit.assert_called_with(
                    'notification_read',
                    {'notification_id': 10}
                )


class TestSocketIOBasic:
    """Test cases for basic SocketIO functionality."""
    
    @patch('app.socketio_basic.emit')
    def test_handle_connect_basic(self, mock_emit):
        """Test basic connection handler."""
        from app.socketio_basic import handle_connect
        
        with patch('app.socketio_basic.request') as mock_request:
            mock_request.sid = 'socket-123'
            
            handle_connect()
            
            mock_emit.assert_called_with('connected', {'data': 'Connected'})
    
    def test_handle_disconnect_basic(self):
        """Test basic disconnection handler."""
        from app.socketio_basic import handle_disconnect
        
        # Should not raise any errors
        handle_disconnect()
        assert True
    
    @patch('app.socketio_basic.join_room')
    @patch('app.socketio_basic.emit')
    def test_handle_join(self, mock_emit, mock_join_room):
        """Test joining a room."""
        from app.socketio_basic import handle_join
        
        data = {'room': 'test-room'}
        
        with patch('app.socketio_basic.request') as mock_request:
            mock_request.sid = 'socket-123'
            
            handle_join(data)
            
            mock_join_room.assert_called_with('test-room')
            mock_emit.assert_called_with(
                'joined',
                {'room': 'test-room'},
                room='test-room'
            )
    
    @patch('app.socketio_basic.leave_room')
    @patch('app.socketio_basic.emit')
    def test_handle_leave(self, mock_emit, mock_leave_room):
        """Test leaving a room."""
        from app.socketio_basic import handle_leave
        
        data = {'room': 'test-room'}
        
        with patch('app.socketio_basic.request') as mock_request:
            mock_request.sid = 'socket-123'
            
            handle_leave(data)
            
            mock_leave_room.assert_called_with('test-room')
            mock_emit.assert_called_with(
                'left',
                {'room': 'test-room'},
                room='test-room'
            )
    
    @patch('app.socketio_basic.emit')
    def test_handle_message(self, mock_emit):
        """Test message handler."""
        from app.socketio_basic import handle_message
        
        data = {'message': 'Hello World', 'room': 'chat-room'}
        
        handle_message(data)
        
        mock_emit.assert_called_with(
            'message',
            data,
            room='chat-room'
        )


class TestWebSocketNotifications:
    """Test cases for WebSocket notifications."""
    
    def test_notification_manager_init(self):
        """Test notification manager initialization."""
        from app.websocket_notifications import NotificationManager
        
        manager = NotificationManager()
        
        assert manager.connections == {}
        assert manager.subscriptions == {}
    
    def test_add_connection(self):
        """Test adding WebSocket connection."""
        from app.websocket_notifications import NotificationManager
        
        manager = NotificationManager()
        
        manager.add_connection('user_123', 'socket_456')
        
        assert 'user_123' in manager.connections
        assert 'socket_456' in manager.connections['user_123']
    
    def test_remove_connection(self):
        """Test removing WebSocket connection."""
        from app.websocket_notifications import NotificationManager
        
        manager = NotificationManager()
        
        manager.add_connection('user_123', 'socket_456')
        manager.remove_connection('user_123', 'socket_456')
        
        assert 'socket_456' not in manager.connections.get('user_123', [])
    
    def test_subscribe_to_channel(self):
        """Test channel subscription."""
        from app.websocket_notifications import NotificationManager
        
        manager = NotificationManager()
        
        manager.subscribe('user_123', 'beneficiary_updates')
        
        assert 'user_123' in manager.subscriptions
        assert 'beneficiary_updates' in manager.subscriptions['user_123']
    
    def test_unsubscribe_from_channel(self):
        """Test channel unsubscription."""
        from app.websocket_notifications import NotificationManager
        
        manager = NotificationManager()
        
        manager.subscribe('user_123', 'beneficiary_updates')
        manager.unsubscribe('user_123', 'beneficiary_updates')
        
        assert 'beneficiary_updates' not in manager.subscriptions.get('user_123', [])
    
    @patch('app.websocket_notifications.socketio')
    def test_broadcast_to_channel(self, mock_socketio):
        """Test broadcasting to channel."""
        from app.websocket_notifications import NotificationManager
        
        manager = NotificationManager()
        
        # Add subscriptions
        manager.subscribe('user_123', 'updates')
        manager.subscribe('user_456', 'updates')
        
        manager.broadcast_to_channel('updates', {'data': 'test'})
        
        # Should emit to all subscribers
        assert mock_socketio.emit.call_count >= 1