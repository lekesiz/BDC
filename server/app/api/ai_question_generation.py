from flask_babel import _

_('api_ai_question_generation.message.ai_question_generation_api_end')
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
from app.models.ai_question_generation import ContentType, QuestionType, BloomsTaxonomy, LearningObjective, QuestionGenerationRequest, GeneratedQuestion, QuestionDuplicate, QuestionBank, QuestionBankQuestion, GenerationAnalytics
from app.models.user import User
from app.services.ai_question_generator_service import AIQuestionGeneratorService
from app.utils.decorators import requires_permission
from app.utils.logging import logger
from flask_babel import _, lazy_gettext as _l
ai_question_generation_bp = Blueprint('ai_question_generation', __name__,
    url_prefix='/api/ai-questions')
# ai_service = AIQuestionGeneratorService()  # TODO: Fix SourceContent dependency
ai_service = None
UPLOAD_FOLDER = '/tmp/question_generation_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', _(
    'services_ai_question_generator_service.message.mp3_1'), 'wav', _(
    'services_ai_question_generator_service.message.m4a'), _(
    'services_storage_service.message.mp4'), 'avi', 'mov'}
MAX_FILE_SIZE = 50 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    _('services_storage_service.message.check_if_file_extension_is_all')
    return '.' in filename and filename.rsplit('.', 1)[1].lower(
        ) in ALLOWED_EXTENSIONS


def get_user_tenant_id():
    _('api_ai_question_generation.message.get_current_user_s_tenant_id')
    current_user_id = get_jwt_identity()
    user = db.session.query(User).get(current_user_id)
    return user.tenant_id if user else None


@ai_question_generation_bp.route('/health', methods=['GET'])
def health_check():
    _('api_ai_question_generation.label.health_check_endpoint')
    return jsonify({'status': 'healthy', 'service': _(
        'api_ai_question_generation.label.ai_question_generation'),
        'timestamp': datetime.utcnow().isoformat()})


@ai_question_generation_bp.route('/content-types', methods=['GET'])
@jwt_required()
def get_content_types():
    _('api_ai_question_generation.message.get_available_content_types')
    try:
        content_types = db.session.query(ContentType).filter(ContentType.
            is_active == True).all()
        return jsonify({'success': True, 'content_types': [ct.to_dict() for
            ct in content_types]})
    except Exception as e:
        current_app.logger.error(f'Error getting content types: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/source-content', methods=['POST'])
@jwt_required()
def create_source_content():
    _('api_ai_question_generation.message.create_new_source_content')
    try:
        current_user_id = get_jwt_identity()
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.utcnow().strftime(_(
                    'analytics_analytics_orchestrator.message.y_m_d_h_m_s_2'))
                filename = f'{timestamp}_{filename}'
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    file.save(file_path)
                except RequestEntityTooLarge:
                    return jsonify({'success': False, 'error':
                        f'File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB'
                        }), 413
                title = request.form.get('title', filename)
                description = request.form.get('description')
                content_type_name = request.form.get('content_type', 'document'
                    )
                source_content = ai_service.create_source_content(tenant_id
                    =tenant_id, creator_id=current_user_id, title=title,
                    description=description, content_type_name=
                    content_type_name, file_path=file_path)
            else:
                return jsonify({'success': False, 'error': _(
                    'i18n_translation_service.error.invalid_file_type')}), 400
        else:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'error': _(
                    'api_ai_question_generation.label.no_data_provided_3')}
                    ), 400
            required_fields = ['title']
            if not all(field in data for field in required_fields):
                return jsonify({'success': False, 'error': _(
                    'api_ai_question_generation.validation.missing_required_fields_3'
                    )}), 400
            source_content = ai_service.create_source_content(tenant_id=
                tenant_id, creator_id=current_user_id, title=data['title'],
                description=data.get('description'), content_type_name=data
                .get('content_type', 'text'), url=data.get('url'),
                text_content=data.get('text_content'))
        return jsonify({'success': True, 'content': source_content.to_dict()}
            ), 201
    except Exception as e:
        current_app.logger.error(f'Error creating source content: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/source-content', methods=['GET'])
