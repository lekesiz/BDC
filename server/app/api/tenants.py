from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.tenant import Tenant
from app.models.user import User
from sqlalchemy.exc import SQLAlchemyError

from app.utils.logging import logger

tenants_bp = Blueprint('tenants', __name__)

@tenants_bp.route('/tenants', methods=['GET'])
@jwt_required()
def get_tenants():
    """Get all tenants (super admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'super_admin':
            return jsonify({'error': 'Unauthorized'}), 403
            
        tenants = Tenant.query.all()
        
        return jsonify([{
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'email': tenant.email,
            'phone': tenant.phone,
            'address': tenant.address,
            'plan': tenant.plan,
            'max_users': tenant.max_users,
            'max_beneficiaries': tenant.max_beneficiaries,
            'is_active': tenant.is_active,
            'user_count': len(tenant.users),
            'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
            'updated_at': tenant.updated_at.isoformat() if tenant.updated_at else None
        } for tenant in tenants]), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@tenants_bp.route('/tenants/<int:tenant_id>', methods=['GET'])
@jwt_required()
def get_tenant(tenant_id):
    """Get a specific tenant."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or (user.role != 'super_admin' and user.tenant_id != tenant_id):
            return jsonify({'error': 'Unauthorized'}), 403
            
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
            
        return jsonify({
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'email': tenant.email,
            'phone': tenant.phone,
            'address': tenant.address,
            'plan': tenant.plan,
            'max_users': tenant.max_users,
            'max_beneficiaries': tenant.max_beneficiaries,
            'is_active': tenant.is_active,
            'user_count': len(tenant.users),
            'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
            'updated_at': tenant.updated_at.isoformat() if tenant.updated_at else None
        }), 200
        
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

@tenants_bp.route('/tenants', methods=['POST'])
@jwt_required()
def create_tenant():
    """Create a new tenant (super admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'super_admin':
            return jsonify({'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({'error': 'Tenant name is required'}), 400
        
        # Generate slug from name
        import re
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', data['name'].lower())
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug.strip('-')
        
        # Check if slug already exists
        existing_tenant = Tenant.query.filter_by(slug=slug).first()
        if existing_tenant:
            # Add a number to make it unique
            counter = 1
            while Tenant.query.filter_by(slug=f"{slug}-{counter}").first():
                counter += 1
            slug = f"{slug}-{counter}"
            
        tenant = Tenant(
            name=data['name'],
            slug=slug,
            email=data.get('email', f"{slug}@example.com"),  # Use provided email or generate one
            phone=data.get('phone'),
            address=data.get('address'),
            plan=data.get('plan', 'basic'),
            max_users=data.get('max_users', 10),
            max_beneficiaries=data.get('max_beneficiaries', 50),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        return jsonify({
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'email': tenant.email,
            'phone': tenant.phone,
            'address': tenant.address,
            'plan': tenant.plan,
            'max_users': tenant.max_users,
            'max_beneficiaries': tenant.max_beneficiaries,
            'is_active': tenant.is_active,
            'user_count': 0,
            'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
            'updated_at': tenant.updated_at.isoformat() if tenant.updated_at else None
        }), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tenants_bp.route('/tenants/<int:tenant_id>', methods=['PUT'])
@jwt_required()
def update_tenant(tenant_id):
    """Update a tenant (super admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'super_admin':
            return jsonify({'error': 'Unauthorized'}), 403
            
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
            
        data = request.get_json()
        
        if 'name' in data:
            tenant.name = data['name']
        if 'is_active' in data:
            tenant.is_active = data['is_active']
        if 'email' in data:
            tenant.email = data['email']
        if 'phone' in data:
            tenant.phone = data['phone']
        if 'address' in data:
            tenant.address = data['address']
        if 'plan' in data:
            tenant.plan = data['plan']
        if 'max_users' in data:
            tenant.max_users = data['max_users']
        if 'max_beneficiaries' in data:
            tenant.max_beneficiaries = data['max_beneficiaries']
            
        db.session.commit()
        
        return jsonify({
            'id': tenant.id,
            'name': tenant.name,
            'slug': tenant.slug,
            'email': tenant.email,
            'phone': tenant.phone,
            'address': tenant.address,
            'plan': tenant.plan,
            'max_users': tenant.max_users,
            'max_beneficiaries': tenant.max_beneficiaries,
            'is_active': tenant.is_active,
            'user_count': len(tenant.users),
            'created_at': tenant.created_at.isoformat() if tenant.created_at else None,
            'updated_at': tenant.updated_at.isoformat() if tenant.updated_at else None
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tenants_bp.route('/tenants/<int:tenant_id>', methods=['DELETE'])
@jwt_required()
def delete_tenant(tenant_id):
    """Delete a tenant (super admin only)."""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or user.role != 'super_admin':
            return jsonify({'error': 'Unauthorized'}), 403
            
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            return jsonify({'error': 'Tenant not found'}), 404
            
        # Check if tenant has users
        if tenant.users:
            return jsonify({'error': 'Cannot delete tenant with users'}), 400
            
        db.session.delete(tenant)
        db.session.commit()
        
        return jsonify({'message': 'Tenant deleted successfully'}), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500