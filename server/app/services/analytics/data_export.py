"""
Data Export and Visualization Service

Comprehensive data export service with multiple formats,
advanced visualizations, and automated data preparation.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, IO
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import json
import csv
import io
import zipfile
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sqlalchemy import func, and_, or_, text
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.beneficiary import Beneficiary
from app.models.appointment import Appointment
from app.models.evaluation import Evaluation
from app.models.user_activity import UserActivity
from app.extensions import db


class ExportFormat(Enum):
    """Export format types"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    PARQUET = "parquet"
    XML = "xml"
    YAML = "yaml"


class VisualizationType(Enum):
    """Visualization types"""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    AREA_CHART = "area_chart"
    GAUGE_CHART = "gauge_chart"
    TREEMAP = "treemap"


@dataclass
class ExportRequest:
    """Data export request configuration"""
    export_id: str
    data_sources: List[str]
    filters: Dict[str, Any]
    format: ExportFormat
    include_metadata: bool
    compression: Optional[str] = None
    schedule: Optional[str] = None


@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    chart_type: VisualizationType
    title: str
    data_source: str
    x_axis: str
    y_axis: str
    filters: Dict[str, Any]
    styling: Dict[str, Any]
    interactive: bool = True


@dataclass
class ExportResult:
    """Export operation result"""
    export_id: str
    file_path: str
    format: ExportFormat
    size_bytes: int
    record_count: int
    created_at: datetime
    metadata: Dict[str, Any]