@jwt_required()
def get_source_content():
    _('api_ai_question_generation.message.get_source_content_list')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        content_type = request.args.get('content_type')
        query = db.session.query(SourceContent).filter(SourceContent.
            tenant_id == tenant_id)
        if status:
            query = query.filter(SourceContent.processing_status == status)
        if content_type:
            query = query.join(ContentType).filter(ContentType.name ==
                content_type)
        query = query.order_by(SourceContent.created_at.desc())
        total = query.count()
        contents = query.offset((page - 1) * per_page).limit(per_page).all()
        return jsonify({'success': True, 'contents': [content.to_dict() for
            content in contents], 'pagination': {'page': page, 'per_page':
            per_page, 'total': total, 'pages': (total + per_page - 1) //
            per_page}})
    except Exception as e:
        current_app.logger.error(f'Error getting source content: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/source-content/<int:content_id>',
    methods=['GET'])
@jwt_required()
def get_source_content_detail(content_id):
    _('api_ai_question_generation.message.get_source_content_details')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        content = db.session.query(SourceContent).filter(SourceContent.id ==
            content_id, SourceContent.tenant_id == tenant_id).first()
        if not content:
            return jsonify({'success': False, 'error': _(
                'api_i18n.label.content_not_found')}), 404
        return jsonify({'success': True, 'content': content.to_dict()})
    except Exception as e:
        current_app.logger.error(
            f'Error getting source content detail: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/source-content/<int:content_id>/process',
    methods=['POST'])
@jwt_required()
def process_source_content(content_id):
    _('api_ai_question_generation.label.reprocess_source_content')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        content = db.session.query(SourceContent).filter(SourceContent.id ==
            content_id, SourceContent.tenant_id == tenant_id).first()
        if not content:
            return jsonify({'success': False, 'error': _(
                'api_i18n.label.content_not_found')}), 404
        result = ai_service.process_source_content(content_id)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Error processing source content: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/question-types', methods=['GET'])
@jwt_required()
def get_question_types():
    _('api_ai_question_generation.message.get_available_question_types')
    try:
        question_types = db.session.query(QuestionType).filter(QuestionType
            .is_active == True).all()
        return jsonify({'success': True, 'question_types': [qt.to_dict() for
            qt in question_types]})
    except Exception as e:
        current_app.logger.error(f'Error getting question types: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/blooms-taxonomy', methods=['GET'])
@jwt_required()
def get_blooms_taxonomy():
    _('api_ai_question_generation.message.get_bloom_s_taxonomy_levels')
    try:
        levels = db.session.query(BloomsTaxonomy).order_by(BloomsTaxonomy.order
            ).all()
        return jsonify({'success': True, 'blooms_levels': [level.to_dict() for
            level in levels]})
    except Exception as e:
        current_app.logger.error(f"Error getting Bloom's taxonomy: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/learning-objectives', methods=['GET'])
@jwt_required()
def get_learning_objectives():
    _('api_ai_question_generation.label.get_learning_objectives')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        objectives = db.session.query(LearningObjective).filter(
            LearningObjective.tenant_id == tenant_id, LearningObjective.
            is_active == True).all()
        return jsonify({'success': True, 'learning_objectives': [obj.
            to_dict() for obj in objectives]})
    except Exception as e:
        current_app.logger.error(f'Error getting learning objectives: {str(e)}'
            )
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/learning-objectives', methods=['POST'])
@jwt_required()
def create_learning_objective():
    _('api_ai_question_generation.message.create_new_learning_objective')
    try:
        current_user_id = get_jwt_identity()
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.label.no_data_provided_3')}), 400
        required_fields = ['title', 'description']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.missing_required_fields_3'
                )}), 400
        objective = LearningObjective(tenant_id=tenant_id, creator_id=
            current_user_id, title=data['title'], description=data[
            'description'], category=data.get('category'), blooms_level_id=
            data.get('blooms_level_id'), tags=data.get('tags', []))
        db.session.add(objective)
        db.session.commit()
        return jsonify({'success': True, 'learning_objective': objective.
            to_dict()}), 201
    except Exception as e:
        current_app.logger.error(f'Error creating learning objective: {str(e)}'
            )
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_questions():
    """Generate questions from source content."""
    try:
        current_user_id = get_jwt_identity()
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.label.no_data_provided_3')}), 400
        required_fields = ['source_content_id']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.missing_required_fields_3'
                )}), 400
        question_count = data.get('question_count', 10)
        if not isinstance(question_count, int
            ) or question_count < 1 or question_count > 100:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.question_count_must_be_between'
                )}), 400
        difficulty_range = data.get('difficulty_range', [1, 10])
        if not isinstance(difficulty_range, list) or len(difficulty_range
            ) != 2 or not all(isinstance(x, (int, float)) for x in
            difficulty_range) or difficulty_range[0] > difficulty_range[1]:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.error.invalid_difficulty_range')}
                ), 400

        async def run_generation():
            return await ai_service.generate_questions(tenant_id=tenant_id,
                creator_id=current_user_id, source_content_id=data[
                'source_content_id'], question_count=question_count,
                question_types=data.get('question_types'), difficulty_range
                =difficulty_range, blooms_levels=data.get('blooms_levels'),
                learning_objectives=data.get('learning_objectives'),
                language=data.get('language', 'en'), topic_focus=data.get(
                'topic_focus'), avoid_topics=data.get('avoid_topics'),
                custom_instructions=data.get('custom_instructions'),
                ai_model=data.get('ai_model', _(
                'orchestration_examples.message.gpt_4_2')))
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(run_generation())
        loop.close()
        if result['success']:
            return jsonify({'success': True, 'request_id': result[
                'request_id'], 'message':
                f"Question generation started. Generated {result['questions_generated']} questions."
                , 'questions_generated': result['questions_generated']}), 201
        else:
            return jsonify({'success': False, 'error': result['error']}), 400
    except Exception as e:
        current_app.logger.error(f'Error generating questions: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/generation-status/<request_id>', methods
    =['GET'])
