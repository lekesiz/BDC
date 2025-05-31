"""Extended tests for various services to improve coverage."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone, timedelta
import os

# Import services we want to test
from app.services.search_service import SearchService
from app.services.program_service import ProgramService
from app.services.evaluation_service import EvaluationService
from app.services.report_service import ReportService
from app.services.export_service import ExportService
from app.services.tenant_service import TenantService
from app.exceptions import NotFoundException, ValidationException, ForbiddenException


class TestSearchService:
    """Test cases for SearchService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.query = Mock()
        db.scalar = Mock()
        return db
    
    @pytest.fixture
    def mock_user(self):
        """Create mock user."""
        user = Mock()
        user.id = 1
        user.tenant_id = 100
        user.role = 'admin'
        return user
    
    def test_global_search_with_results(self, mock_db, mock_user):
        """Test global search with multiple entity results."""
        with patch('app.services.search_service.db', mock_db):
            # Mock query results
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.all.return_value = [
                Mock(id=1, first_name='John', last_name='Doe', email='john@example.com')
            ]
            mock_db.query.return_value = mock_query
            
            result = SearchService.global_search('john', mock_user)
            
            assert 'beneficiaries' in result
            assert 'users' in result
            assert 'programs' in result
            assert 'documents' in result
    
    def test_global_search_empty_query(self, mock_user):
        """Test global search with empty query."""
        result = SearchService.global_search('', mock_user)
        
        assert result['beneficiaries'] == []
        assert result['users'] == []
        assert result['programs'] == []
        assert result['documents'] == []
    
    def test_search_beneficiaries(self, mock_db, mock_user):
        """Test searching beneficiaries."""
        with patch('app.services.search_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(id=1, user=Mock(first_name='John', last_name='Doe'))
            ]
            mock_db.query.return_value = mock_query
            
            result = SearchService.search_beneficiaries('john', mock_user.tenant_id)
            
            assert len(result) == 1
    
    def test_search_users(self, mock_db, mock_user):
        """Test searching users."""
        with patch('app.services.search_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(id=1, first_name='Jane', last_name='Smith', email='jane@example.com')
            ]
            mock_db.query.return_value = mock_query
            
            result = SearchService.search_users('jane', mock_user.tenant_id)
            
            assert len(result) == 1
    
    def test_search_programs(self, mock_db, mock_user):
        """Test searching programs."""
        with patch('app.services.search_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(id=1, name='Python Course', description='Learn Python')
            ]
            mock_db.query.return_value = mock_query
            
            result = SearchService.search_programs('python', mock_user.tenant_id)
            
            assert len(result) == 1
    
    def test_search_documents(self, mock_db, mock_user):
        """Test searching documents."""
        with patch('app.services.search_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(id=1, title='Report', description='Annual report')
            ]
            mock_db.query.return_value = mock_query
            
            result = SearchService.search_documents('report', mock_user.tenant_id)
            
            assert len(result) == 1
    
    def test_advanced_search(self, mock_db, mock_user):
        """Test advanced search with filters."""
        with patch('app.services.search_service.db', mock_db):
            filters = {
                'entity_type': 'beneficiary',
                'status': 'active',
                'date_from': '2023-01-01',
                'date_to': '2023-12-31'
            }
            
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = []
            mock_db.query.return_value = mock_query
            
            result = SearchService.advanced_search('test', filters, mock_user)
            
            assert isinstance(result, dict)


