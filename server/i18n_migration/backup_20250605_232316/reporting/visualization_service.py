"""
Visualization Service

Provides advanced data visualization capabilities:
- Chart generation (bar, line, pie, scatter, area, etc.)
- Geographic maps with various overlays
- Heat maps and density plots
- Interactive visualizations
- Custom color schemes and styling
- Data aggregation and transformation
"""

import json
import io
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import folium
from folium.plugins import HeatMap, MarkerCluster


class VisualizationService:
    """Service for creating advanced data visualizations"""

    def __init__(self):
        self.color_palettes = self._get_color_palettes()
        self.chart_types = self._get_chart_types()
        
    def _get_color_palettes(self) -> Dict[str, List[str]]:
        """Get predefined color palettes"""
        return {
            'default': ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'],
            'blue_scale': ['#0066cc', '#0080ff', '#3399ff', '#66b3ff', '#99ccff', '#cce6ff'],
            'green_scale': ['#006600', '#009900', '#00cc00', '#33ff33', '#66ff66', '#99ff99'],
            'warm': ['#ff6b6b', '#ffa500', '#ffd700', '#ff69b4', '#ff1493', '#dc143c'],
            'cool': ['#00ced1', '#20b2aa', '#4682b4', '#6495ed', '#87ceeb', '#b0e0e6'],
            'viridis': ['#440154', '#31688e', '#35b779', '#fde725'],
            'plasma': ['#0d0887', '#7e03a8', '#cc4778', '#f89441', '#f0f921'],
            'inferno': ['#000004', '#420a68', '#932667', '#dd513a', '#fca50a'],
            'professional': ['#2c3e50', '#34495e', '#7f8c8d', '#95a5a6', '#bdc3c7', '#ecf0f1'],
            'pastel': ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#ff99cc', '#c2c2f0']
        }

    def _get_chart_types(self) -> Dict[str, Dict]:
        """Get available chart types and their configurations"""
        return {
            'bar': {
                'name': 'Bar Chart',
                'description': 'Compare values across categories',
                'supports_grouping': True,
                'supports_stacking': True,
                'min_dimensions': 1,
                'max_dimensions': 3
            },
            'line': {
                'name': 'Line Chart',
                'description': 'Show trends over time or continuous data',
                'supports_grouping': True,
                'supports_multiple_series': True,
                'min_dimensions': 2,
                'max_dimensions': 3
            },
            'pie': {
                'name': 'Pie Chart',
                'description': 'Show proportions of a whole',
                'supports_grouping': False,
                'supports_stacking': False,
                'min_dimensions': 2,
                'max_dimensions': 2
            },
            'doughnut': {
                'name': 'Doughnut Chart',
                'description': 'Show proportions with central space',
                'supports_grouping': False,
                'supports_stacking': False,
                'min_dimensions': 2,
                'max_dimensions': 2
            },
            'scatter': {
                'name': 'Scatter Plot',
                'description': 'Show relationships between variables',
                'supports_grouping': True,
                'supports_sizing': True,
                'min_dimensions': 2,
                'max_dimensions': 4
            },
            'area': {
                'name': 'Area Chart',
                'description': 'Show cumulative totals over time',
                'supports_grouping': True,
                'supports_stacking': True,
                'min_dimensions': 2,
                'max_dimensions': 3
            },
            'histogram': {
                'name': 'Histogram',
                'description': 'Show distribution of values',
                'supports_grouping': False,
                'supports_stacking': False,
                'min_dimensions': 1,
                'max_dimensions': 1
            },
            'box': {
                'name': 'Box Plot',
                'description': 'Show statistical distribution',
                'supports_grouping': True,
                'supports_stacking': False,
                'min_dimensions': 1,
                'max_dimensions': 2
            },
            'heatmap': {
                'name': 'Heat Map',
                'description': 'Show correlation or intensity',
                'supports_grouping': False,
                'supports_stacking': False,
                'min_dimensions': 2,
                'max_dimensions': 3
            },
            'treemap': {
                'name': 'Tree Map',
                'description': 'Show hierarchical data proportions',
                'supports_grouping': True,
                'supports_stacking': False,
                'min_dimensions': 2,
                'max_dimensions': 3
            },
            'sunburst': {
                'name': 'Sunburst Chart',
                'description': 'Show hierarchical data in circular format',
                'supports_grouping': True,
                'supports_stacking': False,
                'min_dimensions': 2,
                'max_dimensions': 4
            },
            'waterfall': {
                'name': 'Waterfall Chart',
                'description': 'Show cumulative effect of changes',
                'supports_grouping': False,
                'supports_stacking': False,
                'min_dimensions': 2,
                'max_dimensions': 2
            }
        }

    def create_chart(self, data: List[Dict], chart_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a chart based on configuration"""
        
        chart_type = chart_config.get('type', 'bar')
        
        if chart_type not in self.chart_types:
            raise ValueError(f"Unsupported chart type: {chart_type}")
        
        # Convert data to DataFrame for easier manipulation
        df = pd.DataFrame(data)
        
        if df.empty:
            return {
                'success': False,
                'error': 'No data provided for visualization'
            }
        
        try:
            # Create chart based on type
            if chart_type == 'bar':
                chart_data = self._create_bar_chart(df, chart_config)
            elif chart_type == 'line':
                chart_data = self._create_line_chart(df, chart_config)
            elif chart_type in ['pie', 'doughnut']:
                chart_data = self._create_pie_chart(df, chart_config)
            elif chart_type == 'scatter':
                chart_data = self._create_scatter_chart(df, chart_config)
            elif chart_type == 'area':
                chart_data = self._create_area_chart(df, chart_config)
            elif chart_type == 'histogram':
                chart_data = self._create_histogram(df, chart_config)
            elif chart_type == 'box':
                chart_data = self._create_box_plot(df, chart_config)
            elif chart_type == 'heatmap':
                chart_data = self._create_heatmap(df, chart_config)
            elif chart_type == 'treemap':
                chart_data = self._create_treemap(df, chart_config)
            elif chart_type == 'sunburst':
                chart_data = self._create_sunburst(df, chart_config)
            elif chart_type == 'waterfall':
                chart_data = self._create_waterfall(df, chart_config)
            else:
                raise ValueError(f"Chart type {chart_type} not implemented")
            
            return {
                'success': True,
                'chart_data': chart_data,
                'chart_type': chart_type,
                'data_points': len(df),
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'chart_type': chart_type
            }

    def _create_bar_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a bar chart"""
        
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        group_col = config.get('group_by')
        orientation = config.get('orientation', 'vertical')
        stacked = config.get('stacked', False)
        
        if not x_col or not y_col:
            raise ValueError("Both x_axis and y_axis are required for bar chart")
        
        fig = go.Figure()
        
        if group_col and group_col in df.columns:
            # Grouped bar chart
            groups = df[group_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'), len(groups))
            
            for i, group in enumerate(groups):
                group_data = df[df[group_col] == group]
                
                if orientation == 'horizontal':
                    fig.add_trace(go.Bar(
                        y=group_data[x_col],
                        x=group_data[y_col],
                        name=str(group),
                        marker_color=colors[i % len(colors)],
                        orientation='h'
                    ))
                else:
                    fig.add_trace(go.Bar(
                        x=group_data[x_col],
                        y=group_data[y_col],
                        name=str(group),
                        marker_color=colors[i % len(colors)]
                    ))
        else:
            # Simple bar chart
            colors = self._get_colors(config.get('color_palette', 'default'), 1)
            
            if orientation == 'horizontal':
                fig.add_trace(go.Bar(
                    y=df[x_col],
                    x=df[y_col],
                    marker_color=colors[0],
                    orientation='h'
                ))
            else:
                fig.add_trace(go.Bar(
                    x=df[x_col],
                    y=df[y_col],
                    marker_color=colors[0]
                ))
        
        # Update layout
        if stacked and group_col:
            fig.update_layout(barmode='stack')
        elif group_col:
            fig.update_layout(barmode='group')
        
        fig.update_layout(
            title=config.get('title', 'Bar Chart'),
            xaxis_title=config.get('x_label', x_col),
            yaxis_title=config.get('y_label', y_col),
            showlegend=config.get('show_legend', True) and group_col is not None,
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'data_points': len(df),
                'groups': len(df[group_col].unique()) if group_col else 1,
                'min_value': df[y_col].min(),
                'max_value': df[y_col].max(),
                'avg_value': df[y_col].mean()
            }
        }

    def _create_line_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a line chart"""
        
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        group_col = config.get('group_by')
        
        if not x_col or not y_col:
            raise ValueError("Both x_axis and y_axis are required for line chart")
        
        fig = go.Figure()
        
        if group_col and group_col in df.columns:
            # Multiple line series
            groups = df[group_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'), len(groups))
            
            for i, group in enumerate(groups):
                group_data = df[df[group_col] == group].sort_values(x_col)
                
                fig.add_trace(go.Scatter(
                    x=group_data[x_col],
                    y=group_data[y_col],
                    mode='lines+markers',
                    name=str(group),
                    line=dict(color=colors[i % len(colors)]),
                    marker=dict(color=colors[i % len(colors)])
                ))
        else:
            # Single line
            df_sorted = df.sort_values(x_col)
            colors = self._get_colors(config.get('color_palette', 'default'), 1)
            
            fig.add_trace(go.Scatter(
                x=df_sorted[x_col],
                y=df_sorted[y_col],
                mode='lines+markers',
                line=dict(color=colors[0]),
                marker=dict(color=colors[0])
            ))
        
        fig.update_layout(
            title=config.get('title', 'Line Chart'),
            xaxis_title=config.get('x_label', x_col),
            yaxis_title=config.get('y_label', y_col),
            showlegend=config.get('show_legend', True) and group_col is not None,
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'data_points': len(df),
                'series': len(df[group_col].unique()) if group_col else 1,
                'x_range': [df[x_col].min(), df[x_col].max()],
                'y_range': [df[y_col].min(), df[y_col].max()]
            }
        }

    def _create_pie_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a pie or doughnut chart"""
        
        label_col = config.get('x_axis')
        value_col = config.get('y_axis')
        chart_type = config.get('type', 'pie')
        
        if not label_col or not value_col:
            raise ValueError("Both label and value columns are required for pie chart")
        
        # Aggregate data if needed
        if len(df) > len(df[label_col].unique()):
            df_agg = df.groupby(label_col)[value_col].sum().reset_index()
        else:
            df_agg = df[[label_col, value_col]].copy()
        
        colors = self._get_colors(config.get('color_palette', 'default'), len(df_agg))
        
        if chart_type == 'doughnut':
            hole = 0.3
        else:
            hole = 0
        
        fig = go.Figure(data=[go.Pie(
            labels=df_agg[label_col],
            values=df_agg[value_col],
            hole=hole,
            marker=dict(colors=colors),
            textinfo='label+percent' if config.get('show_labels', True) else 'percent'
        )])
        
        fig.update_layout(
            title=config.get('title', 'Pie Chart'),
            showlegend=config.get('show_legend', True),
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'categories': len(df_agg),
                'total_value': df_agg[value_col].sum(),
                'largest_segment': df_agg[value_col].max(),
                'smallest_segment': df_agg[value_col].min()
            }
        }

    def _create_scatter_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a scatter plot"""
        
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        size_col = config.get('size_by')
        color_col = config.get('color_by', config.get('group_by'))
        
        if not x_col or not y_col:
            raise ValueError("Both x_axis and y_axis are required for scatter plot")
        
        fig = go.Figure()
        
        if color_col and color_col in df.columns:
            # Colored by category
            groups = df[color_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'), len(groups))
            
            for i, group in enumerate(groups):
                group_data = df[df[color_col] == group]
                
                marker_config = dict(color=colors[i % len(colors)])
                
                if size_col and size_col in df.columns:
                    marker_config['size'] = group_data[size_col]
                    marker_config['sizemode'] = 'diameter'
                    marker_config['sizeref'] = 2 * max(df[size_col]) / (40**2)
                
                fig.add_trace(go.Scatter(
                    x=group_data[x_col],
                    y=group_data[y_col],
                    mode='markers',
                    name=str(group),
                    marker=marker_config
                ))
        else:
            # Single color
            colors = self._get_colors(config.get('color_palette', 'default'), 1)
            marker_config = dict(color=colors[0])
            
            if size_col and size_col in df.columns:
                marker_config['size'] = df[size_col]
                marker_config['sizemode'] = 'diameter'
                marker_config['sizeref'] = 2 * max(df[size_col]) / (40**2)
            
            fig.add_trace(go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode='markers',
                marker=marker_config
            ))
        
        fig.update_layout(
            title=config.get('title', 'Scatter Plot'),
            xaxis_title=config.get('x_label', x_col),
            yaxis_title=config.get('y_label', y_col),
            showlegend=config.get('show_legend', True) and color_col is not None,
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'data_points': len(df),
                'x_range': [df[x_col].min(), df[x_col].max()],
                'y_range': [df[y_col].min(), df[y_col].max()],
                'correlation': df[x_col].corr(df[y_col]) if df[x_col].dtype.kind in 'biufc' and df[y_col].dtype.kind in 'biufc' else None
            }
        }

    def _create_area_chart(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create an area chart"""
        
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        group_col = config.get('group_by')
        stacked = config.get('stacked', False)
        
        if not x_col or not y_col:
            raise ValueError("Both x_axis and y_axis are required for area chart")
        
        fig = go.Figure()
        
        if group_col and group_col in df.columns:
            groups = df[group_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'), len(groups))
            
            stackgroup = 'one' if stacked else None
            
            for i, group in enumerate(groups):
                group_data = df[df[group_col] == group].sort_values(x_col)
                
                fig.add_trace(go.Scatter(
                    x=group_data[x_col],
                    y=group_data[y_col],
                    mode='lines',
                    name=str(group),
                    fill='tonexty' if i > 0 and stacked else 'tozeroy',
                    fillcolor=colors[i % len(colors)],
                    line=dict(color=colors[i % len(colors)]),
                    stackgroup=stackgroup
                ))
        else:
            df_sorted = df.sort_values(x_col)
            colors = self._get_colors(config.get('color_palette', 'default'), 1)
            
            fig.add_trace(go.Scatter(
                x=df_sorted[x_col],
                y=df_sorted[y_col],
                mode='lines',
                fill='tozeroy',
                fillcolor=colors[0],
                line=dict(color=colors[0])
            ))
        
        fig.update_layout(
            title=config.get('title', 'Area Chart'),
            xaxis_title=config.get('x_label', x_col),
            yaxis_title=config.get('y_label', y_col),
            showlegend=config.get('show_legend', True) and group_col is not None,
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'data_points': len(df),
                'series': len(df[group_col].unique()) if group_col else 1,
                'total_area': df[y_col].sum() if not group_col else df.groupby(group_col)[y_col].sum().sum()
            }
        }

    def _create_histogram(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a histogram"""
        
        x_col = config.get('x_axis')
        bins = config.get('bins', 'auto')
        
        if not x_col:
            raise ValueError("x_axis column is required for histogram")
        
        colors = self._get_colors(config.get('color_palette', 'default'), 1)
        
        fig = go.Figure(data=[go.Histogram(
            x=df[x_col],
            nbinsx=bins if isinstance(bins, int) else None,
            marker_color=colors[0]
        )])
        
        fig.update_layout(
            title=config.get('title', 'Histogram'),
            xaxis_title=config.get('x_label', x_col),
            yaxis_title='Frequency',
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'data_points': len(df),
                'mean': df[x_col].mean(),
                'median': df[x_col].median(),
                'std': df[x_col].std(),
                'min': df[x_col].min(),
                'max': df[x_col].max()
            }
        }

    def _create_box_plot(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a box plot"""
        
        y_col = config.get('y_axis')
        group_col = config.get('x_axis')
        
        if not y_col:
            raise ValueError("y_axis column is required for box plot")
        
        fig = go.Figure()
        
        if group_col and group_col in df.columns:
            groups = df[group_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'), len(groups))
            
            for i, group in enumerate(groups):
                group_data = df[df[group_col] == group]
                
                fig.add_trace(go.Box(
                    y=group_data[y_col],
                    name=str(group),
                    marker_color=colors[i % len(colors)]
                ))
        else:
            colors = self._get_colors(config.get('color_palette', 'default'), 1)
            
            fig.add_trace(go.Box(
                y=df[y_col],
                marker_color=colors[0]
            ))
        
        fig.update_layout(
            title=config.get('title', 'Box Plot'),
            xaxis_title=config.get('x_label', group_col) if group_col else '',
            yaxis_title=config.get('y_label', y_col),
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'data_points': len(df),
                'groups': len(df[group_col].unique()) if group_col else 1,
                'quartiles': df[y_col].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        }

    def _create_heatmap(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a heatmap"""
        
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        value_col = config.get('value_column')
        
        if not x_col or not y_col:
            raise ValueError("Both x_axis and y_axis are required for heatmap")
        
        # Create pivot table
        if value_col and value_col in df.columns:
            pivot_df = df.pivot_table(values=value_col, index=y_col, columns=x_col, aggfunc='mean')
        else:
            # Count occurrences
            pivot_df = df.groupby([y_col, x_col]).size().unstack(fill_value=0)
        
        colorscale = config.get('color_scale', 'Viridis')
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale=colorscale,
            text=pivot_df.values,
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=config.get('title', 'Heatmap'),
            xaxis_title=config.get('x_label', x_col),
            yaxis_title=config.get('y_label', y_col),
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'x_categories': len(pivot_df.columns),
                'y_categories': len(pivot_df.index),
                'min_value': pivot_df.min().min(),
                'max_value': pivot_df.max().max(),
                'avg_value': pivot_df.mean().mean()
            }
        }

    def _create_treemap(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a treemap"""
        
        label_col = config.get('labels')
        value_col = config.get('values')
        parent_col = config.get('parents')
        
        if not label_col or not value_col:
            raise ValueError("Both labels and values are required for treemap")
        
        fig = go.Figure(go.Treemap(
            labels=df[label_col],
            values=df[value_col],
            parents=df[parent_col] if parent_col and parent_col in df.columns else [''] * len(df),
            textinfo="label+value+percent parent"
        ))
        
        fig.update_layout(
            title=config.get('title', 'Treemap'),
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'categories': len(df),
                'total_value': df[value_col].sum(),
                'hierarchy_levels': len(df[parent_col].unique()) if parent_col else 1
            }
        }

    def _create_sunburst(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a sunburst chart"""
        
        label_col = config.get('labels')
        value_col = config.get('values')
        parent_col = config.get('parents')
        
        if not label_col or not value_col:
            raise ValueError("Both labels and values are required for sunburst")
        
        fig = go.Figure(go.Sunburst(
            labels=df[label_col],
            values=df[value_col],
            parents=df[parent_col] if parent_col and parent_col in df.columns else [''] * len(df),
            branchvalues="total"
        ))
        
        fig.update_layout(
            title=config.get('title', 'Sunburst Chart'),
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'categories': len(df),
                'total_value': df[value_col].sum(),
                'hierarchy_levels': len(df[parent_col].unique()) if parent_col else 1
            }
        }

    def _create_waterfall(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a waterfall chart"""
        
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        
        if not x_col or not y_col:
            raise ValueError("Both x_axis and y_axis are required for waterfall chart")
        
        # Calculate cumulative values
        df_sorted = df.sort_values(x_col)
        cumulative = df_sorted[y_col].cumsum()
        
        fig = go.Figure(go.Waterfall(
            name="Waterfall",
            orientation="v",
            x=df_sorted[x_col],
            y=df_sorted[y_col],
            text=[f"+{v}" if v > 0 else str(v) for v in df_sorted[y_col]],
            textposition="outside",
            connector={"line": {"color": "rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(
            title=config.get('title', 'Waterfall Chart'),
            xaxis_title=config.get('x_label', x_col),
            yaxis_title=config.get('y_label', y_col),
            template=config.get('theme', 'plotly')
        )
        
        return {
            'plotly_json': fig.to_json(),
            'chart_html': fig.to_html(),
            'summary': {
                'steps': len(df),
                'starting_value': 0,
                'ending_value': cumulative.iloc[-1],
                'net_change': df_sorted[y_col].sum()
            }
        }

    def create_geographic_map(self, data: List[Dict], map_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create geographic maps with various overlays"""
        
        map_type = map_config.get('type', 'markers')
        
        try:
            if map_type == 'markers':
                return self._create_marker_map(data, map_config)
            elif map_type == 'heatmap':
                return self._create_heat_map(data, map_config)
            elif map_type == 'choropleth':
                return self._create_choropleth_map(data, map_config)
            elif map_type == 'cluster':
                return self._create_cluster_map(data, map_config)
            else:
                raise ValueError(f"Unsupported map type: {map_type}")
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'map_type': map_type
            }

    def _create_marker_map(self, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a map with markers"""
        
        lat_col = config.get('latitude_column', 'lat')
        lng_col = config.get('longitude_column', 'lng')
        popup_col = config.get('popup_column')
        color_col = config.get('color_column')
        
        # Create base map
        center_lat = config.get('center_latitude', 40.7128)
        center_lng = config.get('center_longitude', -74.0060)
        zoom = config.get('zoom_level', 10)
        
        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom)
        
        # Add markers
        for row in data:
            lat = row.get(lat_col)
            lng = row.get(lng_col)
            
            if lat is None or lng is None:
                continue
            
            popup_text = row.get(popup_col, f"Lat: {lat}, Lng: {lng}") if popup_col else f"Lat: {lat}, Lng: {lng}"
            
            # Determine marker color
            if color_col and color_col in row:
                # This would need color mapping logic
                marker_color = 'blue'  # Default for now
            else:
                marker_color = config.get('marker_color', 'blue')
            
            folium.Marker(
                location=[lat, lng],
                popup=popup_text,
                icon=folium.Icon(color=marker_color)
            ).add_to(m)
        
        return {
            'success': True,
            'map_html': m._repr_html_(),
            'map_type': 'markers',
            'marker_count': len([d for d in data if d.get(lat_col) and d.get(lng_col)])
        }

    def _create_heat_map(self, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a heat map overlay"""
        
        lat_col = config.get('latitude_column', 'lat')
        lng_col = config.get('longitude_column', 'lng')
        weight_col = config.get('weight_column')
        
        # Create base map
        center_lat = config.get('center_latitude', 40.7128)
        center_lng = config.get('center_longitude', -74.0060)
        zoom = config.get('zoom_level', 10)
        
        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom)
        
        # Prepare heat map data
        heat_data = []
        for row in data:
            lat = row.get(lat_col)
            lng = row.get(lng_col)
            
            if lat is None or lng is None:
                continue
            
            if weight_col and weight_col in row:
                weight = row[weight_col]
                heat_data.append([lat, lng, weight])
            else:
                heat_data.append([lat, lng])
        
        # Add heat map
        if heat_data:
            HeatMap(heat_data).add_to(m)
        
        return {
            'success': True,
            'map_html': m._repr_html_(),
            'map_type': 'heatmap',
            'data_points': len(heat_data)
        }

    def _create_cluster_map(self, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a map with clustered markers"""
        
        lat_col = config.get('latitude_column', 'lat')
        lng_col = config.get('longitude_column', 'lng')
        popup_col = config.get('popup_column')
        
        # Create base map
        center_lat = config.get('center_latitude', 40.7128)
        center_lng = config.get('center_longitude', -74.0060)
        zoom = config.get('zoom_level', 10)
        
        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom)
        
        # Create marker cluster
        marker_cluster = MarkerCluster().add_to(m)
        
        # Add markers to cluster
        for row in data:
            lat = row.get(lat_col)
            lng = row.get(lng_col)
            
            if lat is None or lng is None:
                continue
            
            popup_text = row.get(popup_col, f"Lat: {lat}, Lng: {lng}") if popup_col else f"Lat: {lat}, Lng: {lng}"
            
            folium.Marker(
                location=[lat, lng],
                popup=popup_text
            ).add_to(marker_cluster)
        
        return {
            'success': True,
            'map_html': m._repr_html_(),
            'map_type': 'cluster',
            'marker_count': len([d for d in data if d.get(lat_col) and d.get(lng_col)])
        }

    def _create_choropleth_map(self, data: List[Dict], config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a choropleth map"""
        # This would require GeoJSON data for boundaries
        # Implementation would depend on specific geographic regions needed
        return {
            'success': False,
            'error': 'Choropleth maps require GeoJSON boundary data'
        }

    def _get_colors(self, palette_name: str, count: int) -> List[str]:
        """Get colors from a palette"""
        
        palette = self.color_palettes.get(palette_name, self.color_palettes['default'])
        
        if count <= len(palette):
            return palette[:count]
        
        # If we need more colors than available, repeat the palette
        colors = []
        for i in range(count):
            colors.append(palette[i % len(palette)])
        
        return colors

    def get_chart_types(self) -> Dict[str, Dict]:
        """Return available chart types"""
        return self.chart_types

    def get_color_palettes(self) -> Dict[str, List[str]]:
        """Return available color palettes"""
        return self.color_palettes

    def validate_chart_config(self, config: Dict[str, Any], data: List[Dict]) -> Dict[str, Any]:
        """Validate chart configuration"""
        
        errors = []
        warnings = []
        
        chart_type = config.get('type')
        if not chart_type:
            errors.append("Chart type is required")
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
        
        if chart_type not in self.chart_types:
            errors.append(f"Invalid chart type: {chart_type}")
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
        
        chart_info = self.chart_types[chart_type]
        
        # Check required dimensions
        required_cols = []
        if config.get('x_axis'):
            required_cols.append(config['x_axis'])
        if config.get('y_axis'):
            required_cols.append(config['y_axis'])
        
        if len(required_cols) < chart_info['min_dimensions']:
            errors.append(f"Chart type {chart_type} requires at least {chart_info['min_dimensions']} dimensions")
        
        # Validate data columns exist
        if data:
            available_columns = set(data[0].keys()) if data else set()
            for col in required_cols:
                if col not in available_columns:
                    errors.append(f"Column '{col}' not found in data")
        
        # Check data size
        if len(data) > 10000:
            warnings.append(f"Large dataset ({len(data)} rows) may impact performance")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }