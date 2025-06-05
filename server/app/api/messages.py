"""Messages API endpoints."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models.user import User
from app.models.notification import MessageThread, ThreadParticipant, Message, ReadReceipt

from app.utils.logging import logger

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
        
        # Emit WebSocket event for real-time updates
        from app.websocket_notifications import emit_to_thread
        emit_to_thread(thread.id, 'thread_created', {
            'thread': {
                'id': thread.id,
                'title': thread.title,
                'type': thread.thread_type,
                'created_at': thread.created_at.isoformat()
            }
        })
        
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
        
        # Emit WebSocket event for real-time message delivery
        from app.websocket_notifications import emit_to_thread
        emit_to_thread(thread_id, 'new_message', {
            'thread_id': thread_id,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender': {
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",
                    'avatar': user.profile_picture
                },
                'created_at': message.created_at.isoformat()
            }
        })
        
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


@messages_bp.route('/messages/search', methods=['GET'])
@jwt_required()
def search_messages():
    """Search messages with various filters."""
    user_id = get_jwt_identity()
    
    # Get search parameters
    query = request.args.get('q')
    thread_id = request.args.get('thread_id', type=int)
    sender_id = request.args.get('sender_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    has_attachments = request.args.get('has_attachments', type=lambda x: x.lower() == 'true')
    is_unread = request.args.get('is_unread', type=lambda x: x.lower() == 'true')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Parse dates if provided
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
        except:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
        except:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Import search service
    from app.services.message_search_service import message_search_service
    
    # Search messages
    messages, total = message_search_service.search_messages(
        user_id=user_id,
        query=query,
        thread_id=thread_id,
        sender_id=sender_id,
        start_date=start_date,
        end_date=end_date,
        has_attachments=has_attachments,
        is_unread=is_unread,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Format results
    results = []
    for message in messages:
        results.append({
            'id': message.id,
            'thread_id': message.thread_id,
            'content': message.content,
            'sender': {
                'id': message.sender.id,
                'name': f"{message.sender.first_name} {message.sender.last_name}",
                'email': message.sender.email
            } if message.sender else None,
            'attachments': message.attachments,
            'is_edited': message.is_edited,
            'edited_at': message.edited_at.isoformat() if message.edited_at else None,
            'created_at': message.created_at.isoformat()
        })
    
    return jsonify({
        'messages': results,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }), 200


@messages_bp.route('/messages/threads/search', methods=['GET'])
@jwt_required()
def search_threads():
    """Search message threads with various filters."""
    user_id = get_jwt_identity()
    
    # Get search parameters
    query = request.args.get('q')
    participant_ids = request.args.getlist('participant_ids', type=int)
    thread_type = request.args.get('thread_type')
    is_archived = request.args.get('is_archived', type=lambda x: x.lower() == 'true')
    has_unread = request.args.get('has_unread', type=lambda x: x.lower() == 'true')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort_by', 'updated_at')
    sort_order = request.args.get('sort_order', 'desc')
    
    # Parse dates if provided
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
        except:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
        except:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Import search service
    from app.services.message_search_service import message_search_service
    
    # Search threads
    threads, total = message_search_service.search_threads(
        user_id=user_id,
        query=query,
        participant_ids=participant_ids,
        thread_type=thread_type,
        is_archived=is_archived,
        has_unread=has_unread,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Format results
    results = []
    for thread in threads:
        # Get last message
        last_message = Message.query.filter_by(thread_id=thread.id)\
            .order_by(Message.created_at.desc()).first()
        
        # Get unread count for user
        unread_count = 0
        for message in thread.messages:
            if not any(receipt.user_id == user_id for receipt in message.read_receipts):
                unread_count += 1
        
        # Get participants
        participants = []
        for participant in thread.participants:
            if participant.user:
                participants.append({
                    'id': participant.user.id,
                    'name': f"{participant.user.first_name} {participant.user.last_name}",
                    'email': participant.user.email,
                    'role': participant.user.role
                })
        
        results.append({
            'id': thread.id,
            'title': thread.title or thread.subject or 'Untitled Thread',
            'thread_type': thread.thread_type,
            'is_archived': thread.is_archived,
            'participants': participants,
            'last_message': {
                'content': last_message.content,
                'created_at': last_message.created_at.isoformat(),
                'sender': {
                    'id': last_message.sender.id,
                    'name': f"{last_message.sender.first_name} {last_message.sender.last_name}"
                } if last_message.sender else None
            } if last_message else None,
            'unread_count': unread_count,
            'created_at': thread.created_at.isoformat() if thread.created_at else None,
            'updated_at': thread.updated_at.isoformat() if thread.updated_at else None
        })
    
    return jsonify({
        'threads': results,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }), 200


@messages_bp.route('/messages/search/quick', methods=['GET'])
@jwt_required()
def quick_search():
    """Quick search across threads, messages, and users."""
    user_id = get_jwt_identity()
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Import search service
    from app.services.message_search_service import message_search_service
    
    # Get quick search results
    results = message_search_service.get_conversation_search_results(
        user_id=user_id,
        query=query,
        limit=10
    )
    
    return jsonify(results), 200


@messages_bp.route('/messages/search/attachments', methods=['GET'])
@jwt_required()
def search_attachments():
    """Search for messages with attachments."""
    user_id = get_jwt_identity()
    
    # Get search parameters
    filename = request.args.get('filename')
    file_type = request.args.get('file_type')
    thread_id = request.args.get('thread_id', type=int)
    sender_id = request.args.get('sender_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Parse dates if provided
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
        except:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
        except:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Import search service
    from app.services.message_search_service import message_search_service
    
    # Search attachments
    attachments, total = message_search_service.search_attachments(
        user_id=user_id,
        filename=filename,
        file_type=file_type,
        thread_id=thread_id,
        sender_id=sender_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'attachments': attachments,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }), 200


@messages_bp.route('/messages/statistics', methods=['GET'])
@jwt_required()
def get_message_statistics():
    """Get message statistics for the current user."""
    user_id = get_jwt_identity()
    
    # Get date range parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Parse dates if provided
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
        except:
            return jsonify({'error': 'Invalid start_date format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
        except:
            return jsonify({'error': 'Invalid end_date format'}), 400
    
    # Import search service
    from app.services.message_search_service import message_search_service
    
    # Get statistics
    stats = message_search_service.get_message_statistics(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify(stats), 200


@messages_bp.route('/messages/threads/<int:thread_id>/archive', methods=['POST'])
@jwt_required()
def archive_thread(thread_id):
    """Archive a message thread."""
    user_id = get_jwt_identity()
    
    # Check if user is a participant
    participant = ThreadParticipant.query.filter_by(
        thread_id=thread_id,
        user_id=user_id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Thread not found or unauthorized'}), 404
    
    # Archive the thread
    thread = MessageThread.query.get_or_404(thread_id)
    thread.is_archived = True
    thread.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Emit WebSocket event
    from app.websocket_notifications import emit_to_user
    emit_to_user(user_id, 'thread_archived', {
        'thread_id': thread_id,
        'archived_at': datetime.utcnow().isoformat()
    })
    
    return jsonify({
        'message': 'Thread archived successfully',
        'thread_id': thread_id,
        'is_archived': True
    }), 200


@messages_bp.route('/messages/threads/<int:thread_id>/unarchive', methods=['POST'])
@jwt_required()
def unarchive_thread(thread_id):
    """Unarchive a message thread."""
    user_id = get_jwt_identity()
    
    # Check if user is a participant
    participant = ThreadParticipant.query.filter_by(
        thread_id=thread_id,
        user_id=user_id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Thread not found or unauthorized'}), 404
    
    # Unarchive the thread
    thread = MessageThread.query.get_or_404(thread_id)
    thread.is_archived = False
    thread.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Emit WebSocket event
    from app.websocket_notifications import emit_to_user
    emit_to_user(user_id, 'thread_unarchived', {
        'thread_id': thread_id,
        'unarchived_at': datetime.utcnow().isoformat()
    })
    
    return jsonify({
        'message': 'Thread unarchived successfully',
        'thread_id': thread_id,
        'is_archived': False
    }), 200


@messages_bp.route('/messages/threads/archive', methods=['POST'])
@jwt_required()
def bulk_archive_threads():
    """Archive multiple threads at once."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    thread_ids = data.get('thread_ids', [])
    if not thread_ids:
        return jsonify({'error': 'No thread IDs provided'}), 400
    
    # Verify user is participant in all threads
    participant_count = ThreadParticipant.query.filter(
        ThreadParticipant.thread_id.in_(thread_ids),
        ThreadParticipant.user_id == user_id
    ).count()
    
    if participant_count != len(thread_ids):
        return jsonify({'error': 'Unauthorized access to one or more threads'}), 403
    
    # Archive all threads
    MessageThread.query.filter(
        MessageThread.id.in_(thread_ids)
    ).update(
        {'is_archived': True, 'updated_at': datetime.utcnow()},
        synchronize_session=False
    )
    
    db.session.commit()
    
    # Emit WebSocket events
    from app.websocket_notifications import emit_to_user
    emit_to_user(user_id, 'threads_bulk_archived', {
        'thread_ids': thread_ids,
        'archived_at': datetime.utcnow().isoformat()
    })
    
    return jsonify({
        'message': f'{len(thread_ids)} threads archived successfully',
        'thread_ids': thread_ids
    }), 200


