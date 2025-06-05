"""Assessment templates API endpoints."""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User
from app.models.assessment import AssessmentTemplate, AssessmentSection, AssessmentQuestion
from app.schemas.assessment import (

from app.utils.logging import logger
    AssessmentTemplateSchema,
    AssessmentTemplateCreateSchema,
    AssessmentTemplateUpdateSchema
)

assessment_templates_bp = Blueprint('assessment_templates', __name__)
template_schema = AssessmentTemplateSchema()
template_list_schema = AssessmentTemplateSchema(many=True)
template_create_schema = AssessmentTemplateCreateSchema()
template_update_schema = AssessmentTemplateUpdateSchema()


@assessment_templates_bp.route('/assessment/templates', methods=['GET'])
@jwt_required()
def get_assessment_templates():
    """Get all assessment templates."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get query parameters
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    is_active = request.args.get('is_active', type=bool)
    search = request.args.get('search')
    
    query = AssessmentTemplate.query
    
    # Filter by tenant
    if hasattr(current_user, 'tenant_id') and current_user.tenant_id:
        query = query.filter_by(tenant_id=current_user.tenant_id)
    
    # Apply filters
    if category:
        query = query.filter_by(category=category)
    if difficulty:
        query = query.filter_by(difficulty_level=difficulty)
    if is_active is not None:
        query = query.filter_by(is_active=is_active)
    if search:
        query = query.filter(
            db.or_(
                AssessmentTemplate.name.ilike(f'%{search}%'),
                AssessmentTemplate.description.ilike(f'%{search}%')
            )
        )
    
    # Order by created date
    query = query.order_by(AssessmentTemplate.created_at.desc())
    
    templates = query.all()
    return jsonify(template_list_schema.dump(templates)), 200


@assessment_templates_bp.route('/assessment/templates/<int:template_id>', methods=['GET'])
@jwt_required()
def get_assessment_template(template_id):
    """Get a specific assessment template."""
    current_user_id = get_jwt_identity()
    
    template = AssessmentTemplate.query.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Check permissions
    current_user = User.query.get(current_user_id)
    if hasattr(current_user, 'tenant_id') and current_user.tenant_id:
        if template.tenant_id != current_user.tenant_id:
            return jsonify({'error': 'Unauthorized to view this template'}), 403
    
    return jsonify(template_schema.dump(template)), 200


@assessment_templates_bp.route('/assessment/templates', methods=['POST'])
@jwt_required()
def create_assessment_template():
    """Create a new assessment template."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions - only trainers and admins can create templates
    if current_user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized to create templates'}), 403
    
    # Validate request data
    errors = template_create_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    try:
        # Create template
        template_data = request.json
        sections_data = template_data.pop('sections', [])
        
        # Set tenant_id and created_by
        template_data['tenant_id'] = getattr(current_user, 'tenant_id', None)
        template_data['created_by'] = current_user_id
        
        template = AssessmentTemplate(**template_data)
        db.session.add(template)
        db.session.flush()  # Get template ID
        
        # Create sections and questions
        for section_index, section_data in enumerate(sections_data):
            questions_data = section_data.pop('questions', [])
            section_data['template_id'] = template.id
            section_data['order_index'] = section_index
            
            section = AssessmentSection(**section_data)
            db.session.add(section)
            db.session.flush()  # Get section ID
            
            # Create questions
            for question_index, question_data in enumerate(questions_data):
                question_data['section_id'] = section.id
                question_data['order_index'] = question_index
                
                question = AssessmentQuestion(**question_data)
                db.session.add(question)
        
        db.session.commit()
        return jsonify(template_schema.dump(template)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_templates_bp.route('/assessment/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
def update_assessment_template(template_id):
    """Update an assessment template."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    template = AssessmentTemplate.query.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Check permissions
    if current_user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized to update templates'}), 403
    
    if template.created_by != current_user_id:
        if current_user.role not in ['super_admin', 'tenant_admin']:
            return jsonify({'error': 'Unauthorized to update this template'}), 403
    
    # Validate request data
    errors = template_update_schema.validate(request.json)
    if errors:
        return jsonify({'errors': errors}), 400
    
    try:
        # Update template fields
        for key, value in request.json.items():
            if key != 'sections' and hasattr(template, key):
                setattr(template, key, value)
        
        # Update sections if provided
        if 'sections' in request.json:
            # This is complex - might want to handle in a separate endpoint
            pass
        
        db.session.commit()
        return jsonify(template_schema.dump(template)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_templates_bp.route('/assessment/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
def delete_assessment_template(template_id):
    """Delete an assessment template."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    template = AssessmentTemplate.query.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Check permissions
    if current_user.role not in ['super_admin', 'tenant_admin']:
        if template.created_by != current_user_id:
            return jsonify({'error': 'Unauthorized to delete this template'}), 403
    
    try:
        # Check if template is in use
        if template.assessments:
            return jsonify({'error': 'Cannot delete template that is in use'}), 400
        
        db.session.delete(template)
        db.session.commit()
        return jsonify({'message': 'Template deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_templates_bp.route('/assessment/templates/<int:template_id>/duplicate', methods=['POST'])
@jwt_required()
def duplicate_assessment_template(template_id):
    """Duplicate an assessment template."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions
    if current_user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized to duplicate templates'}), 403
    
    template = AssessmentTemplate.query.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    try:
        # Create duplicate template
        new_template = AssessmentTemplate(
            name=f"{template.name} (Copy)",
            description=template.description,
            category=template.category,
            difficulty_level=template.difficulty_level,
            time_limit=template.time_limit,
            total_points=template.total_points,
            passing_score=template.passing_score,
            instructions=template.instructions,
            is_active=False,  # Set to inactive by default
            tenant_id=template.tenant_id,
            created_by=current_user_id
        )
        db.session.add(new_template)
        db.session.flush()
        
        # Duplicate sections and questions
        for section in template.sections:
            new_section = AssessmentSection(
                template_id=new_template.id,
                name=section.name,
                description=section.description,
                order_index=section.order_index,
                points=section.points
            )
            db.session.add(new_section)
            db.session.flush()
            
            # Duplicate questions
            for question in section.questions:
                new_question = AssessmentQuestion(
                    section_id=new_section.id,
                    question_text=question.question_text,
                    question_type=question.question_type,
                    points=question.points,
                    correct_answer=question.correct_answer,
                    answer_options=question.answer_options,
                    order_index=question.order_index,
                    is_required=question.is_required
                )
                db.session.add(new_question)
        
        db.session.commit()
        return jsonify(template_schema.dump(new_template)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_templates_bp.route('/assessment/templates/<int:template_id>/activate', methods=['POST'])
@jwt_required()
def activate_assessment_template(template_id):
    """Activate or deactivate an assessment template."""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check permissions
    if current_user.role not in ['super_admin', 'tenant_admin', 'trainer']:
        return jsonify({'error': 'Unauthorized to modify template status'}), 403
    
    template = AssessmentTemplate.query.get(template_id)
    if not template:
        return jsonify({'error': 'Template not found'}), 404
    
    # Toggle active status
    is_active = request.json.get('is_active', not template.is_active)
    template.is_active = is_active
    
    try:
        db.session.commit()
        return jsonify({
            'message': f"Template {'activated' if is_active else 'deactivated'} successfully",
            'is_active': template.is_active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_templates_bp.route('/assessment/templates/categories', methods=['GET'])
@jwt_required()
def get_template_categories():
    """Get available template categories."""
    categories = [
        {'id': 'technical', 'name': 'Technical Skills', 'description': 'Programming and technical assessments'},
        {'id': 'soft_skills', 'name': 'Soft Skills', 'description': 'Communication and interpersonal assessments'},
        {'id': 'language', 'name': 'Language Proficiency', 'description': 'Language skill assessments'},
        {'id': 'general', 'name': 'General Knowledge', 'description': 'General aptitude and knowledge tests'},
        {'id': 'compliance', 'name': 'Compliance', 'description': 'Regulatory and compliance assessments'},
        {'id': 'custom', 'name': 'Custom', 'description': 'Custom assessments for specific needs'}
    ]
    return jsonify(categories), 200


@assessment_templates_bp.route('/assessment/templates/question-types', methods=['GET'])
@jwt_required()
def get_question_types():
    """Get available question types."""
    question_types = [
        {'id': 'multiple_choice', 'name': 'Multiple Choice', 'description': 'Select one correct answer'},
        {'id': 'multiple_select', 'name': 'Multiple Select', 'description': 'Select multiple correct answers'},
        {'id': 'true_false', 'name': 'True/False', 'description': 'Binary choice questions'},
        {'id': 'short_answer', 'name': 'Short Answer', 'description': 'Text input for short responses'},
        {'id': 'essay', 'name': 'Essay', 'description': 'Long-form text responses'},
        {'id': 'code', 'name': 'Code', 'description': 'Programming code submission'},
        {'id': 'file_upload', 'name': 'File Upload', 'description': 'Upload documents or files'}
    ]
    return jsonify(question_types), 200