"""AI Question Generation API endpoints."""

import asyncio
import os
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from sqlalchemy import and_, or_, func
from typing import Dict, List, Any

from app.extensions import db
from app.models.ai_question_generation import (
    ContentType, SourceContent, QuestionType, BloomsTaxonomy,
    LearningObjective, QuestionGenerationRequest, GeneratedQuestion,
    QuestionDuplicate, QuestionBank, QuestionBankQuestion,
    GenerationAnalytics
)
from app.models.user import User
from app.services.ai_question_generator_service import AIQuestionGeneratorService
from app.utils.decorators import require_permission
from app.schemas.auth import validate_json_input

from app.utils.logging import logger

# Create blueprint
ai_question_generation_bp = Blueprint('ai_question_generation', __name__, url_prefix='/api/ai-questions')

# Initialize service
ai_service = AIQuestionGeneratorService()

# Configuration
UPLOAD_FOLDER = '/tmp/question_generation_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'mp3', 'wav', 'm4a', 'mp4', 'avi', 'mov'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_user_tenant_id():
    """Get current user's tenant ID."""
    current_user_id = get_jwt_identity()
    user = db.session.query(User).get(current_user_id)
    return user.tenant_id if user else None


@ai_question_generation_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'AI Question Generation',
        'timestamp': datetime.utcnow().isoformat()
    })


# Content Management Endpoints

