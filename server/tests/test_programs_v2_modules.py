import pytest
import json
from datetime import datetime

from app import create_app, db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.program import Program, ProgramModule


@pytest.fixture()
def app():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
    
    with app.app_context():
        db.create_all()
        
        # Create test tenant
        tenant = Tenant(name="Test Tenant")
        db.session.add(tenant)
        
        # Create admin user for testing
        admin = User(
            email="admin@test.com",
            password="password",
            first_name="Admin",
            last_name="User",
            role="tenant_admin",
            tenant_id=1
        )
        db.session.add(admin)
        
        # Create regular user for testing
        user = User(
            email="user@test.com",
            password="password",
            first_name="Regular",
            last_name="User",
            role="trainer",
            tenant_id=1
        )
        db.session.add(user)
        
        # Create test program
        program = Program(
            name="Test Program",
            description="Test Description",
            tenant_id=1,
            created_by_id=1,
            is_active=True
        )
        db.session.add(program)
        
        db.session.commit()
    
    yield app
    
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_headers(client):
    response = client.post(
        '/api/auth/login',
        json={'email': 'admin@test.com', 'password': 'password'}
    )
    token = json.loads(response.data)['token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture()
def user_headers(client):
    response = client.post(
        '/api/auth/login',
        json={'email': 'user@test.com', 'password': 'password'}
    )
    token = json.loads(response.data)['token']
    return {'Authorization': f'Bearer {token}'}


def test_list_modules_empty(client, admin_headers):
    """Test listing modules when there are none."""
    response = client.get('/api/programs/1/modules', headers=admin_headers)
    assert response.status_code == 200
    assert json.loads(response.data) == []


def test_create_module(client, admin_headers, app):
    """Test creating a new module."""
    response = client.post(
        '/api/programs/1/modules',
        json={
            'name': 'Module 1',
            'description': 'Test Module',
            'content': 'Module content',
            'resources': ['resource1', 'resource2'],
            'duration': 120,
            'is_mandatory': True
        },
        headers=admin_headers
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['name'] == 'Module 1'
    assert data['description'] == 'Test Module'
    assert data['duration'] == 120
    assert data['is_mandatory'] == True
    
    # Verify in database
    with app.app_context():
        module = ProgramModule.query.get(1)
        assert module is not None
        assert module.name == 'Module 1'


def test_get_module(client, admin_headers, app):
    """Test getting a specific module."""
    # Create module first
    with app.app_context():
        module = ProgramModule(
            program_id=1,
            name='Get Test Module',
            description='Get Test Description',
            order=1
        )
        db.session.add(module)
        db.session.commit()
    
    response = client.get(f'/api/programs/1/modules/{module.id}', headers=admin_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Get Test Module'
    assert data['description'] == 'Get Test Description'


def test_update_module(client, admin_headers, app):
    """Test updating a module."""
    # Create module first
    with app.app_context():
        module = ProgramModule(
            program_id=1,
            name='Update Test Module',
            description='Initial Description',
            order=1
        )
        db.session.add(module)
        db.session.commit()
        module_id = module.id
    
    # Update module
    response = client.put(
        f'/api/programs/1/modules/{module_id}',
        json={
            'name': 'Updated Module',
            'description': 'Updated Description',
            'is_mandatory': False
        },
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Updated Module'
    assert data['description'] == 'Updated Description'
    assert data['is_mandatory'] == False
    
    # Verify in database
    with app.app_context():
        module = ProgramModule.query.get(module_id)
        assert module.name == 'Updated Module'
        assert module.description == 'Updated Description'
        assert module.is_mandatory == False


def test_delete_module(client, admin_headers, app):
    """Test deleting a module."""
    # Create module first
    with app.app_context():
        module = ProgramModule(
            program_id=1,
            name='Delete Test Module',
            order=1
        )
        db.session.add(module)
        db.session.commit()
        module_id = module.id
    
    # Delete module
    response = client.delete(f'/api/programs/1/modules/{module_id}', headers=admin_headers)
    assert response.status_code == 200
    
    # Verify it's gone
    with app.app_context():
        module = ProgramModule.query.get(module_id)
        assert module is None


def test_reorder_modules(client, admin_headers, app):
    """Test reordering modules."""
    # Create multiple modules
    with app.app_context():
        module1 = ProgramModule(program_id=1, name='Module 1', order=1)
        module2 = ProgramModule(program_id=1, name='Module 2', order=2)
        module3 = ProgramModule(program_id=1, name='Module 3', order=3)
        db.session.add_all([module1, module2, module3])
        db.session.commit()
        
        module_ids = [module3.id, module1.id, module2.id]  # New order: 3, 1, 2
    
    # Reorder modules
    response = client.post(
        '/api/programs/1/modules/reorder',
        json=module_ids,
        headers=admin_headers
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 3
    assert data[0]['name'] == 'Module 3'  # First in new order
    assert data[1]['name'] == 'Module 1'  # Second in new order
    assert data[2]['name'] == 'Module 2'  # Third in new order
    
    # Verify in database
    with app.app_context():
        modules = ProgramModule.query.filter_by(program_id=1).order_by(ProgramModule.order).all()
        assert modules[0].name == 'Module 3'
        assert modules[1].name == 'Module 1'
        assert modules[2].name == 'Module 2'