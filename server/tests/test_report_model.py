"""Tests for Report model."""

import pytest
from datetime import datetime
from app.models.report import Report


class TestReportModel:
    """Test the Report model."""
    
    @pytest.fixture
    def report(self):
        """Create a test report."""
        return Report(
            name='Monthly Performance Report',
            description='Monthly performance metrics',
            type='performance',
            created_by_id=1,
            tenant_id=1
        )
    
    def test_report_creation(self, report):
        """Test report creation with basic fields."""
        assert report.name == 'Monthly Performance Report'
        assert report.description == 'Monthly performance metrics'
        assert report.type == 'performance'
        assert report.format == 'pdf'
        assert report.status == 'draft'
        assert report.created_by_id == 1
        assert report.tenant_id == 1
    
    def test_report_defaults(self):
        """Test report default values."""
        report = Report(
            name='Test Report',
            type='beneficiary',
            created_by_id=1,
            tenant_id=1
        )
        assert report.format == 'pdf'
        assert report.status == 'draft'
        assert report.parameters == {}
        assert report.run_count == 0
    
    def test_report_to_dict(self, report):
        """Test report to_dict method."""
        report.parameters = {'start_date': '2024-01-01', 'end_date': '2024-01-31'}
        report.file_path = '/reports/monthly_01_2024.pdf'
        report.file_size = 1024000
        report.run_count = 5
        report.last_generated = datetime(2024, 1, 31, 23, 59, 59)
        
        result = report.to_dict()
        
        assert result['name'] == 'Monthly Performance Report'
        assert result['type'] == 'performance'
        assert result['format'] == 'pdf'
        assert result['status'] == 'draft'
        assert result['parameters'] == {'start_date': '2024-01-01', 'end_date': '2024-01-31'}
        assert result['file_path'] == '/reports/monthly_01_2024.pdf'
        assert result['file_size'] == 1024000
        assert result['run_count'] == 5
        assert result['last_generated'] == '2024-01-31T23:59:59'
    
    def test_report_update_status(self, report):
        """Test updating report status."""
        report.status = 'generating'
        assert report.status == 'generating'
        
        report.status = 'completed'
        report.file_path = '/reports/test.pdf'
        report.file_size = 500000
        assert report.status == 'completed'
        assert report.file_path == '/reports/test.pdf'
    
    def test_report_increment_run_count(self, report):
        """Test incrementing run count."""
        assert report.run_count == 0
        
        report.run_count += 1
        assert report.run_count == 1
        
        report.run_count += 1
        assert report.run_count == 2
    
    def test_report_relationships(self, report):
        """Test report relationships."""
        assert hasattr(report, 'created_by')
        assert hasattr(report, 'tenant')
        assert hasattr(report, 'schedules')