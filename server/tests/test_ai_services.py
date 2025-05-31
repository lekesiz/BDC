"""Comprehensive tests for AI services."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timezone
import json


class TestContentRecommendations:
    """Test cases for content recommendations service."""
    
    @pytest.fixture
    def recommendation_config(self):
        """Create recommendation configuration."""
        return {
            'model': 'collaborative_filtering',
            'min_confidence': 0.7,
            'max_recommendations': 10,
            'personalization_enabled': True,
            'cache_ttl': 3600
        }
    
    def test_recommendation_service_init(self, recommendation_config):
        """Test recommendation service initialization."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        assert service.config == recommendation_config
        assert service.model_type == 'collaborative_filtering'
        assert service.recommendations_cache == {}
    
    @patch('app.services.ai.content_recommendations.db')
    def test_get_user_profile(self, mock_db, recommendation_config):
        """Test getting user profile for recommendations."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        # Mock user data
        mock_user = Mock(
            id=123,
            interests=['python', 'data science'],
            completed_courses=[1, 2, 3],
            skill_level='intermediate'
        )
        
        mock_db.session.query.return_value.filter_by.return_value.first.return_value = mock_user
        
        profile = service.get_user_profile(123)
        
        assert profile['user_id'] == 123
        assert 'python' in profile['interests']
        assert profile['skill_level'] == 'intermediate'
    
    @patch('app.services.ai.content_recommendations.db')
    def test_get_content_recommendations(self, mock_db, recommendation_config):
        """Test getting content recommendations."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        # Mock available content
        mock_content = [
            Mock(id=1, title='Python Advanced', tags=['python', 'advanced']),
            Mock(id=2, title='Data Science Basics', tags=['data science', 'beginner']),
            Mock(id=3, title='Machine Learning', tags=['ml', 'python'])
        ]
        
        with patch.object(service, 'get_user_profile') as mock_profile:
            mock_profile.return_value = {
                'interests': ['python', 'ml'],
                'skill_level': 'intermediate'
            }
            
            with patch.object(service, 'get_available_content') as mock_get_content:
                mock_get_content.return_value = mock_content
                
                recommendations = service.get_recommendations(user_id=123)
                
                assert len(recommendations) > 0
                assert recommendations[0]['score'] >= service.config['min_confidence']
    
    def test_calculate_content_similarity(self, recommendation_config):
        """Test content similarity calculation."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        content1 = {'tags': ['python', 'programming', 'backend']}
        content2 = {'tags': ['python', 'programming', 'frontend']}
        content3 = {'tags': ['java', 'enterprise', 'backend']}
        
        sim1_2 = service.calculate_similarity(content1, content2)
        sim1_3 = service.calculate_similarity(content1, content3)
        
        # Content 1 and 2 should be more similar than 1 and 3
        assert sim1_2 > sim1_3
        assert 0 <= sim1_2 <= 1
        assert 0 <= sim1_3 <= 1
    
    def test_collaborative_filtering(self, recommendation_config):
        """Test collaborative filtering recommendations."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        # Mock user interactions
        user_interactions = {
            'user_123': [1, 2, 3, 5],
            'user_456': [2, 3, 4, 5],
            'user_789': [1, 3, 4, 6]
        }
        
        # Get recommendations for user who liked items 2, 3, 5
        recommendations = service.collaborative_filter(
            target_user='user_999',
            target_items=[2, 3, 5],
            all_interactions=user_interactions
        )
        
        # Should recommend item 4 (liked by similar users)
        assert 4 in recommendations
    
    def test_content_based_filtering(self, recommendation_config):
        """Test content-based filtering."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        user_profile = {
            'interests': ['python', 'web development'],
            'skill_level': 'intermediate'
        }
        
        content_items = [
            {'id': 1, 'title': 'Django Tutorial', 'tags': ['python', 'web development', 'django']},
            {'id': 2, 'title': 'React Basics', 'tags': ['javascript', 'web development', 'frontend']},
            {'id': 3, 'title': 'Flask API', 'tags': ['python', 'web development', 'api']},
            {'id': 4, 'title': 'Java Spring', 'tags': ['java', 'web development', 'enterprise']}
        ]
        
        recommendations = service.content_based_filter(user_profile, content_items)
        
        # Should prefer Python web development content
        assert recommendations[0]['id'] in [1, 3]
        assert recommendations[-1]['id'] == 4  # Java should be last
    
    def test_hybrid_recommendations(self, recommendation_config):
        """Test hybrid recommendation approach."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        with patch.object(service, 'collaborative_filter') as mock_cf:
            mock_cf.return_value = [1, 2, 3]
            
            with patch.object(service, 'content_based_filter') as mock_cbf:
                mock_cbf.return_value = [
                    {'id': 2, 'score': 0.9},
                    {'id': 3, 'score': 0.8},
                    {'id': 4, 'score': 0.7}
                ]
                
                hybrid = service.get_hybrid_recommendations(user_id=123)
                
                # Should combine both approaches
                assert len(hybrid) > 0
                # Items recommended by both should rank higher
                assert any(item['id'] == 2 for item in hybrid[:2])
    
    def test_recommendation_caching(self, recommendation_config):
        """Test recommendation caching."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        with patch.object(service, '_generate_recommendations') as mock_generate:
            mock_generate.return_value = [
                {'id': 1, 'score': 0.9},
                {'id': 2, 'score': 0.8}
            ]
            
            # First call - should generate
            recs1 = service.get_recommendations(user_id=123, use_cache=True)
            assert mock_generate.call_count == 1
            
            # Second call - should use cache
            recs2 = service.get_recommendations(user_id=123, use_cache=True)
            assert mock_generate.call_count == 1
            assert recs1 == recs2
    
    def test_recommendation_diversity(self, recommendation_config):
        """Test recommendation diversity."""
        from app.services.ai.content_recommendations import ContentRecommendationService
        
        service = ContentRecommendationService(recommendation_config)
        
        # Recommendations with same category
        non_diverse = [
            {'id': 1, 'category': 'python', 'score': 0.95},
            {'id': 2, 'category': 'python', 'score': 0.94},
            {'id': 3, 'category': 'python', 'score': 0.93},
            {'id': 4, 'category': 'javascript', 'score': 0.90}
        ]
        
        diverse = service.ensure_diversity(non_diverse, diversity_factor=0.5)
        
        # Should include more variety
        categories = [item['category'] for item in diverse[:3]]
        assert len(set(categories)) > 1


class TestNoteAnalysis:
    """Test cases for note analysis service."""
    
    def test_note_analysis_init(self):
        """Test note analysis service initialization."""
        from app.services.ai.note_analysis import NoteAnalysisService
        
        service = NoteAnalysisService()
        
        assert service.sentiment_analyzer is not None
        assert service.entity_extractor is not None
        assert service.summarizer is not None
    
    @patch('app.services.ai.note_analysis.TextBlob')
    def test_analyze_sentiment(self, mock_textblob):
        """Test sentiment analysis."""
        from app.services.ai.note_analysis import NoteAnalysisService
        
        service = NoteAnalysisService()
        
        # Mock sentiment
        mock_blob = Mock()
        mock_blob.sentiment.polarity = 0.8
        mock_blob.sentiment.subjectivity = 0.6
        mock_textblob.return_value = mock_blob
        
        result = service.analyze_sentiment("This is a great achievement!")
        
        assert result['polarity'] == 0.8
        assert result['subjectivity'] == 0.6
        assert result['sentiment'] == 'positive'
    
    @patch('app.services.ai.note_analysis.spacy')
    def test_extract_entities(self, mock_spacy):
        """Test entity extraction."""
        from app.services.ai.note_analysis import NoteAnalysisService
        
        service = NoteAnalysisService()
        
        # Mock spacy doc
        mock_doc = Mock()
        mock_entity1 = Mock(text='John Doe', label_='PERSON')
        mock_entity2 = Mock(text='Python', label_='SKILL')
        mock_doc.ents = [mock_entity1, mock_entity2]
        
        service.entity_extractor = Mock(return_value=mock_doc)
        
        entities = service.extract_entities("John Doe is learning Python")
        
        assert len(entities) == 2
        assert entities[0]['text'] == 'John Doe'
        assert entities[0]['type'] == 'PERSON'
    
    def test_summarize_note(self):
        """Test note summarization."""
        from app.services.ai.note_analysis import NoteAnalysisService
        
        service = NoteAnalysisService()
        
        long_note = """
        The beneficiary showed significant progress in the Python programming course.
        They completed all assignments on time and demonstrated good understanding
        of object-oriented programming concepts. The beneficiary also helped other
        students in the class, showing leadership qualities. Areas for improvement
        include advanced algorithms and data structures.
        """
        
        summary = service.summarize_note(long_note, max_length=50)
        
        assert len(summary) < len(long_note)
        assert len(summary.split()) <= 50
    
    def test_extract_action_items(self):
        """Test action item extraction."""
        from app.services.ai.note_analysis import NoteAnalysisService
        
        service = NoteAnalysisService()
        
        note = """
        Meeting notes:
        - Need to schedule follow-up session next week
        - Student should complete Python basics course
        - Review progress in 2 weeks
        - Send learning resources by Friday
        """
        
        action_items = service.extract_action_items(note)
        
        assert len(action_items) >= 3
        assert any('schedule' in item.lower() for item in action_items)
        assert any('complete' in item.lower() for item in action_items)
    
    def test_analyze_progress_indicators(self):
        """Test progress indicator analysis."""
        from app.services.ai.note_analysis import NoteAnalysisService
        
        service = NoteAnalysisService()
        
        note = """
        Student has improved significantly. Completed 80% of the course.
        Test scores increased from 60% to 85%. Struggling with advanced topics.
        Overall performance is excellent.
        """
        
        indicators = service.analyze_progress_indicators(note)
        
        assert indicators['has_progress'] is True
        assert indicators['completion_percentage'] == 80
        assert indicators['performance_trend'] == 'improving'
        assert len(indicators['strengths']) > 0
        assert len(indicators['challenges']) > 0
    
    def test_categorize_note(self):
        """Test note categorization."""
        from app.services.ai.note_analysis import NoteAnalysisService
        
        service = NoteAnalysisService()
        
        notes = {
            'progress': "Student completed module 3 with 90% score",
            'concern': "Student missed 3 sessions this week",
            'achievement': "Student won first place in coding competition",
            'general': "Discussed career goals and interests"
        }
        
        for expected_category, note_text in notes.items():
            category = service.categorize_note(note_text)
            assert category == expected_category


class TestHumanReviewWorkflow:
    """Test cases for human review workflow."""
    
    @pytest.fixture
    def workflow_config(self):
        """Create workflow configuration."""
        return {
            'confidence_threshold': 0.7,
            'review_queue_size': 100,
            'auto_escalate': True,
            'escalation_threshold': 0.5,
            'review_timeout': 3600
        }
    
    def test_workflow_init(self, workflow_config):
        """Test workflow initialization."""
        from app.services.ai.human_review_workflow import HumanReviewWorkflow
        
        workflow = HumanReviewWorkflow(workflow_config)
        
        assert workflow.config == workflow_config
        assert workflow.review_queue == []
        assert workflow.completed_reviews == {}
    
    def test_requires_review(self, workflow_config):
        """Test determining if review is required."""
        from app.services.ai.human_review_workflow import HumanReviewWorkflow
        
        workflow = HumanReviewWorkflow(workflow_config)
        
        # High confidence - no review needed
        assert workflow.requires_review({'confidence': 0.9}) is False
        
        # Low confidence - review needed
        assert workflow.requires_review({'confidence': 0.5}) is True
        
        # Edge case - exactly at threshold
        assert workflow.requires_review({'confidence': 0.7}) is False
    
    def test_submit_for_review(self, workflow_config):
        """Test submitting item for review."""
        from app.services.ai.human_review_workflow import HumanReviewWorkflow
        
        workflow = HumanReviewWorkflow(workflow_config)
        
        item = {
            'id': 'item_123',
            'type': 'content_recommendation',
            'data': {'recommendation': 'Python course'},
            'ai_confidence': 0.6,
            'ai_result': {'score': 0.8}
        }
        
        review_id = workflow.submit_for_review(item)
        
        assert review_id is not None
        assert len(workflow.review_queue) == 1
        assert workflow.review_queue[0]['status'] == 'pending'
    
    def test_process_review(self, workflow_config):
        """Test processing a review."""
        from app.services.ai.human_review_workflow import HumanReviewWorkflow
        
        workflow = HumanReviewWorkflow(workflow_config)
        
        # Submit item
        item = {'id': 'item_123', 'ai_result': {'category': 'progress'}}
        review_id = workflow.submit_for_review(item)
        
        # Process review
        review_result = {
            'approved': True,
            'modified_result': {'category': 'achievement'},
            'reviewer_notes': 'Changed category based on context'
        }
        
        workflow.process_review(review_id, review_result, reviewer_id='user_456')
        
        # Check completed review
        assert review_id in workflow.completed_reviews
        assert workflow.completed_reviews[review_id]['approved'] is True
        assert workflow.completed_reviews[review_id]['reviewer_id'] == 'user_456'
    
    def test_escalation_logic(self, workflow_config):
        """Test review escalation."""
        from app.services.ai.human_review_workflow import HumanReviewWorkflow
        
        workflow = HumanReviewWorkflow(workflow_config)
        
        # Very low confidence item
        critical_item = {
            'id': 'critical_123',
            'ai_confidence': 0.3,
            'priority': 'normal'
        }
        
        review_id = workflow.submit_for_review(critical_item)
        
        # Should auto-escalate
        assert workflow.review_queue[0]['priority'] == 'high'
        assert workflow.review_queue[0]['escalated'] is True
    
    def test_review_timeout_handling(self, workflow_config):
        """Test handling review timeouts."""
        from app.services.ai.human_review_workflow import HumanReviewWorkflow
        
        workflow = HumanReviewWorkflow(workflow_config)
        
        # Submit item with past timestamp
        old_timestamp = datetime.now(timezone.utc) - timedelta(hours=2)
        
        item = {'id': 'timeout_123'}
        review_id = workflow.submit_for_review(item)
        workflow.review_queue[0]['submitted_at'] = old_timestamp
        
        # Check timeouts
        timed_out = workflow.check_timeouts()
        
        assert len(timed_out) == 1
        assert timed_out[0]['id'] == review_id
        assert workflow.review_queue[0]['status'] == 'timed_out'
    
    def test_get_review_statistics(self, workflow_config):
        """Test review statistics generation."""
        from app.services.ai.human_review_workflow import HumanReviewWorkflow
        
        workflow = HumanReviewWorkflow(workflow_config)
        
        # Add some completed reviews
        workflow.completed_reviews = {
            'rev1': {'approved': True, 'processing_time': 300},
            'rev2': {'approved': False, 'processing_time': 600},
            'rev3': {'approved': True, 'processing_time': 450}
        }
        
        stats = workflow.get_statistics()
        
        assert stats['total_reviews'] == 3
        assert stats['approval_rate'] == 2/3
        assert stats['avg_processing_time'] == 450
    
    def test_machine_learning_feedback(self, workflow_config):
        """Test ML feedback from reviews."""
        from app.services.ai.human_review_workflow import HumanReviewWorkflow
        
        workflow = HumanReviewWorkflow(workflow_config)
        
        # Completed review with corrections
        review = {
            'original_item': {
                'text': 'Great progress',
                'ai_result': {'sentiment': 'neutral'}
            },
            'review_result': {
                'modified_result': {'sentiment': 'positive'}
            }
        }
        
        feedback = workflow.generate_ml_feedback(review)
        
        assert feedback['input'] == 'Great progress'
        assert feedback['original_prediction'] == 'neutral'
        assert feedback['correct_label'] == 'positive'
        assert feedback['should_retrain'] is True