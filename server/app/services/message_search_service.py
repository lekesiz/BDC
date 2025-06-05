"""Message search service for advanced message searching."""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models.notification import MessageThread, ThreadParticipant, Message, ReadReceipt
from app.models import User


class MessageSearchService:
    """Service for searching messages and threads."""
    
    @staticmethod
    def search_messages(
        user_id: int,
        query: Optional[str] = None,
        thread_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_attachments: Optional[bool] = None,
        is_unread: Optional[bool] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'created_at',
        sort_order: str = 'desc'
    ) -> Tuple[List[Message], int]:
        """Search messages with various filters.
        
        Args:
            user_id: ID of the user performing the search
            query: Text to search in message content
            thread_id: Filter by specific thread
            sender_id: Filter by sender
            start_date: Filter messages after this date
            end_date: Filter messages before this date
            has_attachments: Filter messages with/without attachments
            is_unread: Filter unread messages
            page: Page number for pagination
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            Tuple of (messages, total_count)
        """
        # Base query - only messages from threads user participates in
        query_obj = db.session.query(Message).join(
            MessageThread, Message.thread_id == MessageThread.id
        ).join(
            ThreadParticipant, MessageThread.id == ThreadParticipant.thread_id
        ).filter(
            ThreadParticipant.user_id == user_id
        )
        
        # Apply filters
        if query:
            query_obj = query_obj.filter(
                func.lower(Message.content).contains(func.lower(query))
            )
        
        if thread_id:
            query_obj = query_obj.filter(Message.thread_id == thread_id)
        
        if sender_id:
            query_obj = query_obj.filter(Message.sender_id == sender_id)
        
        if start_date:
            query_obj = query_obj.filter(Message.created_at >= start_date)
        
        if end_date:
            query_obj = query_obj.filter(Message.created_at <= end_date)
        
        if has_attachments is not None:
            if has_attachments:
                query_obj = query_obj.filter(
                    Message.attachments.isnot(None),
                    Message.attachments != '[]'
                )
            else:
                query_obj = query_obj.filter(
                    or_(
                        Message.attachments.is_(None),
                        Message.attachments == '[]'
                    )
                )
        
        if is_unread is not None:
            # Subquery to check if message has been read by user
            read_subquery = db.session.query(ReadReceipt.message_id).filter(
                ReadReceipt.user_id == user_id
            ).subquery()
            
            if is_unread:
                query_obj = query_obj.filter(
                    Message.id.notin_(read_subquery)
                )
            else:
                query_obj = query_obj.filter(
                    Message.id.in_(read_subquery)
                )
        
        # Apply sorting
        sort_column = getattr(Message, sort_by, Message.created_at)
        if sort_order == 'asc':
            query_obj = query_obj.order_by(asc(sort_column))
        else:
            query_obj = query_obj.order_by(desc(sort_column))
        
        # Get total count
        total_count = query_obj.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        messages = query_obj.options(
            joinedload(Message.sender)
        ).offset(offset).limit(per_page).all()
        
        return messages, total_count
    
    @staticmethod
    def search_threads(
        user_id: int,
        query: Optional[str] = None,
        participant_ids: Optional[List[int]] = None,
        thread_type: Optional[str] = None,
        is_archived: Optional[bool] = None,
        has_unread: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = 'updated_at',
        sort_order: str = 'desc'
    ) -> Tuple[List[MessageThread], int]:
        """Search message threads with various filters.
        
        Args:
            user_id: ID of the user performing the search
            query: Text to search in thread title/subject or message content
            participant_ids: Filter threads with specific participants
            thread_type: Filter by thread type
            is_archived: Filter archived/active threads
            has_unread: Filter threads with unread messages
            start_date: Filter threads updated after this date
            end_date: Filter threads updated before this date
            page: Page number for pagination
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
            
        Returns:
            Tuple of (threads, total_count)
        """
        # Base query - only threads user participates in
        query_obj = db.session.query(MessageThread).join(
            ThreadParticipant, MessageThread.id == ThreadParticipant.thread_id
        ).filter(
            ThreadParticipant.user_id == user_id
        )
        
        # Apply filters
        if query:
            # Search in thread title/subject and message content
            message_subquery = db.session.query(Message.thread_id).filter(
                func.lower(Message.content).contains(func.lower(query))
            ).subquery()
            
            query_obj = query_obj.filter(
                or_(
                    func.lower(MessageThread.title).contains(func.lower(query)),
                    func.lower(MessageThread.subject).contains(func.lower(query)),
                    MessageThread.id.in_(message_subquery)
                )
            )
        
        if participant_ids:
            # Find threads that have all specified participants
            for participant_id in participant_ids:
                participant_subquery = db.session.query(ThreadParticipant.thread_id).filter(
                    ThreadParticipant.user_id == participant_id
                ).subquery()
                query_obj = query_obj.filter(MessageThread.id.in_(participant_subquery))
        
        if thread_type:
            query_obj = query_obj.filter(MessageThread.thread_type == thread_type)
        
        if is_archived is not None:
            query_obj = query_obj.filter(MessageThread.is_archived == is_archived)
        
        if has_unread is not None:
            # Get user's thread participant record
            participant_alias = db.aliased(ThreadParticipant)
            query_obj = query_obj.join(
                participant_alias,
                and_(
                    participant_alias.thread_id == MessageThread.id,
                    participant_alias.user_id == user_id
                )
            )
            
            if has_unread:
                # Thread has messages created after user's last_read_at
                message_subquery = db.session.query(Message.thread_id).filter(
                    or_(
                        participant_alias.last_read_at.is_(None),
                        Message.created_at > participant_alias.last_read_at
                    )
                ).subquery()
                query_obj = query_obj.filter(MessageThread.id.in_(message_subquery))
            else:
                # All messages read
                message_subquery = db.session.query(Message.thread_id).filter(
                    and_(
                        participant_alias.last_read_at.isnot(None),
                        Message.created_at > participant_alias.last_read_at
                    )
                ).subquery()
                query_obj = query_obj.filter(MessageThread.id.notin_(message_subquery))
        
        if start_date:
            query_obj = query_obj.filter(MessageThread.updated_at >= start_date)
        
        if end_date:
            query_obj = query_obj.filter(MessageThread.updated_at <= end_date)
        
        # Apply sorting
        sort_column = getattr(MessageThread, sort_by, MessageThread.updated_at)
        if sort_order == 'asc':
            query_obj = query_obj.order_by(asc(sort_column))
        else:
            query_obj = query_obj.order_by(desc(sort_column))
        
        # Get total count
        total_count = query_obj.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        threads = query_obj.options(
            joinedload(MessageThread.participants).joinedload(ThreadParticipant.user),
            joinedload(MessageThread.messages)
        ).offset(offset).limit(per_page).all()
        
        return threads, total_count
    
    @staticmethod
    def get_conversation_search_results(
        user_id: int,
        query: str,
        limit: int = 10
    ) -> Dict[str, Any]:
        """Get quick search results for conversations.
        
        Args:
            user_id: ID of the user performing the search
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dictionary with search results organized by type
        """
        results = {
            'threads': [],
            'messages': [],
            'users': []
        }
        
        # Search threads
        threads, _ = MessageSearchService.search_threads(
            user_id=user_id,
            query=query,
            page=1,
            per_page=limit
        )
        
        for thread in threads:
            results['threads'].append({
                'id': thread.id,
                'title': thread.title or thread.subject or 'Untitled Thread',
                'type': thread.thread_type,
                'participant_count': len(thread.participants),
                'last_message_at': thread.updated_at.isoformat() if thread.updated_at else None
            })
        
        # Search messages
        messages, _ = MessageSearchService.search_messages(
            user_id=user_id,
            query=query,
            page=1,
            per_page=limit
        )
        
        for message in messages:
            # Get snippet of content around the match
            content = message.content or ''
            snippet = MessageSearchService._get_snippet(content, query, 100)
            
            results['messages'].append({
                'id': message.id,
                'thread_id': message.thread_id,
                'sender': {
                    'id': message.sender.id,
                    'name': f"{message.sender.first_name} {message.sender.last_name}"
                } if message.sender else None,
                'snippet': snippet,
                'created_at': message.created_at.isoformat()
            })
        
        # Search users (for starting new conversations)
        users = User.query.filter(
            and_(
                User.id != user_id,
                or_(
                    func.lower(User.first_name).contains(func.lower(query)),
                    func.lower(User.last_name).contains(func.lower(query)),
                    func.lower(User.email).contains(func.lower(query))
                )
            )
        ).limit(limit).all()
        
        for user in users:
            results['users'].append({
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'role': user.role
            })
        
        return results
    
    @staticmethod
    def get_message_statistics(
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get message statistics for a user.
        
        Args:
            user_id: ID of the user
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with message statistics
        """
        # Base query for user's threads
        thread_ids = db.session.query(ThreadParticipant.thread_id).filter(
            ThreadParticipant.user_id == user_id
        ).subquery()
        
        # Total messages query
        total_query = db.session.query(func.count(Message.id)).filter(
            Message.thread_id.in_(thread_ids)
        )
        
        # Sent messages query
        sent_query = db.session.query(func.count(Message.id)).filter(
            Message.sender_id == user_id
        )
        
        # Unread messages query
        read_message_ids = db.session.query(ReadReceipt.message_id).filter(
            ReadReceipt.user_id == user_id
        ).subquery()
        
        unread_query = db.session.query(func.count(Message.id)).filter(
            and_(
                Message.thread_id.in_(thread_ids),
                Message.sender_id != user_id,
                Message.id.notin_(read_message_ids)
            )
        )
        
        # Apply date filters if provided
        if start_date:
            total_query = total_query.filter(Message.created_at >= start_date)
            sent_query = sent_query.filter(Message.created_at >= start_date)
            unread_query = unread_query.filter(Message.created_at >= start_date)
        
        if end_date:
            total_query = total_query.filter(Message.created_at <= end_date)
            sent_query = sent_query.filter(Message.created_at <= end_date)
            unread_query = unread_query.filter(Message.created_at <= end_date)
        
        # Get counts
        total_messages = total_query.scalar() or 0
        sent_messages = sent_query.scalar() or 0
        unread_messages = unread_query.scalar() or 0
        
        # Get thread statistics
        total_threads = db.session.query(func.count(ThreadParticipant.thread_id)).filter(
            ThreadParticipant.user_id == user_id
        ).scalar() or 0
        
        active_threads = db.session.query(func.count(MessageThread.id)).join(
            ThreadParticipant, MessageThread.id == ThreadParticipant.thread_id
        ).filter(
            and_(
                ThreadParticipant.user_id == user_id,
                MessageThread.is_archived == False
            )
        ).scalar() or 0
        
        archived_threads = total_threads - active_threads
        
        # Get most active conversations
        most_active = db.session.query(
            MessageThread.id,
            MessageThread.title,
            func.count(Message.id).label('message_count')
        ).join(
            ThreadParticipant, MessageThread.id == ThreadParticipant.thread_id
        ).join(
            Message, MessageThread.id == Message.thread_id
        ).filter(
            ThreadParticipant.user_id == user_id
        )
        
        if start_date:
            most_active = most_active.filter(Message.created_at >= start_date)
        if end_date:
            most_active = most_active.filter(Message.created_at <= end_date)
        
        most_active = most_active.group_by(
            MessageThread.id, MessageThread.title
        ).order_by(
            desc('message_count')
        ).limit(5).all()
        
        return {
            'total_messages': total_messages,
            'sent_messages': sent_messages,
            'received_messages': total_messages - sent_messages,
            'unread_messages': unread_messages,
            'total_threads': total_threads,
            'active_threads': active_threads,
            'archived_threads': archived_threads,
            'most_active_conversations': [
                {
                    'thread_id': thread.id,
                    'title': thread.title or 'Untitled Thread',
                    'message_count': thread.message_count
                }
                for thread in most_active
            ]
        }
    
    @staticmethod
    def _get_snippet(content: str, query: str, max_length: int = 100) -> str:
        """Extract a snippet of content around the search query.
        
        Args:
            content: Full content text
            query: Search query
            max_length: Maximum length of snippet
            
        Returns:
            Snippet of content with query highlighted
        """
        if not content or not query:
            return content[:max_length] if content else ''
        
        # Find the position of the query (case-insensitive)
        lower_content = content.lower()
        lower_query = query.lower()
        pos = lower_content.find(lower_query)
        
        if pos == -1:
            # Query not found, return beginning of content
            return content[:max_length] + '...' if len(content) > max_length else content
        
        # Calculate snippet boundaries
        start = max(0, pos - max_length // 2)
        end = min(len(content), pos + len(query) + max_length // 2)
        
        # Extract snippet
        snippet = content[start:end]
        
        # Add ellipsis if needed
        if start > 0:
            snippet = '...' + snippet
        if end < len(content):
            snippet = snippet + '...'
        
        return snippet
    
    @staticmethod
    def search_attachments(
        user_id: int,
        filename: Optional[str] = None,
        file_type: Optional[str] = None,
        thread_id: Optional[int] = None,
        sender_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Search for messages with attachments.
        
        Args:
            user_id: ID of the user performing the search
            filename: Filter by attachment filename
            file_type: Filter by file type (e.g., 'pdf', 'image', 'document')
            thread_id: Filter by specific thread
            sender_id: Filter by sender
            start_date: Filter messages after this date
            end_date: Filter messages before this date
            page: Page number for pagination
            per_page: Items per page
            
        Returns:
            Tuple of (attachments, total_count)
        """
        # Base query for messages with attachments
        query_obj = db.session.query(Message).join(
            MessageThread, Message.thread_id == MessageThread.id
        ).join(
            ThreadParticipant, MessageThread.id == ThreadParticipant.thread_id
        ).filter(
            and_(
                ThreadParticipant.user_id == user_id,
                Message.attachments.isnot(None),
                Message.attachments != '[]'
            )
        )
        
        # Apply filters
        if thread_id:
            query_obj = query_obj.filter(Message.thread_id == thread_id)
        
        if sender_id:
            query_obj = query_obj.filter(Message.sender_id == sender_id)
        
        if start_date:
            query_obj = query_obj.filter(Message.created_at >= start_date)
        
        if end_date:
            query_obj = query_obj.filter(Message.created_at <= end_date)
        
        # Get messages with attachments
        messages = query_obj.all()
        
        # Process attachments
        all_attachments = []
        for message in messages:
            try:
                import json
                attachments = json.loads(message.attachments) if message.attachments else []
                
                for attachment in attachments:
                    # Apply filename filter
                    if filename and filename.lower() not in attachment.get('filename', '').lower():
                        continue
                    
                    # Apply file type filter
                    if file_type:
                        att_filename = attachment.get('filename', '')
                        if file_type == 'image' and not any(att_filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']):
                            continue
                        elif file_type == 'document' and not any(att_filename.lower().endswith(ext) for ext in ['.pdf', '.doc', '.docx', '.txt']):
                            continue
                        elif file_type == 'pdf' and not att_filename.lower().endswith('.pdf'):
                            continue
                    
                    all_attachments.append({
                        'message_id': message.id,
                        'thread_id': message.thread_id,
                        'sender': {
                            'id': message.sender.id,
                            'name': f"{message.sender.first_name} {message.sender.last_name}"
                        } if message.sender else None,
                        'filename': attachment.get('filename'),
                        'size': attachment.get('size'),
                        'url': attachment.get('url'),
                        'uploaded_at': message.created_at.isoformat()
                    })
            except:
                # Skip messages with invalid attachment JSON
                continue
        
        # Apply pagination
        total_count = len(all_attachments)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_attachments = all_attachments[start_idx:end_idx]
        
        return paginated_attachments, total_count


# Create singleton instance
message_search_service = MessageSearchService()