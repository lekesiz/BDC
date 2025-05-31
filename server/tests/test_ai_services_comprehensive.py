"""Comprehensive tests for AI services modules."""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
import json
from datetime import datetime, timedelta

from app.services.ai.content_recommendations import ContentRecommendationService
from app.services.ai.human_review_workflow import HumanReviewWorkflowService
from app.services.ai.note_analysis import NoteAnalysisService
from app.services.ai.recommendations import RecommendationService
from app.services.ai.report_synthesis import ReportSynthesisService


class TestContentRecommendationService:
    """Test suite for ContentRecommendationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ContentRecommendationService()
    
    @pytest.fixture
    def mock_beneficiary(self):
        """Create mock beneficiary."""
        return {
            'id': 1,
            'name': 'John Doe',
            'skills': ['Python', 'JavaScript'],
            'interests': ['web development', 'data science'],
            'level': 'intermediate',
            'learning_style': 'visual',
            'progress': {
                'completed_modules': ['basics', 'functions'],
                'current_module': 'oop',
                'score_average': 85
            }
        }
    
    @pytest.fixture
    def mock_content_library(self):
        """Create mock content library."""
        return [
            {
                'id': 1,
                'title': 'Advanced Python OOP',
                'type': 'video',
                'level': 'intermediate',
                'topics': ['Python', 'OOP'],
                'duration': 120,
                'rating': 4.5
            },
            {
                'id': 2,
                'title': 'React Fundamentals',
                'type': 'course',
                'level': 'beginner',
                'topics': ['JavaScript', 'React'],
                'duration': 300,
                'rating': 4.7
            },
            {
                'id': 3,
                'title': 'Data Science with Python',
                'type': 'path',
                'level': 'intermediate',
                'topics': ['Python', 'data science'],
                'duration': 600,
                'rating': 4.6
            }
        ]
    
    def test_get_personalized_recommendations(self, service, mock_beneficiary, mock_content_library):
        """Test getting personalized content recommendations."""
        with patch.object(service, '_get_content_library', return_value=mock_content_library):
            with patch.object(service, '_calculate_relevance_score') as mock_score:
                mock_score.side_effect = [0.9, 0.6, 0.95]  # Scores for each content
                
                recommendations = service.get_personalized_recommendations(
                    beneficiary=mock_beneficiary,
                    limit=2
                )
                
                assert len(recommendations) == 2
                assert recommendations[0]['id'] == 3  # Highest score
                assert recommendations[1]['id'] == 1  # Second highest
                assert all('relevance_score' in rec for rec in recommendations)
    
    def test_get_adaptive_learning_path(self, service, mock_beneficiary):
        """Test generating adaptive learning path."""
        with patch.object(service, '_analyze_performance') as mock_analyze:
            mock_analyze.return_value = {
                'strengths': ['problem solving'],
                'weaknesses': ['algorithms'],
                'recommended_focus': 'data structures'
            }
            
            with patch.object(service, '_generate_learning_path') as mock_generate:
                mock_path = {
                    'path_id': 'adaptive_123',
                    'modules': [
                        {'name': 'Data Structures', 'duration': 4},
                        {'name': 'Algorithms', 'duration': 6}
                    ],
                    'estimated_duration': 10
                }
                mock_generate.return_value = mock_path
                
                path = service.get_adaptive_learning_path(mock_beneficiary)
                
                assert path == mock_path
                mock_analyze.assert_called_once_with(mock_beneficiary)
                mock_generate.assert_called_once()
    
    def test_update_recommendations_based_on_feedback(self, service):
        """Test updating recommendations based on user feedback."""
        beneficiary_id = 1
        content_id = 123
        feedback = {
            'rating': 5,
            'helpful': True,
            'completed': True,
            'time_spent': 150
        }
        
        with patch.object(service, '_store_feedback') as mock_store:
            with patch.object(service, '_update_recommendation_model') as mock_update:
                result = service.update_recommendations_based_on_feedback(
                    beneficiary_id, content_id, feedback
                )
                
                assert result is True
                mock_store.assert_called_once_with(beneficiary_id, content_id, feedback)
                mock_update.assert_called_once_with(beneficiary_id)
    
    def test_get_collaborative_filtering_recommendations(self, service, mock_beneficiary):
        """Test collaborative filtering recommendations."""
        with patch.object(service, '_get_similar_users') as mock_similar:
            mock_similar.return_value = [2, 3, 4]  # Similar user IDs
            
            with patch.object(service, '_get_user_content_history') as mock_history:
                mock_history.side_effect = [
                    [1, 2, 3],  # User 2's content
                    [2, 3, 4],  # User 3's content
                    [3, 4, 5]   # User 4's content
                ]
                
                with patch.object(service, '_filter_already_seen') as mock_filter:
                    mock_filter.return_value = [4, 5]  # New content
                    
                    recommendations = service.get_collaborative_filtering_recommendations(
                        mock_beneficiary['id']
                    )
                    
                    assert recommendations == [4, 5]
                    assert mock_history.call_count == 3


class TestHumanReviewWorkflowService:
    """Test suite for HumanReviewWorkflowService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return HumanReviewWorkflowService()
    
    @pytest.fixture
    def mock_ai_output(self):
        """Create mock AI output."""
        return {
            'evaluation_id': 1,
            'ai_score': 85,
            'ai_feedback': 'Good performance overall',
            'confidence': 0.75,
            'requires_review': True,
            'flagged_items': [
                {'question_id': 3, 'reason': 'Low confidence'},
                {'question_id': 7, 'reason': 'Unusual answer pattern'}
            ]
        }
    
    def test_submit_for_review(self, service, mock_ai_output):
        """Test submitting AI output for human review."""
        reviewer_id = 10
        
        with patch.object(service, '_create_review_task') as mock_create:
            mock_create.return_value = {
                'task_id': 'review_123',
                'status': 'pending',
                'assigned_to': reviewer_id
            }
            
            result = service.submit_for_review(
                ai_output=mock_ai_output,
                reviewer_id=reviewer_id,
                priority='high'
            )
            
            assert result['task_id'] == 'review_123'
            assert result['status'] == 'pending'
            mock_create.assert_called_once()
    
    def test_process_review_decision(self, service):
        """Test processing human reviewer decision."""
        review_data = {
            'task_id': 'review_123',
            'reviewer_id': 10,
            'decision': 'approve',
            'modifications': {
                'score': 88,
                'feedback': 'Excellent work with minor improvements needed'
            },
            'comments': 'Adjusted score based on creativity'
        }
        
        with patch.object(service, '_update_evaluation') as mock_update:
            with patch.object(service, '_log_review_decision') as mock_log:
                with patch.object(service, '_notify_stakeholders') as mock_notify:
                    result = service.process_review_decision(review_data)
                    
                    assert result['status'] == 'completed'
                    mock_update.assert_called_once()
                    mock_log.assert_called_once_with(review_data)
                    mock_notify.assert_called_once()
    
    def test_get_review_queue(self, service):
        """Test getting review queue for a reviewer."""
        reviewer_id = 10
        
        with patch.object(service, '_fetch_pending_reviews') as mock_fetch:
            mock_fetch.return_value = [
                {
                    'task_id': 'review_123',
                    'priority': 'high',
                    'created_at': datetime.utcnow() - timedelta(hours=2)
                },
                {
                    'task_id': 'review_124',
                    'priority': 'normal',
                    'created_at': datetime.utcnow() - timedelta(hours=1)
                }
            ]
            
            queue = service.get_review_queue(reviewer_id)
            
            assert len(queue) == 2
            assert queue[0]['task_id'] == 'review_123'  # High priority first
    
    def test_calculate_reviewer_metrics(self, service):
        """Test calculating reviewer performance metrics."""
        reviewer_id = 10
        date_range = {'start': datetime.utcnow() - timedelta(days=30), 'end': datetime.utcnow()}
        
        with patch.object(service, '_get_reviewer_history') as mock_history:
            mock_history.return_value = [
                {'decision_time': 120, 'agreement_with_ai': True},
                {'decision_time': 90, 'agreement_with_ai': False},
                {'decision_time': 150, 'agreement_with_ai': True}
            ]
            
            metrics = service.calculate_reviewer_metrics(reviewer_id, date_range)
            
            assert metrics['total_reviews'] == 3
            assert metrics['average_decision_time'] == 120
            assert metrics['ai_agreement_rate'] == 0.67
    
    def test_auto_escalate_complex_cases(self, service):
        """Test auto-escalation of complex cases."""
        with patch.object(service, '_get_pending_reviews') as mock_pending:
            mock_pending.return_value = [
                {
                    'task_id': 'review_125',
                    'complexity_score': 0.9,
                    'assigned_to': 10,
                    'created_at': datetime.utcnow() - timedelta(hours=5)
                }
            ]
            
            with patch.object(service, '_escalate_to_senior') as mock_escalate:
                service.auto_escalate_complex_cases()
                
                mock_escalate.assert_called_once()
                call_args = mock_escalate.call_args[0]
                assert call_args[0]['task_id'] == 'review_125'


