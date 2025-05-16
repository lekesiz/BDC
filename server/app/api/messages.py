"""Messages API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.user import User
from app.models.notification import MessageThread, ThreadParticipant, Message, ReadReceipt

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages/threads', methods=['GET'])
@jwt_required()
def get_message_threads():
    """Get message threads for the current user."""
    user_id = get_jwt_identity()
    
    # Get all threads where user is a participant
    threads = MessageThread.query.join(ThreadParticipant).filter(
        ThreadParticipant.user_id == user_id
    ).order_by(MessageThread.updated_at.desc()).all()
    
    result = []
    for thread in threads:
        # Get last message
        last_message = Message.query.filter_by(thread_id=thread.id)\
            .order_by(Message.created_at.desc()).first()
        
        # Get unread count
        unread_count = Message.query.filter_by(thread_id=thread.id)\
            .filter(~Message.read_receipts.any(user_id=user_id)).count()
        
        # Get other participants
        participants = ThreadParticipant.query.filter(
            ThreadParticipant.thread_id == thread.id,
            ThreadParticipant.user_id != user_id
        ).all()
        
        result.append({
            'id': thread.id,
            'title': thread.title,
            'last_message': {
                'content': last_message.content,
                'created_at': last_message.created_at.isoformat(),
                'sender': {
                    'id': last_message.sender.id,
                    'name': f"{last_message.sender.first_name} {last_message.sender.last_name}"
                }
            } if last_message else None,
            'unread_count': unread_count,
            'participants': [{
                'id': p.user.id,
                'name': f"{p.user.first_name} {p.user.last_name}",
                'avatar': p.user.profile_picture
            } for p in participants],
            'updated_at': thread.updated_at.isoformat()
        })
    
    return jsonify({
        'threads': result,
        'total': len(result)
    }), 200


@messages_bp.route('/messages/threads', methods=['POST'])
@jwt_required()
def create_message_thread():
    """Create a new message thread."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    try:
        # Create thread
        thread = MessageThread(
            title=data.get('title', 'New Conversation'),
            thread_type=data.get('type', 'direct')
        )
        db.session.add(thread)
        db.session.flush()
        
        # Add participants
        participant_ids = data.get('participants', [])
        if user_id not in participant_ids:
            participant_ids.append(user_id)
        
        for pid in participant_ids:
            participant = ThreadParticipant(
                thread_id=thread.id,
                user_id=pid
            )
            db.session.add(participant)
        
        db.session.commit()
        
        return jsonify({
            'id': thread.id,
            'title': thread.title,
            'type': thread.thread_type,
            'message': 'Thread created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/messages/threads/<int:thread_id>/messages', methods=['GET'])
@jwt_required()
def get_thread_messages(thread_id):
    """Get messages in a thread."""
    user_id = get_jwt_identity()
    
    # Check if user is participant
    participant = ThreadParticipant.query.filter_by(
        thread_id=thread_id,
        user_id=user_id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get messages
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    messages = Message.query.filter_by(thread_id=thread_id)\
        .order_by(Message.created_at.desc())\
        .paginate(page=page, per_page=per_page)
    
    result = []
    for message in messages.items:
        # Mark as read
        read_receipt = ReadReceipt.query.filter_by(
            message_id=message.id,
            user_id=user_id
        ).first()
        
        if not read_receipt:
            read_receipt = ReadReceipt(
                message_id=message.id,
                user_id=user_id
            )
            db.session.add(read_receipt)
        
        result.append({
            'id': message.id,
            'content': message.content,
            'sender': {
                'id': message.sender.id,
                'name': f"{message.sender.first_name} {message.sender.last_name}",
                'avatar': message.sender.profile_picture
            },
            'created_at': message.created_at.isoformat(),
            'is_edited': message.is_edited,
            'edited_at': message.edited_at.isoformat() if message.edited_at else None,
            'is_own': message.sender_id == user_id
        })
    
    db.session.commit()
    
    return jsonify({
        'messages': result,
        'page': messages.page,
        'pages': messages.pages,
        'total': messages.total
    }), 200


@messages_bp.route('/messages/threads/<int:thread_id>/messages', methods=['POST'])
@jwt_required()
def send_message(thread_id):
    """Send a message to a thread."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Check if user is participant
    participant = ThreadParticipant.query.filter_by(
        thread_id=thread_id,
        user_id=user_id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        # Create message
        message = Message(
            thread_id=thread_id,
            sender_id=user_id,
            content=data['content']
        )
        db.session.add(message)
        
        # Update thread timestamp
        thread = MessageThread.query.get(thread_id)
        thread.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'id': message.id,
            'content': message.content,
            'sender': {
                'id': message.sender.id,
                'name': f"{message.sender.first_name} {message.sender.last_name}"
            },
            'created_at': message.created_at.isoformat(),
            'message': 'Message sent successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/messages/messages/<int:message_id>', methods=['PUT'])
@jwt_required()
def edit_message(message_id):
    """Edit a message."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    message = Message.query.get_or_404(message_id)
    
    # Check if user is the sender
    if message.sender_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Update message
    message.content = data['content']
    message.is_edited = True
    message.edited_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'id': message.id,
        'content': message.content,
        'is_edited': message.is_edited,
        'edited_at': message.edited_at.isoformat(),
        'message': 'Message updated successfully'
    }), 200


@messages_bp.route('/messages/messages/<int:message_id>', methods=['DELETE'])
@jwt_required()
def delete_message(message_id):
    """Delete a message."""
    user_id = get_jwt_identity()
    
    message = Message.query.get_or_404(message_id)
    
    # Check if user is the sender
    if message.sender_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'message': 'Message deleted successfully'}), 200