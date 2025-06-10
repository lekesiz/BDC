_('analytics_examples.message.analytics_system_usage_exampl')
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from .analytics_orchestrator import analytics_orchestrator
from .real_time_dashboard import dashboard_instance
from .predictive_analytics import predictive_analytics_service
from .user_behavior_analytics import user_behavior_analytics
from .performance_metrics import performance_metrics_service
from .report_generator import custom_report_generator, ReportFormat
from .data_export import data_export_service, ExportRequest, ExportFormat, VisualizationConfig, VisualizationType
from .config import get_analytics_config
from flask_babel import _, lazy_gettext as _l


class AnalyticsExamples:
    _('analytics_examples.message.examples_demonstrating_va')

    def __init__(self):
        self.config = get_analytics_config()

    async def basic_setup_example(self):
        _('analytics_examples.message.example_basic_setup_and_initi')
        print(_('analytics_examples.message.basic_setup_example'))
        print(_('analytics_examples.label.starting_analytics_orchestrato'))
        await analytics_orchestrator.start_orchestrator()
        print(_('analytics_examples.message.analytics_orchestrator_start'))
        summary = await analytics_orchestrator.get_analytics_summary()
        print(
            f"✓ System health score: {summary['performance_health_score']:.1f}%"
            )
        print(
            f"✓ Active workflows: {summary['workflow_status']['active_workflows']}"
            )
        print(f"✓ Recent insights: {len(summary['recent_insights'])}")

    async def real_time_dashboard_example(self):
        _('analytics_examples.message.example_real_time_dashboard_u')
        print(_('analytics_examples.message.real_time_dashboard_examp'))
        print(_('analytics_examples.label.collecting_real_time_metrics'))
        metrics = await dashboard_instance.collect_all_metrics()
        if 'user_metrics' in metrics:
            user_metrics = metrics['user_metrics']
            print(
                f"✓ Active users: {user_metrics['active_users'].current_value}"
                )
            print(
                f"✓ New registrations: {user_metrics['new_registrations'].current_value}"
                )
            print(f"✓ Total users: {user_metrics['total_users'].current_value}"
                )
        print(_('analytics_examples.label.generating_chart_data'))
        chart_data = dashboard_instance.get_chart_data('line',
            'active_users', _('analytics_examples.message.24h'))
        print(
            f'✓ Generated {chart_data.chart_type} chart with {len(chart_data.labels)} data points'
            )
        summary = dashboard_instance.get_dashboard_summary()
        print(f"✓ Dashboard tracking {summary['total_metrics']} metrics")
        print(f"✓ Active connections: {summary['active_connections']}")

    async def predictive_analytics_example(self):
        _('analytics_examples.message.example_predictive_analytics')
        print(_('analytics_examples.message.predictive_analytics_exam'))
        print(_('analytics_examples.label.initializing_predictive_models'))
        await predictive_analytics_service.initialize_models()
        print(_('analytics_examples.message.predictive_models_initialize'))
        performance = await predictive_analytics_service.get_model_performance(
            )
        print(_('analytics_examples.label.model_performance'))
        for model_name, perf in performance.items():
            print(
                f'  - {model_name}: Accuracy {perf.accuracy:.3f}, F1 {perf.f1_score:.3f}'
                )
        try:
            print(_('analytics_examples.label.generating_sample_predictions'))
            noshow_prediction = (await predictive_analytics_service.
                predict_appointment_noshow(123))
            print(
                f'✓ Appointment no-show prediction: {noshow_prediction.prediction} (confidence: {noshow_prediction.confidence:.2%})'
                )
            churn_prediction = (await predictive_analytics_service.
                predict_user_churn(456))
            churn_prob = churn_prediction.prediction.get('probability', 0)
            print(f'✓ User churn prediction: {churn_prob:.2%} probability')
            capacity_forecasts = (await predictive_analytics_service.
                forecast_capacity_needs(7))
            print(
                f'✓ Generated capacity forecasts for {len(capacity_forecasts)} days'
                )
        except Exception as e:
            print(
                f'Note: Prediction examples skipped due to insufficient data: {str(e)}'
                )

    async def user_behavior_example(self):
        _('analytics_examples.message.example_user_behavior_analyti')
        print(_('analytics_examples.message.user_behavior_analytics_e'))
        print(_('analytics_examples.label.performing_cohort_analysis'))
        try:
            cohorts = await user_behavior_analytics.perform_cohort_analysis(
                period_type='monthly', months_back=6)
            print(
                f'✓ Analyzed {len(set(c.cohort_group for c in cohorts))} cohorts'
                )
            if cohorts:
                avg_retention = sum(c.retention_rate for c in cohorts) / len(
                    cohorts)
                print(f'✓ Average retention rate: {avg_retention:.1f}%')
        except Exception as e:
            print(f'Note: Cohort analysis skipped: {str(e)}')
        print(_('analytics_examples.label.calculating_engagement_metrics'))
        try:
            engagement_metrics = (await user_behavior_analytics.
                calculate_engagement_metrics())
            if engagement_metrics:
                avg_engagement = sum(m.engagement_score for m in
                    engagement_metrics) / len(engagement_metrics)
                print(f'✓ Analyzed {len(engagement_metrics)} users')
                print(f'✓ Average engagement score: {avg_engagement:.1f}')
                high_engagement = len([m for m in engagement_metrics if m.
                    engagement_score >= 70])
                print(f'✓ High engagement users: {high_engagement}')
        except Exception as e:
            print(f'Note: Engagement analysis skipped: {str(e)}')
        print(_('analytics_examples.message.segmenting_users_by_behavior'))
        try:
            segments = await user_behavior_analytics.segment_users_by_behavior(
                )
            print(_('analytics_examples.label.behavioral_segments'))
            for segment in segments:
                print(
                    f'  - {segment.segment_name}: {segment.user_count} users ({segment.engagement_level} engagement)'
                    )
        except Exception as e:
            print(f'Note: User segmentation skipped: {str(e)}')
        print(_('analytics_examples.label.analyzing_feature_usage'))
        try:
            feature_usage = (await user_behavior_analytics.
                analyze_feature_usage())
            features = feature_usage.get('feature_usage', [])
            if features:
                print(_('analytics_examples.message.top_features_by_adoption'))
                for feature in features[:3]:
                    print(
                        f"  - {feature['feature_name']}: {feature['adoption_rate']:.1f}% adoption"
                        )
        except Exception as e:
            print(f'Note: Feature usage analysis skipped: {str(e)}')

    async def performance_metrics_example(self):
        _('analytics_examples.message.example_performance_metrics_a')
        print(_('analytics_examples.message.performance_metrics_examp'))
        print(_('analytics_examples.label.getting_performance_dashboard'))
        dashboard = (await performance_metrics_service.
            get_performance_dashboard())
        print(f'✓ Overall health score: {dashboard.overall_health_score:.1f}%')
        print(f'✓ Business metrics: {len(dashboard.business_metrics)}')
        print(f'✓ Operational metrics: {len(dashboard.operational_metrics)}')
        print(f'✓ Technical metrics: {len(dashboard.technical_metrics)}')
        print(
            f'✓ User experience metrics: {len(dashboard.user_experience_metrics)}'
            )
        print(_('analytics_examples.label.key_business_metrics'))
        for metric in dashboard.business_metrics[:3]:
            trend_icon = ('↑' if metric.trend.value == 'up' else '↓' if 
                metric.trend.value == 'down' else '→')
            print(
                f'  - {metric.name}: {metric.current_value} {metric.unit} {trend_icon} ({metric.change_percentage:+.1f}%)'
                )
        if dashboard.alerts:
            print(f'⚠️  Active alerts: {len(dashboard.alerts)}')
            for alert in dashboard.alerts[:3]:
                print(f"  - {alert['level'].upper()}: {alert['message']}")
        else:
            print(_('analytics_examples.message.no_active_alerts'))
        print(_('analytics_examples.label.getting_metric_history'))
        try:
            history = await performance_metrics_service.get_metric_history(
                'user_retention_rate', days=7)
            print(f'✓ Retrieved {len(history)} historical data points')
        except Exception as e:
            print(f'Note: History retrieval skipped: {str(e)}')

    async def report_generation_example(self):
        _('analytics_examples.message.example_custom_report_generat')
        print(_('analytics_examples.message.report_generation_example'))
        print(_('analytics_examples.message.generating_executive_summary_r'))
        try:
            exec_report = await custom_report_generator.generate_report(
                template_id='executive_summary', parameters={'period':
                'monthly', 'include_charts': True, 'include_comparisons': 
                True}, output_format=ReportFormat.JSON)
            print(f'✓ Generated report: {exec_report.title}')
            print(f'✓ Report ID: {exec_report.report_id}')
            print(f'✓ Generated insights: {len(exec_report.insights)}')
            if exec_report.insights:
                print(_('analytics_examples.label.key_insights'))
                for insight in exec_report.insights[:2]:
                    print(f'  - {insight}')
        except Exception as e:
            print(f'Note: Report generation skipped: {str(e)}')
        print(_('analytics_examples.message.generating_operational_analyti'))
        try:
            ops_report = await custom_report_generator.generate_report(
                template_id='operational_analytics', parameters={'period':
                'weekly', 'include_trends': True}, output_format=
                ReportFormat.HTML)
            print(f'✓ Generated operational report: {ops_report.report_id}')
            if ops_report.file_path:
                print(f'✓ Report saved to: {ops_report.file_path}')
        except Exception as e:
            print(f'Note: Operational report skipped: {str(e)}')

    async def data_export_example(self):
        _('analytics_examples.message.example_data_export_and_visua')
        print(_('analytics_examples.message.data_export_example'))
        print(_('analytics_examples.message.creating_data_export_request'))
        export_request = ExportRequest(export_id=
            f"example_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            data_sources=['users', 'appointments'], filters={'users': {
            'start_date': (datetime.utcnow() - timedelta(days=30)).
            isoformat(), 'limit': 1000}, 'appointments': {'start_date': (
            datetime.utcnow() - timedelta(days=7)).isoformat(), 'status': [
            'completed', 'scheduled']}}, format=ExportFormat.JSON,
            include_metadata=True)
        print(_('analytics_examples.label.exporting_data'))
        try:
            export_result = await data_export_service.export_data(
                export_request)
            print(f'✓ Export completed: {export_result.export_id}')
            print(f'✓ File size: {export_result.size_bytes / 1024:.1f} KB')
            print(f'✓ Record count: {export_result.record_count}')
            print(f'✓ File path: {export_result.file_path}')
        except Exception as e:
            print(f'Note: Data export skipped: {str(e)}')
        print(_('analytics_examples.label.creating_visualization'))
        try:
            viz_config = VisualizationConfig(chart_type=VisualizationType.
                BAR_CHART, title=_(
                'analytics_examples.label.user_registration_trends'),
                data_source='users', x_axis='registration_month', y_axis=
                'count', filters={'start_date': (datetime.utcnow() -
                timedelta(days=90)).isoformat()}, styling={'color': 'blue'},
                interactive=True)
            chart_path = await data_export_service.create_visualization(
                viz_config)
            print(f'✓ Visualization created: {chart_path}')
        except Exception as e:
            print(f'Note: Visualization creation skipped: {str(e)}')

    async def workflow_orchestration_example(self):
        _('analytics_examples.label.example_workflow_orchestratio')
        print(_('analytics_examples.message.workflow_orchestration_ex'))
        print(_('analytics_examples.message.executing_daily_insights_workf'))
        try:
            execution = await analytics_orchestrator.execute_workflow(
                'daily_insights', parameters={'include_forecasts': True})
            print(f'✓ Workflow execution: {execution.execution_id}')
            print(f'✓ Status: {execution.status}')
            print(f'✓ Components executed: {len(execution.results)}')
            if execution.errors:
                print(f'⚠️  Errors encountered: {len(execution.errors)}')
            if 'insights' in execution.results:
                insights = execution.results['insights']
                print(f'✓ Generated {len(insights)} insights')
        except Exception as e:
            print(f'Note: Workflow execution skipped: {str(e)}')
        print(_('analytics_examples.label.creating_custom_workflow'))
        try:
            custom_workflow = (await analytics_orchestrator.
                create_custom_workflow({'workflow_id':
                'example_custom_workflow', 'name': _(
                'analytics_examples.label.example_custom_workflow'),
                'description': _(
                'analytics_examples.message.custom_analytics_workflow_for'),
                'workflow_type': 'custom_workflow', 'components': [
                'performance_metrics', 'user_behavior'], 'parameters': {
                'analysis_depth': 'detailed', 'include_recommendations': 
                True}}))
            print(f'✓ Custom workflow created: {custom_workflow.workflow_id}')
            print(f"✓ Components: {', '.join(custom_workflow.components)}")
        except Exception as e:
            print(f'Note: Custom workflow creation skipped: {str(e)}')
        print(_('analytics_examples.label.getting_workflow_status'))
        try:
            status = await analytics_orchestrator.get_workflow_status(
                'daily_insights')
            print(f"✓ Workflow active: {status['workflow']['active']}")
            print(f"✓ Currently running: {status['is_running']}")
            print(f"✓ Total executions: {status['total_executions']}")
        except Exception as e:
            print(f'Note: Workflow status check skipped: {str(e)}')

    async def insights_and_alerts_example(self):
        _('analytics_examples.message.example_insights_and_alerts')
        print(_('analytics_examples.message.insights_and_alerts_examp'))
        print(_('analytics_examples.label.getting_recent_insights'))
        try:
            insights = await analytics_orchestrator.get_insights(limit=10)
            print(f'✓ Retrieved {len(insights)} insights')
            categories = {}
            for insight in insights:
                category = insight.category
                if category not in categories:
                    categories[category] = []
                categories[category].append(insight)
            print(_('analytics_examples.label.insights_by_category'))
            for category, category_insights in categories.items():
                print(f'  - {category}: {len(category_insights)} insights')
            high_priority = [i for i in insights if i.priority == 'high']
            if high_priority:
                print(_('analytics_examples.label.high_priority_insights'))
                for insight in high_priority[:3]:
                    print(f'  - {insight.title}: {insight.description}')
        except Exception as e:
            print(f'Note: Insights retrieval skipped: {str(e)}')
        print(_('analytics_examples.label.getting_critical_insights'))
        try:
            critical_insights = await analytics_orchestrator.get_insights(
                priority='critical', limit=5)
            if critical_insights:
                print(f'⚠️  Critical insights found: {len(critical_insights)}')
                for insight in critical_insights:
                    print(f'  - {insight.title}')
                    print(
                        f"    Recommendations: {', '.join(insight.recommendations[:2])}"
                        )
            else:
                print(_(
                    'analytics_examples.message.no_critical_insights_found'))
        except Exception as e:
            print(f'Note: Critical insights check skipped: {str(e)}')

    async def advanced_configuration_example(self):
        _('analytics_examples.message.example_advanced_configuratio')
        print(_('analytics_examples.message.advanced_configuration_ex'))
        config = get_analytics_config()
        print(f'✓ Environment: {config.environment.value}')
        print(
            f'✓ Dashboard update interval: {config.dashboard.update_interval}s'
            )
        print(
            f'✓ Predictive auto-retrain: {config.predictive.enable_auto_retrain}'
            )
        print(
            f'✓ Security anonymization: {config.security.enable_data_anonymization}'
            )
        model_config = config.get_ml_model_config('appointment_noshow')
        print(_('analytics_examples.message.appointment_no_show_model_conf'))
        print(f"  - Estimators: {model_config.get('n_estimators')}")
        print(f"  - Max depth: {model_config.get('max_depth')}")
        print(f"  - Class weight: {model_config.get('class_weight')}")
        chart_config = config.get_chart_config('line')
        print(_('analytics_examples.label.line_chart_config'))
        print(f"  - Width: {chart_config.get('width')}")
        print(f"  - Height: {chart_config.get('height')}")
        print(f"  - Theme: {chart_config.get('theme')}")
        config_dict = config.to_dict()
        print(f"✓ Configuration sections: {', '.join(config_dict.keys())}")

    async def error_handling_example(self):
        _('analytics_examples.error.example_error_handling_and_re')
        print(_('analytics_examples.error.error_handling_example'))
        print(_('analytics_examples.error.testing_error_handling'))
        try:
            await user_behavior_analytics.perform_cohort_analysis(months_back
                =24)
            print(_('analytics_examples.success.cohort_analysis_completed_su'))
        except Exception as e:
            print(f'⚠️  Cohort analysis failed gracefully: {type(e).__name__}')
        try:
            await predictive_analytics_service.predict_user_churn(99999)
            print(_('analytics_examples.success.prediction_completed_success'))
        except Exception as e:
            print(f'⚠️  Prediction failed gracefully: {type(e).__name__}')
        summary = await analytics_orchestrator.get_analytics_summary()
        print(
            f"✓ System remains operational (health: {summary['performance_health_score']:.1f}%)"
            )

    async def run_all_examples(self):
        _('analytics_examples.message.run_all_examples_in_sequence')
        print(_('analytics_examples.message.running_analytics_system_exa'))
        print('=' * 50)
        examples = [self.basic_setup_example, self.
            real_time_dashboard_example, self.predictive_analytics_example,
            self.user_behavior_example, self.performance_metrics_example,
            self.report_generation_example, self.data_export_example, self.
            workflow_orchestration_example, self.
            insights_and_alerts_example, self.
            advanced_configuration_example, self.error_handling_example]
        for example in examples:
            try:
                await example()
            except Exception as e:
                print(f'❌ Example failed: {example.__name__} - {str(e)}')
            await asyncio.sleep(1)
        print('\n' + '=' * 50)
        print(_('analytics_examples.success.all_examples_completed'))