@ai_question_generation_bp.route('/content-types', methods=['GET'])
@jwt_required()
def get_content_types():
    """Get available content types."""
    try:
        content_types = db.session.query(ContentType).filter(
            ContentType.is_active == True
        ).all()
        
        return jsonify({
            'success': True,
            'content_types': [ct.to_dict() for ct in content_types]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting content types: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/source-content', methods=['POST'])
@jwt_required()
def create_source_content():
    """Create new source content."""
    try:
        current_user_id = get_jwt_identity()
        tenant_id = get_user_tenant_id()
        
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                try:
                    file.save(file_path)
                except RequestEntityTooLarge:
                    return jsonify({
                        'success': False, 
                        'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'
                    }), 413
                
                # Get form data
                title = request.form.get('title', filename)
                description = request.form.get('description')
                content_type_name = request.form.get('content_type', 'document')
                
                source_content = ai_service.create_source_content(
                    tenant_id=tenant_id,
                    creator_id=current_user_id,
                    title=title,
                    description=description,
                    content_type_name=content_type_name,
                    file_path=file_path
                )
            else:
                return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        else:
            # Handle JSON data
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': 'No data provided'}), 400
            
            required_fields = ['title']
            if not all(field in data for field in required_fields):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            source_content = ai_service.create_source_content(
                tenant_id=tenant_id,
                creator_id=current_user_id,
                title=data['title'],
                description=data.get('description'),
                content_type_name=data.get('content_type', 'text'),
                url=data.get('url'),
                text_content=data.get('text_content')
            )
        
        return jsonify({
            'success': True,
            'content': source_content.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating source content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/source-content', methods=['GET'])
@jwt_required()
def get_source_content():
    """Get source content list."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        content_type = request.args.get('content_type')
        
        query = db.session.query(SourceContent).filter(
            SourceContent.tenant_id == tenant_id
        )
        
        if status:
            query = query.filter(SourceContent.processing_status == status)
        
        if content_type:
            query = query.join(ContentType).filter(ContentType.name == content_type)
        
        # Order by most recent
        query = query.order_by(SourceContent.created_at.desc())
        
        # Pagination
        total = query.count()
        contents = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'contents': [content.to_dict() for content in contents],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting source content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/source-content/<int:content_id>', methods=['GET'])
@jwt_required()
def get_source_content_detail(content_id):
    """Get source content details."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        content = db.session.query(SourceContent).filter(
            SourceContent.id == content_id,
            SourceContent.tenant_id == tenant_id
        ).first()
        
        if not content:
            return jsonify({'success': False, 'error': 'Content not found'}), 404
        
        return jsonify({
            'success': True,
            'content': content.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting source content detail: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/source-content/<int:content_id>/process', methods=['POST'])
@jwt_required()
def process_source_content(content_id):
    """Reprocess source content."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        content = db.session.query(SourceContent).filter(
            SourceContent.id == content_id,
            SourceContent.tenant_id == tenant_id
        ).first()
        
        if not content:
            return jsonify({'success': False, 'error': 'Content not found'}), 404
        
        result = ai_service.process_source_content(content_id)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error processing source content: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Question Generation Endpoints

@ai_question_generation_bp.route('/question-types', methods=['GET'])
@jwt_required()
def get_question_types():
    """Get available question types."""
    try:
        question_types = db.session.query(QuestionType).filter(
            QuestionType.is_active == True
        ).all()
        
        return jsonify({
            'success': True,
            'question_types': [qt.to_dict() for qt in question_types]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting question types: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/blooms-taxonomy', methods=['GET'])
@jwt_required()
def get_blooms_taxonomy():
    """Get Bloom's taxonomy levels."""
    try:
        levels = db.session.query(BloomsTaxonomy).order_by(BloomsTaxonomy.order).all()
        
        return jsonify({
            'success': True,
            'blooms_levels': [level.to_dict() for level in levels]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting Bloom's taxonomy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/learning-objectives', methods=['GET'])
@jwt_required()
def get_learning_objectives():
    """Get learning objectives."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        objectives = db.session.query(LearningObjective).filter(
            LearningObjective.tenant_id == tenant_id,
            LearningObjective.is_active == True
        ).all()
        
        return jsonify({
            'success': True,
            'learning_objectives': [obj.to_dict() for obj in objectives]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting learning objectives: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/learning-objectives', methods=['POST'])
@jwt_required()
def create_learning_objective():
    """Create new learning objective."""
    try:
        current_user_id = get_jwt_identity()
        tenant_id = get_user_tenant_id()
        
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        required_fields = ['title', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        objective = LearningObjective(
            tenant_id=tenant_id,
            creator_id=current_user_id,
            title=data['title'],
            description=data['description'],
            category=data.get('category'),
            blooms_level_id=data.get('blooms_level_id'),
            tags=data.get('tags', [])
        )
        
        db.session.add(objective)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'learning_objective': objective.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating learning objective: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_questions():
    """Generate questions from source content."""
    try:
        current_user_id = get_jwt_identity()
        tenant_id = get_user_tenant_id()
        
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        required_fields = ['source_content_id']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        # Validate parameters
        question_count = data.get('question_count', 10)
        if not isinstance(question_count, int) or question_count < 1 or question_count > 100:
            return jsonify({'success': False, 'error': 'Question count must be between 1 and 100'}), 400
        
        difficulty_range = data.get('difficulty_range', [1, 10])
        if (not isinstance(difficulty_range, list) or 
            len(difficulty_range) != 2 or 
            not all(isinstance(x, (int, float)) for x in difficulty_range) or
            difficulty_range[0] > difficulty_range[1]):
            return jsonify({'success': False, 'error': 'Invalid difficulty range'}), 400
        
        # Start async generation
        async def run_generation():
            return await ai_service.generate_questions(
                tenant_id=tenant_id,
                creator_id=current_user_id,
                source_content_id=data['source_content_id'],
                question_count=question_count,
                question_types=data.get('question_types'),
                difficulty_range=difficulty_range,
                blooms_levels=data.get('blooms_levels'),
                learning_objectives=data.get('learning_objectives'),
                language=data.get('language', 'en'),
                topic_focus=data.get('topic_focus'),
                avoid_topics=data.get('avoid_topics'),
                custom_instructions=data.get('custom_instructions'),
                ai_model=data.get('ai_model', 'gpt-4')
            )
        
        # Run in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_generation())
        loop.close()
        
        if result['success']:
            return jsonify({
                'success': True,
                'request_id': result['request_id'],
                'message': f"Question generation started. Generated {result['questions_generated']} questions.",
                'questions_generated': result['questions_generated']
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error generating questions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/generation-status/<request_id>', methods=['GET'])
@jwt_required()
def get_generation_status(request_id):
    """Get generation request status."""
    try:
        result = ai_service.get_generation_status(request_id)
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error getting generation status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_generated_questions():
    """Get generated questions."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        # Query parameters
        request_id = request.args.get('request_id')
        status = request.args.get('status')
        min_quality = request.args.get('min_quality', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        include_sensitive = request.args.get('include_answers', 'false').lower() == 'true'
        
        result = ai_service.get_generated_questions(
            tenant_id=tenant_id,
            request_id=request_id,
            status=status,
            min_quality=min_quality,
            page=page,
            per_page=per_page
        )
        
        # Filter sensitive data if needed
        if not include_sensitive:
            for question in result['questions']:
                question.pop('correct_answer', None)
                question.pop('generation_prompt', None)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error getting generated questions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/questions/<int:question_id>', methods=['GET'])
@jwt_required()
def get_question_detail(question_id):
    """Get question details."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        question = db.session.query(GeneratedQuestion).join(QuestionGenerationRequest).filter(
            GeneratedQuestion.id == question_id,
            QuestionGenerationRequest.tenant_id == tenant_id
        ).first()
        
        if not question:
            return jsonify({'success': False, 'error': 'Question not found'}), 404
        
        include_sensitive = request.args.get('include_answers', 'false').lower() == 'true'
        
        return jsonify({
            'success': True,
            'question': question.to_dict(include_sensitive=include_sensitive)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting question detail: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/questions/<int:question_id>/approve', methods=['POST'])
@jwt_required()
def approve_question(question_id):
    """Approve a question."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        
        result = ai_service.approve_question(
            question_id=question_id,
            reviewer_id=current_user_id,
            notes=data.get('notes')
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error approving question: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/questions/<int:question_id>/reject', methods=['POST'])
@jwt_required()
def reject_question(question_id):
    """Reject a question."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'notes' not in data:
            return jsonify({'success': False, 'error': 'Rejection notes required'}), 400
        
        result = ai_service.reject_question(
            question_id=question_id,
            reviewer_id=current_user_id,
            notes=data['notes']
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error rejecting question: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Question Bank Endpoints

@ai_question_generation_bp.route('/question-banks', methods=['GET'])
@jwt_required()
def get_question_banks():
    """Get question banks."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        banks = db.session.query(QuestionBank).filter(
            QuestionBank.tenant_id == tenant_id,
            QuestionBank.is_active == True
        ).order_by(QuestionBank.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'question_banks': [bank.to_dict() for bank in banks]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting question banks: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/question-banks', methods=['POST'])
@jwt_required()
def create_question_bank():
    """Create new question bank."""
    try:
        current_user_id = get_jwt_identity()
        tenant_id = get_user_tenant_id()
        
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        required_fields = ['name']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        bank = ai_service.create_question_bank(
            tenant_id=tenant_id,
            creator_id=current_user_id,
            name=data['name'],
            description=data.get('description'),
            category=data.get('category'),
            auto_add_criteria=data.get('auto_add_criteria')
        )
        
        return jsonify({
            'success': True,
            'question_bank': bank.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating question bank: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/question-banks/<int:bank_id>/questions', methods=['POST'])
@jwt_required()
def add_question_to_bank(bank_id):
    """Add question to bank."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'question_id' not in data:
            return jsonify({'success': False, 'error': 'Question ID required'}), 400
        
        result = ai_service.add_question_to_bank(
            bank_id=bank_id,
            question_id=data['question_id'],
            user_id=current_user_id,
            tags=data.get('tags')
        )
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error adding question to bank: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/question-banks/<int:bank_id>/questions', methods=['GET'])
@jwt_required()
def get_bank_questions(bank_id):
    """Get questions in a bank."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Check bank access
        bank = db.session.query(QuestionBank).filter(
            QuestionBank.id == bank_id,
            QuestionBank.tenant_id == tenant_id
        ).first()
        
        if not bank:
            return jsonify({'success': False, 'error': 'Question bank not found'}), 404
        
        # Get questions
        query = db.session.query(GeneratedQuestion).join(QuestionBankQuestion).filter(
            QuestionBankQuestion.question_bank_id == bank_id
        ).order_by(QuestionBankQuestion.created_at.desc())
        
        total = query.count()
        questions = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'bank': bank.to_dict(),
            'questions': [q.to_dict() for q in questions],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting bank questions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Analytics Endpoints

@ai_question_generation_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    """Get question generation analytics."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        days = request.args.get('days', 30, type=int)
        
        result = ai_service.get_analytics(tenant_id, days)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error getting analytics: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/analytics/summary', methods=['GET'])
@jwt_required()
def get_analytics_summary():
    """Get analytics summary."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        # Get summary statistics
        total_requests = db.session.query(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.tenant_id == tenant_id
        ).count()
        
        completed_requests = db.session.query(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.tenant_id == tenant_id,
            QuestionGenerationRequest.status == 'completed'
        ).count()
        
        total_questions = db.session.query(GeneratedQuestion).join(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.tenant_id == tenant_id
        ).count()
        
        approved_questions = db.session.query(GeneratedQuestion).join(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.tenant_id == tenant_id,
            GeneratedQuestion.status == 'approved'
        ).count()
        
        avg_quality = db.session.query(func.avg(GeneratedQuestion.quality_score)).join(
            QuestionGenerationRequest
        ).filter(
            QuestionGenerationRequest.tenant_id == tenant_id,
            GeneratedQuestion.quality_score.isnot(None)
        ).scalar() or 0.0
        
        total_banks = db.session.query(QuestionBank).filter(
            QuestionBank.tenant_id == tenant_id,
            QuestionBank.is_active == True
        ).count()
        
        return jsonify({
            'success': True,
            'summary': {
                'total_requests': total_requests,
                'completed_requests': completed_requests,
                'success_rate': completed_requests / max(total_requests, 1),
                'total_questions_generated': total_questions,
                'approved_questions': approved_questions,
                'approval_rate': approved_questions / max(total_questions, 1),
                'average_quality_score': round(avg_quality, 2),
                'total_question_banks': total_banks
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting analytics summary: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Duplicate Detection Endpoints

@ai_question_generation_bp.route('/duplicates', methods=['GET'])
@jwt_required()
def get_duplicates():
    """Get detected duplicate questions."""
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        status = request.args.get('status', 'pending')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        query = db.session.query(QuestionDuplicate).join(
            GeneratedQuestion, QuestionDuplicate.question1_id == GeneratedQuestion.id
        ).join(
            QuestionGenerationRequest, GeneratedQuestion.generation_request_id == QuestionGenerationRequest.id
        ).filter(
            QuestionGenerationRequest.tenant_id == tenant_id,
            QuestionDuplicate.status == status
        ).order_by(QuestionDuplicate.similarity_score.desc())
        
        total = query.count()
        duplicates = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'duplicates': [dup.to_dict() for dup in duplicates],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting duplicates: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/duplicates/<int:duplicate_id>/resolve', methods=['POST'])
@jwt_required()
def resolve_duplicate(duplicate_id):
    """Resolve a duplicate question detection."""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or 'action' not in data:
            return jsonify({'success': False, 'error': 'Action required'}), 400
        
        duplicate = db.session.query(QuestionDuplicate).get(duplicate_id)
        if not duplicate:
            return jsonify({'success': False, 'error': 'Duplicate not found'}), 404
        
        action = data['action']  # 'confirm' or 'dismiss'
        
        if action == 'confirm':
            duplicate.status = 'confirmed'
        elif action == 'dismiss':
            duplicate.status = 'dismissed'
        else:
            return jsonify({'success': False, 'error': 'Invalid action'}), 400
        
        duplicate.reviewed_by = current_user_id
        duplicate.resolution_notes = data.get('notes')
        
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error resolving duplicate: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Utility Endpoints

@ai_question_generation_bp.route('/export/questions', methods=['POST'])
@jwt_required()
def export_questions():
    """Export questions to various formats."""
    try:
        data = request.get_json()
        if not data or 'question_ids' not in data:
            return jsonify({'success': False, 'error': 'Question IDs required'}), 400
        
        format_type = data.get('format', 'json')  # json, csv, xlsx, pdf
        
        if format_type not in ['json', 'csv']:
            return jsonify({'success': False, 'error': 'Unsupported format'}), 400
        
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': 'User tenant not found'}), 400
        
        # Get questions
        questions = db.session.query(GeneratedQuestion).join(QuestionGenerationRequest).filter(
            GeneratedQuestion.id.in_(data['question_ids']),
            QuestionGenerationRequest.tenant_id == tenant_id
        ).all()
        
        if not questions:
            return jsonify({'success': False, 'error': 'No questions found'}), 404
        
        # Export based on format
        if format_type == 'json':
            export_data = {
                'questions': [q.to_dict(include_sensitive=True) for q in questions],
                'exported_at': datetime.utcnow().isoformat(),
                'total_questions': len(questions)
            }
            
            return jsonify({
                'success': True,
                'data': export_data
            })
        
        # For other formats, you would implement file generation and return file
        return jsonify({'success': False, 'error': 'Format not implemented yet'}), 501
        
    except Exception as e:
        current_app.logger.error(f"Error exporting questions: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/initialize', methods=['POST'])
@jwt_required()
def initialize_system():
    """Initialize system with default data."""
    try:
        # This should only be accessible to admins
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(current_user_id)
        
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'error': 'Admin access required'}), 403
        
        ai_service.initialize_default_data()
        
        return jsonify({
            'success': True,
            'message': 'System initialized with default data'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error initializing system: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Error handlers
@ai_question_generation_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    return jsonify({
        'success': False,
        'error': f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB'
    }), 413


@ai_question_generation_bp.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors."""
    current_app.logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500