class TestProgramService:
    """Test cases for ProgramService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.delete = Mock()
        db.query = Mock()
        return db
    
    def test_get_programs(self, mock_db):
        """Test getting all programs."""
        with patch('app.services.program_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(id=1, name='Program 1'),
                Mock(id=2, name='Program 2')
            ]
            mock_db.query.return_value = mock_query
            
            result = ProgramService.get_programs(tenant_id=100)
            
            assert len(result) == 2
    
    def test_get_program_by_id(self, mock_db):
        """Test getting program by ID."""
        with patch('app.services.program_service.db', mock_db):
            mock_program = Mock(id=1, name='Test Program')
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_program
            mock_db.query.return_value = mock_query
            
            result = ProgramService.get_program_by_id(1)
            
            assert result == mock_program
    
    def test_get_program_by_id_not_found(self, mock_db):
        """Test getting non-existent program."""
        with patch('app.services.program_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = None
            mock_db.query.return_value = mock_query
            
            with pytest.raises(NotFoundException):
                ProgramService.get_program_by_id(999)
    
    def test_create_program(self, mock_db):
        """Test creating a program."""
        with patch('app.services.program_service.db', mock_db):
            with patch('app.services.program_service.Program') as MockProgram:
                mock_program = Mock(id=1, name='New Program')
                MockProgram.return_value = mock_program
                
                data = {
                    'name': 'New Program',
                    'description': 'Test description',
                    'tenant_id': 100
                }
                
                result = ProgramService.create_program(data)
                
                assert result == mock_program
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
    
    def test_update_program(self, mock_db):
        """Test updating a program."""
        with patch('app.services.program_service.db', mock_db):
            mock_program = Mock(id=1, name='Old Name')
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_program
            mock_db.query.return_value = mock_query
            
            data = {'name': 'New Name', 'description': 'Updated description'}
            
            result = ProgramService.update_program(1, data)
            
            assert mock_program.name == 'New Name'
            assert mock_program.description == 'Updated description'
            mock_db.commit.assert_called_once()
    
    def test_delete_program(self, mock_db):
        """Test deleting a program."""
        with patch('app.services.program_service.db', mock_db):
            mock_program = Mock(id=1)
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_program
            mock_db.query.return_value = mock_query
            
            result = ProgramService.delete_program(1)
            
            assert result is True
            mock_db.delete.assert_called_once_with(mock_program)
            mock_db.commit.assert_called_once()
    
    def test_enroll_beneficiary(self, mock_db):
        """Test enrolling beneficiary in program."""
        with patch('app.services.program_service.db', mock_db):
            with patch('app.services.program_service.ProgramEnrollment') as MockEnrollment:
                mock_enrollment = Mock()
                MockEnrollment.return_value = mock_enrollment
                
                # Check if already enrolled
                mock_query = Mock()
                mock_query.filter_by.return_value = mock_query
                mock_query.first.return_value = None  # Not enrolled
                mock_db.query.return_value = mock_query
                
                result = ProgramService.enroll_beneficiary(1, 10)
                
                assert result == mock_enrollment
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
    
    def test_enroll_beneficiary_already_enrolled(self, mock_db):
        """Test enrolling already enrolled beneficiary."""
        with patch('app.services.program_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = Mock()  # Already enrolled
            mock_db.query.return_value = mock_query
            
            with pytest.raises(ValidationException):
                ProgramService.enroll_beneficiary(1, 10)
    
    def test_get_program_enrollments(self, mock_db):
        """Test getting program enrollments."""
        with patch('app.services.program_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(beneficiary_id=1),
                Mock(beneficiary_id=2)
            ]
            mock_db.query.return_value = mock_query
            
            result = ProgramService.get_program_enrollments(1)
            
            assert len(result) == 2
    
    def test_get_beneficiary_programs(self, mock_db):
        """Test getting beneficiary's programs."""
        with patch('app.services.program_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(program=Mock(id=1, name='Program 1')),
                Mock(program=Mock(id=2, name='Program 2'))
            ]
            mock_db.query.return_value = mock_query
            
            result = ProgramService.get_beneficiary_programs(10)
            
            assert len(result) == 2