class FlaskIntegrationExample:
    _('analytics_examples.label.example_flask_integration')

    @staticmethod
    def create_flask_routes():
        _('analytics_examples.message.create_flask_routes_for_analyt')
        from flask import Blueprint, jsonify, request
        analytics_bp = Blueprint('analytics', __name__, url_prefix=
            '/api/analytics')

        @analytics_bp.route('/dashboard')
        async def get_dashboard():
            try:
                summary = await analytics_orchestrator.get_analytics_summary()
                return jsonify(summary)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @analytics_bp.route('/metrics/<metric_name>')
        async def get_metric_history(metric_name):
            try:
                days = request.args.get('days', 30, type=int)
                history = await performance_metrics_service.get_metric_history(
                    metric_name, days)
                return jsonify(history)
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @analytics_bp.route('/reports', methods=['POST'])
        async def generate_report():
            try:
                data = request.get_json()
                report = await custom_report_generator.generate_report(
                    template_id=data['template_id'], parameters=data.get(
                    'parameters', {}), output_format=ReportFormat(data.get(
                    'format', 'json')))
                return jsonify({'report_id': report.report_id, 'title':
                    report.title, 'file_path': report.file_path, 'insights':
                    report.insights})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @analytics_bp.route('/export', methods=['POST'])
        async def export_data():
            try:
                data = request.get_json()
                export_request = ExportRequest(**data)
                result = await data_export_service.export_data(export_request)
                return jsonify({'export_id': result.export_id, 'file_path':
                    result.file_path, 'size_bytes': result.size_bytes,
                    'record_count': result.record_count})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        return analytics_bp


