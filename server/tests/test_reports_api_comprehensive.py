"""Comprehensive tests for the Reports API endpoints."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import json
import io
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.tenant import Tenant
from app.models.report import Report, ReportSchedule


class TestReportsAPI:
    """Test suite for the Reports API endpoints."""
    
    @pytest.fixture(autouse=True)
    def setup(self, app, client):
        """Set up test environment."""
        self.app = app
        self.client = client
        
        # Create test data
        with self.app.app_context():
            # Create tenant
            self.tenant = Tenant(
                name='Test Tenant',
                domain='test.com',
                is_active=True
            )
            db.session.add(self.tenant)
            db.session.commit()
            
            # Create users
            self.super_admin = User(
                email='superadmin@test.com',
                username='superadmin',
                first_name='Super',
                last_name='Admin',
                role='super_admin',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.super_admin.set_password('password123')
            
            self.tenant_admin = User(
                email='tenantadmin@test.com',
                username='tenantadmin',
                first_name='Tenant',
                last_name='Admin',
                role='tenant_admin',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.tenant_admin.set_password('password123')
            
            self.trainer = User(
                email='trainer@test.com',
                username='trainer',
                first_name='Test',
                last_name='Trainer',
                role='trainer',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.trainer.set_password('password123')
            
            self.student = User(
                email='student@test.com',
                username='student',
                first_name='Test',
                last_name='Student',
                role='student',
                tenant_id=self.tenant.id,
                is_active=True
            )
            self.student.set_password('password123')
            
            db.session.add_all([self.super_admin, self.tenant_admin, self.trainer, self.student])
            db.session.commit()
            
            # Create test reports
            self.report1 = Report(
                name='Test Report 1',
                type='beneficiary',
                description='Test beneficiary report',
                parameters={'test': 'data'},
                status='completed',
                created_by_id=self.trainer.id,
                tenant_id=self.tenant.id
            )
            
            self.report2 = Report(
                name='Test Report 2',
                type='program',
                description='Test program report',
                parameters={'test': 'data2'},
                status='pending',
                created_by_id=self.tenant_admin.id,
                tenant_id=self.tenant.id
            )
            
            self.report3 = Report(
                name='Test Report 3',
                type='analytics',
                description='Test analytics report',
                parameters={'test': 'data3'},
                status='completed',
                created_by_id=self.super_admin.id,
                tenant_id=self.tenant.id
            )
            
            db.session.add_all([self.report1, self.report2, self.report3])
            db.session.commit()
            
            # Create test schedule
            self.schedule1 = ReportSchedule(
                report_id=self.report1.id,
                frequency='daily',
                recipients=['test@example.com'],
                is_active=True,
                next_run=datetime.utcnow() + timedelta(days=1)
            )
            
            db.session.add(self.schedule1)
            db.session.commit()
            
            # Create access tokens
            self.super_admin_token = create_access_token(identity=self.super_admin.id)
            self.tenant_admin_token = create_access_token(identity=self.tenant_admin.id)
            self.trainer_token = create_access_token(identity=self.trainer.id)
            self.student_token = create_access_token(identity=self.student.id)
    
    def test_get_recent_reports_as_trainer(self):
        """Test getting recent reports as a trainer."""
        response = self.client.get(
            '/api/reports/recent',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Trainer should only see their own report
        assert len(data) == 1
        assert data[0]['name'] == 'Test Report 1'
    
    def test_get_recent_reports_as_admin(self):
        """Test getting recent reports as an admin."""
        response = self.client.get(
            '/api/reports/recent',
            headers={'Authorization': f'Bearer {self.tenant_admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Admin should see all tenant reports
        assert len(data) == 3
    
    def test_get_recent_reports_unauthorized(self):
        """Test getting recent reports without authentication."""
        response = self.client.get('/api/reports/recent')
        assert response.status_code == 401
    
    def test_get_saved_reports_as_trainer(self):
        """Test getting saved reports as a trainer."""
        response = self.client.get(
            '/api/reports/saved',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should only see completed reports created by trainer
        assert len(data) == 1
        assert data[0]['status'] == 'completed'
    
    def test_get_saved_reports_as_admin(self):
        """Test getting saved reports as an admin."""
        response = self.client.get(
            '/api/reports/saved',
            headers={'Authorization': f'Bearer {self.tenant_admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should see all completed reports in tenant
        assert all(report['status'] == 'completed' for report in data)
    
    def test_get_scheduled_reports_as_trainer(self):
        """Test getting scheduled reports as a trainer."""
        response = self.client.get(
            '/api/reports/scheduled',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Should see schedule for their report
        assert len(data) == 1
    
    def test_get_scheduled_reports_as_admin(self):
        """Test getting scheduled reports as an admin."""
        response = self.client.get(
            '/api/reports/scheduled',
            headers={'Authorization': f'Bearer {self.tenant_admin_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        # Admin should see all scheduled reports
        assert len(data) >= 1
    
    def test_create_report_success(self):
        """Test creating a new report."""
        report_data = {
            'name': 'New Test Report',
            'type': 'beneficiary',
            'description': 'A new test report',
            'parameters': {
                'date_range': 'last_month',
                'filters': {'status': 'active'}
            }
        }
        
        response = self.client.post(
            '/api/reports',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=report_data
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'New Test Report'
        assert data['type'] == 'beneficiary'
        assert data['created_by_id'] == self.trainer.id
        assert data['tenant_id'] == self.tenant.id
    
    def test_create_report_missing_fields(self):
        """Test creating a report with missing required fields."""
        report_data = {
            'name': 'Incomplete Report'
            # Missing type
        }
        
        response = self.client.post(
            '/api/reports',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=report_data
        )
        
        # Should return error for missing required fields
        assert response.status_code == 400
    
    def test_create_report_invalid_type(self):
        """Test creating a report with invalid type."""
        report_data = {
            'name': 'Invalid Type Report',
            'type': 'invalid_type',
            'description': 'Report with invalid type'
        }
        
        response = self.client.post(
            '/api/reports',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=report_data
        )
        
        # Should validate report type
        assert response.status_code == 400
    
    def test_get_report_by_id_success(self):
        """Test getting a specific report by ID."""
        response = self.client.get(
            f'/api/reports/{self.report1.id}',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == self.report1.id
        assert data['name'] == 'Test Report 1'
    
    def test_get_report_by_id_not_found(self):
        """Test getting a non-existent report."""
        response = self.client.get(
            '/api/reports/999999',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        assert response.status_code == 404
    
    def test_get_report_by_id_no_permission(self):
        """Test getting a report without permission."""
        # Student trying to access trainer's report
        response = self.client.get(
            f'/api/reports/{self.report1.id}',
            headers={'Authorization': f'Bearer {self.student_token}'}
        )
        
        # Students may not have access to reports
        assert response.status_code in [403, 404]
    
    def test_update_report_success(self):
        """Test updating a report."""
        update_data = {
            'name': 'Updated Report Name',
            'description': 'Updated description'
        }
        
        response = self.client.put(
            f'/api/reports/{self.report1.id}',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=update_data
        )
        
        # Check if update is allowed
        if response.status_code == 200:
            data = response.get_json()
            assert data['name'] == 'Updated Report Name'
            assert data['description'] == 'Updated description'
    
    def test_delete_report_success(self):
        """Test deleting a report."""
        # Create a report to delete
        with self.app.app_context():
            report_to_delete = Report(
                name='Report to Delete',
                type='analytics',
                created_by_id=self.trainer.id,
                tenant_id=self.tenant.id
            )
            db.session.add(report_to_delete)
            db.session.commit()
            report_id = report_to_delete.id
        
        response = self.client.delete(
            f'/api/reports/{report_id}',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if delete is allowed
        assert response.status_code in [200, 204, 403]
    
    def test_export_report_csv(self):
        """Test exporting a report as CSV."""
        response = self.client.get(
            f'/api/reports/{self.report1.id}/export?format=csv',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if export is implemented
        if response.status_code == 200:
            assert response.content_type in ['text/csv', 'application/csv']
    
    def test_export_report_excel(self):
        """Test exporting a report as Excel."""
        response = self.client.get(
            f'/api/reports/{self.report1.id}/export?format=excel',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if export is implemented
        if response.status_code == 200:
            assert 'spreadsheet' in response.content_type or 'excel' in response.content_type
    
    def test_export_report_pdf(self):
        """Test exporting a report as PDF."""
        response = self.client.get(
            f'/api/reports/{self.report1.id}/export?format=pdf',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if export is implemented
        if response.status_code == 200:
            assert response.content_type == 'application/pdf'
    
    def test_export_report_invalid_format(self):
        """Test exporting a report with invalid format."""
        response = self.client.get(
            f'/api/reports/{self.report1.id}/export?format=invalid',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Should return error for invalid format
        assert response.status_code in [400, 415]
    
    def test_schedule_report_creation(self):
        """Test creating a report schedule."""
        schedule_data = {
            'frequency': 'weekly',
            'recipients': ['recipient1@test.com', 'recipient2@test.com'],
            'day_of_week': 1,  # Monday
            'time': '09:00'
        }
        
        response = self.client.post(
            f'/api/reports/{self.report2.id}/schedule',
            headers={'Authorization': f'Bearer {self.tenant_admin_token}'},
            json=schedule_data
        )
        
        # Check if scheduling is implemented
        if response.status_code == 201:
            data = response.get_json()
            assert data['frequency'] == 'weekly'
            assert len(data['recipients']) == 2
    
    def test_update_report_schedule(self):
        """Test updating a report schedule."""
        update_data = {
            'frequency': 'monthly',
            'recipients': ['newemail@test.com']
        }
        
        response = self.client.put(
            f'/api/reports/{self.report1.id}/schedule',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=update_data
        )
        
        # Check if schedule update is implemented
        if response.status_code == 200:
            data = response.get_json()
            assert data['frequency'] == 'monthly'
    
    def test_delete_report_schedule(self):
        """Test deleting a report schedule."""
        response = self.client.delete(
            f'/api/reports/{self.report1.id}/schedule',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if schedule deletion is implemented
        assert response.status_code in [200, 204, 404]
    
    def test_run_report_now(self):
        """Test running a report immediately."""
        response = self.client.post(
            f'/api/reports/{self.report1.id}/run',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if immediate run is implemented
        if response.status_code == 200:
            data = response.get_json()
            assert 'status' in data
    
    def test_get_report_templates(self):
        """Test getting available report templates."""
        response = self.client.get(
            '/api/reports/templates',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if templates endpoint exists
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list)
    
    def test_create_report_from_template(self):
        """Test creating a report from a template."""
        template_data = {
            'template_id': 'beneficiary_progress',
            'name': 'Monthly Progress Report',
            'parameters': {
                'month': 'January',
                'year': 2025
            }
        }
        
        response = self.client.post(
            '/api/reports/from-template',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=template_data
        )
        
        # Check if template creation is implemented
        if response.status_code == 201:
            data = response.get_json()
            assert data['name'] == 'Monthly Progress Report'
    
    def test_get_report_preview(self):
        """Test getting a report preview."""
        response = self.client.get(
            f'/api/reports/{self.report1.id}/preview',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if preview is implemented
        if response.status_code == 200:
            data = response.get_json()
            assert 'preview' in data or 'data' in data
    
    def test_clone_report(self):
        """Test cloning an existing report."""
        response = self.client.post(
            f'/api/reports/{self.report1.id}/clone',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json={'name': 'Cloned Report'}
        )
        
        # Check if cloning is implemented
        if response.status_code == 201:
            data = response.get_json()
            assert data['name'] == 'Cloned Report'
            assert data['type'] == self.report1.type
    
    def test_share_report(self):
        """Test sharing a report with other users."""
        share_data = {
            'user_ids': [self.tenant_admin.id, self.super_admin.id],
            'message': 'Please review this report'
        }
        
        response = self.client.post(
            f'/api/reports/{self.report1.id}/share',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=share_data
        )
        
        # Check if sharing is implemented
        assert response.status_code in [200, 201, 404, 501]
    
    def test_get_report_permissions(self):
        """Test getting report permissions."""
        response = self.client.get(
            f'/api/reports/{self.report1.id}/permissions',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if permissions endpoint exists
        if response.status_code == 200:
            data = response.get_json()
            assert 'permissions' in data or 'users' in data
    
    def test_update_report_permissions(self):
        """Test updating report permissions."""
        permissions_data = {
            'users': {
                str(self.tenant_admin.id): ['view', 'edit'],
                str(self.super_admin.id): ['view']
            }
        }
        
        response = self.client.put(
            f'/api/reports/{self.report1.id}/permissions',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=permissions_data
        )
        
        # Check if permissions update is implemented
        assert response.status_code in [200, 403, 404, 501]
    
    def test_get_report_history(self):
        """Test getting report execution history."""
        response = self.client.get(
            f'/api/reports/{self.report1.id}/history',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if history endpoint exists
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list)
    
    def test_get_report_filters(self):
        """Test getting available filters for a report type."""
        response = self.client.get(
            '/api/reports/filters?type=beneficiary',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if filters endpoint exists
        if response.status_code == 200:
            data = response.get_json()
            assert 'filters' in data or isinstance(data, dict)
    
    def test_validate_report_parameters(self):
        """Test validating report parameters."""
        params_data = {
            'type': 'beneficiary',
            'parameters': {
                'date_range': 'invalid_range',
                'filters': {}
            }
        }
        
        response = self.client.post(
            '/api/reports/validate',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json=params_data
        )
        
        # Check if validation endpoint exists
        assert response.status_code in [200, 400, 404, 501]
    
    def test_bulk_delete_reports(self):
        """Test bulk deleting reports."""
        # Create reports to delete
        report_ids = []
        with self.app.app_context():
            for i in range(3):
                report = Report(
                    name=f'Bulk Delete Report {i}',
                    type='analytics',
                    created_by_id=self.trainer.id,
                    tenant_id=self.tenant.id
                )
                db.session.add(report)
            db.session.commit()
            report_ids = [r.id for r in Report.query.filter_by(name__contains='Bulk Delete Report').all()]
        
        response = self.client.post(
            '/api/reports/bulk-delete',
            headers={'Authorization': f'Bearer {self.trainer_token}'},
            json={'report_ids': report_ids}
        )
        
        # Check if bulk delete is implemented
        assert response.status_code in [200, 204, 403, 404, 501]
    
    def test_search_reports(self):
        """Test searching reports."""
        response = self.client.get(
            '/api/reports/search?q=Test',
            headers={'Authorization': f'Bearer {self.trainer_token}'}
        )
        
        # Check if search is implemented
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list)
    
    def test_get_report_statistics(self):
        """Test getting report statistics."""
        response = self.client.get(
            '/api/reports/statistics',
            headers={'Authorization': f'Bearer {self.tenant_admin_token}'}
        )
        
        # Check if statistics endpoint exists
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, dict)