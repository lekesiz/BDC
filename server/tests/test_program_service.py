"""Tests for program service."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from app.services.program_service import ProgramService


class TestProgramService:
    """Test the ProgramService class."""
    
    @pytest.fixture
    def app(self):
        """Create a Flask app for testing."""
        app = Flask(__name__)
        app.logger = Mock()
        return app
    
    @patch('app.services.program_service.Program')
    def test_list_programs_no_tenant(self, mock_program):
        """Test listing programs without tenant filter."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [Mock(), Mock()]
        mock_program.query = mock_query
        
        # Setup mock for order_by
        mock_program.created_at = Mock()
        mock_program.created_at.desc.return_value = Mock()
        
        result = ProgramService.list_programs()
        
        mock_query.filter_by.assert_called_with(is_active=True)
        mock_query.order_by.assert_called_once()
        assert len(result) == 2
    
    @patch('app.services.program_service.Program')
    def test_list_programs_with_tenant(self, mock_program):
        """Test listing programs with tenant filter."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter_by.side_effect = [mock_query, mock_query]
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [Mock()]
        mock_program.query = mock_query
        
        # Setup mock for order_by
        mock_program.created_at = Mock()
        mock_program.created_at.desc.return_value = Mock()
        
        result = ProgramService.list_programs(tenant_id=123)
        
        # Check both filter_by calls
        assert mock_query.filter_by.call_count == 2
        calls = mock_query.filter_by.call_args_list
        assert calls[0][1] == {'is_active': True}
        assert calls[1][1] == {'tenant_id': 123}
        assert len(result) == 1
    
    @patch('app.services.program_service.Program')
    def test_get_program(self, mock_program):
        """Test getting a program by ID."""
        mock_program_instance = Mock()
        mock_program.query.get.return_value = mock_program_instance
        
        result = ProgramService.get_program(42)
        
        mock_program.query.get.assert_called_with(42)
        assert result == mock_program_instance
    
    @patch('app.services.program_service.Program')
    def test_get_program_not_found(self, mock_program):
        """Test getting a non-existent program."""
        mock_program.query.get.return_value = None
        
        result = ProgramService.get_program(999)
        
        assert result is None
    
    @patch('app.services.program_service.db')
    @patch('app.services.program_service.Program')
    def test_create_program_basic(self, mock_program, mock_db, app):
        """Test creating a program without real-time events."""
        # Setup mock program instance
        mock_program_instance = Mock()
        mock_program_instance.to_dict.return_value = {'id': 1, 'name': 'Test Program'}
        mock_program.return_value = mock_program_instance
        
        with app.app_context():
            result = ProgramService.create_program(
                name='Test Program',
                tenant_id=1,
                description='Test description'
            )
        
        # Verify program was created with correct arguments
        mock_program.assert_called_with(
            name='Test Program',
            tenant_id=1,
            is_active=True,
            description='Test description'
        )
        mock_db.session.add.assert_called_with(mock_program_instance)
        mock_db.session.commit.assert_called_once()
        assert result == mock_program_instance
    
    @patch('app.services.program_service.emit_to_tenant')
    @patch('app.services.program_service.db')
    @patch('app.services.program_service.Program')
    def test_create_program_with_realtime(self, mock_program, mock_db, mock_emit, app):
        """Test creating a program with real-time events."""
        # Setup mock program instance
        mock_program_instance = Mock()
        mock_program_instance.to_dict.return_value = {'id': 1, 'name': 'Test Program'}
        mock_program.return_value = mock_program_instance
        
        with app.app_context():
            result = ProgramService.create_program(
                name='Test Program',
                tenant_id=1
            )
        
        # Verify real-time event was emitted
        mock_emit.assert_called_once_with(
            1,
            'program_created',
            {'program': {'id': 1, 'name': 'Test Program'}}
        )
    
    @patch('app.services.program_service.emit_to_tenant')
    @patch('app.services.program_service.db')
    @patch('app.services.program_service.Program')
    def test_create_program_realtime_failure(self, mock_program, mock_db, mock_emit, app):
        """Test creating a program when real-time event fails."""
        # Setup mock program instance
        mock_program_instance = Mock()
        mock_program_instance.to_dict.return_value = {'id': 1, 'name': 'Test Program'}
        mock_program.return_value = mock_program_instance
        
        # Mock emit to raise exception
        mock_emit.side_effect = Exception('Socket error')
        
        with app.app_context():
            result = ProgramService.create_program(
                name='Test Program',
                tenant_id=1
            )
        
        # Program should still be created despite emit failure
        mock_db.session.add.assert_called_with(mock_program_instance)
        mock_db.session.commit.assert_called_once()
        app.logger.warning.assert_called_once()
        assert result == mock_program_instance
    
    @patch('app.services.program_service.datetime')
    @patch('app.services.program_service.db')
    def test_update_program_basic(self, mock_db, mock_datetime, app):
        """Test updating a program without real-time events."""
        # Setup mock program
        mock_program = Mock()
        mock_program.name = 'Old Name'
        mock_program.description = 'Old Description'
        mock_program.tenant_id = 1
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        
        with app.app_context():
            result = ProgramService.update_program(
                mock_program,
                name='New Name',
                description='New Description',
                invalid_field='Should be ignored'
            )
        
        assert mock_program.name == 'New Name'
        assert mock_program.description == 'New Description'
        assert mock_program.updated_at == mock_now
        assert not hasattr(mock_program, 'invalid_field')
        mock_db.session.commit.assert_called_once()
        assert result == mock_program
    
    @patch('app.services.program_service.emit_to_tenant')
    @patch('app.services.program_service.datetime')
    @patch('app.services.program_service.db')
    def test_update_program_with_realtime(self, mock_db, mock_datetime, mock_emit, app):
        """Test updating a program with real-time events."""
        # Setup mock program
        mock_program = Mock()
        mock_program.tenant_id = 1
        mock_program.to_dict.return_value = {'id': 1, 'name': 'Updated Program'}
        
        # Mock datetime
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        
        with app.app_context():
            result = ProgramService.update_program(mock_program, name='Updated Name')
        
        # Verify real-time event was emitted
        mock_emit.assert_called_once_with(
            1,
            'program_updated',
            {'program': {'id': 1, 'name': 'Updated Program'}}
        )
    
    @patch('app.services.program_service.db')
    def test_delete_program_basic(self, mock_db, app):
        """Test deleting a program without real-time events."""
        # Setup mock program
        mock_program = Mock()
        mock_program.tenant_id = 1
        mock_program.id = 42
        
        with app.app_context():
            ProgramService.delete_program(mock_program)
        
        mock_db.session.delete.assert_called_with(mock_program)
        mock_db.session.commit.assert_called_once()
    
    @patch('app.services.program_service.emit_to_tenant')
    @patch('app.services.program_service.db')
    def test_delete_program_with_realtime(self, mock_db, mock_emit, app):
        """Test deleting a program with real-time events."""
        # Setup mock program
        mock_program = Mock()
        mock_program.tenant_id = 1
        mock_program.id = 42
        
        with app.app_context():
            ProgramService.delete_program(mock_program)
        
        # Verify real-time event was emitted
        mock_emit.assert_called_once_with(
            1,
            'program_deleted',
            {'program_id': 42}
        )
    
    @patch('app.services.program_service.emit_to_tenant')
    @patch('app.services.program_service.db')
    def test_delete_program_realtime_failure(self, mock_db, mock_emit, app):
        """Test deleting a program when real-time event fails."""
        # Setup mock program
        mock_program = Mock()
        mock_program.tenant_id = 1
        mock_program.id = 42
        
        # Mock emit to raise exception
        mock_emit.side_effect = Exception('Socket error')
        
        with app.app_context():
            ProgramService.delete_program(mock_program)
        
        # Program should still be deleted despite emit failure
        mock_db.session.delete.assert_called_with(mock_program)
        mock_db.session.commit.assert_called_once()
        app.logger.warning.assert_called_once()