class TestNoteAnalysisService:
    """Test suite for NoteAnalysisService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return NoteAnalysisService()
    
    @pytest.fixture
    def mock_notes(self):
        """Create mock notes."""
        return [
            {
                'id': 1,
                'content': 'Student shows excellent understanding of core concepts',
                'author': 'Trainer A',
                'date': datetime.utcnow() - timedelta(days=7),
                'tags': ['progress', 'positive']
            },
            {
                'id': 2,
                'content': 'Struggling with advanced algorithms, needs extra support',
                'author': 'Trainer B',
                'date': datetime.utcnow() - timedelta(days=3),
                'tags': ['concern', 'support needed']
            }
        ]
    
    def test_analyze_notes_sentiment(self, service, mock_notes):
        """Test analyzing sentiment of notes."""
        with patch.object(service, '_perform_sentiment_analysis') as mock_sentiment:
            mock_sentiment.side_effect = [
                {'sentiment': 'positive', 'score': 0.8},
                {'sentiment': 'negative', 'score': 0.3}
            ]
            
            analysis = service.analyze_notes_sentiment(mock_notes)
            
            assert analysis['overall_sentiment'] == 'mixed'
            assert analysis['positive_ratio'] == 0.5
            assert len(analysis['sentiments']) == 2
    
    def test_extract_key_themes(self, service, mock_notes):
        """Test extracting key themes from notes."""
        with patch.object(service, '_perform_theme_extraction') as mock_extract:
            mock_extract.return_value = [
                {'theme': 'conceptual understanding', 'frequency': 2},
                {'theme': 'algorithm difficulty', 'frequency': 1},
                {'theme': 'support needs', 'frequency': 1}
            ]
            
            themes = service.extract_key_themes(mock_notes)
            
            assert len(themes) == 3
            assert themes[0]['theme'] == 'conceptual understanding'
            assert themes[0]['frequency'] == 2
    
    def test_generate_summary_report(self, service, mock_notes):
        """Test generating summary report from notes."""
        beneficiary_id = 1
        
        with patch.object(service, 'analyze_notes_sentiment') as mock_sentiment:
            mock_sentiment.return_value = {
                'overall_sentiment': 'positive',
                'positive_ratio': 0.7
            }
            
            with patch.object(service, 'extract_key_themes') as mock_themes:
                mock_themes.return_value = [
                    {'theme': 'progress', 'frequency': 3}
                ]
                
                with patch.object(service, '_generate_actionable_insights') as mock_insights:
                    mock_insights.return_value = [
                        'Continue current learning path',
                        'Consider advanced challenges'
                    ]
                    
                    report = service.generate_summary_report(beneficiary_id, mock_notes)
                    
                    assert report['beneficiary_id'] == beneficiary_id
                    assert report['sentiment']['overall_sentiment'] == 'positive'
                    assert len(report['themes']) == 1
                    assert len(report['insights']) == 2
    
    def test_detect_patterns_over_time(self, service):
        """Test detecting patterns in notes over time."""
        beneficiary_id = 1
        time_period = 30  # days
        
        with patch.object(service, '_fetch_historical_notes') as mock_fetch:
            mock_fetch.return_value = [
                {'date': datetime.utcnow() - timedelta(days=i), 'sentiment': 'positive' if i % 2 == 0 else 'negative'}
                for i in range(10)
            ]
            
            with patch.object(service, '_analyze_temporal_patterns') as mock_analyze:
                mock_analyze.return_value = {
                    'trend': 'improving',
                    'volatility': 'high',
                    'critical_periods': [5, 15]
                }
                
                patterns = service.detect_patterns_over_time(beneficiary_id, time_period)
                
                assert patterns['trend'] == 'improving'
                assert patterns['volatility'] == 'high'
                assert len(patterns['critical_periods']) == 2


class TestRecommendationService:
    """Test suite for RecommendationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return RecommendationService()
    
    @pytest.fixture
    def mock_beneficiary_profile(self):
        """Create mock beneficiary profile."""
        return {
            'id': 1,
            'demographics': {'age': 25, 'education': 'bachelor'},
            'skills': {'current': ['Python', 'SQL'], 'target': ['Machine Learning', 'Cloud']},
            'performance': {'average_score': 82, 'completion_rate': 0.75},
            'preferences': {'learning_style': 'hands-on', 'time_availability': 'evenings'}
        }
    
    def test_generate_program_recommendations(self, service, mock_beneficiary_profile):
        """Test generating program recommendations."""
        with patch.object(service, '_analyze_skill_gap') as mock_gap:
            mock_gap.return_value = ['Machine Learning', 'Cloud Computing']
            
            with patch.object(service, '_match_programs_to_needs') as mock_match:
                mock_match.return_value = [
                    {'program_id': 1, 'name': 'ML Fundamentals', 'match_score': 0.9},
                    {'program_id': 2, 'name': 'AWS Basics', 'match_score': 0.85}
                ]
                
                recommendations = service.generate_program_recommendations(
                    mock_beneficiary_profile,
                    max_recommendations=2
                )
                
                assert len(recommendations) == 2
                assert recommendations[0]['match_score'] == 0.9
                mock_gap.assert_called_once()
    
    def test_suggest_learning_interventions(self, service):
        """Test suggesting learning interventions."""
        performance_data = {
            'recent_scores': [65, 70, 68, 72, 69],
            'struggling_topics': ['recursion', 'dynamic programming'],
            'engagement_level': 'low'
        }
        
        with patch.object(service, '_identify_intervention_triggers') as mock_triggers:
            mock_triggers.return_value = ['low_performance', 'low_engagement']
            
            with patch.object(service, '_generate_intervention_plan') as mock_plan:
                mock_plan.return_value = {
                    'interventions': [
                        {'type': 'tutoring', 'frequency': 'weekly'},
                        {'type': 'gamification', 'elements': ['badges', 'leaderboard']}
                    ]
                }
                
                interventions = service.suggest_learning_interventions(performance_data)
                
                assert len(interventions['interventions']) == 2
                assert interventions['interventions'][0]['type'] == 'tutoring'
    
    def test_optimize_learning_schedule(self, service):
        """Test optimizing learning schedule."""
        constraints = {
            'available_hours': [18, 19, 20],  # 6-9 PM
            'days': ['Monday', 'Wednesday', 'Friday'],
            'max_session_duration': 90,
            'preferred_break_duration': 15
        }
        
        learning_goals = {
            'topics': ['Python Advanced', 'Data Structures'],
            'target_completion': 30,  # days
            'priority_order': ['Data Structures', 'Python Advanced']
        }
        
        with patch.object(service, '_calculate_optimal_schedule') as mock_calc:
            mock_calc.return_value = {
                'schedule': [
                    {'day': 'Monday', 'time': '18:00', 'topic': 'Data Structures', 'duration': 75},
                    {'day': 'Wednesday', 'time': '18:00', 'topic': 'Python Advanced', 'duration': 75}
                ],
                'estimated_completion': 28
            }
            
            schedule = service.optimize_learning_schedule(constraints, learning_goals)
            
            assert len(schedule['schedule']) == 2
            assert schedule['estimated_completion'] <= 30
    
    def test_predict_success_probability(self, service, mock_beneficiary_profile):
        """Test predicting success probability."""
        program_id = 1
        
        with patch.object(service, '_load_prediction_model') as mock_load:
            mock_model = Mock()
            mock_model.predict_proba.return_value = [[0.25, 0.75]]  # 75% success
            mock_load.return_value = mock_model
            
            with patch.object(service, '_prepare_features') as mock_features:
                mock_features.return_value = [[1, 0, 1, 0.82, 0.75]]  # Feature vector
                
                probability = service.predict_success_probability(
                    mock_beneficiary_profile,
                    program_id
                )
                
                assert probability == 0.75
                mock_model.predict_proba.assert_called_once()


