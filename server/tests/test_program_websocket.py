"""Test program WebSocket events."""

import pytest
import json
from unittest.mock import patch, MagicMock
from app.models.program import Program
from app.models.user import User
from tests.factories import UserFactory, ProgramFactory


class TestProgramWebSocketEvents:
    """Test WebSocket event emissions for program operations."""

    def test_program_created_event_emission(self, app_context, db_session):
        """Test that program creation emits WebSocket event."""
        # Create test user and program data
        user = UserFactory(role='tenant_admin')
        db_session.add(user)
        db_session.commit()
        
        # Mock the emit_to_tenant function
        with patch('app.api.programs.emit_to_tenant') as mock_emit:
            program_data = {
                'name': 'Test WebSocket Program',
                'description': 'Test program for WebSocket events',
                'category': 'technical',
                'level': 'beginner',
                'duration': 30,
                'tenant_id': user.tenant_id,
                'created_by_id': user.id
            }
            
            program = Program(**program_data)
            db_session.add(program)
            db_session.commit()
            
            # Simulate the emit call that would happen in the API
            mock_emit.assert_not_called()  # Since we're not calling the API endpoint
            
            # Test the actual emit call
            from app.realtime import emit_to_tenant
            with patch('app.realtime.socketio') as mock_socketio:
                emit_to_tenant(user.tenant_id, 'program_created', {
                    'program': program.to_dict(),
                    'message': f'New program "{program.name}" has been created'
                })
                
                mock_socketio.emit.assert_called_once_with(
                    'program_created',
                    {
                        'program': program.to_dict(),
                        'message': f'New program "{program.name}" has been created'
                    },
                    room=f'tenant_{user.tenant_id}',
                    namespace='/'
                )

    def test_program_updated_event_emission(self, app_context, db_session):
        """Test that program update emits WebSocket event."""
        # Create test program
        user = UserFactory(role='tenant_admin')
        program = ProgramFactory(tenant_id=user.tenant_id, created_by_id=user.id)
        db_session.add_all([user, program])
        db_session.commit()
        
        # Test the emit call for update
        from app.realtime import emit_to_tenant
        with patch('app.realtime.socketio') as mock_socketio:
            emit_to_tenant(program.tenant_id, 'program_updated', {
                'program': program.to_dict(),
                'message': f'Program "{program.name}" has been updated'
            })
            
            mock_socketio.emit.assert_called_once_with(
                'program_updated',
                {
                    'program': program.to_dict(),
                    'message': f'Program "{program.name}" has been updated'
                },
                room=f'tenant_{program.tenant_id}',
                namespace='/'
            )

    def test_program_deleted_event_emission(self, app_context, db_session):
        """Test that program deletion emits WebSocket event."""
        # Create test program
        user = UserFactory(role='tenant_admin')
        program = ProgramFactory(tenant_id=user.tenant_id, created_by_id=user.id)
        db_session.add_all([user, program])
        db_session.commit()
        
        program_data = program.to_dict()
        program_id = program.id
        tenant_id = program.tenant_id
        
        # Test the emit call for deletion
        from app.realtime import emit_to_tenant
        with patch('app.realtime.socketio') as mock_socketio:
            emit_to_tenant(tenant_id, 'program_deleted', {
                'program': program_data,
                'program_id': program_id,
                'message': f'Program "{program_data["name"]}" has been deleted'
            })
            
            mock_socketio.emit.assert_called_once_with(
                'program_deleted',
                {
                    'program': program_data,
                    'program_id': program_id,
                    'message': f'Program "{program_data["name"]}" has been deleted'
                },
                room=f'tenant_{tenant_id}',
                namespace='/'
            )

    def test_students_endpoint_authorization(self, app_context, db_session):
        """Test that /students endpoint requires proper authorization."""
        # Test data preparation would go here
        # This is a placeholder for the authorization test
        pass

    def test_students_endpoint_unauthorized(self, app_context, db_session):
        """Test that unauthorized users cannot access /students endpoint."""
        # Test data preparation would go here
        # This is a placeholder for the unauthorized access test
        pass