from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.program import Program
from app.models.user import User

from . import programs_bp


@programs_bp.route('/programs', methods=['GET'])
@jwt_required()
def list_programs():
    """List active programs for tenant."""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    query = Program.query.filter_by(is_active=True)
    if user.tenant_id:
        query = query.filter_by(tenant_id=user.tenant_id)

    programs = query.order_by(Program.created_at.desc()).all()
    return jsonify([p.to_dict() for p in programs]), 200 