class TestReportSynthesisService:
    """Test suite for ReportSynthesisService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return ReportSynthesisService()
    
    @pytest.fixture
    def mock_data_sources(self):
        """Create mock data sources."""
        return {
            'evaluations': [
                {'date': '2025-01-15', 'score': 85, 'topic': 'Python'},
                {'date': '2025-01-20', 'score': 90, 'topic': 'JavaScript'}
            ],
            'attendance': {
                'total_sessions': 20,
                'attended': 18,
                'rate': 0.9
            },
            'assignments': [
                {'submitted': 10, 'total': 12, 'average_score': 88}
            ],
            'trainer_notes': [
                'Shows consistent improvement',
                'Excellent participation in group work'
            ]
        }
    
    def test_synthesize_comprehensive_report(self, service, mock_data_sources):
        """Test synthesizing comprehensive report."""
        beneficiary_id = 1
        report_period = {'start': '2025-01-01', 'end': '2025-01-31'}
        
        with patch.object(service, '_aggregate_data') as mock_aggregate:
            mock_aggregate.return_value = mock_data_sources
            
            with patch.object(service, '_analyze_trends') as mock_trends:
                mock_trends.return_value = {
                    'performance_trend': 'improving',
                    'consistency': 'high'
                }
                
                with patch.object(service, '_generate_insights') as mock_insights:
                    mock_insights.return_value = [
                        'Strong upward trajectory in technical skills',
                        'Excellent engagement and participation'
                    ]
                    
                    report = service.synthesize_comprehensive_report(
                        beneficiary_id,
                        report_period
                    )
                    
                    assert report['beneficiary_id'] == beneficiary_id
                    assert report['performance']['trend'] == 'improving'
                    assert len(report['insights']) == 2
    
    def test_generate_executive_summary(self, service):
        """Test generating executive summary."""
        full_report = {
            'performance': {'average_score': 87, 'trend': 'improving'},
            'attendance': {'rate': 0.92},
            'key_achievements': ['Completed advanced module', 'Top performer in cohort'],
            'areas_of_concern': ['Time management'],
            'recommendations': ['Consider leadership role', 'Focus on time management skills']
        }
        
        with patch.object(service, '_extract_key_points') as mock_extract:
            mock_extract.return_value = [
                'Overall excellent performance with 87% average',
                'Consistent improvement trend observed',
                'Recommended for leadership opportunities'
            ]
            
            summary = service.generate_executive_summary(full_report, max_length=500)
            
            assert len(summary) <= 500
            assert 'excellent performance' in summary
            assert '87%' in summary
    
    def test_create_visual_report(self, service, mock_data_sources):
        """Test creating visual report."""
        with patch.object(service, '_generate_charts') as mock_charts:
            mock_charts.return_value = {
                'performance_chart': 'base64_encoded_chart_1',
                'attendance_chart': 'base64_encoded_chart_2',
                'progress_chart': 'base64_encoded_chart_3'
            }
            
            with patch.object(service, '_create_pdf_report') as mock_pdf:
                mock_pdf.return_value = b'PDF_CONTENT'
                
                pdf_report = service.create_visual_report(
                    mock_data_sources,
                    template='modern'
                )
                
                assert pdf_report == b'PDF_CONTENT'
                mock_charts.assert_called_once()
                mock_pdf.assert_called_once()
    
    def test_batch_report_generation(self, service):
        """Test batch report generation."""
        beneficiary_ids = [1, 2, 3, 4, 5]
        report_config = {
            'type': 'monthly_progress',
            'include_visuals': True,
            'format': 'pdf'
        }
        
        with patch.object(service, 'synthesize_comprehensive_report') as mock_synthesize:
            mock_synthesize.return_value = {'status': 'completed'}
            
            with patch.object(service, '_queue_report_generation') as mock_queue:
                mock_queue.return_value = {'job_id': 'batch_123', 'status': 'queued'}
                
                result = service.batch_report_generation(beneficiary_ids, report_config)
                
                assert result['job_id'] == 'batch_123'
                assert result['total_reports'] == 5
                assert result['status'] == 'queued'
    
    def test_report_caching_and_retrieval(self, service):
        """Test report caching mechanism."""
        report_id = 'report_123'
        report_data = {
            'id': report_id,
            'content': 'Full report content',
            'generated_at': datetime.utcnow().isoformat()
        }
        
        with patch.object(service, '_cache_report') as mock_cache:
            with patch.object(service, '_get_cached_report') as mock_get:
                mock_get.return_value = None  # Not in cache
                
                # Generate and cache
                service._store_report(report_id, report_data)
                mock_cache.assert_called_once_with(report_id, report_data)
                
                # Retrieve from cache
                mock_get.return_value = report_data
                cached = service._get_report(report_id)
                
                assert cached == report_data