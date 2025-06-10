"""
Dashboard Service

Provides custom dashboard creation with widgets:
- Widget management and configuration
- Layout management with drag-and-drop
- Data source integration
- Real-time dashboard updates
- Dashboard templates and sharing
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import and_, or_, desc, func
from sqlalchemy.orm import Session

from app.models.report import Report
from app.core.database_manager import DatabaseManager
from .report_builder_service import ReportBuilderService


class DashboardService:
    """Service for creating and managing custom dashboards with widgets"""

    def __init__(self, db_session: Session = None):
        self.db = db_session or DatabaseManager.get_session()
        self.report_builder = ReportBuilderService(self.db)
        self.widget_types = self._get_widget_types()
        
    def _get_widget_types(self) -> Dict[str, Dict]:
        """Get available widget types and their configurations"""
        return {
            'chart': {
                'name': 'Chart Widget',
                'description': 'Display data in various chart formats',
                'icon': 'chart-bar',
                'config_schema': {
                    'chart_type': {
                        'type': 'select',
                        'options': ['bar', 'line', 'pie', 'doughnut', 'area', 'scatter'],
                        'default': 'bar'
                    },
                    'data_source': {'type': 'select', 'required': True},
                    'x_axis': {'type': 'field_select', 'required': True},
                    'y_axis': {'type': 'field_select', 'required': True},
                    'group_by': {'type': 'field_select'},
                    'aggregation': {
                        'type': 'select',
                        'options': ['sum', 'count', 'avg', 'min', 'max'],
                        'default': 'count'
                    },
                    'colors': {'type': 'color_palette'},
                    'show_legend': {'type': 'boolean', 'default': True},
                    'show_labels': {'type': 'boolean', 'default': True}
                }
            },
            'metric': {
                'name': 'Metric Widget',
                'description': 'Display key performance indicators',
                'icon': 'gauge',
                'config_schema': {
                    'metric_type': {
                        'type': 'select',
                        'options': ['single_value', 'comparison', 'progress', 'goal_tracking'],
                        'default': 'single_value'
                    },
                    'data_source': {'type': 'select', 'required': True},
                    'metric_field': {'type': 'field_select', 'required': True},
                    'aggregation': {
                        'type': 'select',
                        'options': ['sum', 'count', 'avg', 'min', 'max'],
                        'default': 'count'
                    },
                    'format': {
                        'type': 'select',
                        'options': ['number', 'currency', 'percentage'],
                        'default': 'number'
                    },
                    'target_value': {'type': 'number'},
                    'comparison_period': {
                        'type': 'select',
                        'options': ['previous_day', 'previous_week', 'previous_month', 'previous_year']
                    },
                    'color': {'type': 'color'},
                    'icon': {'type': 'icon_select'}
                }
            },
            'table': {
                'name': 'Data Table',
                'description': 'Display data in tabular format',
                'icon': 'table',
                'config_schema': {
                    'data_source': {'type': 'select', 'required': True},
                    'columns': {'type': 'field_multi_select', 'required': True},
                    'pagination': {'type': 'boolean', 'default': True},
                    'page_size': {'type': 'number', 'default': 10},
                    'sorting': {'type': 'boolean', 'default': True},
                    'filtering': {'type': 'boolean', 'default': True},
                    'search': {'type': 'boolean', 'default': True},
                    'export': {'type': 'boolean', 'default': True}
                }
            },
            'map': {
                'name': 'Geographic Map',
                'description': 'Display data on interactive maps',
                'icon': 'map',
                'config_schema': {
                    'map_type': {
                        'type': 'select',
                        'options': ['choropleth', 'markers', 'heatmap', 'cluster'],
                        'default': 'markers'
                    },
                    'data_source': {'type': 'select', 'required': True},
                    'location_field': {'type': 'field_select', 'required': True},
                    'value_field': {'type': 'field_select'},
                    'zoom_level': {'type': 'number', 'default': 10},
                    'center_lat': {'type': 'number'},
                    'center_lng': {'type': 'number'},
                    'color_scale': {'type': 'color_scale'}
                }
            },
            'calendar': {
                'name': 'Calendar View',
                'description': 'Display scheduled events and appointments',
                'icon': 'calendar',
                'config_schema': {
                    'data_source': {'type': 'select', 'required': True},
                    'date_field': {'type': 'field_select', 'required': True},
                    'title_field': {'type': 'field_select', 'required': True},
                    'view_type': {
                        'type': 'select',
                        'options': ['month', 'week', 'day', 'agenda'],
                        'default': 'month'
                    },
                    'color_field': {'type': 'field_select'},
                    'show_weekends': {'type': 'boolean', 'default': True}
                }
            },
            'progress': {
                'name': 'Progress Tracker',
                'description': 'Track progress towards goals',
                'icon': 'progress',
                'config_schema': {
                    'progress_type': {
                        'type': 'select',
                        'options': ['linear', 'circular', 'stepped'],
                        'default': 'linear'
                    },
                    'data_source': {'type': 'select', 'required': True},
                    'current_field': {'type': 'field_select', 'required': True},
                    'target_field': {'type': 'field_select'},
                    'target_value': {'type': 'number'},
                    'show_percentage': {'type': 'boolean', 'default': True},
                    'color_scheme': {
                        'type': 'select',
                        'options': ['default', 'success', 'warning', 'danger'],
                        'default': 'default'
                    }
                }
            },
            'text': {
                'name': 'Text Widget',
                'description': 'Display custom text and markdown content',
                'icon': 'text',
                'config_schema': {
                    'content_type': {
                        'type': 'select',
                        'options': ['plain_text', 'markdown', 'html'],
                        'default': 'markdown'
                    },
                    'content': {'type': 'textarea', 'required': True},
                    'font_size': {
                        'type': 'select',
                        'options': ['small', 'medium', 'large', 'extra_large'],
                        'default': 'medium'
                    },
                    'text_align': {
                        'type': 'select',
                        'options': ['left', 'center', 'right'],
                        'default': 'left'
                    },
                    'background_color': {'type': 'color'},
                    'text_color': {'type': 'color'}
                }
            }
        }

    def get_widget_types(self) -> Dict[str, Dict]:
        """Return available widget types"""
        return self.widget_types

    def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dashboard"""
        dashboard = {
            'id': str(uuid.uuid4()),
            'name': dashboard_data.get('name', 'Untitled Dashboard'),
            'description': dashboard_data.get('description', ''),
            'layout': dashboard_data.get('layout', {'type': 'grid', 'columns': 12}),
            'widgets': dashboard_data.get('widgets', []),
            'filters': dashboard_data.get('filters', []),
            'refresh_interval': dashboard_data.get('refresh_interval', 300),  # 5 minutes
            'is_public': dashboard_data.get('is_public', False),
            'theme': dashboard_data.get('theme', 'light'),
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'created_by': dashboard_data.get('created_by'),
            'shared_with': dashboard_data.get('shared_with', []),
            'tags': dashboard_data.get('tags', [])
        }
        
        # Save dashboard to database
        report = Report(
            name=dashboard['name'],
            description=dashboard['description'],
            template_data=json.dumps(dashboard),
            created_by=dashboard['created_by'],
            is_template=False,
            report_type='dashboard'
        )
        
        self.db.add(report)
        self.db.commit()
        
        dashboard['id'] = str(report.id)
        return dashboard

    def update_dashboard(self, dashboard_id: str, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing dashboard"""
        report = self.db.query(Report).filter(Report.id == dashboard_id).first()
        if not report:
            raise ValueError(f"Dashboard with ID {dashboard_id} not found")
        
        # Update dashboard data
        existing_dashboard = json.loads(report.template_data) if report.template_data else {}
        existing_dashboard.update({
            'name': dashboard_data.get('name', existing_dashboard.get('name')),
            'description': dashboard_data.get('description', existing_dashboard.get('description')),
            'layout': dashboard_data.get('layout', existing_dashboard.get('layout')),
            'widgets': dashboard_data.get('widgets', existing_dashboard.get('widgets', [])),
            'filters': dashboard_data.get('filters', existing_dashboard.get('filters', [])),
            'refresh_interval': dashboard_data.get('refresh_interval', existing_dashboard.get('refresh_interval')),
            'is_public': dashboard_data.get('is_public', existing_dashboard.get('is_public')),
            'theme': dashboard_data.get('theme', existing_dashboard.get('theme')),
            'updated_at': datetime.utcnow().isoformat(),
            'shared_with': dashboard_data.get('shared_with', existing_dashboard.get('shared_with', [])),
            'tags': dashboard_data.get('tags', existing_dashboard.get('tags', []))
        })
        
        report.name = existing_dashboard['name']
        report.description = existing_dashboard['description']
        report.template_data = json.dumps(existing_dashboard)
        
        self.db.commit()
        return existing_dashboard

    def get_dashboards(self, user_id: Optional[str] = None, 
                      tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get user's dashboards"""
        query = self.db.query(Report).filter(
            and_(Report.is_template == False, Report.report_type == 'dashboard')
        )
        
        if user_id:
            query = query.filter(
                or_(Report.created_by == user_id, Report.is_public == True)
            )
        
        dashboards = []
        for report in query.all():
            dashboard_data = json.loads(report.template_data) if report.template_data else {}
            
            # Filter by tags if provided
            if tags:
                dashboard_tags = dashboard_data.get('tags', [])
                if not any(tag in dashboard_tags for tag in tags):
                    continue
            
            dashboards.append({
                'id': str(report.id),
                'name': report.name,
                'description': report.description,
                'widget_count': len(dashboard_data.get('widgets', [])),
                'created_at': dashboard_data.get('created_at'),
                'updated_at': dashboard_data.get('updated_at'),
                'created_by': report.created_by,
                'is_public': dashboard_data.get('is_public', False),
                'theme': dashboard_data.get('theme', 'light'),
                'tags': dashboard_data.get('tags', []),
                'preview': self._generate_dashboard_preview(dashboard_data)
            })
        
        return dashboards

    def get_dashboard(self, dashboard_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get a specific dashboard"""
        report = self.db.query(Report).filter(Report.id == dashboard_id).first()
        if not report:
            raise ValueError(f"Dashboard with ID {dashboard_id} not found")
        
        dashboard_data = json.loads(report.template_data) if report.template_data else {}
        
        # Check access permissions
        if user_id:
            is_owner = report.created_by == user_id
            is_public = dashboard_data.get('is_public', False)
            is_shared = user_id in dashboard_data.get('shared_with', [])
            
            if not (is_owner or is_public or is_shared):
                raise PermissionError("Access denied to this dashboard")
        
        # Load widget data
        widgets_with_data = []
        for widget in dashboard_data.get('widgets', []):
            widget_with_data = self.load_widget_data(widget)
            widgets_with_data.append(widget_with_data)
        
        dashboard_data['widgets'] = widgets_with_data
        dashboard_data['id'] = str(report.id)
        
        return dashboard_data

    def add_widget(self, dashboard_id: str, widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a widget to a dashboard"""
        dashboard = self.get_dashboard(dashboard_id)
        
        # Generate widget ID
        widget_id = str(uuid.uuid4())
        widget_config['id'] = widget_id
        widget_config['created_at'] = datetime.utcnow().isoformat()
        
        # Validate widget configuration
        validation_result = self.validate_widget_config(widget_config)
        if not validation_result['is_valid']:
            raise ValueError(f"Invalid widget configuration: {validation_result['errors']}")
        
        # Add widget to dashboard
        dashboard['widgets'].append(widget_config)
        dashboard['updated_at'] = datetime.utcnow().isoformat()
        
        # Update dashboard in database
        self.update_dashboard(dashboard_id, dashboard)
        
        return widget_config

    def update_widget(self, dashboard_id: str, widget_id: str, 
                     widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update a widget in a dashboard"""
        dashboard = self.get_dashboard(dashboard_id)
        
        # Find and update widget
        widget_found = False
        for i, widget in enumerate(dashboard['widgets']):
            if widget.get('id') == widget_id:
                widget_config['id'] = widget_id
                widget_config['updated_at'] = datetime.utcnow().isoformat()
                
                # Validate widget configuration
                validation_result = self.validate_widget_config(widget_config)
                if not validation_result['is_valid']:
                    raise ValueError(f"Invalid widget configuration: {validation_result['errors']}")
                
                dashboard['widgets'][i] = widget_config
                widget_found = True
                break
        
        if not widget_found:
            raise ValueError(f"Widget with ID {widget_id} not found")
        
        dashboard['updated_at'] = datetime.utcnow().isoformat()
        
        # Update dashboard in database
        self.update_dashboard(dashboard_id, dashboard)
        
        return widget_config

    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove a widget from a dashboard"""
        dashboard = self.get_dashboard(dashboard_id)
        
        # Find and remove widget
        original_count = len(dashboard['widgets'])
        dashboard['widgets'] = [
            widget for widget in dashboard['widgets'] 
            if widget.get('id') != widget_id
        ]
        
        if len(dashboard['widgets']) == original_count:
            raise ValueError(f"Widget with ID {widget_id} not found")
        
        dashboard['updated_at'] = datetime.utcnow().isoformat()
        
        # Update dashboard in database
        self.update_dashboard(dashboard_id, dashboard)
        
        return True

    def load_widget_data(self, widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Load data for a specific widget"""
        widget_type = widget_config.get('type')
        
        if widget_type in ['chart', 'metric', 'table', 'map', 'calendar', 'progress']:
            # These widgets need data from database
            data_config = self._build_widget_data_config(widget_config)
            
            try:
                if data_config:
                    result = self.report_builder.execute_report(
                        data_config, 
                        limit=widget_config.get('data_limit', 1000)
                    )
                    widget_config['data'] = result['data']
                    widget_config['metadata'] = result['metadata']
                else:
                    widget_config['data'] = []
                    widget_config['metadata'] = {}
            except Exception as e:
                widget_config['data'] = []
                widget_config['error'] = str(e)
        
        elif widget_type == 'text':
            # Text widgets don't need dynamic data
            pass
        
        return widget_config

    def _build_widget_data_config(self, widget_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Build data configuration for widget based on its type and settings"""
        widget_type = widget_config.get('type')
        config = widget_config.get('config', {})
        
        if not config.get('data_source'):
            return None
        
        data_config = {
            'fields': [],
            'filters': widget_config.get('filters', []),
            'grouping': [],
            'sorting': []
        }
        
        if widget_type == 'chart':
            # Add X and Y axis fields
            if config.get('x_axis'):
                data_config['fields'].append({
                    'field': config['x_axis'],
                    'source': config['data_source'],
                    'alias': 'x_axis'
                })
            
            if config.get('y_axis'):
                data_config['fields'].append({
                    'field': config['y_axis'],
                    'source': config['data_source'],
                    'alias': 'y_axis'
                })
            
            # Add grouping if specified
            if config.get('group_by'):
                data_config['grouping'].append({
                    'field': config['group_by'],
                    'source': config['data_source']
                })
        
        elif widget_type == 'metric':
            # Add metric field
            if config.get('metric_field'):
                data_config['fields'].append({
                    'field': config['metric_field'],
                    'source': config['data_source'],
                    'alias': 'metric_value',
                    'aggregation': config.get('aggregation', 'count')
                })
        
        elif widget_type == 'table':
            # Add all selected columns
            for column in config.get('columns', []):
                data_config['fields'].append({
                    'field': column,
                    'source': config['data_source'],
                    'alias': column
                })
        
        elif widget_type == 'map':
            # Add location and value fields
            if config.get('location_field'):
                data_config['fields'].append({
                    'field': config['location_field'],
                    'source': config['data_source'],
                    'alias': 'location'
                })
            
            if config.get('value_field'):
                data_config['fields'].append({
                    'field': config['value_field'],
                    'source': config['data_source'],
                    'alias': 'value'
                })
        
        elif widget_type == 'calendar':
            # Add date and title fields
            if config.get('date_field'):
                data_config['fields'].append({
                    'field': config['date_field'],
                    'source': config['data_source'],
                    'alias': 'date'
                })
            
            if config.get('title_field'):
                data_config['fields'].append({
                    'field': config['title_field'],
                    'source': config['data_source'],
                    'alias': 'title'
                })
            
            if config.get('color_field'):
                data_config['fields'].append({
                    'field': config['color_field'],
                    'source': config['data_source'],
                    'alias': 'color'
                })
        
        elif widget_type == 'progress':
            # Add current and target fields
            if config.get('current_field'):
                data_config['fields'].append({
                    'field': config['current_field'],
                    'source': config['data_source'],
                    'alias': 'current_value'
                })
            
            if config.get('target_field'):
                data_config['fields'].append({
                    'field': config['target_field'],
                    'source': config['data_source'],
                    'alias': 'target_value'
                })
        
        return data_config if data_config['fields'] else None

    def validate_widget_config(self, widget_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate widget configuration"""
        errors = []
        warnings = []
        
        widget_type = widget_config.get('type')
        if not widget_type:
            errors.append("Widget type is required")
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
        
        if widget_type not in self.widget_types:
            errors.append(f"Invalid widget type: {widget_type}")
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate against schema
        schema = self.widget_types[widget_type]['config_schema']
        config = widget_config.get('config', {})
        
        for field_name, field_schema in schema.items():
            if field_schema.get('required', False) and field_name not in config:
                errors.append(f"Required field '{field_name}' is missing")
            
            if field_name in config:
                value = config[field_name]
                field_type = field_schema.get('type')
                
                # Type validation
                if field_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Field '{field_name}' must be a number")
                elif field_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Field '{field_name}' must be a boolean")
                elif field_type == 'select' and value not in field_schema.get('options', []):
                    errors.append(f"Field '{field_name}' has invalid value: {value}")
        
        # Layout validation
        layout = widget_config.get('layout', {})
        if 'position' in layout:
            position = layout['position']
            if not all(key in position for key in ['x', 'y', 'width', 'height']):
                errors.append("Widget position must include x, y, width, and height")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def _generate_dashboard_preview(self, dashboard_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a preview of the dashboard"""
        widgets = dashboard_data.get('widgets', [])
        
        widget_types_count = {}
        for widget in widgets:
            widget_type = widget.get('type', 'unknown')
            widget_types_count[widget_type] = widget_types_count.get(widget_type, 0) + 1
        
        return {
            'widget_count': len(widgets),
            'widget_types': widget_types_count,
            'layout_type': dashboard_data.get('layout', {}).get('type', 'grid'),
            'theme': dashboard_data.get('theme', 'light'),
            'has_filters': len(dashboard_data.get('filters', [])) > 0,
            'is_public': dashboard_data.get('is_public', False),
            'refresh_interval': dashboard_data.get('refresh_interval', 300)
        }

    def duplicate_dashboard(self, dashboard_id: str, new_name: str, 
                          user_id: str) -> Dict[str, Any]:
        """Duplicate an existing dashboard"""
        original_dashboard = self.get_dashboard(dashboard_id)
        
        # Create new dashboard data
        new_dashboard_data = original_dashboard.copy()
        new_dashboard_data['name'] = new_name
        new_dashboard_data['created_by'] = user_id
        new_dashboard_data['is_public'] = False
        new_dashboard_data['shared_with'] = []
        
        # Generate new IDs for all widgets
        for widget in new_dashboard_data['widgets']:
            widget['id'] = str(uuid.uuid4())
        
        # Create new dashboard
        return self.create_dashboard(new_dashboard_data)

    def share_dashboard(self, dashboard_id: str, user_ids: List[str], 
                       permissions: str = 'view') -> Dict[str, Any]:
        """Share dashboard with other users"""
        dashboard = self.get_dashboard(dashboard_id)
        
        shared_with = dashboard.get('shared_with', [])
        for user_id in user_ids:
            if user_id not in [share['user_id'] for share in shared_with]:
                shared_with.append({
                    'user_id': user_id,
                    'permissions': permissions,
                    'shared_at': datetime.utcnow().isoformat()
                })
        
        dashboard['shared_with'] = shared_with
        self.update_dashboard(dashboard_id, dashboard)
        
        return dashboard

    def get_dashboard_analytics(self, dashboard_id: str, 
                              days: int = 30) -> Dict[str, Any]:
        """Get analytics for dashboard usage"""
        # This would integrate with actual analytics tracking
        # For now, return mock data structure
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        return {
            'dashboard_id': dashboard_id,
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days
            },
            'metrics': {
                'total_views': 0,  # Would come from analytics tracking
                'unique_viewers': 0,
                'avg_session_duration': 0,
                'most_viewed_widget': None,
                'peak_usage_hour': None
            },
            'usage_by_day': [],  # Daily usage statistics
            'widget_interactions': {},  # Per-widget interaction counts
            'user_engagement': {}  # User-specific engagement metrics
        }