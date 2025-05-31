"""Integration tests for WebSocket functionality."""

import pytest
import time
import json
from flask_socketio import SocketIOTestClient
from flask_jwt_extended import create_access_token

from app import create_app, db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.notification import MessageThread, ThreadParticipant, Message


@pytest.fixture()
def app():
    """Create and configure a Flask application for testing."""
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret',
        'SECRET_KEY': 'test-secret',
        'CORS_ORIGINS': '*'
    })
    
    with app.app_context():
        db.create_all()
        
        # Create test tenant
        tenant = Tenant(name="Test Tenant")
        db.session.add(tenant)
        
        # Create test users
        admin = User(
            email="admin@test.com",
            password="password",
            first_name="Admin",
            last_name="User",
            role="tenant_admin",
            tenant_id=1
        )
        db.session.add(admin)
        
        trainer = User(
            email="trainer@test.com",
            password="password",
            first_name="Trainer",
            last_name="User",
            role="trainer",
            tenant_id=1
        )
        db.session.add(trainer)
        
        student = User(
            email="student@test.com",
            password="password",
            first_name="Student",
            last_name="User",
            role="student",
            tenant_id=1
        )
        db.session.add(student)
        
        # Create a message thread between trainer and student
        thread = MessageThread(
            title="Test Thread",
            tenant_id=1,
            created_by_id=2  # trainer
        )
        db.session.add(thread)
        
        # Add participants
        trainer_participant = ThreadParticipant(
            thread_id=1,
            user_id=2
        )
        student_participant = ThreadParticipant(
            thread_id=1,
            user_id=3
        )
        db.session.add_all([trainer_participant, student_participant])
        
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.drop_all()


@pytest.fixture()
def socketio_client(app):
    """Create a SocketIO test client."""
    from app.extensions import socketio
    return SocketIOTestClient(app, socketio)


@pytest.fixture()
def admin_token(app):
    """Generate admin token."""
    with app.app_context():
        return create_access_token(identity=1)


@pytest.fixture()
def trainer_token(app):
    """Generate trainer token."""
    with app.app_context():
        return create_access_token(identity=2)


@pytest.fixture()
def student_token(app):
    """Generate student token."""
    with app.app_context():
        return create_access_token(identity=3)


def test_socket_connect_authenticated(socketio_client, trainer_token):
    """Test authenticated connection to SocketIO."""
    socketio_client.connect(headers={'Authorization': f'Bearer {trainer_token}'})
    
    received = socketio_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'connected'
    
    # Disconnect cleanly
    socketio_client.disconnect()


def test_socket_connect_query_param(socketio_client, trainer_token):
    """Test connection with token as query parameter."""
    socketio_client.connect(query_string=f'token={trainer_token}')
    
    received = socketio_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'connected'
    
    # Disconnect cleanly
    socketio_client.disconnect()


def test_socket_connect_anonymous(socketio_client):
    """Test anonymous connection to SocketIO."""
    socketio_client.connect()
    
    received = socketio_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'connected'
    assert 'anonymously' in received[0]['args'][0]['status']
    
    # Disconnect cleanly
    socketio_client.disconnect()


def test_send_message(app, socketio_client, trainer_token, student_token):
    """Test sending and receiving a message."""
    # Connect first client (trainer)
    trainer_client = socketio_client
    trainer_client.connect(query_string=f'token={trainer_token}')
    trainer_client.get_received()  # Clear the connected event
    
    # Connect second client (student)
    from app.extensions import socketio
    student_client = SocketIOTestClient(app, socketio)
    student_client.connect(query_string=f'token={student_token}')
    student_client.get_received()  # Clear the connected event
    
    # Trainer sends a message to the thread
    trainer_client.emit('send_message', {
        'thread_id': 1,
        'content': 'Hello student, how are you?',
        'token': trainer_token
    })
    
    # Wait for message processing
    time.sleep(0.1)
    
    # Check if student received the message
    received = student_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'new_message'
    assert 'Hello student' in received[0]['args'][0]['content']
    
    # Clean up
    trainer_client.disconnect()
    student_client.disconnect()


def test_typing_indicator(app, socketio_client, trainer_token, student_token):
    """Test typing indicator functionality."""
    # Connect first client (trainer)
    trainer_client = socketio_client
    trainer_client.connect(query_string=f'token={trainer_token}')
    trainer_client.get_received()  # Clear the connected event
    
    # Connect second client (student)
    from app.extensions import socketio
    student_client = SocketIOTestClient(app, socketio)
    student_client.connect(query_string=f'token={student_token}')
    student_client.get_received()  # Clear the connected event
    
    # Trainer sends typing indicator
    trainer_client.emit('typing', {
        'thread_id': 1,
        'is_typing': True,
        'token': trainer_token
    })
    
    # Wait for processing
    time.sleep(0.1)
    
    # Check if student received typing indicator
    received = student_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'user_typing'
    assert received[0]['args'][0]['is_typing'] is True
    
    # Clean up
    trainer_client.disconnect()
    student_client.disconnect()


def test_tenant_broadcast(app, socketio_client, admin_token):
    """Test broadcasting to a tenant."""
    from app.socketio_events import broadcast_to_tenant
    
    # Connect client as admin
    admin_client = socketio_client
    admin_client.connect(query_string=f'token={admin_token}')
    admin_client.get_received()  # Clear the connected event
    
    # Send tenant broadcast
    with app.app_context():
        success = broadcast_to_tenant(1, 'tenant_announcement', {'message': 'Important announcement'})
        assert success is True
    
    # Wait for processing
    time.sleep(0.1)
    
    # Check if admin received broadcast
    received = admin_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'tenant_announcement'
    assert 'Important announcement' in received[0]['args'][0]['message']
    
    # Clean up
    admin_client.disconnect()


def test_mark_read(app, socketio_client, student_token):
    """Test marking messages as read."""
    # Connect client as student
    student_client = socketio_client
    student_client.connect(query_string=f'token={student_token}')
    student_client.get_received()  # Clear the connected event
    
    # Create a test message and notification
    with app.app_context():
        # Add a test message
        message = Message(
            thread_id=1,
            sender_id=2,  # trainer
            content="Test message for read status"
        )
        db.session.add(message)
        
        # Add a test notification
        from app.models.notification import Notification
        notification = Notification(
            recipient_id=3,  # student
            sender_id=2,     # trainer
            notification_type='message',
            content='New message notification',
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()
        notification_id = notification.id
    
    # Mark thread as read
    student_client.emit('mark_read', {
        'thread_id': 1,
        'token': student_token
    })
    
    # Wait for processing
    time.sleep(0.1)
    
    # Check response
    received = student_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'thread_read'
    assert received[0]['args'][0]['thread_id'] == 1
    
    # Mark notification as read
    student_client.emit('mark_read', {
        'notification_ids': [notification_id],
        'token': student_token
    })
    
    # Wait for processing
    time.sleep(0.1)
    
    # Check response
    received = student_client.get_received()
    assert len(received) >= 1
    assert received[0]['name'] == 'notifications_read'
    assert notification_id in received[0]['args'][0]['notification_ids']
    
    # Verify notification is marked as read in database
    with app.app_context():
        notification = Notification.query.get(notification_id)
        assert notification.is_read is True
    
    # Clean up
    student_client.disconnect()