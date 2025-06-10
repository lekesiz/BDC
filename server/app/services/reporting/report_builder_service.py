"""
Report Builder Service

Provides drag-and-drop report building capabilities with:
- Dynamic field selection and arrangement
- Advanced filtering and grouping
- Custom layout configuration
- Template management
- Real-time preview
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.orm import Session

from app.models.report import Report
from app.models.beneficiary import Beneficiary
from app.models.program import Program
from app.models.evaluation import Evaluation
from app.models.appointment import Appointment
from app.core.database_manager import DatabaseManager


class ReportBuilderService:
    """Service for building custom reports with drag-and-drop functionality"""

    def __init__(self, db_session: Session = None):
        self.db = db_session or DatabaseManager.get_session()
        self.available_fields = self._get_available_fields()
        
    def _get_available_fields(self) -> Dict[str, List[Dict]]:
        """Get all available fields for report building"""
        return {
            'beneficiaries': [
                {'id': 'id', 'name': 'ID', 'type': 'number', 'category': 'identity'},
                {'id': 'first_name', 'name': 'First Name', 'type': 'text', 'category': 'identity'},
                {'id': 'last_name', 'name': 'Last Name', 'type': 'text', 'category': 'identity'},
                {'id': 'email', 'name': 'Email', 'type': 'email', 'category': 'contact'},
                {'id': 'phone', 'name': 'Phone', 'type': 'phone', 'category': 'contact'},
                {'id': 'date_of_birth', 'name': 'Date of Birth', 'type': 'date', 'category': 'demographics'},
                {'id': 'gender', 'name': 'Gender', 'type': 'text', 'category': 'demographics'},
                {'id': 'status', 'name': 'Status', 'type': 'select', 'category': 'status'},
                {'id': 'created_at', 'name': 'Registration Date', 'type': 'datetime', 'category': 'timeline'},
                {'id': 'updated_at', 'name': 'Last Updated', 'type': 'datetime', 'category': 'timeline'},
            ],
            'programs': [
                {'id': 'id', 'name': 'Program ID', 'type': 'number', 'category': 'identity'},
                {'id': 'name', 'name': 'Program Name', 'type': 'text', 'category': 'details'},
                {'id': 'description', 'name': 'Description', 'type': 'text', 'category': 'details'},
                {'id': 'start_date', 'name': 'Start Date', 'type': 'date', 'category': 'timeline'},
                {'id': 'end_date', 'name': 'End Date', 'type': 'date', 'category': 'timeline'},
                {'id': 'status', 'name': 'Status', 'type': 'select', 'category': 'status'},
                {'id': 'capacity', 'name': 'Capacity', 'type': 'number', 'category': 'metrics'},
                {'id': 'enrolled_count', 'name': 'Enrolled Count', 'type': 'number', 'category': 'metrics'},
                {'id': 'completion_rate', 'name': 'Completion Rate', 'type': 'percentage', 'category': 'metrics'},
            ],
            'evaluations': [
                {'id': 'id', 'name': 'Evaluation ID', 'type': 'number', 'category': 'identity'},
                {'id': 'title', 'name': 'Title', 'type': 'text', 'category': 'details'},
                {'id': 'score', 'name': 'Score', 'type': 'number', 'category': 'performance'},
                {'id': 'max_score', 'name': 'Max Score', 'type': 'number', 'category': 'performance'},
                {'id': 'percentage', 'name': 'Percentage', 'type': 'percentage', 'category': 'performance'},
                {'id': 'passed', 'name': 'Passed', 'type': 'boolean', 'category': 'performance'},
                {'id': 'submitted_at', 'name': 'Submitted Date', 'type': 'datetime', 'category': 'timeline'},
                {'id': 'graded_at', 'name': 'Graded Date', 'type': 'datetime', 'category': 'timeline'},
            ],
            'appointments': [
                {'id': 'id', 'name': 'Appointment ID', 'type': 'number', 'category': 'identity'},
                {'id': 'title', 'name': 'Title', 'type': 'text', 'category': 'details'},
                {'id': 'start_time', 'name': 'Start Time', 'type': 'datetime', 'category': 'schedule'},
                {'id': 'end_time', 'name': 'End Time', 'type': 'datetime', 'category': 'schedule'},
                {'id': 'status', 'name': 'Status', 'type': 'select', 'category': 'status'},
                {'id': 'attendance', 'name': 'Attendance', 'type': 'select', 'category': 'status'},
                {'id': 'location', 'name': 'Location', 'type': 'text', 'category': 'details'},
                {'id': 'notes', 'name': 'Notes', 'type': 'text', 'category': 'details'},
            ]
        }

    def get_available_fields(self) -> Dict[str, List[Dict]]:
        """Return available fields for the report builder"""
        return self.available_fields

    def create_report_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new report template"""
        template = {
            'id': str(uuid.uuid4()),
            'name': template_data.get('name', 'Untitled Report'),
            'description': template_data.get('description', ''),
            'layout': template_data.get('layout', {}),
            'fields': template_data.get('fields', []),
            'filters': template_data.get('filters', []),
            'grouping': template_data.get('grouping', []),
            'sorting': template_data.get('sorting', []),
            'styling': template_data.get('styling', {}),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'created_by': template_data.get('created_by'),
            'is_public': template_data.get('is_public', False),
            'category': template_data.get('category', 'custom')
        }
        
        # Save template to database
        report = Report(
            name=template['name'],
            description=template['description'],
            template_data=json.dumps(template),
            created_by=template['created_by'],
            is_template=True
        )
        
        self.db.add(report)
        self.db.commit()
        
        template['id'] = str(report.id)
        return template

    def update_report_template(self, template_id: str, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing report template"""
        report = self.db.query(Report).filter(Report.id == template_id).first()
        if not report:
            raise ValueError(f"Template with ID {template_id} not found")
        
        # Update template data
        existing_template = json.loads(report.template_data) if report.template_data else {}
        existing_template.update({
            'name': template_data.get('name', existing_template.get('name')),
            'description': template_data.get('description', existing_template.get('description')),
            'layout': template_data.get('layout', existing_template.get('layout', {})),
            'fields': template_data.get('fields', existing_template.get('fields', [])),
            'filters': template_data.get('filters', existing_template.get('filters', [])),
            'grouping': template_data.get('grouping', existing_template.get('grouping', [])),
            'sorting': template_data.get('sorting', existing_template.get('sorting', [])),
            'styling': template_data.get('styling', existing_template.get('styling', {})),
            'updated_at': datetime.utcnow().isoformat()
        })
        
        report.name = existing_template['name']
        report.description = existing_template['description']
        report.template_data = json.dumps(existing_template)
        
        self.db.commit()
        return existing_template

    def get_report_templates(self, user_id: Optional[str] = None, 
                           category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get available report templates"""
        query = self.db.query(Report).filter(Report.is_template == True)
        
        if user_id:
            query = query.filter(
                or_(Report.created_by == user_id, Report.is_public == True)
            )
        
        templates = []
        for report in query.all():
            template_data = json.loads(report.template_data) if report.template_data else {}
            
            if category and template_data.get('category') != category:
                continue
                
            templates.append({
                'id': str(report.id),
                'name': report.name,
                'description': report.description,
                'category': template_data.get('category', 'custom'),
                'created_at': template_data.get('created_at'),
                'updated_at': template_data.get('updated_at'),
                'created_by': report.created_by,
                'is_public': template_data.get('is_public', False),
                'preview': self._generate_template_preview(template_data)
            })
        
        return templates

    def _generate_template_preview(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a preview of the template"""
        return {
            'field_count': len(template_data.get('fields', [])),
            'filter_count': len(template_data.get('filters', [])),
            'grouping_count': len(template_data.get('grouping', [])),
            'layout_type': template_data.get('layout', {}).get('type', 'table'),
            'data_sources': list(set(
                field.get('source', 'unknown') 
                for field in template_data.get('fields', [])
            ))
        }

    def build_query(self, fields: List[Dict], filters: List[Dict], 
                   grouping: List[Dict], sorting: List[Dict]) -> Dict[str, Any]:
        """Build SQL query based on report configuration"""
        
        # Determine main data source
        data_sources = set(field.get('source') for field in fields)
        
        if 'beneficiaries' in data_sources:
            base_query = self.db.query(Beneficiary)
            main_table = 'beneficiaries'
        elif 'programs' in data_sources:
            base_query = self.db.query(Program)
            main_table = 'programs'
        elif 'evaluations' in data_sources:
            base_query = self.db.query(Evaluation)
            main_table = 'evaluations'
        elif 'appointments' in data_sources:
            base_query = self.db.query(Appointment)
            main_table = 'appointments'
        else:
            raise ValueError("No valid data source found in fields")

        # Apply joins if multiple data sources
        if len(data_sources) > 1:
            base_query = self._apply_joins(base_query, data_sources, main_table)

        # Apply filters
        if filters:
            base_query = self._apply_filters(base_query, filters)

        # Apply grouping
        if grouping:
            base_query = self._apply_grouping(base_query, grouping)

        # Apply sorting
        if sorting:
            base_query = self._apply_sorting(base_query, sorting)

        return {
            'query': base_query,
            'main_table': main_table,
            'data_sources': list(data_sources)
        }

    def _apply_joins(self, query, data_sources: set, main_table: str):
        """Apply necessary joins based on data sources"""
        
        if main_table == 'beneficiaries':
            if 'programs' in data_sources:
                query = query.join(Program, Beneficiary.programs)
            if 'evaluations' in data_sources:
                query = query.join(Evaluation, Beneficiary.evaluations)
            if 'appointments' in data_sources:
                query = query.join(Appointment, Beneficiary.appointments)
                
        elif main_table == 'programs':
            if 'beneficiaries' in data_sources:
                query = query.join(Beneficiary, Program.beneficiaries)
            if 'evaluations' in data_sources:
                query = query.join(Evaluation, Program.evaluations)
                
        elif main_table == 'evaluations':
            if 'beneficiaries' in data_sources:
                query = query.join(Beneficiary, Evaluation.beneficiary)
            if 'programs' in data_sources:
                query = query.join(Program, Evaluation.program)
                
        elif main_table == 'appointments':
            if 'beneficiaries' in data_sources:
                query = query.join(Beneficiary, Appointment.beneficiary)

        return query

    def _apply_filters(self, query, filters: List[Dict]):
        """Apply filters to the query"""
        
        for filter_config in filters:
            field = filter_config.get('field')
            operator = filter_config.get('operator', 'equals')
            value = filter_config.get('value')
            source = filter_config.get('source', 'beneficiaries')
            
            # Get the appropriate model class
            model_class = self._get_model_class(source)
            if not model_class:
                continue
                
            # Get the field attribute
            field_attr = getattr(model_class, field, None)
            if not field_attr:
                continue
            
            # Apply the filter based on operator
            if operator == 'equals':
                query = query.filter(field_attr == value)
            elif operator == 'not_equals':
                query = query.filter(field_attr != value)
            elif operator == 'contains':
                query = query.filter(field_attr.like(f'%{value}%'))
            elif operator == 'starts_with':
                query = query.filter(field_attr.like(f'{value}%'))
            elif operator == 'ends_with':
                query = query.filter(field_attr.like(f'%{value}'))
            elif operator == 'greater_than':
                query = query.filter(field_attr > value)
            elif operator == 'less_than':
                query = query.filter(field_attr < value)
            elif operator == 'greater_equal':
                query = query.filter(field_attr >= value)
            elif operator == 'less_equal':
                query = query.filter(field_attr <= value)
            elif operator == 'between':
                if isinstance(value, list) and len(value) == 2:
                    query = query.filter(field_attr.between(value[0], value[1]))
            elif operator == 'in':
                if isinstance(value, list):
                    query = query.filter(field_attr.in_(value))
            elif operator == 'not_in':
                if isinstance(value, list):
                    query = query.filter(~field_attr.in_(value))
            elif operator == 'is_null':
                query = query.filter(field_attr.is_(None))
            elif operator == 'is_not_null':
                query = query.filter(field_attr.isnot(None))
                
        return query

    def _apply_grouping(self, query, grouping: List[Dict]):
        """Apply grouping to the query"""
        
        group_fields = []
        for group_config in grouping:
            field = group_config.get('field')
            source = group_config.get('source', 'beneficiaries')
            
            model_class = self._get_model_class(source)
            if model_class:
                field_attr = getattr(model_class, field, None)
                if field_attr:
                    group_fields.append(field_attr)
        
        if group_fields:
            query = query.group_by(*group_fields)
            
        return query

    def _apply_sorting(self, query, sorting: List[Dict]):
        """Apply sorting to the query"""
        
        for sort_config in sorting:
            field = sort_config.get('field')
            direction = sort_config.get('direction', 'asc')
            source = sort_config.get('source', 'beneficiaries')
            
            model_class = self._get_model_class(source)
            if model_class:
                field_attr = getattr(model_class, field, None)
                if field_attr:
                    if direction == 'desc':
                        query = query.order_by(desc(field_attr))
                    else:
                        query = query.order_by(asc(field_attr))
                        
        return query

    def _get_model_class(self, source: str):
        """Get the model class for a data source"""
        model_map = {
            'beneficiaries': Beneficiary,
            'programs': Program,
            'evaluations': Evaluation,
            'appointments': Appointment
        }
        return model_map.get(source)

    def execute_report(self, report_config: Dict[str, Any], 
                      limit: Optional[int] = None, 
                      offset: Optional[int] = None) -> Dict[str, Any]:
        """Execute a report and return the results"""
        
        fields = report_config.get('fields', [])
        filters = report_config.get('filters', [])
        grouping = report_config.get('grouping', [])
        sorting = report_config.get('sorting', [])
        
        # Build query
        query_info = self.build_query(fields, filters, grouping, sorting)
        query = query_info['query']
        
        # Apply pagination
        total_count = query.count()
        
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        
        # Execute query
        results = query.all()
        
        # Format results
        formatted_results = []
        for row in results:
            formatted_row = {}
            for field in fields:
                field_name = field.get('field')
                source = field.get('source', 'beneficiaries')
                alias = field.get('alias', field_name)
                
                # Extract value from row
                if hasattr(row, field_name):
                    value = getattr(row, field_name)
                    
                    # Format value based on field type
                    field_type = field.get('type', 'text')
                    formatted_value = self._format_field_value(value, field_type)
                    formatted_row[alias] = formatted_value
            
            formatted_results.append(formatted_row)
        
        return {
            'data': formatted_results,
            'total_count': total_count,
            'limit': limit,
            'offset': offset,
            'fields': fields,
            'metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'data_sources': query_info['data_sources'],
                'filter_count': len(filters),
                'group_count': len(grouping),
                'sort_count': len(sorting)
            }
        }

    def _format_field_value(self, value: Any, field_type: str) -> Any:
        """Format field value based on type"""
        
        if value is None:
            return None
            
        if field_type == 'date' and hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        elif field_type == 'datetime' and hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        elif field_type == 'percentage' and isinstance(value, (int, float)):
            return f"{value:.2f}%"
        elif field_type == 'currency' and isinstance(value, (int, float)):
            return f"${value:.2f}"
        elif field_type == 'boolean':
            return bool(value)
        
        return value

    def get_field_suggestions(self, source: str, search_term: str = '') -> List[Dict]:
        """Get field suggestions for autocomplete"""
        
        available_fields = self.available_fields.get(source, [])
        
        if not search_term:
            return available_fields
            
        # Filter fields based on search term
        filtered_fields = [
            field for field in available_fields
            if search_term.lower() in field['name'].lower() or 
               search_term.lower() in field['id'].lower()
        ]
        
        return filtered_fields

    def validate_report_config(self, report_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate report configuration"""
        
        errors = []
        warnings = []
        
        # Check required fields
        if not report_config.get('fields'):
            errors.append("At least one field must be selected")
        
        # Validate fields
        for field in report_config.get('fields', []):
            if not field.get('field'):
                errors.append("Field name is required")
            if not field.get('source'):
                errors.append("Field source is required")
        
        # Validate filters
        for filter_config in report_config.get('filters', []):
            if not filter_config.get('field'):
                errors.append("Filter field is required")
            if 'value' not in filter_config:
                errors.append("Filter value is required")
        
        # Check for performance issues
        field_count = len(report_config.get('fields', []))
        if field_count > 50:
            warnings.append(f"Large number of fields ({field_count}) may impact performance")
        
        filter_count = len(report_config.get('filters', []))
        if filter_count > 20:
            warnings.append(f"Large number of filters ({filter_count}) may impact performance")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def preview_report(self, report_config: Dict[str, Any], sample_size: int = 10) -> Dict[str, Any]:
        """Generate a preview of the report with limited data"""
        
        # Validate configuration
        validation = self.validate_report_config(report_config)
        if not validation['is_valid']:
            return {
                'success': False,
                'errors': validation['errors']
            }
        
        try:
            # Execute report with limited data
            results = self.execute_report(report_config, limit=sample_size)
            
            return {
                'success': True,
                'preview_data': results['data'],
                'total_available': results['total_count'],
                'sample_size': sample_size,
                'warnings': validation.get('warnings', [])
            }
            
        except Exception as e:
            return {
                'success': False,
                'errors': [str(e)]
            }