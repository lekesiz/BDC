_('reporting_visualization_service.validation.visualization_service_provid')
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
from flask_babel import _, lazy_gettext as _l


class VisualizationService:
    _('reporting_visualization_service.message.service_for_creating_advanced')

    def __init__(self):
        self.color_palettes = self._get_color_palettes()
        self.chart_types = self._get_chart_types()

    def _get_color_palettes(self) ->Dict[str, List[str]]:
        _('reporting_visualization_service.message.get_predefined_color_palettes'
            )
        return {'default': [_(
            'reporting_visualization_service.message.3498db'), _(
            'reporting_visualization_service.message.e74c3c'), _(
            'reporting_visualization_service.message.2ecc71'), _(
            'reporting_visualization_service.message.f39c12'), _(
            'reporting_visualization_service.message.9b59b6'), _(
            'reporting_visualization_service.message.1abc9c')],
            'blue_scale': [_(
            'reporting_visualization_service.message.0066cc'), _(
            'reporting_visualization_service.message.0080ff'), _(
            'reporting_visualization_service.message.3399ff'), _(
            'reporting_visualization_service.message.66b3ff_1'), _(
            'reporting_visualization_service.message.99ccff'), _(
            'reporting_visualization_service.message.cce6ff')],
            'green_scale': [_(
            'reporting_visualization_service.message.006600'), _(
            'reporting_visualization_service.message.009900'), _(
            'reporting_visualization_service.message.00cc00'), _(
            'reporting_visualization_service.message.33ff33'), _(
            'reporting_visualization_service.message.66ff66'), _(
            'reporting_visualization_service.message.99ff99_1')], 'warm': [
            _('reporting_visualization_service.message.ff6b6b'), _(
            'reporting_visualization_service.message.ffa500'), _(
            'reporting_visualization_service.message.ffd700'), _(
            'reporting_visualization_service.message.ff69b4'), _(
            'reporting_visualization_service.message.ff1493'), _(
            'reporting_visualization_service.message.dc143c')], 'cool': [_(
            'reporting_visualization_service.message.00ced1'), _(
            'reporting_visualization_service.message.20b2aa'), _(
            'reporting_visualization_service.message.4682b4'), _(
            'reporting_visualization_service.message.6495ed'), _(
            'reporting_visualization_service.message.87ceeb'), _(
            'reporting_visualization_service.message.b0e0e6')], 'viridis':
            [_('reporting_visualization_service.message.440154'), _(
            'reporting_visualization_service.message.31688e'), _(
            'reporting_visualization_service.message.35b779'), _(
            'reporting_visualization_service.message.fde725')], 'plasma': [
            _('reporting_visualization_service.message.0d0887'), _(
            'reporting_visualization_service.message.7e03a8'), _(
            'reporting_visualization_service.message.cc4778'), _(
            'reporting_visualization_service.message.f89441'), _(
            'reporting_visualization_service.message.f0f921')], 'inferno':
            [_('reporting_visualization_service.message.000004'), _(
            'reporting_visualization_service.message.420a68'), _(
            'reporting_visualization_service.message.932667'), _(
            'reporting_visualization_service.message.dd513a'), _(
            'reporting_visualization_service.message.fca50a')],
            'professional': [_(
            'reporting_visualization_service.message.2c3e50'), _(
            'reporting_visualization_service.message.34495e'), _(
            'reporting_visualization_service.message.7f8c8d'), _(
            'reporting_visualization_service.message.95a5a6'), _(
            'reporting_visualization_service.message.bdc3c7'), _(
            'reporting_visualization_service.message.ecf0f1')], 'pastel': [
            _('reporting_visualization_service.message.ff9999'), _(
            'reporting_visualization_service.message.66b3ff_1'), _(
            'reporting_visualization_service.message.99ff99_1'), _(
            'reporting_visualization_service.message.ffcc99'), _(
            'reporting_visualization_service.message.ff99cc'), _(
            'reporting_visualization_service.message.c2c2f0')]}

    def _get_chart_types(self) ->Dict[str, Dict]:
        _('reporting_visualization_service.message.get_available_chart_types_and'
            )
        return {'bar': {'name': _(
            'reporting_visualization_service.label.bar_chart_1'),
            'description': _(
            'reporting_visualization_service.message.compare_values_across_categori'
            ), 'supports_grouping': True, 'supports_stacking': True,
            'min_dimensions': 1, 'max_dimensions': 3}, 'line': {'name': _(
            'reporting_visualization_service.label.line_chart_1'),
            'description': _(
            'reporting_visualization_service.message.show_trends_over_time_or_conti'
            ), 'supports_grouping': True, 'supports_multiple_series': True,
            'min_dimensions': 2, 'max_dimensions': 3}, 'pie': {'name': _(
            'reporting_visualization_service.label.pie_chart_1'),
            'description': _(
            'reporting_visualization_service.message.show_proportions_of_a_whole'
            ), 'supports_grouping': False, 'supports_stacking': False,
            'min_dimensions': 2, 'max_dimensions': 2}, 'doughnut': {'name':
            _('reporting_visualization_service.label.doughnut_chart'),
            'description': _(
            'reporting_visualization_service.message.show_proportions_with_central'
            ), 'supports_grouping': False, 'supports_stacking': False,
            'min_dimensions': 2, 'max_dimensions': 2}, 'scatter': {'name':
            _('reporting_visualization_service.label.scatter_plot_1'),
            'description': _(
            'reporting_visualization_service.message.show_relationships_between_var'
            ), 'supports_grouping': True, 'supports_sizing': True,
            'min_dimensions': 2, 'max_dimensions': 4}, 'area': {'name': _(
            'reporting_visualization_service.label.area_chart_1'),
            'description': _(
            'reporting_visualization_service.message.show_cumulative_totals_over_ti'
            ), 'supports_grouping': True, 'supports_stacking': True,
            'min_dimensions': 2, 'max_dimensions': 3}, 'histogram': {'name':
            _('reporting_visualization_service.label.histogram_1'),
            'description': _(
            'reporting_visualization_service.message.show_distribution_of_values'
            ), 'supports_grouping': False, 'supports_stacking': False,
            'min_dimensions': 1, 'max_dimensions': 1}, 'box': {'name': _(
            'reporting_visualization_service.label.box_plot_1'),
            'description': _(
            'reporting_visualization_service.label.show_statistical_distribution'
            ), 'supports_grouping': True, 'supports_stacking': False,
            'min_dimensions': 1, 'max_dimensions': 2}, 'heatmap': {'name':
            _('reporting_visualization_service.label.heat_map'),
            'description': _(
            'reporting_visualization_service.message.show_correlation_or_intensity'
            ), 'supports_grouping': False, 'supports_stacking': False,
            'min_dimensions': 2, 'max_dimensions': 3}, 'treemap': {'name':
            _('reporting_visualization_service.label.tree_map'),
            'description': _(
            'reporting_visualization_service.message.show_hierarchical_data_proport'
            ), 'supports_grouping': True, 'supports_stacking': False,
            'min_dimensions': 2, 'max_dimensions': 3}, 'sunburst': {'name':
            _('reporting_visualization_service.label.sunburst_chart_1'),
            'description': _(
            'reporting_visualization_service.validation.show_hierarchical_data_in_circ'
            ), 'supports_grouping': True, 'supports_stacking': False,
            'min_dimensions': 2, 'max_dimensions': 4}, 'waterfall': {'name':
            _('reporting_visualization_service.label.waterfall_chart_1'),
            'description': _(
            'reporting_visualization_service.message.show_cumulative_effect_of_chan'
            ), 'supports_grouping': False, 'supports_stacking': False,
            'min_dimensions': 2, 'max_dimensions': 2}}

    def create_chart(self, data: List[Dict], chart_config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_chart_based_on_config'
            )
        chart_type = chart_config.get('type', 'bar')
        if chart_type not in self.chart_types:
            raise ValueError(f'Unsupported chart type: {chart_type}')
        df = pd.DataFrame(data)
        if df.empty:
            return {'success': False, 'error': _(
                'reporting_visualization_service.message.no_data_provided_for_visualiza'
                )}
        try:
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
                raise ValueError(f'Chart type {chart_type} not implemented')
            return {'success': True, 'chart_data': chart_data, 'chart_type':
                chart_type, 'data_points': len(df), 'generated_at':
                datetime.utcnow().isoformat()}
        except Exception as e:
            return {'success': False, 'error': str(e), 'chart_type': chart_type
                }

    def _create_bar_chart(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_bar_chart')
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        group_col = config.get('group_by')
        orientation = config.get('orientation', 'vertical')
        stacked = config.get('stacked', False)
        if not x_col or not y_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_x_axis_and_y_axis_are_req'
                ))
        fig = go.Figure()
        if group_col and group_col in df.columns:
            groups = df[group_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'
                ), len(groups))
            for i, group in enumerate(groups):
                group_data = df[df[group_col] == group]
                if orientation == 'horizontal':
                    fig.add_trace(go.Bar(y=group_data[x_col], x=group_data[
                        y_col], name=str(group), marker_color=colors[i %
                        len(colors)], orientation='h'))
                else:
                    fig.add_trace(go.Bar(x=group_data[x_col], y=group_data[
                        y_col], name=str(group), marker_color=colors[i %
                        len(colors)]))
        else:
            colors = self._get_colors(config.get('color_palette', 'default'), 1
                )
            if orientation == 'horizontal':
                fig.add_trace(go.Bar(y=df[x_col], x=df[y_col], marker_color
                    =colors[0], orientation='h'))
            else:
                fig.add_trace(go.Bar(x=df[x_col], y=df[y_col], marker_color
                    =colors[0]))
        if stacked and group_col:
            fig.update_layout(barmode='stack')
        elif group_col:
            fig.update_layout(barmode='group')
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.bar_chart_1')),
            xaxis_title=config.get('x_label', x_col), yaxis_title=config.
            get('y_label', y_col), showlegend=config.get('show_legend', 
            True) and group_col is not None, template=config.get('theme',
            'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'data_points': len(df), 'groups': len(df[group_col]
            .unique()) if group_col else 1, 'min_value': df[y_col].min(),
            'max_value': df[y_col].max(), 'avg_value': df[y_col].mean()}}

    def _create_line_chart(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_line_chart')
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        group_col = config.get('group_by')
        if not x_col or not y_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_x_axis_and_y_axis_are_req_1'
                ))
        fig = go.Figure()
        if group_col and group_col in df.columns:
            groups = df[group_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'
                ), len(groups))
            for i, group in enumerate(groups):
                group_data = df[df[group_col] == group].sort_values(x_col)
                fig.add_trace(go.Scatter(x=group_data[x_col], y=group_data[
                    y_col], mode=_(
                    'reporting_visualization_service.message.lines_markers_1'
                    ), name=str(group), line=dict(color=colors[i % len(
                    colors)]), marker=dict(color=colors[i % len(colors)])))
        else:
            df_sorted = df.sort_values(x_col)
            colors = self._get_colors(config.get('color_palette', 'default'), 1
                )
            fig.add_trace(go.Scatter(x=df_sorted[x_col], y=df_sorted[y_col],
                mode=_(
                'reporting_visualization_service.message.lines_markers_1'),
                line=dict(color=colors[0]), marker=dict(color=colors[0])))
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.line_chart_1')),
            xaxis_title=config.get('x_label', x_col), yaxis_title=config.
            get('y_label', y_col), showlegend=config.get('show_legend', 
            True) and group_col is not None, template=config.get('theme',
            'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'data_points': len(df), 'series': len(df[group_col]
            .unique()) if group_col else 1, 'x_range': [df[x_col].min(), df
            [x_col].max()], 'y_range': [df[y_col].min(), df[y_col].max()]}}

    def _create_pie_chart(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_pie_or_doughnut_chart'
            )
        label_col = config.get('x_axis')
        value_col = config.get('y_axis')
        chart_type = config.get('type', 'pie')
        if not label_col or not value_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_label_and_value_columns_a'
                ))
        if len(df) > len(df[label_col].unique()):
            df_agg = df.groupby(label_col)[value_col].sum().reset_index()
        else:
            df_agg = df[[label_col, value_col]].copy()
        colors = self._get_colors(config.get('color_palette', 'default'),
            len(df_agg))
        if chart_type == 'doughnut':
            hole = 0.3
        else:
            hole = 0
        fig = go.Figure(data=[go.Pie(labels=df_agg[label_col], values=
            df_agg[value_col], hole=hole, marker=dict(colors=colors),
            textinfo=_(
            'reporting_visualization_service.message.label_percent') if
            config.get('show_labels', True) else 'percent')])
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.pie_chart_1')),
            showlegend=config.get('show_legend', True), template=config.get
            ('theme', 'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'categories': len(df_agg), 'total_value': df_agg[
            value_col].sum(), 'largest_segment': df_agg[value_col].max(),
            'smallest_segment': df_agg[value_col].min()}}

    def _create_scatter_chart(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_scatter_plot')
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        size_col = config.get('size_by')
        color_col = config.get('color_by', config.get('group_by'))
        if not x_col or not y_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_x_axis_and_y_axis_are_req_2'
                ))
        fig = go.Figure()
        if color_col and color_col in df.columns:
            groups = df[color_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'
                ), len(groups))
            for i, group in enumerate(groups):
                group_data = df[df[color_col] == group]
                marker_config = dict(color=colors[i % len(colors)])
                if size_col and size_col in df.columns:
                    marker_config['size'] = group_data[size_col]
                    marker_config['sizemode'] = 'diameter'
                    marker_config['sizeref'] = 2 * max(df[size_col]) / 40 ** 2
                fig.add_trace(go.Scatter(x=group_data[x_col], y=group_data[
                    y_col], mode='markers', name=str(group), marker=
                    marker_config))
        else:
            colors = self._get_colors(config.get('color_palette', 'default'), 1
                )
            marker_config = dict(color=colors[0])
            if size_col and size_col in df.columns:
                marker_config['size'] = df[size_col]
                marker_config['sizemode'] = 'diameter'
                marker_config['sizeref'] = 2 * max(df[size_col]) / 40 ** 2
            fig.add_trace(go.Scatter(x=df[x_col], y=df[y_col], mode=
                'markers', marker=marker_config))
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.scatter_plot_1')),
            xaxis_title=config.get('x_label', x_col), yaxis_title=config.
            get('y_label', y_col), showlegend=config.get('show_legend', 
            True) and color_col is not None, template=config.get('theme',
            'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'data_points': len(df), 'x_range': [df[x_col].min(),
            df[x_col].max()], 'y_range': [df[y_col].min(), df[y_col].max()],
            'correlation': df[x_col].corr(df[y_col]) if df[x_col].dtype.
            kind in 'biufc' and df[y_col].dtype.kind in 'biufc' else None}}

    def _create_area_chart(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_an_area_chart')
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        group_col = config.get('group_by')
        stacked = config.get('stacked', False)
        if not x_col or not y_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_x_axis_and_y_axis_are_req_3'
                ))
        fig = go.Figure()
        if group_col and group_col in df.columns:
            groups = df[group_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'
                ), len(groups))
            stackgroup = 'one' if stacked else None
            for i, group in enumerate(groups):
                group_data = df[df[group_col] == group].sort_values(x_col)
                fig.add_trace(go.Scatter(x=group_data[x_col], y=group_data[
                    y_col], mode='lines', name=str(group), fill='tonexty' if
                    i > 0 and stacked else 'tozeroy', fillcolor=colors[i %
                    len(colors)], line=dict(color=colors[i % len(colors)]),
                    stackgroup=stackgroup))
        else:
            df_sorted = df.sort_values(x_col)
            colors = self._get_colors(config.get('color_palette', 'default'), 1
                )
            fig.add_trace(go.Scatter(x=df_sorted[x_col], y=df_sorted[y_col],
                mode='lines', fill='tozeroy', fillcolor=colors[0], line=
                dict(color=colors[0])))
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.area_chart_1')),
            xaxis_title=config.get('x_label', x_col), yaxis_title=config.
            get('y_label', y_col), showlegend=config.get('show_legend', 
            True) and group_col is not None, template=config.get('theme',
            'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'data_points': len(df), 'series': len(df[group_col]
            .unique()) if group_col else 1, 'total_area': df[y_col].sum() if
            not group_col else df.groupby(group_col)[y_col].sum().sum()}}

    def _create_histogram(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.label.create_a_histogram')
        x_col = config.get('x_axis')
        bins = config.get('bins', 'auto')
        if not x_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.x_axis_column_is_required_for'
                ))
        colors = self._get_colors(config.get('color_palette', 'default'), 1)
        fig = go.Figure(data=[go.Histogram(x=df[x_col], nbinsx=bins if
            isinstance(bins, int) else None, marker_color=colors[0])])
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.histogram_1')),
            xaxis_title=config.get('x_label', x_col), yaxis_title=_(
            'reporting_visualization_service.label.frequency'), template=
            config.get('theme', 'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'data_points': len(df), 'mean': df[x_col].mean(),
            'median': df[x_col].median(), 'std': df[x_col].std(), 'min': df
            [x_col].min(), 'max': df[x_col].max()}}

    def _create_box_plot(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_box_plot')
        y_col = config.get('y_axis')
        group_col = config.get('x_axis')
        if not y_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.y_axis_column_is_required_for'
                ))
        fig = go.Figure()
        if group_col and group_col in df.columns:
            groups = df[group_col].unique()
            colors = self._get_colors(config.get('color_palette', 'default'
                ), len(groups))
            for i, group in enumerate(groups):
                group_data = df[df[group_col] == group]
                fig.add_trace(go.Box(y=group_data[y_col], name=str(group),
                    marker_color=colors[i % len(colors)]))
        else:
            colors = self._get_colors(config.get('color_palette', 'default'), 1
                )
            fig.add_trace(go.Box(y=df[y_col], marker_color=colors[0]))
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.box_plot_1')),
            xaxis_title=config.get('x_label', group_col) if group_col else
            '', yaxis_title=config.get('y_label', y_col), template=config.
            get('theme', 'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'data_points': len(df), 'groups': len(df[group_col]
            .unique()) if group_col else 1, 'quartiles': df[y_col].quantile
            ([0.25, 0.5, 0.75]).to_dict()}}

    def _create_heatmap(self, df: pd.DataFrame, config: Dict[str, Any]) ->Dict[
        str, Any]:
        _('reporting_visualization_service.label.create_a_heatmap')
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        value_col = config.get('value_column')
        if not x_col or not y_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_x_axis_and_y_axis_are_req_4'
                ))
        if value_col and value_col in df.columns:
            pivot_df = df.pivot_table(values=value_col, index=y_col,
                columns=x_col, aggfunc='mean')
        else:
            pivot_df = df.groupby([y_col, x_col]).size().unstack(fill_value=0)
        colorscale = config.get('color_scale', _(
            'reporting_visualization_service.label.viridis'))
        fig = go.Figure(data=go.Heatmap(z=pivot_df.values, x=pivot_df.
            columns, y=pivot_df.index, colorscale=colorscale, text=pivot_df
            .values, texttemplate=_(
            'reporting_visualization_service.message.text'), textfont={
            'size': 10}, hoverongaps=False))
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.heatmap')), xaxis_title=
            config.get('x_label', x_col), yaxis_title=config.get('y_label',
            y_col), template=config.get('theme', 'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'x_categories': len(pivot_df.columns),
            'y_categories': len(pivot_df.index), 'min_value': pivot_df.min(
            ).min(), 'max_value': pivot_df.max().max(), 'avg_value':
            pivot_df.mean().mean()}}

    def _create_treemap(self, df: pd.DataFrame, config: Dict[str, Any]) ->Dict[
        str, Any]:
        _('reporting_visualization_service.label.create_a_treemap')
        label_col = config.get('labels')
        value_col = config.get('values')
        parent_col = config.get('parents')
        if not label_col or not value_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_labels_and_values_are_req'
                ))
        fig = go.Figure(go.Treemap(labels=df[label_col], values=df[
            value_col], parents=df[parent_col] if parent_col and parent_col in
            df.columns else [''] * len(df), textinfo=_(
            'reporting_visualization_service.message.label_value_percent_parent'
            )))
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.treemap')), template=
            config.get('theme', 'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'categories': len(df), 'total_value': df[value_col]
            .sum(), 'hierarchy_levels': len(df[parent_col].unique()) if
            parent_col else 1}}

    def _create_sunburst(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_sunburst_chart')
        label_col = config.get('labels')
        value_col = config.get('values')
        parent_col = config.get('parents')
        if not label_col or not value_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_labels_and_values_are_req_1'
                ))
        fig = go.Figure(go.Sunburst(labels=df[label_col], values=df[
            value_col], parents=df[parent_col] if parent_col and parent_col in
            df.columns else [''] * len(df), branchvalues='total'))
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.sunburst_chart_1')),
            template=config.get('theme', 'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'categories': len(df), 'total_value': df[value_col]
            .sum(), 'hierarchy_levels': len(df[parent_col].unique()) if
            parent_col else 1}}

    def _create_waterfall(self, df: pd.DataFrame, config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_waterfall_chart')
        x_col = config.get('x_axis')
        y_col = config.get('y_axis')
        if not x_col or not y_col:
            raise ValueError(_(
                'reporting_visualization_service.validation.both_x_axis_and_y_axis_are_req_5'
                ))
        df_sorted = df.sort_values(x_col)
        cumulative = df_sorted[y_col].cumsum()
        fig = go.Figure(go.Waterfall(name=_(
            'reporting_visualization_service.label.waterfall'), orientation
            ='v', x=df_sorted[x_col], y=df_sorted[y_col], text=[(f'+{v}' if
            v > 0 else str(v)) for v in df_sorted[y_col]], textposition=
            'outside', connector={'line': {'color': _(
            'reporting_visualization_service.message.rgb_63_63_63')}}))
        fig.update_layout(title=config.get('title', _(
            'reporting_visualization_service.label.waterfall_chart_1')),
            xaxis_title=config.get('x_label', x_col), yaxis_title=config.
            get('y_label', y_col), template=config.get('theme', 'plotly'))
        return {'plotly_json': fig.to_json(), 'chart_html': fig.to_html(),
            'summary': {'steps': len(df), 'starting_value': 0,
            'ending_value': cumulative.iloc[-1], 'net_change': df_sorted[
            y_col].sum()}}

    def create_geographic_map(self, data: List[Dict], map_config: Dict[str,
        Any]) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_geographic_maps_with_va'
            )
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
                raise ValueError(f'Unsupported map type: {map_type}')
        except Exception as e:
            return {'success': False, 'error': str(e), 'map_type': map_type}

    def _create_marker_map(self, data: List[Dict], config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_map_with_markers')
        lat_col = config.get('latitude_column', 'lat')
        lng_col = config.get('longitude_column', 'lng')
        popup_col = config.get('popup_column')
        color_col = config.get('color_column')
        center_lat = config.get('center_latitude', 40.7128)
        center_lng = config.get('center_longitude', -74.006)
        zoom = config.get('zoom_level', 10)
        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom)
        for row in data:
            lat = row.get(lat_col)
            lng = row.get(lng_col)
            if lat is None or lng is None:
                continue
            popup_text = row.get(popup_col, f'Lat: {lat}, Lng: {lng}'
                ) if popup_col else f'Lat: {lat}, Lng: {lng}'
            if color_col and color_col in row:
                marker_color = 'blue'
            else:
                marker_color = config.get('marker_color', 'blue')
            folium.Marker(location=[lat, lng], popup=popup_text, icon=
                folium.Icon(color=marker_color)).add_to(m)
        return {'success': True, 'map_html': m._repr_html_(), 'map_type':
            'markers', 'marker_count': len([d for d in data if d.get(
            lat_col) and d.get(lng_col)])}

    def _create_heat_map(self, data: List[Dict], config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_heat_map_overlay')
        lat_col = config.get('latitude_column', 'lat')
        lng_col = config.get('longitude_column', 'lng')
        weight_col = config.get('weight_column')
        center_lat = config.get('center_latitude', 40.7128)
        center_lng = config.get('center_longitude', -74.006)
        zoom = config.get('zoom_level', 10)
        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom)
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
        if heat_data:
            HeatMap(heat_data).add_to(m)
        return {'success': True, 'map_html': m._repr_html_(), 'map_type':
            'heatmap', 'data_points': len(heat_data)}

    def _create_cluster_map(self, data: List[Dict], config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_map_with_clustered_ma'
            )
        lat_col = config.get('latitude_column', 'lat')
        lng_col = config.get('longitude_column', 'lng')
        popup_col = config.get('popup_column')
        center_lat = config.get('center_latitude', 40.7128)
        center_lng = config.get('center_longitude', -74.006)
        zoom = config.get('zoom_level', 10)
        m = folium.Map(location=[center_lat, center_lng], zoom_start=zoom)
        marker_cluster = MarkerCluster().add_to(m)
        for row in data:
            lat = row.get(lat_col)
            lng = row.get(lng_col)
            if lat is None or lng is None:
                continue
            popup_text = row.get(popup_col, f'Lat: {lat}, Lng: {lng}'
                ) if popup_col else f'Lat: {lat}, Lng: {lng}'
            folium.Marker(location=[lat, lng], popup=popup_text).add_to(
                marker_cluster)
        return {'success': True, 'map_html': m._repr_html_(), 'map_type':
            'cluster', 'marker_count': len([d for d in data if d.get(
            lat_col) and d.get(lng_col)])}

    def _create_choropleth_map(self, data: List[Dict], config: Dict[str, Any]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.message.create_a_choropleth_map')
        return {'success': False, 'error': _(
            'reporting_visualization_service.message.choropleth_maps_require_geojso'
            )}

    def _get_colors(self, palette_name: str, count: int) ->List[str]:
        """Get colors from a palette"""
        palette = self.color_palettes.get(palette_name, self.color_palettes
            ['default'])
        if count <= len(palette):
            return palette[:count]
        colors = []
        for i in range(count):
            colors.append(palette[i % len(palette)])
        return colors

    def get_chart_types(self) ->Dict[str, Dict]:
        _('reporting_visualization_service.message.return_available_chart_types'
            )
        return self.chart_types

    def get_color_palettes(self) ->Dict[str, List[str]]:
        _('reporting_visualization_service.message.return_available_color_palette'
            )
        return self.color_palettes

    def validate_chart_config(self, config: Dict[str, Any], data: List[Dict]
        ) ->Dict[str, Any]:
        _('reporting_visualization_service.validation.validate_chart_configuration'
            )
        errors = []
        warnings = []
        chart_type = config.get('type')
        if not chart_type:
            errors.append(_(
                'reporting_visualization_service.validation.chart_type_is_required'
                ))
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
        if chart_type not in self.chart_types:
            errors.append(f'Invalid chart type: {chart_type}')
            return {'is_valid': False, 'errors': errors, 'warnings': warnings}
        chart_info = self.chart_types[chart_type]
        required_cols = []
        if config.get('x_axis'):
            required_cols.append(config['x_axis'])
        if config.get('y_axis'):
            required_cols.append(config['y_axis'])
        if len(required_cols) < chart_info['min_dimensions']:
            errors.append(
                f"Chart type {chart_type} requires at least {chart_info['min_dimensions']} dimensions"
                )
        if data:
            available_columns = set(data[0].keys()) if data else set()
            for col in required_cols:
                if col not in available_columns:
                    errors.append(f"Column '{col}' not found in data")
        if len(data) > 10000:
            warnings.append(
                f'Large dataset ({len(data)} rows) may impact performance')
        return {'is_valid': len(errors) == 0, 'errors': errors, 'warnings':
            warnings}