class TestEvaluationService:
    """Test cases for EvaluationService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.query = Mock()
        return db
    
    def test_get_evaluations(self, mock_db):
        """Test getting evaluations."""
        with patch('app.services.evaluation_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(id=1, title='Evaluation 1'),
                Mock(id=2, title='Evaluation 2')
            ]
            mock_db.query.return_value = mock_query
            
            result = EvaluationService.get_evaluations(tenant_id=100)
            
            assert len(result) == 2
    
    def test_get_evaluation_by_id(self, mock_db):
        """Test getting evaluation by ID."""
        with patch('app.services.evaluation_service.db', mock_db):
            mock_evaluation = Mock(id=1, title='Test Evaluation')
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_evaluation
            mock_db.query.return_value = mock_query
            
            result = EvaluationService.get_evaluation_by_id(1)
            
            assert result == mock_evaluation
    
    def test_create_evaluation(self, mock_db):
        """Test creating evaluation."""
        with patch('app.services.evaluation_service.db', mock_db):
            with patch('app.services.evaluation_service.Evaluation') as MockEvaluation:
                mock_evaluation = Mock(id=1)
                MockEvaluation.return_value = mock_evaluation
                
                data = {
                    'title': 'New Evaluation',
                    'description': 'Test',
                    'tenant_id': 100
                }
                
                result = EvaluationService.create_evaluation(data)
                
                assert result == mock_evaluation
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
    
    def test_assign_evaluation(self, mock_db):
        """Test assigning evaluation to beneficiary."""
        with patch('app.services.evaluation_service.db', mock_db):
            with patch('app.services.evaluation_service.EvaluationAssignment') as MockAssignment:
                mock_assignment = Mock()
                MockAssignment.return_value = mock_assignment
                
                # Check not already assigned
                mock_query = Mock()
                mock_query.filter_by.return_value = mock_query
                mock_query.first.return_value = None
                mock_db.query.return_value = mock_query
                
                result = EvaluationService.assign_evaluation(1, 10, 5)
                
                assert result == mock_assignment
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
    
    def test_complete_evaluation(self, mock_db):
        """Test completing evaluation."""
        with patch('app.services.evaluation_service.db', mock_db):
            mock_assignment = Mock(status='assigned')
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_assignment
            mock_db.query.return_value = mock_query
            
            responses = {'q1': 'answer1', 'q2': 'answer2'}
            
            result = EvaluationService.complete_evaluation(1, 10, responses)
            
            assert mock_assignment.status == 'completed'
            assert mock_assignment.responses == responses
            assert mock_assignment.completed_at is not None
            mock_db.commit.assert_called_once()
    
    def test_get_evaluation_results(self, mock_db):
        """Test getting evaluation results."""
        with patch('app.services.evaluation_service.db', mock_db):
            mock_assignment = Mock(
                status='completed',
                responses={'q1': 'answer1'},
                score=85,
                completed_at=datetime.now(timezone.utc)
            )
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_assignment
            mock_db.query.return_value = mock_query
            
            result = EvaluationService.get_evaluation_results(1, 10)
            
            assert result == mock_assignment


class TestReportService:
    """Test cases for ReportService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.query = Mock()
        return db
    
    def test_generate_beneficiary_report(self, mock_db):
        """Test generating beneficiary report."""
        with patch('app.services.report_service.db', mock_db):
            # Mock beneficiary data
            mock_beneficiary = Mock(
                id=10,
                user=Mock(first_name='John', last_name='Doe'),
                created_at=datetime.now(timezone.utc),
                notes=[Mock(content='Note 1'), Mock(content='Note 2')],
                appointments=[Mock(status='completed'), Mock(status='scheduled')]
            )
            
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_beneficiary
            mock_db.query.return_value = mock_query
            
            with patch('app.services.report_service.Report') as MockReport:
                mock_report = Mock(id=1)
                MockReport.return_value = mock_report
                
                result = ReportService.generate_beneficiary_report(10, 1)
                
                assert result == mock_report
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
    
    def test_generate_program_report(self, mock_db):
        """Test generating program report."""
        with patch('app.services.report_service.db', mock_db):
            # Mock program data
            mock_program = Mock(
                id=1,
                name='Test Program',
                enrollments=[
                    Mock(status='active'),
                    Mock(status='completed'),
                    Mock(status='active')
                ]
            )
            
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_program
            mock_db.query.return_value = mock_query
            
            with patch('app.services.report_service.Report') as MockReport:
                mock_report = Mock(id=1)
                MockReport.return_value = mock_report
                
                result = ReportService.generate_program_report(1, 1)
                
                assert result == mock_report
    
    def test_generate_tenant_report(self, mock_db):
        """Test generating tenant report."""
        with patch('app.services.report_service.db', mock_db):
            # Mock aggregated data
            mock_db.query().filter_by().count.return_value = 50  # Total beneficiaries
            
            with patch('app.services.report_service.Report') as MockReport:
                mock_report = Mock(id=1)
                MockReport.return_value = mock_report
                
                result = ReportService.generate_tenant_report(100, 1)
                
                assert result == mock_report
    
    def test_get_reports(self, mock_db):
        """Test getting reports."""
        with patch('app.services.report_service.db', mock_db):
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(id=1, type='beneficiary'),
                Mock(id=2, type='program')
            ]
            mock_db.query.return_value = mock_query
            
            result = ReportService.get_reports(user_id=1)
            
            assert len(result) == 2
    
    def test_get_report_by_id(self, mock_db):
        """Test getting report by ID."""
        with patch('app.services.report_service.db', mock_db):
            mock_report = Mock(id=1, type='beneficiary')
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_report
            mock_db.query.return_value = mock_query
            
            result = ReportService.get_report_by_id(1)
            
            assert result == mock_report
    
    def test_delete_report(self, mock_db):
        """Test deleting report."""
        with patch('app.services.report_service.db', mock_db):
            mock_report = Mock(id=1)
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_report
            mock_db.query.return_value = mock_query
            
            result = ReportService.delete_report(1)
            
            assert result is True
            mock_db.delete.assert_called_once_with(mock_report)
            mock_db.commit.assert_called_once()


class TestExportService:
    """Test cases for ExportService."""
    
    def test_export_to_csv(self):
        """Test exporting data to CSV."""
        data = [
            {'name': 'John Doe', 'email': 'john@example.com'},
            {'name': 'Jane Smith', 'email': 'jane@example.com'}
        ]
        
        with patch('app.services.export_service.StringIO') as MockStringIO:
            mock_output = Mock()
            mock_output.getvalue.return_value = 'csv_content'
            MockStringIO.return_value = mock_output
            
            result = ExportService.export_to_csv(data, ['name', 'email'])
            
            assert result == 'csv_content'
    
    def test_export_to_excel(self):
        """Test exporting data to Excel."""
        data = [
            {'name': 'John Doe', 'email': 'john@example.com'},
            {'name': 'Jane Smith', 'email': 'jane@example.com'}
        ]
        
        with patch('app.services.export_service.BytesIO') as MockBytesIO:
            with patch('app.services.export_service.pd') as mock_pd:
                mock_output = Mock()
                MockBytesIO.return_value = mock_output
                
                result = ExportService.export_to_excel(data)
                
                assert result == mock_output
                mock_pd.DataFrame.assert_called_once_with(data)
    
    def test_export_to_pdf(self):
        """Test exporting data to PDF."""
        content = {
            'title': 'Test Report',
            'data': [{'field': 'value'}]
        }
        
        with patch('app.services.export_service.BytesIO') as MockBytesIO:
            with patch('app.services.export_service.SimpleDocTemplate') as MockDoc:
                mock_output = Mock()
                MockBytesIO.return_value = mock_output
                
                mock_doc = Mock()
                MockDoc.return_value = mock_doc
                
                result = ExportService.export_to_pdf(content)
                
                assert result == mock_output
                mock_doc.build.assert_called_once()
    
    def test_export_beneficiaries(self):
        """Test exporting beneficiaries data."""
        with patch('app.services.export_service.db') as mock_db:
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(
                    id=1,
                    user=Mock(first_name='John', last_name='Doe', email='john@example.com'),
                    phone='123456789',
                    status='active'
                )
            ]
            mock_db.query.return_value = mock_query
            
            with patch.object(ExportService, 'export_to_csv') as mock_export:
                mock_export.return_value = 'csv_content'
                
                result = ExportService.export_beneficiaries(100, 'csv')
                
                assert result == 'csv_content'
    
    def test_export_programs(self):
        """Test exporting programs data."""
        with patch('app.services.export_service.db') as mock_db:
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.all.return_value = [
                Mock(
                    id=1,
                    name='Program 1',
                    description='Test program',
                    status='active',
                    enrollments=[]
                )
            ]
            mock_db.query.return_value = mock_query
            
            with patch.object(ExportService, 'export_to_excel') as mock_export:
                mock_export.return_value = Mock()
                
                result = ExportService.export_programs(100, 'excel')
                
                assert result is not None


