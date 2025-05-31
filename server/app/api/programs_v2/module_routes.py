from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.program import Program, ProgramModule
from app.models.user import User

from . import programs_bp


def _check_admin(user):
    return user.role in ['super_admin', 'tenant_admin']


@programs_bp.route('/programs/<int:program_id>/modules', methods=['GET'])
@jwt_required()
def list_program_modules(program_id):
    """List all modules for a program."""
    program = Program.query.get_or_404(program_id)
    modules = ProgramModule.query.filter_by(program_id=program_id).order_by(ProgramModule.order).all()
    return jsonify([m.to_dict() for m in modules]), 200


@programs_bp.route('/programs/<int:program_id>/modules/<int:module_id>', methods=['GET'])
@jwt_required()
def get_program_module(program_id, module_id):
    """Get a specific module."""
    program = Program.query.get_or_404(program_id)
    module = ProgramModule.query.filter_by(id=module_id, program_id=program_id).first_or_404()
    return jsonify(module.to_dict()), 200


@programs_bp.route('/programs/<int:program_id>/modules', methods=['POST'])
@jwt_required()
def create_program_module(program_id):
    """Create a new module for a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check permissions
    if not _check_admin(user):
        return jsonify({'error': 'Unauthorized'}), 403
        
    program = Program.query.get_or_404(program_id)
    
    # Ensure user has access to this program's tenant
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'error': 'Module name is required'}), 400
        
    # Get highest order value to append new module at the end
    max_order = db.session.query(db.func.max(ProgramModule.order)).filter_by(program_id=program_id).scalar() or 0
        
    # Create module
    module = ProgramModule(
        program_id=program_id,
        name=data['name'],
        description=data.get('description', ''),
        order=data.get('order', max_order + 1),
        content=data.get('content', ''),
        resources=data.get('resources', []),
        duration=data.get('duration'),
        is_mandatory=data.get('is_mandatory', True)
    )
    
    db.session.add(module)
    db.session.commit()
    
    # Emit real-time event
    try:
        from app.realtime import emit_to_tenant
        emit_to_tenant(
            program.tenant_id,
            'program_module_created',
            {
                'program_id': program_id,
                'module': module.to_dict()
            }
        )
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(f"Failed to emit program_module_created event: {e}")
    
    return jsonify(module.to_dict()), 201


@programs_bp.route('/programs/<int:program_id>/modules/<int:module_id>', methods=['PUT'])
@jwt_required()
def update_program_module(program_id, module_id):
    """Update a program module."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check permissions
    if not _check_admin(user):
        return jsonify({'error': 'Unauthorized'}), 403
        
    program = Program.query.get_or_404(program_id)
    
    # Ensure user has access to this program's tenant
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    module = ProgramModule.query.filter_by(id=module_id, program_id=program_id).first_or_404()
    data = request.get_json()
    
    # Update fields
    if 'name' in data:
        module.name = data['name']
    if 'description' in data:
        module.description = data['description']
    if 'order' in data:
        module.order = data['order']
    if 'content' in data:
        module.content = data['content']
    if 'resources' in data:
        module.resources = data['resources']
    if 'duration' in data:
        module.duration = data['duration']
    if 'is_mandatory' in data:
        module.is_mandatory = data['is_mandatory']
        
    db.session.commit()
    
    # Emit real-time event
    try:
        from app.realtime import emit_to_tenant
        emit_to_tenant(
            program.tenant_id,
            'program_module_updated',
            {
                'program_id': program_id,
                'module': module.to_dict()
            }
        )
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(f"Failed to emit program_module_updated event: {e}")
    
    return jsonify(module.to_dict()), 200


@programs_bp.route('/programs/<int:program_id>/modules/<int:module_id>', methods=['DELETE'])
@jwt_required()
def delete_program_module(program_id, module_id):
    """Delete a program module."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check permissions
    if not _check_admin(user):
        return jsonify({'error': 'Unauthorized'}), 403
        
    program = Program.query.get_or_404(program_id)
    
    # Ensure user has access to this program's tenant
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    module = ProgramModule.query.filter_by(id=module_id, program_id=program_id).first_or_404()
    
    # Store tenant_id for event emission
    tenant_id = program.tenant_id
    
    db.session.delete(module)
    
    # Reorder remaining modules
    remaining_modules = ProgramModule.query.filter_by(program_id=program_id).order_by(ProgramModule.order).all()
    for i, mod in enumerate(remaining_modules):
        mod.order = i + 1
    
    db.session.commit()
    
    # Emit real-time event
    try:
        from app.realtime import emit_to_tenant
        emit_to_tenant(
            tenant_id,
            'program_module_deleted',
            {
                'program_id': program_id,
                'module_id': module_id
            }
        )
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(f"Failed to emit program_module_deleted event: {e}")
    
    return jsonify({'message': 'Module deleted'}), 200


@programs_bp.route('/programs/<int:program_id>/modules/reorder', methods=['POST'])
@jwt_required()
def reorder_program_modules(program_id):
    """Reorder modules for a program."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check permissions
    if not _check_admin(user):
        return jsonify({'error': 'Unauthorized'}), 403
        
    program = Program.query.get_or_404(program_id)
    
    # Ensure user has access to this program's tenant
    if user.tenant_id and program.tenant_id != user.tenant_id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    
    if not data or not isinstance(data, list):
        return jsonify({'error': 'Invalid module order data'}), 400
        
    # Get all modules to reorder
    module_dict = {m.id: m for m in ProgramModule.query.filter_by(program_id=program_id).all()}
    
    # Update the order field
    for i, module_id in enumerate(data):
        if int(module_id) in module_dict:
            module_dict[int(module_id)].order = i + 1
    
    db.session.commit()
    
    # Emit real-time event
    try:
        from app.realtime import emit_to_tenant
        emit_to_tenant(
            program.tenant_id,
            'program_modules_reordered',
            {
                'program_id': program_id,
                'modules': [m.to_dict() for m in 
                           ProgramModule.query.filter_by(program_id=program_id).order_by(ProgramModule.order).all()]
            }
        )
    except Exception as e:
        from flask import current_app
        current_app.logger.warning(f"Failed to emit program_modules_reordered event: {e}")
    
    return jsonify([m.to_dict() for m in 
                  ProgramModule.query.filter_by(program_id=program_id).order_by(ProgramModule.order).all()]), 200