class CeleryTasksExample:
    _('analytics_examples.message.example_celery_tasks_for_analy')

    @staticmethod
    def create_celery_tasks(celery_app):
        _('analytics_examples.message.create_celery_tasks_for_schedu')

        @celery_app.task(name=_(
            'analytics_examples.message.analytics_daily_insights'))
        def daily_insights_task():
            _('analytics_examples.message.daily_insights_generation_task')

            async def run_task():
                await analytics_orchestrator.execute_workflow('daily_insights')
            import asyncio
            asyncio.run(run_task())

        @celery_app.task(name=_(
            'analytics_examples.message.analytics_weekly_reports'))
        def weekly_reports_task():
            _('analytics_examples.message.weekly_reports_generation_task')

            async def run_task():
                await analytics_orchestrator.execute_workflow('weekly_reports')
            import asyncio
            asyncio.run(run_task())

        @celery_app.task(name=_(
            'analytics_examples.message.analytics_model_retraining'))
        def model_retraining_task():
            _('analytics_examples.label.model_retraining_task')

            async def run_task():
                await predictive_analytics_service.retrain_models_if_needed()
            import asyncio
            asyncio.run(run_task())
        return {'daily_insights': daily_insights_task, 'weekly_reports':
            weekly_reports_task, 'model_retraining': model_retraining_task}


async def main():
    _('analytics_examples.label.main_example_runner')
    examples = AnalyticsExamples()
    await examples.run_all_examples()


if __name__ == '__main__':
    asyncio.run(main())
