# Tenant Isolation System Migration Guide

## Overview

This guide helps you integrate the comprehensive tenant isolation system into your existing BDC project models and endpoints.

## Step 1: Update Your Models

### For New Models

```python
from app.extensions import db
from app.core.tenant_isolation import TenantMixin

class NewModel(TenantMixin, db.Model):
    __tablename__ = 'new_models'
    
    id = db.Column(db.Integer, primary_key=True)
    # Your fields here
    # tenant_id is automatically included from TenantMixin
```

### For Existing Models

Option 1: Add TenantMixin (Recommended)

```python
# Before
class Beneficiary(db.Model):
    __tablename__ = 'beneficiaries'
    id = db.Column(db.Integer, primary_key=True)
    # ... other fields ...

# After
from app.core.tenant_isolation import TenantMixin

class Beneficiary(TenantMixin, db.Model):
    __tablename__ = 'beneficiaries'
    id = db.Column(db.Integer, primary_key=True)
    # ... other fields ...
    # tenant_id is automatically included from TenantMixin
```

Option 2: Manual Integration (if you can't use inheritance)

```python
class Beneficiary(db.Model):
    __tablename__ = 'beneficiaries'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False, index=True)
    # ... other fields ...
    
    def validate_tenant_access(self, tenant_id=None):
        from app.core.tenant_isolation import TenantContextManager
        if tenant_id is None:
            tenant_id = TenantContextManager.get_current_tenant_id()
        return self.tenant_id == tenant_id
```

## Step 2: Database Migration

Create a migration to add tenant_id to existing tables:

```sql
-- For each table that needs tenant isolation
ALTER TABLE beneficiaries ADD COLUMN tenant_id INTEGER;
ALTER TABLE beneficiaries ADD CONSTRAINT fk_beneficiaries_tenant 
    FOREIGN KEY (tenant_id) REFERENCES tenants(id);
CREATE INDEX idx_beneficiaries_tenant ON beneficiaries(tenant_id);

-- Set default tenant for existing data (replace 1 with your default tenant ID)
UPDATE beneficiaries SET tenant_id = 1 WHERE tenant_id IS NULL;

-- Make tenant_id NOT NULL after setting values
ALTER TABLE beneficiaries ALTER COLUMN tenant_id SET NOT NULL;
```

## Step 3: Update Your API Endpoints

### Basic Protection

```python
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.core.tenant_isolation import require_tenant

beneficiaries_bp = Blueprint('beneficiaries', __name__)

@beneficiaries_bp.route('/beneficiaries', methods=['GET'])
@jwt_required()
@require_tenant  # Add this decorator
def list_beneficiaries():
    # Queries are automatically filtered by tenant
    beneficiaries = Beneficiary.query.all()
    return jsonify([b.to_dict() for b in beneficiaries])
```

### Creating New Records

```python
@beneficiaries_bp.route('/beneficiaries', methods=['POST'])
@jwt_required()
@require_tenant
def create_beneficiary():
    data = request.get_json()
    
    # Option 1: Using create_for_tenant
    beneficiary = Beneficiary.create_for_tenant(
        name=data['name'],
        email=data['email']
        # tenant_id is automatically set
    )
    
    # Option 2: Manual creation
    from app.core.tenant_isolation import validate_tenant_data
    validated_data = validate_tenant_data(data)
    beneficiary = Beneficiary(**validated_data)
    
    beneficiary.save()
    return jsonify(beneficiary.to_dict()), 201
```

## Step 4: Update Services

### Service Layer Updates

```python
from app.core.tenant_isolation import TenantContextManager, with_tenant

class BeneficiaryService:
    @staticmethod
    def get_all_beneficiaries():
        # Automatically filtered by current tenant
        return Beneficiary.query.all()
    
    @staticmethod
    def get_beneficiary_by_id(beneficiary_id):
        beneficiary = Beneficiary.query.get(beneficiary_id)
        if beneficiary:
            # Validate tenant access
            beneficiary.ensure_tenant_access()
        return beneficiary
    
    @staticmethod
    @with_tenant(1)  # Execute with specific tenant context
    def process_tenant_beneficiaries():
        # All queries in this method are scoped to tenant 1
        beneficiaries = Beneficiary.query.filter_by(processed=False).all()
        for b in beneficiaries:
            # Process beneficiary
            b.processed = True
            b.save()
```

## Step 5: Initialize Tenant Isolation

In your application factory (`app/core/app_factory.py`):

```python
from app.core.tenant_isolation import init_tenant_isolation

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # ... existing initialization ...
    
    # Initialize tenant isolation
    init_tenant_isolation(app)
    
    return app
```

## Step 6: Handle Special Cases

### Admin Endpoints

```python
@admin_bp.route('/admin/all-beneficiaries', methods=['GET'])
@jwt_required()
def list_all_beneficiaries():
    user = User.query.get(get_jwt_identity())
    if not user or user.role != 'super_admin':
        abort(403)
    
    # Query without tenant filtering
    beneficiaries = Beneficiary.query.without_tenant().all()
    return jsonify([b.to_dict() for b in beneficiaries])
```

### Background Tasks

```python
# In your Celery tasks
from app.core.tenant_isolation import with_tenant

@celery.task
@with_tenant(1)  # Specify tenant ID
def process_tenant_data():
    # All database operations are scoped to tenant 1
    pass
```

### Multi-Tenant Operations

```python
from app.core.tenant_isolation import TenantContextManager

def copy_beneficiary_to_another_tenant(beneficiary_id, target_tenant_id):
    # Get beneficiary from current tenant
    beneficiary = Beneficiary.query.get(beneficiary_id)
    
    # Create copy in target tenant
    with TenantContextManager.tenant_context(target_tenant_id):
        new_beneficiary = Beneficiary.create_for_tenant(
            name=beneficiary.name,
            email=beneficiary.email
        )
        new_beneficiary.save()
```

## Step 7: Testing

### Unit Tests

```python
from app.core.tenant_isolation import TenantContextManager

class TestBeneficiary(unittest.TestCase):
    def setUp(self):
        # Set up test tenant context
        self.tenant_id = 1
        TenantContextManager.set_tenant_id(self.tenant_id)
    
    def tearDown(self):
        # Clear tenant context
        TenantContextManager.clear_tenant_context()
    
    def test_beneficiary_creation(self):
        beneficiary = Beneficiary.create_for_tenant(name="Test")
        self.assertEqual(beneficiary.tenant_id, self.tenant_id)
```

## Step 8: Common Patterns

### Repository Pattern

```python
from app.core.tenant_isolation import TenantMixin

class BeneficiaryRepository:
    @staticmethod
    def find_by_id(beneficiary_id):
        # Automatically filtered by tenant
        return Beneficiary.query.get(beneficiary_id)
    
    @staticmethod
    def find_all():
        # Automatically filtered by tenant
        return Beneficiary.query.all()
    
    @staticmethod
    def find_by_email(email):
        # Automatically filtered by tenant
        return Beneficiary.query.filter_by(email=email).first()
```

### Complex Queries

```python
# Joins are automatically filtered
results = db.session.query(Beneficiary, Program)\
    .join(Program, Beneficiary.program_id == Program.id)\
    .all()
# Both Beneficiary and Program are filtered by current tenant

# Subqueries
subquery = Beneficiary.query.filter_by(active=True).subquery()
# Subquery is automatically filtered by tenant
```

## Migration Checklist

- [ ] Add TenantMixin to all models that need tenant isolation
- [ ] Run database migrations to add tenant_id columns
- [ ] Update existing data with appropriate tenant IDs
- [ ] Add @require_tenant decorator to all protected endpoints
- [ ] Update services to use tenant-aware queries
- [ ] Add tenant context to background tasks
- [ ] Update tests to handle tenant context
- [ ] Initialize tenant isolation in app factory
- [ ] Test multi-tenant scenarios
- [ ] Update documentation

## Troubleshooting

### No Tenant Context Error

If you get "No tenant context available" errors:
1. Ensure @require_tenant decorator is used
2. Check that JWT token contains tenant information
3. Verify user has tenant assignment

### Wrong Tenant Data

If you're seeing data from wrong tenants:
1. Check that models inherit from TenantMixin
2. Verify tenant_id column exists and has proper constraints
3. Ensure you're not using without_tenant() inappropriately

### Performance Issues

If queries are slow:
1. Ensure tenant_id columns are indexed
2. Consider composite indexes for (tenant_id, other_column)
3. Monitor query plans with EXPLAIN

## Best Practices

1. **Always use TenantMixin** for new models
2. **Use @require_tenant** on all tenant-specific endpoints
3. **Validate tenant access** before any destructive operations
4. **Test with multiple tenants** to ensure proper isolation
5. **Document tenant requirements** in your API documentation
6. **Use with_tenant** for background tasks
7. **Monitor for tenant leaks** in production