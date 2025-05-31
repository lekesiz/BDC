"""Unit tests for the refactored Program Service."""

import pytest
from datetime import datetime, date, timezone
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.exc import IntegrityError

from app.services.program_service_refactored import (
    ProgramServiceRefactored,
    ProgramStatus,
    ProgramLevel,
    PaginationResult
)
from app.models.program import Program, ProgramModule, ProgramEnrollment, TrainingSession
from app.exceptions import NotFoundException, ValidationException


class TestProgramServiceRefactored:
    """Test cases for ProgramServiceRefactored."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        session = Mock()
        session.query = Mock()
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.refresh = Mock()
        session.delete = Mock()
        return session
    
    @pytest.fixture
    def mock_realtime_emitter(self):
        """Create a mock realtime emitter."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db_session, mock_realtime_emitter):
        """Create a ProgramServiceRefactored instance with mocked dependencies."""
        return ProgramServiceRefactored(
            db_session=mock_db_session,
            realtime_emitter=mock_realtime_emitter
        )
    
    @pytest.fixture
    def sample_program_data(self):
        """Sample program data for testing."""
        return {
            'name': 'Test Program',
            'tenant_id': 1,
            'description': 'A test program',
            'code': 'TEST001',
            'duration': 30,
            'level': 'beginner',
            'category': 'technical',
            'prerequisites': 'None',
            'minimum_attendance': 80.0,
            'passing_score': 70.0,
            'status': 'draft',
            'is_active': True,
            'start_date': date(2024, 1, 1),
            'end_date': date(2024, 2, 1),
            'max_participants': 20,
            'created_by_id': 1
        }
    
    @pytest.fixture
    def mock_program(self, sample_program_data):
        """Create a mock Program object."""
        program = Mock()
        program.id = 1
        program.name = sample_program_data['name']
        program.tenant_id = sample_program_data['tenant_id']
        program.description = sample_program_data['description']
        program.code = sample_program_data['code']
        program.duration = sample_program_data['duration']
        program.level = sample_program_data['level']
        program.category = sample_program_data['category']
        program.prerequisites = sample_program_data['prerequisites']
        program.minimum_attendance = sample_program_data['minimum_attendance']
        program.passing_score = sample_program_data['passing_score']
        program.status = sample_program_data['status']
        program.is_active = sample_program_data['is_active']
        program.start_date = sample_program_data['start_date']
        program.end_date = sample_program_data['end_date']
        program.max_participants = sample_program_data['max_participants']
        program.created_at = datetime.now(timezone.utc)
        program.updated_at = datetime.now(timezone.utc)
        program.enrollments = []
        program.modules = []
        program.sessions = []
        
        # Mock to_dict method
        program.to_dict.return_value = {
            'id': program.id,
            'name': program.name,
            'description': program.description,
            'code': program.code,
            'duration': program.duration,
            'duration_weeks': round(program.duration / 7.0, 2),
            'level': program.level,
            'category': program.category,
            'prerequisites': program.prerequisites,
            'minimum_attendance': program.minimum_attendance,
            'passing_score': program.passing_score,
            'status': program.status,
            'is_active': program.is_active,
            'start_date': program.start_date.isoformat() if hasattr(program.start_date, 'isoformat') else str(program.start_date),
            'end_date': program.end_date.isoformat() if hasattr(program.end_date, 'isoformat') else str(program.end_date),
            'max_participants': program.max_participants,
            'enrolled_count': len(program.enrollments),
            'module_count': len(program.modules),
            'session_count': len(program.sessions),
            'created_at': program.created_at.isoformat() if program.created_at else None,
            'updated_at': program.updated_at.isoformat() if program.updated_at else None
        }
        
        return program
    
    # Test create_program method
    
    def test_create_program_success(self, service, mock_db_session, sample_program_data, mock_realtime_emitter):
        """Test successful program creation."""
        # Arrange
        mock_db_session.refresh.side_effect = lambda x: setattr(x, 'id', 1)
        
        # Act
        with patch('app.models.program.Program') as MockProgram:
            mock_instance = Mock()
            mock_instance.id = 1
            mock_instance.tenant_id = sample_program_data['tenant_id']
            mock_instance.enrollments = []
            mock_instance.modules = []
            mock_instance.sessions = []
            mock_instance.created_at = datetime.utcnow()
            mock_instance.updated_at = datetime.utcnow()
            
            # Mock to_dict to return a complete response
            mock_to_dict_result = {
                'id': 1,
                'name': sample_program_data['name'],
                'description': sample_program_data['description'],
                'code': sample_program_data['code'],
                'duration': sample_program_data['duration'],
                'duration_weeks': round(sample_program_data['duration'] / 7.0, 2),
                'level': sample_program_data['level'],
                'category': sample_program_data['category'],
                'prerequisites': sample_program_data['prerequisites'],
                'minimum_attendance': sample_program_data['minimum_attendance'],
                'passing_score': sample_program_data['passing_score'],
                'status': sample_program_data['status'],
                'is_active': sample_program_data['is_active'],
                'start_date': sample_program_data['start_date'].isoformat(),
                'end_date': sample_program_data['end_date'].isoformat(),
                'max_participants': sample_program_data['max_participants'],
                'enrolled_count': 0,
                'module_count': 0,
                'session_count': 0,
                'created_at': mock_instance.created_at.isoformat(),
                'updated_at': mock_instance.updated_at.isoformat()
            }
            mock_instance.to_dict.return_value = mock_to_dict_result
            MockProgram.return_value = mock_instance
            
            result = service.create_program(sample_program_data)
        
        # Assert
        assert result['id'] == 1
        assert result['name'] == sample_program_data['name']
        assert result['duration_weeks'] == round(sample_program_data['duration'] / 7.0, 2)
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()
        # Check that realtime emitter was called with correct tenant and event
        mock_realtime_emitter.assert_called_once()
        call_args = mock_realtime_emitter.call_args
        assert call_args[0][0] == sample_program_data['tenant_id']
        assert call_args[0][1] == 'program_created'
        # Check that program data is included (without checking exact timestamps)
        assert 'program' in call_args[0][2]
        assert call_args[0][2]['program']['name'] == sample_program_data['name']
    
    def test_create_program_missing_name(self, service):
        """Test program creation with missing name."""
        # Arrange
        program_data = {'tenant_id': 1}
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.create_program(program_data)
        assert "Program name is required" in str(exc_info.value)
    
    def test_create_program_missing_tenant_id(self, service):
        """Test program creation with missing tenant ID."""
        # Arrange
        program_data = {'name': 'Test Program'}
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.create_program(program_data)
        assert "Tenant ID is required" in str(exc_info.value)
    
    def test_create_program_invalid_status(self, service):
        """Test program creation with invalid status."""
        # Arrange
        program_data = {
            'name': 'Test Program',
            'tenant_id': 1,
            'status': 'invalid_status'
        }
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.create_program(program_data)
        assert "Invalid status" in str(exc_info.value)
    
    def test_create_program_invalid_level(self, service):
        """Test program creation with invalid level."""
        # Arrange
        program_data = {
            'name': 'Test Program',
            'tenant_id': 1,
            'level': 'invalid_level'
        }
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.create_program(program_data)
        assert "Invalid level" in str(exc_info.value)
    
    def test_create_program_invalid_minimum_attendance(self, service):
        """Test program creation with invalid minimum attendance."""
        # Arrange
        program_data = {
            'name': 'Test Program',
            'tenant_id': 1,
            'minimum_attendance': 150.0
        }
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.create_program(program_data)
        assert "Minimum attendance must be between 0 and 100" in str(exc_info.value)
    
    def test_create_program_duplicate_code(self, service, mock_db_session, sample_program_data):
        """Test program creation with duplicate code."""
        # Arrange
        mock_db_session.commit.side_effect = IntegrityError(
            "statement", "params", "UNIQUE constraint failed: programs.code"
        )
        
        # Act & Assert
        with patch('app.models.program.Program'):
            with pytest.raises(ValidationException) as exc_info:
                service.create_program(sample_program_data)
            assert "Program with this code already exists" in str(exc_info.value)
            mock_db_session.rollback.assert_called()
    
    def test_create_program_realtime_emitter_failure(self, service, mock_db_session, sample_program_data, mock_realtime_emitter):
        """Test program creation when realtime emitter fails."""
        # Arrange
        mock_realtime_emitter.side_effect = Exception("Emitter error")
        mock_db_session.refresh.side_effect = lambda x: setattr(x, 'id', 1)
        
        # Act
        with patch('app.models.program.Program') as MockProgram:
            mock_instance = Mock()
            mock_instance.id = 1
            mock_instance.tenant_id = sample_program_data['tenant_id']
            mock_instance.to_dict.return_value = {'id': 1, **sample_program_data}
            MockProgram.return_value = mock_instance
            
            # Should not raise exception even if emitter fails
            result = service.create_program(sample_program_data)
        
        # Assert
        assert result['id'] == 1
        mock_db_session.commit.assert_called_once()
    
    # Test get_program method
    
    def test_get_program_success(self, service, mock_db_session, mock_program):
        """Test successful program retrieval."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.get_program(1)
        
        # Assert
        assert result is not None
        assert result['id'] == 1
        assert result['name'] == mock_program.name
        mock_db_session.query.assert_called_once_with(Program)
        mock_query.filter_by.assert_called_once_with(id=1)
    
    def test_get_program_not_found(self, service, mock_db_session):
        """Test program retrieval when not found."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.get_program(999)
        
        # Assert
        assert result is None
    
    # Test update_program method
    
    def test_update_program_success(self, service, mock_db_session, mock_program, mock_realtime_emitter):
        """Test successful program update."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        update_data = {
            'name': 'Updated Program',
            'description': 'Updated description',
            'status': 'active'
        }
        
        # Act
        result = service.update_program(1, update_data)
        
        # Assert
        assert result is not None
        assert mock_program.name == 'Updated Program'
        assert mock_program.description == 'Updated description'
        assert mock_program.status == 'active'
        mock_db_session.commit.assert_called_once()
        mock_realtime_emitter.assert_called_once()
    
    def test_update_program_not_found(self, service, mock_db_session):
        """Test program update when not found."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # Act & Assert
        with pytest.raises(NotFoundException) as exc_info:
            service.update_program(999, {'name': 'Updated'})
        assert "Program with ID 999 not found" in str(exc_info.value)
    
    def test_update_program_invalid_status(self, service, mock_db_session, mock_program):
        """Test program update with invalid status."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.update_program(1, {'status': 'invalid'})
        assert "Invalid status" in str(exc_info.value)
        mock_db_session.rollback.assert_called()
    
    def test_update_program_duplicate_code(self, service, mock_db_session, mock_program):
        """Test program update with duplicate code."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        mock_db_session.commit.side_effect = IntegrityError(
            "statement", "params", "UNIQUE constraint failed: programs.code"
        )
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.update_program(1, {'code': 'DUPLICATE'})
        assert "Program with this code already exists" in str(exc_info.value)
        mock_db_session.rollback.assert_called()
    
    # Test delete_program method
    
    def test_delete_program_success(self, service, mock_db_session, mock_program, mock_realtime_emitter):
        """Test successful program deletion."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.delete_program(1)
        
        # Assert
        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_program)
        mock_db_session.commit.assert_called_once()
        mock_realtime_emitter.assert_called_once_with(
            mock_program.tenant_id,
            'program_deleted',
            {'program_id': 1}
        )
    
    def test_delete_program_not_found(self, service, mock_db_session):
        """Test program deletion when not found."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.delete_program(999)
        
        # Assert
        assert result is False
        mock_db_session.delete.assert_not_called()
    
    def test_delete_program_with_enrollments(self, service, mock_db_session, mock_program):
        """Test program deletion with active enrollments."""
        # Arrange
        mock_enrollment = Mock(spec=ProgramEnrollment)
        mock_program.enrollments = [mock_enrollment]
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.delete_program(1)
        assert "Cannot delete program with active enrollments" in str(exc_info.value)
        mock_db_session.rollback.assert_called()
    
    # Test list_programs method
    
    def test_list_programs_success(self, service, mock_db_session, mock_program):
        """Test successful program listing with pagination."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 2
        mock_query.offset.return_value.limit.return_value.all.return_value = [mock_program, mock_program]
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.list_programs(page=1, per_page=10)
        
        # Assert
        assert isinstance(result, PaginationResult)
        assert result.total == 2
        assert len(result.items) == 2
        assert result.current_page == 1
        assert result.pages == 1
        mock_query.filter_by.assert_called_with(is_active=True)
    
    def test_list_programs_with_filters(self, service, mock_db_session):
        """Test program listing with various filters."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.list_programs(
            tenant_id=1,
            is_active=True,
            status='active',
            level='beginner',
            category='technical',
            sort_by='name',
            sort_direction='asc'
        )
        
        # Assert
        assert result.total == 0
        assert len(result.items) == 0
        # Verify filter_by was called with correct parameters
        calls = mock_query.filter_by.call_args_list
        assert any(call == ((), {'tenant_id': 1}) for call in calls)
        assert any(call == ((), {'is_active': True}) for call in calls)
        assert any(call == ((), {'status': 'active'}) for call in calls)
        assert any(call == ((), {'level': 'beginner'}) for call in calls)
        assert any(call == ((), {'category': 'technical'}) for call in calls)
    
    def test_list_programs_empty_result(self, service, mock_db_session):
        """Test program listing with no results."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.list_programs()
        
        # Assert
        assert result.total == 0
        assert len(result.items) == 0
        assert result.pages == 0
    
    # Test get_program_by_code method
    
    def test_get_program_by_code_success(self, service, mock_db_session, mock_program):
        """Test successful program retrieval by code."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.get_program_by_code('TEST001')
        
        # Assert
        assert result is not None
        assert result['code'] == mock_program.code
        mock_query.filter_by.assert_called_once_with(code='TEST001')
    
    def test_get_program_by_code_not_found(self, service, mock_db_session):
        """Test program retrieval by code when not found."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.get_program_by_code('NOTFOUND')
        
        # Assert
        assert result is None
    
    # Test get_program_statistics method
    
    def test_get_program_statistics_success(self, service, mock_db_session, mock_program):
        """Test successful program statistics retrieval."""
        # Arrange
        # Create mock enrollments
        enrollment1 = Mock(status='active', overall_score=85.0, attendance_rate=90.0)
        enrollment2 = Mock(status='completed', overall_score=75.0, attendance_rate=85.0)
        enrollment3 = Mock(status='completed', overall_score=90.0, attendance_rate=95.0)
        mock_program.enrollments = [enrollment1, enrollment2, enrollment3]
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.get_program_statistics(1)
        
        # Assert
        assert result['program_id'] == 1
        assert result['total_enrollments'] == 3
        assert result['active_enrollments'] == 1
        assert result['completed_enrollments'] == 2
        assert result['completion_rate'] == 66.67  # 2/3 * 100
        assert result['average_score'] == 82.5  # (75 + 90) / 2
        assert result['average_attendance'] == 90.0  # (85 + 95) / 2
    
    def test_get_program_statistics_no_enrollments(self, service, mock_db_session, mock_program):
        """Test program statistics with no enrollments."""
        # Arrange
        mock_program.enrollments = []
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.get_program_statistics(1)
        
        # Assert
        assert result['total_enrollments'] == 0
        assert result['completion_rate'] == 0
        assert result['average_score'] == 0
        assert result['average_attendance'] == 0
    
    def test_get_program_statistics_not_found(self, service, mock_db_session):
        """Test program statistics when program not found."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            service.get_program_statistics(999)
    
    # Test archive_program method
    
    def test_archive_program_success(self, service, mock_db_session, mock_program, mock_realtime_emitter):
        """Test successful program archival."""
        # Arrange
        mock_program.status = 'active'
        mock_program.enrollments = []
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.archive_program(1)
        
        # Assert
        assert mock_program.status == ProgramStatus.ARCHIVED.value
        assert mock_program.is_active is False
        mock_db_session.commit.assert_called_once()
        mock_realtime_emitter.assert_called_once()
    
    def test_archive_program_already_archived(self, service, mock_db_session, mock_program):
        """Test archiving an already archived program."""
        # Arrange
        mock_program.status = ProgramStatus.ARCHIVED.value
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.archive_program(1)
        assert "Program is already archived" in str(exc_info.value)
    
    def test_archive_program_with_active_enrollments(self, service, mock_db_session, mock_program):
        """Test archiving program with active enrollments."""
        # Arrange
        enrollment = Mock(status='active')
        mock_program.enrollments = [enrollment]
        
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        # Act & Assert
        with pytest.raises(ValidationException) as exc_info:
            service.archive_program(1)
        assert "Cannot archive program with 1 active enrollments" in str(exc_info.value)
    
    # Test search_programs method
    
    def test_search_programs_success(self, service, mock_db_session, mock_program):
        """Test successful program search."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value.all.return_value = [mock_program]
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.search_programs('test', tenant_id=1, limit=5)
        
        # Assert
        assert len(result) == 1
        assert result[0]['name'] == mock_program.name
        mock_query.filter_by.assert_any_call(is_active=True)
        mock_query.filter_by.assert_any_call(tenant_id=1)
        mock_query.limit.assert_called_once_with(5)
    
    def test_search_programs_no_results(self, service, mock_db_session):
        """Test program search with no results."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        # Act
        result = service.search_programs('nonexistent')
        
        # Assert
        assert len(result) == 0
    
    # Test edge cases and error handling
    
    def test_service_initialization_without_realtime_emitter(self, mock_db_session):
        """Test service initialization without realtime emitter."""
        # Act
        service = ProgramServiceRefactored(db_session=mock_db_session)
        
        # Assert
        assert service.db == mock_db_session
        assert service.realtime_emitter is None
    
    def test_create_program_db_exception(self, service, mock_db_session, sample_program_data):
        """Test program creation with unexpected database exception."""
        # Arrange
        mock_db_session.commit.side_effect = Exception("Database error")
        
        # Act & Assert
        with patch('app.models.program.Program'):
            with pytest.raises(ValidationException) as exc_info:
                service.create_program(sample_program_data)
            assert "Failed to create program" in str(exc_info.value)
            mock_db_session.rollback.assert_called()
    
    def test_update_program_partial_update(self, service, mock_db_session, mock_program):
        """Test partial program update."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value.first.return_value = mock_program
        mock_db_session.query.return_value = mock_query
        
        update_data = {'description': 'New description only'}
        
        # Act
        result = service.update_program(1, update_data)
        
        # Assert
        assert mock_program.description == 'New description only'
        # Other fields should remain unchanged
        assert mock_program.name == 'Test Program'
        mock_db_session.commit.assert_called_once()
    
    def test_list_programs_invalid_page(self, service, mock_db_session):
        """Test program listing with invalid page number."""
        # Arrange
        mock_query = Mock()
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.count.return_value = 10
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        # Act - Should handle gracefully
        result = service.list_programs(page=100, per_page=10)
        
        # Assert
        assert result.total == 10
        assert len(result.items) == 0
        assert result.current_page == 100
    
    def test_program_date_handling(self, service, mock_db_session, sample_program_data):
        """Test program creation with date handling."""
        # Arrange
        mock_db_session.refresh.side_effect = lambda x: setattr(x, 'id', 1)
        
        # Act
        with patch('app.models.program.Program') as MockProgram:
            mock_instance = Mock()
            mock_instance.id = 1
            mock_instance.tenant_id = sample_program_data['tenant_id']
            mock_instance.to_dict.return_value = {'id': 1, **sample_program_data}
            MockProgram.return_value = mock_instance
            
            result = service.create_program(sample_program_data)
        
        # Assert
        assert result is not None
        # Verify that Program was called
        MockProgram.assert_called_once()
        # Check that dates were included in the call
        call_kwargs = MockProgram.call_args.kwargs if MockProgram.call_args else {}
        assert call_kwargs.get('start_date') == date(2024, 1, 1)
        assert call_kwargs.get('end_date') == date(2024, 2, 1)