class DataExportService:
    """
    Comprehensive data export and visualization service
    with support for multiple formats and advanced analytics.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.export_history = {}
        self.export_directory = Path("/tmp/exports")
        self.export_directory.mkdir(exist_ok=True)
        
        # Configure visualization styles
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Data source mapping
        self.data_sources = {
            'users': User,
            'beneficiaries': Beneficiary,
            'appointments': Appointment,
            'evaluations': Evaluation,
            'user_activities': UserActivity
        }
    
    async def export_data(self, export_request: ExportRequest) -> ExportResult:
        """Export data based on request configuration"""
        try:
            self.logger.info(f"Starting data export: {export_request.export_id}")
            
            # Collect data from sources
            data = await self.collect_data(export_request.data_sources, export_request.filters)
            
            # Prepare data for export
            prepared_data = await self.prepare_data_for_export(data, export_request)
            
            # Export to specified format
            file_path = await self.export_to_format(prepared_data, export_request)
            
            # Create result
            file_size = Path(file_path).stat().st_size
            record_count = self.calculate_record_count(prepared_data)
            
            result = ExportResult(
                export_id=export_request.export_id,
                file_path=file_path,
                format=export_request.format,
                size_bytes=file_size,
                record_count=record_count,
                created_at=datetime.utcnow(),
                metadata=await self.generate_export_metadata(export_request, prepared_data)
            )
            
            # Store in history
            self.export_history[export_request.export_id] = result
            
            self.logger.info(f"Export completed: {export_request.export_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error during data export: {str(e)}")
            raise
    
    async def collect_data(self, data_sources: List[str], 
                          filters: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Collect data from specified sources with filters"""
        try:
            collected_data = {}
            
            with db.session() as session:
                for source in data_sources:
                    if source not in self.data_sources:
                        self.logger.warning(f"Unknown data source: {source}")
                        continue
                    
                    model = self.data_sources[source]
                    
                    # Build query with filters
                    query = session.query(model)
                    query = self.apply_filters(query, model, filters.get(source, {}))
                    
                    # Execute query and convert to DataFrame
                    records = query.all()
                    df = self.convert_to_dataframe(records, source)
                    
                    collected_data[source] = df
                    
                    self.logger.info(f"Collected {len(df)} records from {source}")
            
            return collected_data
            
        except Exception as e:
            self.logger.error(f"Error collecting data: {str(e)}")
            raise
    
    def apply_filters(self, query, model, filters: Dict[str, Any]):
        """Apply filters to database query"""
        try:
            # Date range filters
            if 'start_date' in filters and hasattr(model, 'created_at'):
                start_date = datetime.fromisoformat(filters['start_date'])
                query = query.filter(model.created_at >= start_date)
            
            if 'end_date' in filters and hasattr(model, 'created_at'):
                end_date = datetime.fromisoformat(filters['end_date'])
                query = query.filter(model.created_at <= end_date)
            
            # Status filters
            if 'status' in filters and hasattr(model, 'status'):
                if isinstance(filters['status'], list):
                    query = query.filter(model.status.in_(filters['status']))
                else:
                    query = query.filter(model.status == filters['status'])
            
            # User ID filters
            if 'user_ids' in filters and hasattr(model, 'user_id'):
                query = query.filter(model.user_id.in_(filters['user_ids']))
            
            # Limit results
            if 'limit' in filters:
                query = query.limit(filters['limit'])
            
            return query
            
        except Exception as e:
            self.logger.error(f"Error applying filters: {str(e)}")
            return query
    
    def convert_to_dataframe(self, records: List, source: str) -> pd.DataFrame:
        """Convert database records to pandas DataFrame"""
        try:
            if not records:
                return pd.DataFrame()
            
            # Convert records to dictionaries
            data = []
            for record in records:
                record_dict = {}
                for column in record.__table__.columns:
                    value = getattr(record, column.name)
                    # Handle datetime serialization
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    record_dict[column.name] = value
                data.append(record_dict)
            
            df = pd.DataFrame(data)
            
            # Data type optimization
            df = self.optimize_dataframe_dtypes(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error converting to DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def optimize_dataframe_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame data types for memory efficiency"""
        try:
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Try to convert to numeric
                    try:
                        df[col] = pd.to_numeric(df[col], downcast='integer')
                    except (ValueError, TypeError):
                        # Try to convert to datetime
                        try:
                            df[col] = pd.to_datetime(df[col])
                        except (ValueError, TypeError):
                            # Keep as string but optimize
                            if df[col].nunique() < len(df) * 0.5:
                                df[col] = df[col].astype('category')
                
                elif df[col].dtype in ['int64', 'float64']:
                    # Downcast numeric types
                    if df[col].dtype == 'int64':
                        df[col] = pd.to_numeric(df[col], downcast='integer')
                    else:
                        df[col] = pd.to_numeric(df[col], downcast='float')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error optimizing DataFrame: {str(e)}")
            return df
    
    async def prepare_data_for_export(self, data: Dict[str, pd.DataFrame],
                                    export_request: ExportRequest) -> Dict[str, pd.DataFrame]:
        """Prepare data for export with cleaning and transformations"""
        try:
            prepared_data = {}
            
            for source, df in data.items():
                # Clean data
                cleaned_df = self.clean_dataframe(df)
                
                # Apply transformations
                transformed_df = await self.apply_transformations(cleaned_df, source, export_request)
                
                # Add metadata columns if requested
                if export_request.include_metadata:
                    transformed_df = self.add_metadata_columns(transformed_df, export_request)
                
                prepared_data[source] = transformed_df
            
            return prepared_data
            
        except Exception as e:
            self.logger.error(f"Error preparing data for export: {str(e)}")
            raise
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean DataFrame by handling missing values and duplicates"""
        try:
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Handle missing values
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    # Fill numeric missing values with median
                    df[col] = df[col].fillna(df[col].median())
                elif df[col].dtype == 'object' or df[col].dtype.name == 'category':
                    # Fill categorical missing values with mode
                    mode_value = df[col].mode().iloc[0] if not df[col].mode().empty else 'Unknown'
                    df[col] = df[col].fillna(mode_value)
                elif df[col].dtype == 'datetime64[ns]':
                    # Fill datetime missing values with forward fill
                    df[col] = df[col].fillna(method='ffill')
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error cleaning DataFrame: {str(e)}")
            return df
    
    async def apply_transformations(self, df: pd.DataFrame, source: str,
                                  export_request: ExportRequest) -> pd.DataFrame:
        """Apply data transformations based on source and requirements"""
        try:
            # Source-specific transformations
            if source == 'users':
                df = self.transform_user_data(df)
            elif source == 'appointments':
                df = self.transform_appointment_data(df)
            elif source == 'evaluations':
                df = self.transform_evaluation_data(df)
            elif source == 'user_activities':
                df = self.transform_activity_data(df)
            
            # General transformations
            df = self.apply_general_transformations(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error applying transformations: {str(e)}")
            return df
    
    def transform_user_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply user-specific data transformations"""
        if 'created_at' in df.columns:
            df['registration_month'] = pd.to_datetime(df['created_at']).dt.to_period('M')
            df['days_since_registration'] = (datetime.utcnow() - pd.to_datetime(df['created_at'])).dt.days
        
        if 'last_login' in df.columns:
            df['days_since_last_login'] = (datetime.utcnow() - pd.to_datetime(df['last_login'])).dt.days
        
        return df
    
    def transform_appointment_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply appointment-specific data transformations"""
        if 'scheduled_for' in df.columns:
            df['appointment_hour'] = pd.to_datetime(df['scheduled_for']).dt.hour
            df['appointment_day_of_week'] = pd.to_datetime(df['scheduled_for']).dt.day_name()
            df['appointment_month'] = pd.to_datetime(df['scheduled_for']).dt.to_period('M')
        
        if 'created_at' in df.columns and 'scheduled_for' in df.columns:
            df['days_in_advance'] = (pd.to_datetime(df['scheduled_for']) - pd.to_datetime(df['created_at'])).dt.days
        
        return df
    
    def transform_evaluation_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply evaluation-specific data transformations"""
        if 'score' in df.columns:
            df['score_category'] = pd.cut(df['score'], 
                                        bins=[0, 40, 60, 80, 100], 
                                        labels=['Poor', 'Fair', 'Good', 'Excellent'])
        
        if 'created_at' in df.columns:
            df['evaluation_month'] = pd.to_datetime(df['created_at']).dt.to_period('M')
        
        return df
    
    def transform_activity_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply activity-specific data transformations"""
        if 'timestamp' in df.columns:
            df['activity_hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['activity_day_of_week'] = pd.to_datetime(df['timestamp']).dt.day_name()
            df['activity_month'] = pd.to_datetime(df['timestamp']).dt.to_period('M')
        
        return df
    
    def apply_general_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply general transformations to any DataFrame"""
        # Add row numbers
        df['row_number'] = range(1, len(df) + 1)
        
        # Add data quality indicators
        df['data_quality_score'] = self.calculate_data_quality_score(df)
        
        return df
    
    def calculate_data_quality_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate data quality score for each row"""
        # Simple data quality score based on missing values
        missing_ratio = df.isnull().sum(axis=1) / len(df.columns)
        quality_score = (1 - missing_ratio) * 100
        return quality_score.round(2)
    
    def add_metadata_columns(self, df: pd.DataFrame, export_request: ExportRequest) -> pd.DataFrame:
        """Add metadata columns to DataFrame"""
        df['export_id'] = export_request.export_id
        df['export_timestamp'] = datetime.utcnow().isoformat()
        df['export_format'] = export_request.format.value
        
        return df
    
    async def export_to_format(self, data: Dict[str, pd.DataFrame],
                             export_request: ExportRequest) -> str:
        """Export data to specified format"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            
            if export_request.format == ExportFormat.CSV:
                return await self.export_to_csv(data, export_request, timestamp)
            elif export_request.format == ExportFormat.JSON:
                return await self.export_to_json(data, export_request, timestamp)
            elif export_request.format == ExportFormat.EXCEL:
                return await self.export_to_excel(data, export_request, timestamp)
            elif export_request.format == ExportFormat.PARQUET:
                return await self.export_to_parquet(data, export_request, timestamp)
            elif export_request.format == ExportFormat.XML:
                return await self.export_to_xml(data, export_request, timestamp)
            elif export_request.format == ExportFormat.YAML:
                return await self.export_to_yaml(data, export_request, timestamp)
            else:
                raise ValueError(f"Unsupported export format: {export_request.format}")
                
        except Exception as e:
            self.logger.error(f"Error exporting to format: {str(e)}")
            raise
    
    async def export_to_csv(self, data: Dict[str, pd.DataFrame],
                          export_request: ExportRequest, timestamp: str) -> str:
        """Export data to CSV format"""
        if len(data) == 1:
            # Single file
            source_name = list(data.keys())[0]
            filename = f"{export_request.export_id}_{source_name}_{timestamp}.csv"
            file_path = self.export_directory / filename
            
            data[source_name].to_csv(file_path, index=False)
            
        else:
            # Multiple files in ZIP
            filename = f"{export_request.export_id}_{timestamp}.zip"
            file_path = self.export_directory / filename
            
            with zipfile.ZipFile(file_path, 'w') as zipf:
                for source_name, df in data.items():
                    csv_filename = f"{source_name}.csv"
                    csv_data = df.to_csv(index=False)
                    zipf.writestr(csv_filename, csv_data)
        
        return str(file_path)
    
    async def export_to_json(self, data: Dict[str, pd.DataFrame],
                           export_request: ExportRequest, timestamp: str) -> str:
        """Export data to JSON format"""
        filename = f"{export_request.export_id}_{timestamp}.json"
        file_path = self.export_directory / filename
        
        export_data = {}
        for source_name, df in data.items():
            export_data[source_name] = df.to_dict('records')
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return str(file_path)
    
    async def export_to_excel(self, data: Dict[str, pd.DataFrame],
                            export_request: ExportRequest, timestamp: str) -> str:
        """Export data to Excel format"""
        filename = f"{export_request.export_id}_{timestamp}.xlsx"
        file_path = self.export_directory / filename
        
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            for source_name, df in data.items():
                # Limit sheet name length
                sheet_name = source_name[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Add formatting
                workbook = writer.book
                worksheet = writer.sheets[sheet_name]
                
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                # Apply header format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
        
        return str(file_path)
    
    async def export_to_parquet(self, data: Dict[str, pd.DataFrame],
                              export_request: ExportRequest, timestamp: str) -> str:
        """Export data to Parquet format"""
        if len(data) == 1:
            # Single file
            source_name = list(data.keys())[0]
            filename = f"{export_request.export_id}_{source_name}_{timestamp}.parquet"
            file_path = self.export_directory / filename
            
            data[source_name].to_parquet(file_path, index=False)
            
        else:
            # Multiple files in directory
            dir_name = f"{export_request.export_id}_{timestamp}"
            dir_path = self.export_directory / dir_name
            dir_path.mkdir(exist_ok=True)
            
            for source_name, df in data.items():
                file_path = dir_path / f"{source_name}.parquet"
                df.to_parquet(file_path, index=False)
            
            # Create ZIP of directory
            zip_filename = f"{dir_name}.zip"
            zip_path = self.export_directory / zip_filename
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in dir_path.glob('*.parquet'):
                    zipf.write(file, file.name)
            
            file_path = zip_path
        
        return str(file_path)
    
    async def export_to_xml(self, data: Dict[str, pd.DataFrame],
                          export_request: ExportRequest, timestamp: str) -> str:
        """Export data to XML format"""
        filename = f"{export_request.export_id}_{timestamp}.xml"
        file_path = self.export_directory / filename
        
        with open(file_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<export>\n')
            f.write(f'  <metadata>\n')
            f.write(f'    <export_id>{export_request.export_id}</export_id>\n')
            f.write(f'    <timestamp>{datetime.utcnow().isoformat()}</timestamp>\n')
            f.write(f'  </metadata>\n')
            
            for source_name, df in data.items():
                f.write(f'  <{source_name}>\n')
                xml_data = df.to_xml(index=False, row_name='record', root_name='data')
                # Remove the XML declaration from pandas output
                xml_data = xml_data.split('\n', 1)[1] if xml_data.startswith('<?xml') else xml_data
                f.write('    ' + xml_data.replace('\n', '\n    '))
                f.write(f'  </{source_name}>\n')
            
            f.write('</export>\n')
        
        return str(file_path)
    
    async def export_to_yaml(self, data: Dict[str, pd.DataFrame],
                           export_request: ExportRequest, timestamp: str) -> str:
        """Export data to YAML format"""
        import yaml
        
        filename = f"{export_request.export_id}_{timestamp}.yaml"
        file_path = self.export_directory / filename
        
        export_data = {
            'metadata': {
                'export_id': export_request.export_id,
                'timestamp': datetime.utcnow().isoformat(),
                'format': export_request.format.value
            },
            'data': {}
        }
        
        for source_name, df in data.items():
            export_data['data'][source_name] = df.to_dict('records')
        
        with open(file_path, 'w') as f:
            yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
        
        return str(file_path)
    
    def calculate_record_count(self, data: Dict[str, pd.DataFrame]) -> int:
        """Calculate total record count across all DataFrames"""
        return sum(len(df) for df in data.values())
    
    async def generate_export_metadata(self, export_request: ExportRequest,
                                     data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate metadata for export"""
        metadata = {
            'export_request': asdict(export_request),
            'data_summary': {},
            'quality_metrics': {},
            'processing_info': {
                'processed_at': datetime.utcnow().isoformat(),
                'total_sources': len(data),
                'total_records': self.calculate_record_count(data)
            }
        }
        
        # Add per-source metadata
        for source_name, df in data.items():
            metadata['data_summary'][source_name] = {
                'record_count': len(df),
                'column_count': len(df.columns),
                'columns': list(df.columns),
                'data_types': df.dtypes.to_dict(),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            }
            
            # Quality metrics
            metadata['quality_metrics'][source_name] = {
                'missing_values': df.isnull().sum().to_dict(),
                'duplicate_rows': df.duplicated().sum(),
                'data_quality_score': df['data_quality_score'].mean() if 'data_quality_score' in df.columns else None
            }
        
        return metadata
    
    async def create_visualization(self, config: VisualizationConfig) -> str:
        """Create visualization based on configuration"""
        try:
            # Collect data for visualization
            filters = config.filters
            data = await self.collect_data([config.data_source], {config.data_source: filters})
            
            if config.data_source not in data or data[config.data_source].empty:
                raise ValueError(f"No data available for visualization: {config.data_source}")
            
            df = data[config.data_source]
            
            # Create visualization based on type
            if config.chart_type == VisualizationType.LINE_CHART:
                fig = self.create_line_chart(df, config)
            elif config.chart_type == VisualizationType.BAR_CHART:
                fig = self.create_bar_chart(df, config)
            elif config.chart_type == VisualizationType.PIE_CHART:
                fig = self.create_pie_chart(df, config)
            elif config.chart_type == VisualizationType.SCATTER_PLOT:
                fig = self.create_scatter_plot(df, config)
            elif config.chart_type == VisualizationType.HEATMAP:
                fig = self.create_heatmap(df, config)
            elif config.chart_type == VisualizationType.HISTOGRAM:
                fig = self.create_histogram(df, config)
            elif config.chart_type == VisualizationType.BOX_PLOT:
                fig = self.create_box_plot(df, config)
            elif config.chart_type == VisualizationType.AREA_CHART:
                fig = self.create_area_chart(df, config)
            elif config.chart_type == VisualizationType.GAUGE_CHART:
                fig = self.create_gauge_chart(df, config)
            elif config.chart_type == VisualizationType.TREEMAP:
                fig = self.create_treemap(df, config)
            else:
                raise ValueError(f"Unsupported chart type: {config.chart_type}")
            
            # Save visualization
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"viz_{config.chart_type.value}_{timestamp}.html"
            file_path = self.export_directory / filename
            
            if config.interactive:
                fig.write_html(file_path)
            else:
                fig.write_image(str(file_path).replace('.html', '.png'))
                file_path = str(file_path).replace('.html', '.png')
            
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error creating visualization: {str(e)}")
            raise
    
    def create_line_chart(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create line chart visualization"""
        fig = px.line(df, x=config.x_axis, y=config.y_axis, title=config.title)
        return fig
    
    def create_bar_chart(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create bar chart visualization"""
        fig = px.bar(df, x=config.x_axis, y=config.y_axis, title=config.title)
        return fig
    
    def create_pie_chart(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create pie chart visualization"""
        fig = px.pie(df, names=config.x_axis, values=config.y_axis, title=config.title)
        return fig
    
    def create_scatter_plot(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create scatter plot visualization"""
        fig = px.scatter(df, x=config.x_axis, y=config.y_axis, title=config.title)
        return fig
    
    def create_heatmap(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create heatmap visualization"""
        # Create correlation matrix if not specified
        if df.select_dtypes(include=[np.number]).empty:
            raise ValueError("Heatmap requires numeric data")
        
        corr_matrix = df.select_dtypes(include=[np.number]).corr()
        
        fig = px.imshow(corr_matrix, title=config.title, color_continuous_scale='RdBu')
        return fig
    
    def create_histogram(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create histogram visualization"""
        fig = px.histogram(df, x=config.x_axis, title=config.title)
        return fig
    
    def create_box_plot(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create box plot visualization"""
        fig = px.box(df, y=config.y_axis, title=config.title)
        return fig
    
    def create_area_chart(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create area chart visualization"""
        fig = px.area(df, x=config.x_axis, y=config.y_axis, title=config.title)
        return fig
    
    def create_gauge_chart(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create gauge chart visualization"""
        value = df[config.y_axis].mean() if config.y_axis in df.columns else 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': config.title},
            gauge={'axis': {'range': [None, 100]},
                  'bar': {'color': "darkblue"},
                  'steps': [{'range': [0, 50], 'color': "lightgray"},
                           {'range': [50, 100], 'color': "gray"}],
                  'threshold': {'line': {'color': "red", 'width': 4},
                               'thickness': 0.75, 'value': 90}}))
        
        return fig
    
    def create_treemap(self, df: pd.DataFrame, config: VisualizationConfig) -> go.Figure:
        """Create treemap visualization"""
        fig = px.treemap(df, path=[config.x_axis], values=config.y_axis, title=config.title)
        return fig
    
    async def get_export_history(self, limit: int = 50) -> List[ExportResult]:
        """Get export history"""
        exports = list(self.export_history.values())
        exports.sort(key=lambda x: x.created_at, reverse=True)
        return exports[:limit]
    
    async def delete_export(self, export_id: str) -> bool:
        """Delete export file and remove from history"""
        try:
            if export_id not in self.export_history:
                return False
            
            export_result = self.export_history[export_id]
            
            # Delete file
            if Path(export_result.file_path).exists():
                Path(export_result.file_path).unlink()
            
            # Remove from history
            del self.export_history[export_id]
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting export: {str(e)}")
            return False


# Initialize service instance
data_export_service = DataExportService()