@jwt_required()
def get_generation_status(request_id):
    _('api_ai_question_generation.message.get_generation_request_status')
    try:
        result = ai_service.get_generation_status(request_id)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Error getting generation status: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/questions', methods=['GET'])
@jwt_required()
def get_generated_questions():
    _('api_ai_question_generation.label.get_generated_questions')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        request_id = request.args.get('request_id')
        status = request.args.get('status')
        min_quality = request.args.get('min_quality', type=float)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        include_sensitive = request.args.get('include_answers', 'false').lower(
            ) == 'true'
        result = ai_service.get_generated_questions(tenant_id=tenant_id,
            request_id=request_id, status=status, min_quality=min_quality,
            page=page, per_page=per_page)
        if not include_sensitive:
            for question in result['questions']:
                question.pop('correct_answer', None)
                question.pop('generation_prompt', None)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Error getting generated questions: {str(e)}'
            )
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/questions/<int:question_id>', methods=[
    'GET'])
@jwt_required()
def get_question_detail(question_id):
    _('api_ai_question_generation.label.get_question_details')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        question = db.session.query(GeneratedQuestion).join(
            QuestionGenerationRequest).filter(GeneratedQuestion.id ==
            question_id, QuestionGenerationRequest.tenant_id == tenant_id
            ).first()
        if not question:
            return jsonify({'success': False, 'error': _(
                'services_ai_question_generator_service.label.question_not_found_1'
                )}), 404
        include_sensitive = request.args.get('include_answers', 'false').lower(
            ) == 'true'
        return jsonify({'success': True, 'question': question.to_dict(
            include_sensitive=include_sensitive)})
    except Exception as e:
        current_app.logger.error(f'Error getting question detail: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/questions/<int:question_id>/approve',
    methods=['POST'])
@jwt_required()
def approve_question(question_id):
    _('api_ai_question_generation.label.approve_a_question')
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json() or {}
        result = ai_service.approve_question(question_id=question_id,
            reviewer_id=current_user_id, notes=data.get('notes'))
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Error approving question: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/questions/<int:question_id>/reject',
    methods=['POST'])
@jwt_required()
def reject_question(question_id):
    _('api_ai_question_generation.label.reject_a_question')
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        if not data or 'notes' not in data:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.rejection_notes_required'
                )}), 400
        result = ai_service.reject_question(question_id=question_id,
            reviewer_id=current_user_id, notes=data['notes'])
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Error rejecting question: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/question-banks', methods=['GET'])
@jwt_required()
def get_question_banks():
    _('api_ai_question_generation.label.get_question_banks')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        banks = db.session.query(QuestionBank).filter(QuestionBank.
            tenant_id == tenant_id, QuestionBank.is_active == True).order_by(
            QuestionBank.created_at.desc()).all()
        return jsonify({'success': True, 'question_banks': [bank.to_dict() for
            bank in banks]})
    except Exception as e:
        current_app.logger.error(f'Error getting question banks: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/question-banks', methods=['POST'])
