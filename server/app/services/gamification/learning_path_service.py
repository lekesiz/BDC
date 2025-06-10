"""
Learning Path Service

Manages personalized learning paths with gamified elements.
Handles adaptive recommendations, skill-based progression, and customized challenges.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from enum import Enum
import json

from app.models.gamification import LearningPath, LearningPathNode, UserLearningPath, SkillAssessment
from app.models.user import User
from app.models.program import Program
from app.models.evaluation import Evaluation
from app.services.core.base_service import BaseService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class PathStatus(Enum):
    """Learning path statuses"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABANDONED = "abandoned"


class NodeType(Enum):
    """Learning path node types"""
    LESSON = "lesson"
    EVALUATION = "evaluation"
    PROJECT = "project"
    CHALLENGE = "challenge"
    MILESTONE = "milestone"
    SKILL_CHECK = "skill_check"
    OPTIONAL = "optional"
    BRANCHING = "branching"


class DifficultyLevel(Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LearningPathService(BaseService):
    """Service for managing personalized learning paths"""
    
    def __init__(self, db: Session):
        super().__init__(db)
        self.path_generators = {
            'skill_based': self._generate_skill_based_path,
            'goal_oriented': self._generate_goal_oriented_path,
            'adaptive': self._generate_adaptive_path,
            'competency': self._generate_competency_based_path
        }
    
    def create_learning_path(self, path_data: Dict[str, Any], creator_id: int) -> LearningPath:
        """Create a new learning path"""
        try:
            learning_path = LearningPath(
                name=path_data['name'],
                description=path_data.get('description', ''),
                category=path_data.get('category', 'general'),
                difficulty_level=path_data.get('difficulty_level', DifficultyLevel.INTERMEDIATE.value),
                estimated_duration=path_data.get('estimated_duration', 0),  # in hours
                prerequisites=path_data.get('prerequisites', []),
                learning_objectives=path_data.get('learning_objectives', []),
                skills_covered=path_data.get('skills_covered', []),
                tags=path_data.get('tags', []),
                is_public=path_data.get('is_public', True),
                is_adaptive=path_data.get('is_adaptive', False),
                gamification_settings=path_data.get('gamification_settings', {}),
                created_by=creator_id
            )
            
            self.db.add(learning_path)
            self.db.commit()
            self.db.refresh(learning_path)
            
            logger.info(f"Created learning path: {learning_path.name}")
            return learning_path
            
        except Exception as e:
            logger.error(f"Error creating learning path: {str(e)}")
            self.db.rollback()
            raise
    
    def add_path_node(self, path_id: int, node_data: Dict[str, Any]) -> LearningPathNode:
        """Add a node to a learning path"""
        try:
            node = LearningPathNode(
                learning_path_id=path_id,
                name=node_data['name'],
                description=node_data.get('description', ''),
                node_type=node_data['type'],
                order_index=node_data.get('order_index', 0),
                content_id=node_data.get('content_id'),
                content_type=node_data.get('content_type'),
                prerequisites=node_data.get('prerequisites', []),
                estimated_duration=node_data.get('estimated_duration', 0),
                xp_reward=node_data.get('xp_reward', 0),
                is_mandatory=node_data.get('is_mandatory', True),
                unlock_criteria=node_data.get('unlock_criteria', {}),
                completion_criteria=node_data.get('completion_criteria', {}),
                metadata=node_data.get('metadata', {})
            )
            
            self.db.add(node)
            self.db.commit()
            self.db.refresh(node)
            
            logger.info(f"Added node to learning path {path_id}: {node.name}")
            return node
            
        except Exception as e:
            logger.error(f"Error adding path node: {str(e)}")
            self.db.rollback()
            raise
    
    def generate_personalized_path(self, user_id: int, generation_type: str,
                                 parameters: Dict[str, Any]) -> Optional[LearningPath]:
        """Generate a personalized learning path for a user"""
        try:
            if generation_type not in self.path_generators:
                logger.error(f"Unknown path generation type: {generation_type}")
                return None
            
            generator = self.path_generators[generation_type]
            path_data = generator(user_id, parameters)
            
            if not path_data:
                return None
            
            # Create the learning path
            learning_path = self.create_learning_path(path_data, user_id)
            
            # Add nodes to the path
            for node_data in path_data.get('nodes', []):
                self.add_path_node(learning_path.id, node_data)
            
            # Assign path to user
            self.assign_path_to_user(learning_path.id, user_id)
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Error generating personalized path: {str(e)}")
            return None
    
    def assign_path_to_user(self, path_id: int, user_id: int, 
                           custom_settings: Optional[Dict] = None) -> UserLearningPath:
        """Assign a learning path to a user"""
        try:
            # Check if user already has this path
            existing = self.db.query(UserLearningPath).filter_by(
                learning_path_id=path_id,
                user_id=user_id
            ).first()
            
            if existing:
                return existing
            
            user_path = UserLearningPath(
                learning_path_id=path_id,
                user_id=user_id,
                status=PathStatus.NOT_STARTED.value,
                progress_percentage=0,
                current_node_id=None,
                started_at=None,
                estimated_completion=self._calculate_estimated_completion(path_id, user_id),
                custom_settings=custom_settings or {},
                progress_data={}
            )
            
            self.db.add(user_path)
            self.db.commit()
            self.db.refresh(user_path)
            
            logger.info(f"Assigned path {path_id} to user {user_id}")
            return user_path
            
        except Exception as e:
            logger.error(f"Error assigning path to user: {str(e)}")
            self.db.rollback()
            raise
    
    def start_learning_path(self, user_id: int, path_id: int) -> bool:
        """Start a learning path for a user"""
        try:
            user_path = self.db.query(UserLearningPath).filter_by(
                learning_path_id=path_id,
                user_id=user_id
            ).first()
            
            if not user_path:
                return False
            
            # Find the first node
            first_node = self.db.query(LearningPathNode).filter_by(
                learning_path_id=path_id
            ).order_by(LearningPathNode.order_index.asc()).first()
            
            user_path.status = PathStatus.IN_PROGRESS.value
            user_path.started_at = datetime.utcnow()
            user_path.current_node_id = first_node.id if first_node else None
            
            self.db.commit()
            
            logger.info(f"Started learning path {path_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting learning path: {str(e)}")
            self.db.rollback()
            return False
    
    def complete_node(self, user_id: int, path_id: int, node_id: int,
                     completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mark a node as completed and update progress"""
        try:
            user_path = self.db.query(UserLearningPath).filter_by(
                learning_path_id=path_id,
                user_id=user_id
            ).first()
            
            if not user_path:
                return {'success': False, 'error': 'User path not found'}
            
            node = self.db.query(LearningPathNode).get(node_id)
            if not node:
                return {'success': False, 'error': 'Node not found'}
            
            # Update progress data
            progress_data = user_path.progress_data or {}
            completed_nodes = progress_data.get('completed_nodes', [])
            
            if node_id not in completed_nodes:
                completed_nodes.append(node_id)
                progress_data['completed_nodes'] = completed_nodes
                progress_data[f'node_{node_id}_completed_at'] = datetime.utcnow().isoformat()
                progress_data[f'node_{node_id}_data'] = completion_data
            
            user_path.progress_data = progress_data
            
            # Calculate new progress percentage
            total_nodes = self.db.query(LearningPathNode).filter_by(
                learning_path_id=path_id,
                is_mandatory=True
            ).count()
            
            completed_mandatory = len([n for n in completed_nodes 
                                     if self._is_node_mandatory(path_id, n)])
            
            user_path.progress_percentage = (completed_mandatory / total_nodes) * 100 if total_nodes > 0 else 0
            
            # Find next node
            next_node = self._get_next_available_node(user_id, path_id, node_id)
            user_path.current_node_id = next_node.id if next_node else None
            
            # Check if path is completed
            if user_path.progress_percentage >= 100:
                user_path.status = PathStatus.COMPLETED.value
                user_path.completed_at = datetime.utcnow()
            
            self.db.commit()
            
            # Award XP for node completion
            xp_awarded = node.xp_reward or 0
            if xp_awarded > 0:
                # This would integrate with XP service
                pass
            
            result = {
                'success': True,
                'progress_percentage': user_path.progress_percentage,
                'xp_awarded': xp_awarded,
                'path_completed': user_path.status == PathStatus.COMPLETED.value,
                'next_node': {
                    'id': next_node.id,
                    'name': next_node.name,
                    'type': next_node.node_type
                } if next_node else None
            }
            
            logger.info(f"Completed node {node_id} for user {user_id} in path {path_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error completing node: {str(e)}")
            self.db.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_user_learning_paths(self, user_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all learning paths for a user"""
        try:
            query = self.db.query(UserLearningPath, LearningPath).join(LearningPath).filter(
                UserLearningPath.user_id == user_id
            )
            
            if status:
                query = query.filter(UserLearningPath.status == status)
            
            results = query.order_by(UserLearningPath.assigned_at.desc()).all()
            
            paths = []
            for user_path, learning_path in results:
                # Get current node info
                current_node = None
                if user_path.current_node_id:
                    current_node_obj = self.db.query(LearningPathNode).get(user_path.current_node_id)
                    if current_node_obj:
                        current_node = {
                            'id': current_node_obj.id,
                            'name': current_node_obj.name,
                            'type': current_node_obj.node_type,
                            'description': current_node_obj.description
                        }
                
                paths.append({
                    'id': learning_path.id,
                    'name': learning_path.name,
                    'description': learning_path.description,
                    'category': learning_path.category,
                    'difficulty_level': learning_path.difficulty_level,
                    'estimated_duration': learning_path.estimated_duration,
                    'skills_covered': learning_path.skills_covered,
                    'status': user_path.status,
                    'progress_percentage': user_path.progress_percentage,
                    'current_node': current_node,
                    'started_at': user_path.started_at,
                    'assigned_at': user_path.assigned_at,
                    'estimated_completion': user_path.estimated_completion,
                    'completed_at': getattr(user_path, 'completed_at', None)
                })
            
            return paths
            
        except Exception as e:
            logger.error(f"Error getting user learning paths: {str(e)}")
            return []
    
    def get_path_progress(self, user_id: int, path_id: int) -> Dict[str, Any]:
        """Get detailed progress for a specific learning path"""
        try:
            user_path = self.db.query(UserLearningPath).filter_by(
                learning_path_id=path_id,
                user_id=user_id
            ).first()
            
            if not user_path:
                return {}
            
            # Get all nodes in the path
            nodes = self.db.query(LearningPathNode).filter_by(
                learning_path_id=path_id
            ).order_by(LearningPathNode.order_index.asc()).all()
            
            progress_data = user_path.progress_data or {}
            completed_nodes = progress_data.get('completed_nodes', [])
            
            node_progress = []
            for node in nodes:
                is_completed = node.id in completed_nodes
                is_available = self._is_node_available(user_id, path_id, node.id)
                
                node_progress.append({
                    'id': node.id,
                    'name': node.name,
                    'description': node.description,
                    'type': node.node_type,
                    'order_index': node.order_index,
                    'is_mandatory': node.is_mandatory,
                    'is_completed': is_completed,
                    'is_available': is_available,
                    'is_current': node.id == user_path.current_node_id,
                    'estimated_duration': node.estimated_duration,
                    'xp_reward': node.xp_reward,
                    'completion_data': progress_data.get(f'node_{node.id}_data', {}),
                    'completed_at': progress_data.get(f'node_{node.id}_completed_at')
                })
            
            return {
                'path_id': path_id,
                'status': user_path.status,
                'progress_percentage': user_path.progress_percentage,
                'nodes': node_progress,
                'total_nodes': len(nodes),
                'completed_nodes': len(completed_nodes),
                'started_at': user_path.started_at,
                'estimated_completion': user_path.estimated_completion
            }
            
        except Exception as e:
            logger.error(f"Error getting path progress: {str(e)}")
            return {}
    
    def get_recommended_paths(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recommended learning paths for a user"""
        try:
            # Get user's current skills and interests
            user_profile = self._get_user_learning_profile(user_id)
            
            # Get available paths
            available_paths = self.db.query(LearningPath).filter(
                LearningPath.is_public == True
            ).all()
            
            # Score and rank paths
            scored_paths = []
            for path in available_paths:
                # Check if user already has this path
                existing = self.db.query(UserLearningPath).filter_by(
                    learning_path_id=path.id,
                    user_id=user_id
                ).first()
                
                if existing:
                    continue
                
                score = self._calculate_path_relevance_score(user_profile, path)
                scored_paths.append((path, score))
            
            # Sort by score and take top recommendations
            scored_paths.sort(key=lambda x: x[1], reverse=True)
            top_paths = scored_paths[:limit]
            
            recommendations = []
            for path, score in top_paths:
                recommendations.append({
                    'id': path.id,
                    'name': path.name,
                    'description': path.description,
                    'category': path.category,
                    'difficulty_level': path.difficulty_level,
                    'estimated_duration': path.estimated_duration,
                    'skills_covered': path.skills_covered,
                    'learning_objectives': path.learning_objectives,
                    'relevance_score': score,
                    'recommendation_reason': self._get_recommendation_reason(user_profile, path)
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommended paths: {str(e)}")
            return []
    
    def create_adaptive_path(self, user_id: int, goal: str, preferences: Dict[str, Any]) -> Optional[LearningPath]:
        """Create an adaptive learning path based on user goals and preferences"""
        try:
            # Assess user's current skill level
            skill_assessment = self._assess_user_skills(user_id)
            
            # Generate adaptive path structure
            path_data = {
                'name': f"Adaptive Path: {goal}",
                'description': f"Personalized learning path to achieve: {goal}",
                'category': preferences.get('category', 'adaptive'),
                'difficulty_level': self._determine_difficulty_level(skill_assessment),
                'is_adaptive': True,
                'gamification_settings': {
                    'enable_adaptive_xp': True,
                    'enable_difficulty_scaling': True,
                    'enable_personalized_challenges': True
                },
                'nodes': self._generate_adaptive_nodes(user_id, goal, skill_assessment, preferences)
            }
            
            return self.generate_personalized_path(user_id, 'adaptive', path_data)
            
        except Exception as e:
            logger.error(f"Error creating adaptive path: {str(e)}")
            return None
    
    # Path generation methods
    
    def _generate_skill_based_path(self, user_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a skill-based learning path"""
        target_skills = parameters.get('target_skills', [])
        current_level = parameters.get('current_level', 'beginner')
        
        return {
            'name': f"Skill Development: {', '.join(target_skills)}",
            'description': f"Develop skills in: {', '.join(target_skills)}",
            'category': 'skill_development',
            'difficulty_level': current_level,
            'skills_covered': target_skills,
            'nodes': self._create_skill_nodes(target_skills, current_level)
        }
    
    def _generate_goal_oriented_path(self, user_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a goal-oriented learning path"""
        goal = parameters.get('goal', 'General Learning')
        timeline = parameters.get('timeline', 30)  # days
        
        return {
            'name': f"Goal-Oriented: {goal}",
            'description': f"Achieve your goal: {goal}",
            'category': 'goal_oriented',
            'estimated_duration': timeline * 24,  # convert to hours
            'nodes': self._create_goal_nodes(goal, timeline)
        }
    
    def _generate_adaptive_path(self, user_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate an adaptive learning path"""
        return parameters  # Use provided parameters directly
    
    def _generate_competency_based_path(self, user_id: int, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a competency-based learning path"""
        competencies = parameters.get('competencies', [])
        
        return {
            'name': f"Competency Development",
            'description': f"Develop competencies in: {', '.join(competencies)}",
            'category': 'competency',
            'skills_covered': competencies,
            'nodes': self._create_competency_nodes(competencies)
        }
    
    # Helper methods
    
    def _calculate_estimated_completion(self, path_id: int, user_id: int) -> Optional[datetime]:
        """Calculate estimated completion date for a learning path"""
        try:
            path = self.db.query(LearningPath).get(path_id)
            if not path or not path.estimated_duration:
                return None
            
            # Assume user studies 2 hours per day on average
            daily_study_hours = 2
            days_needed = path.estimated_duration / daily_study_hours
            
            return datetime.utcnow() + timedelta(days=days_needed)
            
        except Exception as e:
            logger.error(f"Error calculating estimated completion: {str(e)}")
            return None
    
    def _get_next_available_node(self, user_id: int, path_id: int, current_node_id: int) -> Optional[LearningPathNode]:
        """Get the next available node in the learning path"""
        try:
            current_node = self.db.query(LearningPathNode).get(current_node_id)
            if not current_node:
                return None
            
            # Get next node by order
            next_node = self.db.query(LearningPathNode).filter(
                LearningPathNode.learning_path_id == path_id,
                LearningPathNode.order_index > current_node.order_index
            ).order_by(LearningPathNode.order_index.asc()).first()
            
            # Check if node is available (prerequisites met)
            if next_node and self._is_node_available(user_id, path_id, next_node.id):
                return next_node
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting next available node: {str(e)}")
            return None
    
    def _is_node_available(self, user_id: int, path_id: int, node_id: int) -> bool:
        """Check if a node is available to the user"""
        try:
            node = self.db.query(LearningPathNode).get(node_id)
            if not node:
                return False
            
            # Check prerequisites
            prerequisites = node.prerequisites or []
            if not prerequisites:
                return True
            
            user_path = self.db.query(UserLearningPath).filter_by(
                learning_path_id=path_id,
                user_id=user_id
            ).first()
            
            if not user_path:
                return False
            
            completed_nodes = user_path.progress_data.get('completed_nodes', [])
            
            # Check if all prerequisites are completed
            for prereq_id in prerequisites:
                if prereq_id not in completed_nodes:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking node availability: {str(e)}")
            return False
    
    def _is_node_mandatory(self, path_id: int, node_id: int) -> bool:
        """Check if a node is mandatory"""
        try:
            node = self.db.query(LearningPathNode).get(node_id)
            return node.is_mandatory if node else False
            
        except Exception as e:
            logger.error(f"Error checking if node is mandatory: {str(e)}")
            return False
    
    def _get_user_learning_profile(self, user_id: int) -> Dict[str, Any]:
        """Get user's learning profile for recommendations"""
        try:
            user = self.db.query(User).get(user_id)
            if not user:
                return {}
            
            # This would analyze user's learning history, preferences, performance
            # For now, returning a basic profile
            return {
                'level': user.level or 1,
                'interests': [],  # Would be derived from user activity
                'learning_style': 'mixed',  # Would be assessed
                'preferred_difficulty': 'intermediate',
                'available_time': 2  # hours per day
            }
            
        except Exception as e:
            logger.error(f"Error getting user learning profile: {str(e)}")
            return {}
    
    def _calculate_path_relevance_score(self, user_profile: Dict[str, Any], path: LearningPath) -> float:
        """Calculate relevance score for a learning path"""
        try:
            score = 0.0
            
            # Difficulty match
            user_level = user_profile.get('level', 1)
            if path.difficulty_level == 'beginner' and user_level <= 10:
                score += 0.3
            elif path.difficulty_level == 'intermediate' and 5 <= user_level <= 25:
                score += 0.3
            elif path.difficulty_level == 'advanced' and user_level >= 20:
                score += 0.3
            
            # Interest match (would be more sophisticated in real implementation)
            interests = user_profile.get('interests', [])
            if path.category in interests:
                score += 0.4
            
            # Duration match
            available_time = user_profile.get('available_time', 2)
            if path.estimated_duration and path.estimated_duration <= available_time * 30:  # 30 days
                score += 0.3
            
            return min(1.0, score)
            
        except Exception as e:
            logger.error(f"Error calculating path relevance score: {str(e)}")
            return 0.0
    
    def _get_recommendation_reason(self, user_profile: Dict[str, Any], path: LearningPath) -> str:
        """Get reason for recommending a path"""
        reasons = []
        
        if path.difficulty_level == 'beginner' and user_profile.get('level', 1) <= 10:
            reasons.append("Perfect for beginners")
        
        if path.category in user_profile.get('interests', []):
            reasons.append("Matches your interests")
        
        if not reasons:
            reasons.append("Popular learning path")
        
        return ", ".join(reasons)
    
    def _assess_user_skills(self, user_id: int) -> Dict[str, Any]:
        """Assess user's current skills"""
        # This would implement skill assessment logic
        return {
            'overall_level': 'intermediate',
            'strengths': [],
            'weaknesses': [],
            'learning_pace': 'normal'
        }
    
    def _determine_difficulty_level(self, skill_assessment: Dict[str, Any]) -> str:
        """Determine appropriate difficulty level"""
        overall_level = skill_assessment.get('overall_level', 'beginner')
        return overall_level
    
    def _generate_adaptive_nodes(self, user_id: int, goal: str, 
                                skill_assessment: Dict[str, Any], 
                                preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate adaptive nodes for a learning path"""
        # This would create a sophisticated adaptive structure
        return [
            {
                'name': 'Introduction',
                'type': NodeType.LESSON.value,
                'order_index': 1,
                'is_mandatory': True,
                'estimated_duration': 1,
                'xp_reward': 50
            },
            {
                'name': 'Skill Assessment',
                'type': NodeType.SKILL_CHECK.value,
                'order_index': 2,
                'is_mandatory': True,
                'estimated_duration': 0.5,
                'xp_reward': 25
            }
        ]
    
    def _create_skill_nodes(self, skills: List[str], level: str) -> List[Dict[str, Any]]:
        """Create nodes for skill-based learning"""
        nodes = []
        for i, skill in enumerate(skills):
            nodes.append({
                'name': f"Learn {skill}",
                'type': NodeType.LESSON.value,
                'order_index': i + 1,
                'is_mandatory': True,
                'estimated_duration': 2,
                'xp_reward': 100
            })
        return nodes
    
    def _create_goal_nodes(self, goal: str, timeline: int) -> List[Dict[str, Any]]:
        """Create nodes for goal-oriented learning"""
        return [
            {
                'name': f"Step 1: Foundation for {goal}",
                'type': NodeType.LESSON.value,
                'order_index': 1,
                'is_mandatory': True,
                'estimated_duration': 3,
                'xp_reward': 150
            }
        ]
    
    def _create_competency_nodes(self, competencies: List[str]) -> List[Dict[str, Any]]:
        """Create nodes for competency-based learning"""
        nodes = []
        for i, competency in enumerate(competencies):
            nodes.append({
                'name': f"Develop {competency}",
                'type': NodeType.PROJECT.value,
                'order_index': i + 1,
                'is_mandatory': True,
                'estimated_duration': 4,
                'xp_reward': 200
            })
        return nodes