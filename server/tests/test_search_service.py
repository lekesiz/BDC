"""Tests for search service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.search_service import SearchService


class TestSearchService:
    """Test the SearchService class."""
    
    def test_global_search_empty_query(self):
        """Test global search with empty query."""
        user = Mock()
        result = SearchService.global_search('', user)
        
        expected = {
            'users': [],
            'beneficiaries': [],
            'documents': [],
            'tests': [],
            'programs': [],
            'reports': []
        }
        assert result == expected
    
    @patch('app.services.search_service.User')
    @patch('app.services.search_service.Beneficiary')
    @patch('app.services.search_service.Document')
    @patch('app.services.search_service.Test')
    @patch('app.services.search_service.Program')
    @patch('app.services.search_service.Report')
    def test_global_search_super_admin(self, mock_report, mock_program, mock_test,
                                     mock_document, mock_beneficiary, mock_user):
        """Test global search as super admin."""
        # Setup user
        user = Mock()
        user.role = 'super_admin'
        user.tenant_id = 1
        user.id = 1
        
        # Setup mock queries
        mock_user_query = Mock()
        mock_user_query.filter.return_value = mock_user_query
        mock_user_query.limit.return_value = mock_user_query
        mock_user_query.all.return_value = []
        mock_user.query = mock_user_query
        
        mock_beneficiary_query = Mock()
        mock_beneficiary_query.filter.return_value = mock_beneficiary_query
        mock_beneficiary_query.limit.return_value = mock_beneficiary_query
        mock_beneficiary_query.all.return_value = []
        mock_beneficiary.query = mock_beneficiary_query
        
        mock_document_query = Mock()
        mock_document_query.filter.return_value = mock_document_query
        mock_document_query.limit.return_value = mock_document_query
        mock_document_query.all.return_value = []
        mock_document.query = mock_document_query
        
        mock_test_query = Mock()
        mock_test_query.filter.return_value = mock_test_query
        mock_test_query.limit.return_value = mock_test_query
        mock_test_query.all.return_value = []
        mock_test.query = mock_test_query
        
        mock_program_query = Mock()
        mock_program_query.filter.return_value = mock_program_query
        mock_program_query.limit.return_value = mock_program_query
        mock_program_query.all.return_value = []
        mock_program.query = mock_program_query
        
        mock_report_query = Mock()
        mock_report_query.filter.return_value = mock_report_query
        mock_report_query.filter_by.return_value = mock_report_query
        mock_report_query.limit.return_value = mock_report_query
        mock_report_query.all.return_value = []
        mock_report.query = mock_report_query
        
        result = SearchService.global_search('test query', user, limit=5)
        
        # Verify all searches were performed
        assert mock_user_query.filter.called
        assert mock_beneficiary_query.filter.called
        assert mock_document_query.filter.called
        assert mock_test_query.filter.called
        assert mock_program_query.filter.called
        assert mock_report_query.filter.called
        
        # Verify limit was applied
        mock_user_query.limit.assert_called_with(5)
    
    @patch('app.services.search_service.User')
    @patch('app.services.search_service.Beneficiary')
    def test_global_search_tenant_admin(self, mock_beneficiary, mock_user):
        """Test global search as tenant admin."""
        # Setup user
        user = Mock()
        user.role = 'tenant_admin'
        user.tenant_id = 2
        user.id = 10
        
        # Setup mock user query
        mock_user_query = Mock()
        mock_user_query.filter.return_value = mock_user_query
        mock_user_query.filter_by.return_value = mock_user_query
        mock_user_query.limit.return_value = mock_user_query
        mock_user_query.all.return_value = []
        mock_user.query = mock_user_query
        
        # Setup mock beneficiary query
        mock_beneficiary_query = Mock()
        mock_beneficiary_query.filter.return_value = mock_beneficiary_query
        mock_beneficiary_query.filter_by.return_value = mock_beneficiary_query
        mock_beneficiary_query.limit.return_value = mock_beneficiary_query
        mock_beneficiary_query.all.return_value = []
        mock_beneficiary.query = mock_beneficiary_query
        
        # Mock other models to avoid errors
        with patch('app.services.search_service.Document'), \
             patch('app.services.search_service.Test'), \
             patch('app.services.search_service.Program'), \
             patch('app.services.search_service.Report'):
            
            SearchService.global_search('search term', user)
            
            # Verify tenant filtering was applied
            mock_user_query.filter_by.assert_called_with(tenant_id=2)
            mock_beneficiary_query.filter_by.assert_called_with(tenant_id=2)
    
    @patch('app.services.search_service.Beneficiary')
    def test_global_search_trainer(self, mock_beneficiary):
        """Test global search as trainer."""
        # Setup user
        user = Mock()
        user.role = 'trainer'
        user.id = 20
        
        # Setup mock beneficiary query
        mock_beneficiary_query = Mock()
        mock_beneficiary_query.filter.return_value = mock_beneficiary_query
        mock_beneficiary_query.filter_by.return_value = mock_beneficiary_query
        mock_beneficiary_query.limit.return_value = mock_beneficiary_query
        mock_beneficiary_query.all.return_value = []
        mock_beneficiary.query = mock_beneficiary_query
        
        # Mock other models
        with patch('app.services.search_service.User'), \
             patch('app.services.search_service.Document'), \
             patch('app.services.search_service.Test'), \
             patch('app.services.search_service.Program'), \
             patch('app.services.search_service.Report'):
            
            SearchService.global_search('search', user)
            
            # Verify trainer filtering was applied
            mock_beneficiary_query.filter_by.assert_called_with(trainer_id=20)
    
    def test_apply_filters_none_value(self):
        """Test apply_filters with None values."""
        query = Mock()
        model = Mock()
        
        result = SearchService.apply_filters(query, model, {'field': None})
        
        assert result == query
        assert not query.filter.called
    
    def test_apply_filters_range(self):
        """Test apply_filters with range values."""
        query = Mock()
        query.filter.return_value = query
        model = Mock()
        model.age = Mock()
        
        filters = {
            'age': {'min': 18, 'max': 65}
        }
        
        result = SearchService.apply_filters(query, model, filters)
        
        assert query.filter.call_count == 2
    
    def test_apply_filters_list(self):
        """Test apply_filters with list values."""
        query = Mock()
        query.filter.return_value = query
        model = Mock()
        model.status = Mock()
        model.status.in_ = Mock()
        
        filters = {
            'status': ['active', 'pending']
        }
        
        result = SearchService.apply_filters(query, model, filters)
        
        assert query.filter.called
        model.status.in_.assert_called_with(['active', 'pending'])
    
    def test_apply_filters_string(self):
        """Test apply_filters with string values."""
        query = Mock()
        query.filter.return_value = query
        model = Mock()
        model.name = Mock()
        
        filters = {
            'name': 'john'
        }
        
        with patch('app.services.search_service.func') as mock_func:
            mock_func.lower.return_value.contains.return_value = Mock()
            
            result = SearchService.apply_filters(query, model, filters)
            
            assert query.filter.called
    
    def test_apply_filters_exact_match(self):
        """Test apply_filters with exact match."""
        query = Mock()
        query.filter.return_value = query
        model = Mock()
        model.id = 123
        
        filters = {
            'id': 123
        }
        
        result = SearchService.apply_filters(query, model, filters)
        
        assert query.filter.called
    
    def test_apply_sorting_no_sort_by(self):
        """Test apply_sorting with no sort_by."""
        query = Mock()
        model = Mock()
        
        result = SearchService.apply_sorting(query, model, None)
        
        assert result == query
        assert not query.order_by.called
    
    def test_apply_sorting_invalid_field(self):
        """Test apply_sorting with invalid field."""
        query = Mock()
        model = Mock()
        
        result = SearchService.apply_sorting(query, model, 'invalid_field')
        
        assert result == query
        assert not query.order_by.called
    
    def test_apply_sorting_asc(self):
        """Test apply_sorting ascending."""
        query = Mock()
        query.order_by.return_value = query
        model = Mock()
        model.name = Mock()
        
        result = SearchService.apply_sorting(query, model, 'name', 'asc')
        
        query.order_by.assert_called_with(model.name)
    
    def test_apply_sorting_desc(self):
        """Test apply_sorting descending."""
        query = Mock()
        query.order_by.return_value = query
        model = Mock()
        model.created_at = Mock()
        model.created_at.desc.return_value = Mock()
        
        result = SearchService.apply_sorting(query, model, 'created_at', 'desc')
        
        model.created_at.desc.assert_called_once()
        query.order_by.assert_called_once()
    
    def test_paginate_query(self):
        """Test paginate_query."""
        # Mock query and pagination
        query = Mock()
        pagination = Mock()
        pagination.items = [Mock(to_dict=lambda: {'id': 1}), Mock(to_dict=lambda: {'id': 2})]
        pagination.total = 100
        pagination.pages = 10
        pagination.page = 1
        pagination.per_page = 10
        pagination.has_next = True
        pagination.has_prev = False
        query.paginate.return_value = pagination
        
        result = SearchService.paginate_query(query, page=1, per_page=10)
        
        query.paginate.assert_called_with(page=1, per_page=10, error_out=False)
        
        assert result['items'] == [{'id': 1}, {'id': 2}]
        assert result['total'] == 100
        assert result['pages'] == 10
        assert result['current_page'] == 1
        assert result['per_page'] == 10
        assert result['has_next'] is True
        assert result['has_prev'] is False