class TestTenantService:
    """Test cases for TenantService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        db = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.query = Mock()
        db.delete = Mock()
        return db
    
    def test_get_tenants(self, mock_db):
        """Test getting all tenants."""
        with patch('app.services.tenant_service.db', mock_db):
            mock_query = Mock()
            mock_query.all.return_value = [
                Mock(id=1, name='Tenant 1'),
                Mock(id=2, name='Tenant 2')
            ]
            mock_db.query.return_value = mock_query
            
            result = TenantService.get_tenants()
            
            assert len(result) == 2
    
    def test_get_tenant_by_id(self, mock_db):
        """Test getting tenant by ID."""
        with patch('app.services.tenant_service.db', mock_db):
            mock_tenant = Mock(id=1, name='Test Tenant')
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_tenant
            mock_db.query.return_value = mock_query
            
            result = TenantService.get_tenant_by_id(1)
            
            assert result == mock_tenant
    
    def test_create_tenant(self, mock_db):
        """Test creating tenant."""
        with patch('app.services.tenant_service.db', mock_db):
            with patch('app.services.tenant_service.Tenant') as MockTenant:
                mock_tenant = Mock(id=1, name='New Tenant')
                MockTenant.return_value = mock_tenant
                
                data = {
                    'name': 'New Tenant',
                    'domain': 'newtenant.com',
                    'settings': {}
                }
                
                result = TenantService.create_tenant(data)
                
                assert result == mock_tenant
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()
    
    def test_update_tenant(self, mock_db):
        """Test updating tenant."""
        with patch('app.services.tenant_service.db', mock_db):
            mock_tenant = Mock(id=1, name='Old Name')
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_tenant
            mock_db.query.return_value = mock_query
            
            data = {'name': 'New Name', 'settings': {'theme': 'dark'}}
            
            result = TenantService.update_tenant(1, data)
            
            assert mock_tenant.name == 'New Name'
            assert mock_tenant.settings == {'theme': 'dark'}
            mock_db.commit.assert_called_once()
    
    def test_delete_tenant(self, mock_db):
        """Test deleting tenant."""
        with patch('app.services.tenant_service.db', mock_db):
            mock_tenant = Mock(id=1)
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_tenant
            mock_db.query.return_value = mock_query
            
            result = TenantService.delete_tenant(1)
            
            assert result is True
            mock_db.delete.assert_called_once_with(mock_tenant)
            mock_db.commit.assert_called_once()
    
    def test_get_tenant_statistics(self, mock_db):
        """Test getting tenant statistics."""
        with patch('app.services.tenant_service.db', mock_db):
            # Mock counts
            mock_db.query().filter_by().count.side_effect = [100, 50, 20, 10]
            
            result = TenantService.get_tenant_statistics(1)
            
            assert 'total_users' in result
            assert 'total_beneficiaries' in result
            assert 'total_programs' in result
            assert 'total_evaluations' in result
    
    def test_get_tenant_settings(self, mock_db):
        """Test getting tenant settings."""
        with patch('app.services.tenant_service.db', mock_db):
            mock_tenant = Mock(
                id=1,
                settings={'theme': 'light', 'language': 'en'}
            )
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_tenant
            mock_db.query.return_value = mock_query
            
            result = TenantService.get_tenant_settings(1)
            
            assert result == {'theme': 'light', 'language': 'en'}
    
    def test_update_tenant_settings(self, mock_db):
        """Test updating tenant settings."""
        with patch('app.services.tenant_service.db', mock_db):
            mock_tenant = Mock(
                id=1,
                settings={'theme': 'light'}
            )
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_tenant
            mock_db.query.return_value = mock_query
            
            new_settings = {'theme': 'dark', 'language': 'es'}
            
            result = TenantService.update_tenant_settings(1, new_settings)
            
            assert mock_tenant.settings == new_settings
            mock_db.commit.assert_called_once()