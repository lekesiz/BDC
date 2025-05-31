"""
Real-time notifications and events using Socket.IO.

This module provides a centralized way to emit real-time events to clients
using Socket.IO. It's designed to be imported by services and API endpoints
that need to notify clients of changes or events.
"""

from flask import current_app
from app.extensions import socketio

def configure_socketio(app):
    """Configure Socket.IO with the application context."""
    app.socketio = socketio
    app.logger.info("Socket.IO configured for real-time notifications")

def emit_to_user(user_id, event_name, data):
    """
    Emit an event to a specific user.
    
    Args:
        user_id (int): The user's ID
        event_name (str): The name of the event
        data (dict): The data to send with the event
    """
    try:
        room = f'user_{user_id}'
        socketio.emit(event_name, data, room=room)
        current_app.logger.debug(f"Emitted {event_name} to user {user_id}")
    except Exception as e:
        current_app.logger.warning(f"Failed to emit {event_name} to user {user_id}: {e}")

def emit_to_tenant(tenant_id, event_name, data):
    """
    Emit an event to all users in a tenant.
    
    Args:
        tenant_id (int): The tenant's ID
        event_name (str): The name of the event
        data (dict): The data to send with the event
    """
    try:
        room = f'tenant_{tenant_id}'
        socketio.emit(event_name, data, room=room)
        current_app.logger.debug(f"Emitted {event_name} to tenant {tenant_id}")
    except Exception as e:
        current_app.logger.warning(f"Failed to emit {event_name} to tenant {tenant_id}: {e}")

def emit_to_role(role, event_name, data):
    """
    Emit an event to all users with a specific role.
    
    Args:
        role (str): The role name (e.g. 'admin', 'trainer')
        event_name (str): The name of the event
        data (dict): The data to send with the event
    """
    try:
        room = f'role_{role}'
        socketio.emit(event_name, data, room=room)
        current_app.logger.debug(f"Emitted {event_name} to role {role}")
    except Exception as e:
        current_app.logger.warning(f"Failed to emit {event_name} to role {role}: {e}")

def broadcast_event(event_name, data, include_sender=False):
    """
    Broadcast an event to all connected clients.
    
    Args:
        event_name (str): The name of the event
        data (dict): The data to send with the event
        include_sender (bool): Whether to include the sender in the broadcast
    """
    try:
        socketio.emit(event_name, data, broadcast=True, include_self=include_sender)
        current_app.logger.debug(f"Broadcast {event_name} to all clients")
    except Exception as e:
        current_app.logger.warning(f"Failed to broadcast {event_name}: {e}")

# Events related to programs
def program_created(program, tenant_id):
    """Emit event when a program is created."""
    emit_to_tenant(tenant_id, 'program_created', {'program': program.to_dict()})

def program_updated(program):
    """Emit event when a program is updated."""
    emit_to_tenant(program.tenant_id, 'program_updated', {'program': program.to_dict()})

def program_deleted(program_id, tenant_id):
    """Emit event when a program is deleted."""
    emit_to_tenant(tenant_id, 'program_deleted', {'program_id': program_id})

# Events related to modules
def module_created(module, program, tenant_id):
    """Emit event when a module is created."""
    emit_to_tenant(tenant_id, 'program_module_created', {
        'program_id': program.id,
        'module': module.to_dict()
    })

def module_updated(module, program, tenant_id):
    """Emit event when a module is updated."""
    emit_to_tenant(tenant_id, 'program_module_updated', {
        'program_id': program.id,
        'module': module.to_dict()
    })

def module_deleted(module_id, program_id, tenant_id):
    """Emit event when a module is deleted."""
    emit_to_tenant(tenant_id, 'program_module_deleted', {
        'program_id': program_id,
        'module_id': module_id
    })

def modules_reordered(program, modules):
    """Emit event when modules are reordered."""
    emit_to_tenant(program.tenant_id, 'program_modules_reordered', {
        'program_id': program.id,
        'modules': [m.to_dict() for m in modules]
    })

# Events related to enrollments
def enrollment_progress_updated(enrollment, program):
    """Emit event when enrollment progress is updated."""
    emit_to_tenant(program.tenant_id, 'enrollment_progress_updated', {
        'program_id': program.id,
        'enrollment': enrollment.to_dict()
    })

def enrollment_created(enrollment, program):
    """Emit event when an enrollment is created."""
    emit_to_tenant(program.tenant_id, 'enrollment_created', {
        'program_id': program.id,
        'enrollment': enrollment.to_dict()
    })

def enrollment_deleted(enrollment_id, program_id, tenant_id):
    """Emit event when an enrollment is deleted."""
    emit_to_tenant(tenant_id, 'enrollment_deleted', {
        'program_id': program_id,
        'enrollment_id': enrollment_id
    })

# Events related to notifications
def notification_created(notification, user_id):
    """Emit event when a notification is created."""
    emit_to_user(user_id, 'notification_created', {'notification': notification.to_dict()})

def notifications_marked_read(notification_ids, user_id):
    """Emit event when notifications are marked as read."""
    emit_to_user(user_id, 'notifications_read', {'notification_ids': notification_ids})

def notification_count_updated(user_id, count):
    """Emit event when unread notification count changes."""
    emit_to_user(user_id, 'notification_count_updated', {'count': count})