@messages_bp.route('/messages/threads/unarchive', methods=['POST'])
@jwt_required()
def bulk_unarchive_threads():
    """Unarchive multiple threads at once."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    thread_ids = data.get('thread_ids', [])
    if not thread_ids:
        return jsonify({'error': 'No thread IDs provided'}), 400
    
    # Verify user is participant in all threads
    participant_count = ThreadParticipant.query.filter(
        ThreadParticipant.thread_id.in_(thread_ids),
        ThreadParticipant.user_id == user_id
    ).count()
    
    if participant_count != len(thread_ids):
        return jsonify({'error': 'Unauthorized access to one or more threads'}), 403
    
    # Unarchive all threads
    MessageThread.query.filter(
        MessageThread.id.in_(thread_ids)
    ).update(
        {'is_archived': False, 'updated_at': datetime.utcnow()},
        synchronize_session=False
    )
    
    db.session.commit()
    
    # Emit WebSocket events
    from app.websocket_notifications import emit_to_user
    emit_to_user(user_id, 'threads_bulk_unarchived', {
        'thread_ids': thread_ids,
        'unarchived_at': datetime.utcnow().isoformat()
    })
    
    return jsonify({
        'message': f'{len(thread_ids)} threads unarchived successfully',
        'thread_ids': thread_ids
    }), 200


@messages_bp.route('/messages/threads/<int:thread_id>/mute', methods=['POST'])
@jwt_required()
def mute_thread(thread_id):
    """Mute notifications for a thread."""
    user_id = get_jwt_identity()
    
    # Get participant record
    participant = ThreadParticipant.query.filter_by(
        thread_id=thread_id,
        user_id=user_id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Thread not found or unauthorized'}), 404
    
    # Mute the thread
    participant.is_muted = True
    db.session.commit()
    
    return jsonify({
        'message': 'Thread muted successfully',
        'thread_id': thread_id,
        'is_muted': True
    }), 200


@messages_bp.route('/messages/threads/<int:thread_id>/unmute', methods=['POST'])
@jwt_required()
def unmute_thread(thread_id):
    """Unmute notifications for a thread."""
    user_id = get_jwt_identity()
    
    # Get participant record
    participant = ThreadParticipant.query.filter_by(
        thread_id=thread_id,
        user_id=user_id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Thread not found or unauthorized'}), 404
    
    # Unmute the thread
    participant.is_muted = False
    db.session.commit()
    
    return jsonify({
        'message': 'Thread unmuted successfully',
        'thread_id': thread_id,
        'is_muted': False
    }), 200