@jwt_required()
def create_question_bank():
    _('api_ai_question_generation.message.create_new_question_bank')
    try:
        current_user_id = get_jwt_identity()
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.label.no_data_provided_3')}), 400
        required_fields = ['name']
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.missing_required_fields_3'
                )}), 400
        bank = ai_service.create_question_bank(tenant_id=tenant_id,
            creator_id=current_user_id, name=data['name'], description=data
            .get('description'), category=data.get('category'),
            auto_add_criteria=data.get('auto_add_criteria'))
        return jsonify({'success': True, 'question_bank': bank.to_dict()}), 201
    except Exception as e:
        current_app.logger.error(f'Error creating question bank: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/question-banks/<int:bank_id>/questions',
    methods=['POST'])
@jwt_required()
def add_question_to_bank(bank_id):
    _('api_ai_question_generation.message.add_question_to_bank')
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        if not data or 'question_id' not in data:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.question_id_required')}
                ), 400
        result = ai_service.add_question_to_bank(bank_id=bank_id,
            question_id=data['question_id'], user_id=current_user_id, tags=
            data.get('tags'))
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Error adding question to bank: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/question-banks/<int:bank_id>/questions',
    methods=['GET'])
@jwt_required()
def get_bank_questions(bank_id):
    _('api_ai_question_generation.message.get_questions_in_a_bank')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        bank = db.session.query(QuestionBank).filter(QuestionBank.id ==
            bank_id, QuestionBank.tenant_id == tenant_id).first()
        if not bank:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.question_bank_not_found')}
                ), 404
        query = db.session.query(GeneratedQuestion).join(QuestionBankQuestion
            ).filter(QuestionBankQuestion.question_bank_id == bank_id
            ).order_by(QuestionBankQuestion.created_at.desc())
        total = query.count()
        questions = query.offset((page - 1) * per_page).limit(per_page).all()
        return jsonify({'success': True, 'bank': bank.to_dict(),
            'questions': [q.to_dict() for q in questions], 'pagination': {
            'page': page, 'per_page': per_page, 'total': total, 'pages': (
            total + per_page - 1) // per_page}})
    except Exception as e:
        current_app.logger.error(f'Error getting bank questions: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    _('services_ai_question_generator_service.message.get_question_generation_analyt'
        )
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        days = request.args.get('days', 30, type=int)
        result = ai_service.get_analytics(tenant_id, days)
        return jsonify(result)
    except Exception as e:
        current_app.logger.error(f'Error getting analytics: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/analytics/summary', methods=['GET'])
@jwt_required()
def get_analytics_summary():
    _('api_ai_question_generation.label.get_analytics_summary')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        total_requests = db.session.query(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.tenant_id == tenant_id).count()
        completed_requests = db.session.query(QuestionGenerationRequest
            ).filter(QuestionGenerationRequest.tenant_id == tenant_id, 
            QuestionGenerationRequest.status == 'completed').count()
        total_questions = db.session.query(GeneratedQuestion).join(
            QuestionGenerationRequest).filter(QuestionGenerationRequest.
            tenant_id == tenant_id).count()
        approved_questions = db.session.query(GeneratedQuestion).join(
            QuestionGenerationRequest).filter(QuestionGenerationRequest.
            tenant_id == tenant_id, GeneratedQuestion.status == 'approved'
            ).count()
        avg_quality = db.session.query(func.avg(GeneratedQuestion.
            quality_score)).join(QuestionGenerationRequest).filter(
            QuestionGenerationRequest.tenant_id == tenant_id,
            GeneratedQuestion.quality_score.isnot(None)).scalar() or 0.0
        total_banks = db.session.query(QuestionBank).filter(QuestionBank.
            tenant_id == tenant_id, QuestionBank.is_active == True).count()
        return jsonify({'success': True, 'summary': {'total_requests':
            total_requests, 'completed_requests': completed_requests,
            'success_rate': completed_requests / max(total_requests, 1),
            'total_questions_generated': total_questions,
            'approved_questions': approved_questions, 'approval_rate': 
            approved_questions / max(total_questions, 1),
            'average_quality_score': round(avg_quality, 2),
            'total_question_banks': total_banks}})
    except Exception as e:
        current_app.logger.error(f'Error getting analytics summary: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/duplicates', methods=['GET'])
@jwt_required()
def get_duplicates():
    _('api_ai_question_generation.message.get_detected_duplicate_questio')
    try:
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        status = request.args.get('status', 'pending')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        query = db.session.query(QuestionDuplicate).join(GeneratedQuestion,
            QuestionDuplicate.question1_id == GeneratedQuestion.id).join(
            QuestionGenerationRequest, GeneratedQuestion.
            generation_request_id == QuestionGenerationRequest.id).filter(
            QuestionGenerationRequest.tenant_id == tenant_id, 
            QuestionDuplicate.status == status).order_by(QuestionDuplicate.
            similarity_score.desc())
        total = query.count()
        duplicates = query.offset((page - 1) * per_page).limit(per_page).all()
        return jsonify({'success': True, 'duplicates': [dup.to_dict() for
            dup in duplicates], 'pagination': {'page': page, 'per_page':
            per_page, 'total': total, 'pages': (total + per_page - 1) //
            per_page}})
    except Exception as e:
        current_app.logger.error(f'Error getting duplicates: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/duplicates/<int:duplicate_id>/resolve',
    methods=['POST'])
@jwt_required()
def resolve_duplicate(duplicate_id):
    _('api_ai_question_generation.message.resolve_a_duplicate_question_d')
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        if not data or 'action' not in data:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.action_required')}), 400
        duplicate = db.session.query(QuestionDuplicate).get(duplicate_id)
        if not duplicate:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.label.duplicate_not_found')}), 404
        action = data['action']
        if action == 'confirm':
            duplicate.status = 'confirmed'
        elif action == 'dismiss':
            duplicate.status = 'dismissed'
        else:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.error.invalid_action')}), 400
        duplicate.reviewed_by = current_user_id
        duplicate.resolution_notes = data.get('notes')
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        current_app.logger.error(f'Error resolving duplicate: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/export/questions', methods=['POST'])
@jwt_required()
def export_questions():
    _('api_ai_question_generation.validation.export_questions_to_various_fo')
    try:
        data = request.get_json()
        if not data or 'question_ids' not in data:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.question_ids_required')}
                ), 400
        format_type = data.get('format', 'json')
        if format_type not in ['json', 'csv']:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.unsupported_format')}
                ), 400
        tenant_id = get_user_tenant_id()
        if not tenant_id:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.message.user_tenant_not_found_15')}
                ), 400
        questions = db.session.query(GeneratedQuestion).join(
            QuestionGenerationRequest).filter(GeneratedQuestion.id.in_(data
            ['question_ids']), QuestionGenerationRequest.tenant_id == tenant_id
            ).all()
        if not questions:
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.label.no_questions_found')}), 404
        if format_type == 'json':
            export_data = {'questions': [q.to_dict(include_sensitive=True) for
                q in questions], 'exported_at': datetime.utcnow().isoformat
                (), 'total_questions': len(questions)}
            return jsonify({'success': True, 'data': export_data})
        return jsonify({'success': False, 'error': _(
            'api_ai_question_generation.validation.format_not_implemented_yet'
            )}), 501
    except Exception as e:
        current_app.logger.error(f'Error exporting questions: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.route('/initialize', methods=['POST'])
@jwt_required()
def initialize_system():
    _('api_ai_question_generation.message.initialize_system_with_default')
    try:
        current_user_id = get_jwt_identity()
        user = db.session.query(User).get(current_user_id)
        if not user or user.role != 'admin':
            return jsonify({'success': False, 'error': _(
                'api_ai_question_generation.validation.admin_access_required')}
                ), 403
        ai_service.initialize_default_data()
        return jsonify({'success': True, 'message': _(
            'api_ai_question_generation.message.system_initialized_with_defaul'
            )})
    except Exception as e:
        current_app.logger.error(f'Error initializing system: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@ai_question_generation_bp.errorhandler(413)
def request_entity_too_large(error):
    _('api_ai_question_generation.error.handle_file_too_large_error')
    return jsonify({'success': False, 'error':
        f'File too large. Maximum size is {MAX_FILE_SIZE // (1024 * 1024)}MB'}
        ), 413


@ai_question_generation_bp.errorhandler(500)
def internal_server_error(error):
    _('api_ai_question_generation.error.handle_internal_server_errors')
    current_app.logger.error(f'Internal server error: {str(error)}')
    return jsonify({'success': False, 'error': _(
        'file_upload_api_example.error.internal_server_error_6')}), 500
