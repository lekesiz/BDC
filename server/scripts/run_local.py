#\!/usr/bin/env python3
"""Local development server for BDC with authentication"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os

from app.utils.logging import logger

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdc_local.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app, 
     origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
     supports_credentials=False,  # Changed to False
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create tables and seed data
with app.app_context():
    db.create_all()
    
    # Create test users if they don't exist
    if not User.query.filter_by(email='admin@bdc.com').first():
        users = [
            {
                'email': 'admin@bdc.com',
                'password': 'Admin123\!',
                'role': 'super_admin',
                'first_name': 'Admin',
                'last_name': 'User'
            },
            {
                'email': 'student@bdc.com',
                'password': 'Student123\!',
                'role': 'student',
                'first_name': 'Student',  
                'last_name': 'User'
            },
            {
                'email': 'trainer@bdc.com',
                'password': 'Trainer123\!',
                'role': 'trainer',
                'first_name': 'Trainer',
                'last_name': 'User'
            }
        ]
        
        for user_data in users:
            user = User(
                email=user_data['email'],
                role=user_data['role'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
        
        db.session.commit()
        logger.info("✅ Test users created")

# Routes
@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'BDC Local Backend is running'
    })

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    return jsonify({
        'status': 'ok',
        'message': 'API is working',
        'method': request.method
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    logger.info(f"Login attempt - Data received: {data}")  # Debug log
    
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember', False)  # Get remember field, default False
    
    # Handle escaped exclamation mark from frontend
    if password and '\\!' in password:
        password = password.replace('\\!', '!')
        logger.info(f"Fixed escaped password")  # Debug log
    
    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400
    
    user = User.query.filter_by(email=email).first()
    logger.info(f"User found: {user.email if user else 'No user found'}")  # Debug log
    
    if user and user.check_password(password):
        logger.info(f"Password check passed for user: {user.email}")  # Debug log
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }), 200
    
    logger.info(f"Login failed - User exists: {bool(user)}, Password check: {user.check_password(password) if user else 'N/A'}")  # Debug log
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user:
        return jsonify({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    
    return jsonify({'message': 'User not found'}), 404

# Dashboard and analytics endpoints
@app.route('/api/analytics/dashboard', methods=['GET'])
@jwt_required()
def analytics_dashboard():
    return jsonify({
        'statistics': {
            'total_beneficiaries': 25,
            'active_evaluations': 12,
            'documents_generated': 45,
            'upcoming_appointments': 3,
            'completed_evaluations': 8,
            'assigned_beneficiaries': 25,
            'upcoming_sessions': 3,
            'total_programs': 5,
            'completion_rate': 78.5,
            'satisfaction_score': 4.2
        },
        'charts': {
            'monthly_enrollments': [
                {'month': 'Jan', 'count': 12},
                {'month': 'Feb', 'count': 15},
                {'month': 'Mar', 'count': 18},
                {'month': 'Apr', 'count': 22},
                {'month': 'May', 'count': 20},
                {'month': 'Jun', 'count': 25}
            ],
            'skills_distribution': [
                {'skill': 'Technical', 'value': 85},
                {'skill': 'Communication', 'value': 70},
                {'skill': 'Leadership', 'value': 60},
                {'skill': 'Problem Solving', 'value': 75}
            ],
            'program_completion': [
                {'program': 'Basic Training', 'completed': 45, 'in_progress': 15},
                {'program': 'Advanced Training', 'completed': 23, 'in_progress': 8}
            ]
        },
        'recent_activities': [
            {
                'id': 1,
                'type': 'evaluation_completed',
                'description': 'John Doe completed midterm evaluation',
                'timestamp': '2025-06-04T10:00:00Z'
            },
            {
                'id': 2,
                'type': 'beneficiary_enrolled',
                'description': 'New beneficiary enrolled in Basic Training',
                'timestamp': '2025-06-03T14:30:00Z'
            }
        ],
        'top_performers': [
            {
                'id': 1,
                'name': 'John Doe',
                'score': 92,
                'program': 'Basic Training'
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'score': 88,
                'program': 'Advanced Training'
            }
        ]
    })

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def notifications():
    return jsonify({
        'notifications': [],
        'unread_count': 0
    })

@app.route('/api/notifications/unread-count', methods=['GET'])
@jwt_required()
def notifications_unread_count():
    return jsonify({
        'unread_count': 0
    })

@app.route('/api/users/me', methods=['GET'])
@jwt_required()
def users_me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if user:
        return jsonify({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active
        })
    
    return jsonify({'message': 'User not found'}), 404

@app.route('/api/reports/recent', methods=['GET'])
@jwt_required()
def recent_reports():
    return jsonify({
        'reports': [
            {
                'id': 1,
                'title': 'Monthly Progress Report',
                'type': 'progress',
                'date': '2025-06-01',
                'status': 'completed'
            }
        ]
    })

@app.route('/api/calendar/events', methods=['GET'])
@jwt_required()
def calendar_events():
    return jsonify({
        'events': [
            {
                'id': 1,
                'title': 'Team Meeting',
                'description': 'Monthly team sync-up meeting',
                'start_time': '2025-06-05T10:00:00',
                'end_time': '2025-06-05T11:00:00',
                'start': '2025-06-05T10:00:00',
                'end': '2025-06-05T11:00:00',
                'type': 'meeting',
                'status': 'confirmed',
                'location': 'Conference Room A',
                'beneficiary': {
                    'id': 1,
                    'name': 'John Doe'
                },
                'trainer': {
                    'id': 2,
                    'name': 'Trainer User'
                },
                'beneficiary_id': 1,
                'trainer_id': 2
            }
        ]
    })

@app.route('/api/tests', methods=['GET'])
@jwt_required()
def tests():
    return jsonify({
        'items': [
            {
                'id': 1,
                'title': 'Basic Assessment',
                'status': 'active',
                'created_at': '2025-06-01'
            }
        ],
        'total': 1
    })

@app.route('/api/beneficiaries', methods=['GET'])
@jwt_required()
def beneficiaries():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    return jsonify({
        'items': [
            {
                'id': 1,
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '+1234567890',
                'status': 'active',
                'created_at': '2025-06-01T10:00:00Z',
                'program': 'Basic Training',
                'assigned_trainer': 'Trainer User'
            },
            {
                'id': 2,
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@example.com',
                'phone': '+0987654321',
                'status': 'active',
                'created_at': '2025-05-15T14:30:00Z',
                'program': 'Advanced Training',
                'assigned_trainer': 'Trainer User'
            }
        ],
        'total': 2,
        'page': page,
        'per_page': per_page,
        'total_pages': 1
    })

@app.route('/api/beneficiaries/<int:id>', methods=['GET'])
@jwt_required()
def get_beneficiary(id):
    # Return mock beneficiary details
    if id == 1:
        return jsonify({
            'id': 1,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'phone': '+1234567890',
            'status': 'active',
            'created_at': '2025-06-01T10:00:00Z',
            'updated_at': '2025-06-01T10:00:00Z',
            'program': {
                'id': 1,
                'name': 'Basic Training',
                'duration': '3 months'
            },
            'assigned_trainer': {
                'id': 3,
                'name': 'Trainer User',
                'email': 'trainer@bdc.com'
            },
            'address': '123 Main St, City, Country',
            'date_of_birth': '1990-01-15',
            'emergency_contact': {
                'name': 'Jane Doe',
                'phone': '+0987654321',
                'relationship': 'Spouse'
            },
            'notes': [
                {
                    'id': 1,
                    'content': 'Excellent progress in the program',
                    'created_at': '2025-06-01T10:00:00Z',
                    'created_by': 'Trainer User'
                }
            ],
            'documents': [
                {
                    'id': 1,
                    'name': 'Registration Form.pdf',
                    'type': 'application/pdf',
                    'uploaded_at': '2025-06-01T10:00:00Z'
                }
            ],
            'evaluations': [
                {
                    'id': 1,
                    'title': 'Initial Assessment',
                    'date': '2025-06-01',
                    'score': 85,
                    'status': 'completed'
                }
            ]
        })
    elif id == 2:
        return jsonify({
            'id': 2,
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'phone': '+0987654321',
            'status': 'active',
            'created_at': '2025-05-15T14:30:00Z',
            'updated_at': '2025-05-20T10:00:00Z',
            'program': {
                'id': 2,
                'name': 'Advanced Training',
                'duration': '6 months'
            },
            'assigned_trainer': {
                'id': 3,
                'name': 'Trainer User',
                'email': 'trainer@bdc.com'
            },
            'address': '456 Oak Ave, Town, Country',
            'date_of_birth': '1985-03-22',
            'emergency_contact': {
                'name': 'John Smith',
                'phone': '+1122334455',
                'relationship': 'Brother'
            },
            'notes': [
                {
                    'id': 2,
                    'content': 'Strong technical skills, needs improvement in communication',
                    'created_at': '2025-05-20T10:00:00Z',
                    'created_by': 'Trainer User'
                }
            ],
            'documents': [],
            'evaluations': []
        })
    else:
        return jsonify({'message': 'Beneficiary not found'}), 404

@app.route('/api/beneficiaries/<int:id>/evaluations', methods=['GET'])
@jwt_required()
def get_beneficiary_evaluations(id):
    return jsonify({
        'evaluations': [
            {
                'id': 1,
                'title': 'Initial Assessment',
                'type': 'test',
                'evaluation_date': '2025-06-01',
                'date': '2025-06-01',
                'score': 85,
                'max_score': 100,
                'percentage_score': 85,
                'status': 'completed',
                'trainer': 'Trainer User',
                'evaluator_name': 'Trainer User',
                'time_taken': '45 minutes'
            },
            {
                'id': 2,
                'title': 'Mid-term Evaluation',
                'type': 'practical',
                'evaluation_date': '2025-06-15',
                'date': '2025-06-15',
                'score': None,
                'max_score': 100,
                'percentage_score': None,
                'status': 'pending',
                'trainer': 'Trainer User',
                'evaluator_name': 'Trainer User',
                'time_taken': None
            }
        ]
    })

@app.route('/api/beneficiaries/<int:id>/sessions', methods=['GET'])
@jwt_required()
def get_beneficiary_sessions(id):
    return jsonify({
        'sessions': [
            {
                'id': 1,
                'title': 'Introduction Session',
                'date': '2025-06-01T10:00:00Z',
                'duration': 60,
                'status': 'completed',
                'trainer': 'Trainer User',
                'notes': 'Good first session'
            },
            {
                'id': 2,
                'title': 'Technical Training',
                'date': '2025-06-08T14:00:00Z',
                'duration': 90,
                'status': 'scheduled',
                'trainer': 'Trainer User',
                'notes': ''
            }
        ]
    })

@app.route('/api/beneficiaries/<int:id>/trainers', methods=['GET'])
@jwt_required()
def get_beneficiary_trainers(id):
    return jsonify({
        'trainers': [
            {
                'id': 3,
                'name': 'Trainer User',
                'email': 'trainer@bdc.com',
                'role': 'trainer',
                'assigned_date': '2025-06-01',
                'is_primary': True
            }
        ]
    })

@app.route('/api/beneficiaries/<int:id>/progress', methods=['GET'])
@jwt_required()
def get_beneficiary_progress(id):
    return jsonify({
        'progress': {
            'overall_completion': 45,
            'modules_completed': 3,
            'total_modules': 8,
            'average_score': 85,
            'attendance_rate': 95,
            'milestones': [
                {
                    'id': 1,
                    'title': 'Program Started',
                    'date': '2025-06-01',
                    'status': 'completed'
                },
                {
                    'id': 2,
                    'title': 'Basic Module Completed',
                    'date': '2025-06-10',
                    'status': 'completed'
                },
                {
                    'id': 3,
                    'title': 'Mid-term Evaluation',
                    'date': '2025-06-15',
                    'status': 'pending'
                }
            ]
        }
    })

@app.route('/api/beneficiaries/<int:id>/documents', methods=['GET'])
@jwt_required()
def get_beneficiary_documents(id):
    return jsonify({
        'documents': [
            {
                'id': 1,
                'name': 'Registration Form.pdf',
                'type': 'application/pdf',
                'file_type': 'pdf',
                'document_type': 'registration',
                'size': 1024000,
                'uploaded_at': '2025-06-01T10:00:00Z',
                'uploaded_by': 'Admin User',
                'uploaded_by_name': 'Admin User',
                'category': 'Registration'
            },
            {
                'id': 2,
                'name': 'ID Document.jpg',
                'type': 'image/jpeg',
                'file_type': 'jpg',
                'document_type': 'identity',
                'size': 512000,
                'uploaded_at': '2025-06-02T14:30:00Z',
                'uploaded_by': 'Trainer User',
                'uploaded_by_name': 'Trainer User',
                'category': 'Identity'
            }
        ]
    })

@app.route('/api/evaluations', methods=['GET'])
@jwt_required()
def evaluations():
    return jsonify({
        'items': [
            {
                'id': 1,
                'title': 'Midterm Evaluation',
                'type': 'test',
                'status': 'active',
                'created_at': '2025-06-01T10:00:00Z',
                'created_by': 'Admin User',
                'questions_count': 20
            }
        ],
        'total': 1
    })

@app.route('/api/evaluations/<int:id>', methods=['GET'])
@jwt_required()
def get_evaluation(id):
    return jsonify({
        'id': id,
        'title': 'Midterm Evaluation',
        'type': 'test',
        'status': 'active',
        'created_at': '2025-06-01T10:00:00Z',
        'created_by': 'Admin User',
        'description': 'This is a comprehensive evaluation test',
        'duration': 60,
        'questions_count': 20,
        'questions': [
            {
                'id': 1,
                'question': 'What is the capital of France?',
                'type': 'multiple_choice',
                'options': ['London', 'Berlin', 'Paris', 'Madrid'],
                'correct_answer': 'Paris',
                'points': 5
            },
            {
                'id': 2,
                'question': 'Explain the importance of training programs',
                'type': 'essay',
                'points': 10
            }
        ],
        'participants': [
            {
                'id': 1,
                'name': 'John Doe',
                'status': 'completed',
                'score': 85,
                'completed_at': '2025-06-02T14:30:00Z'
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'status': 'pending',
                'score': None,
                'completed_at': None
            }
        ]
    })

@app.route('/api/trainer-evaluations/<int:id>', methods=['GET'])
@jwt_required()
def get_trainer_evaluation(id):
    return jsonify({
        'id': id,
        'beneficiary_id': 1,
        'title': 'Trainer Evaluation - John Doe',
        'type': 'trainer_evaluation',
        'status': 'completed',
        'created_at': '2025-06-01T10:00:00Z',
        'completed_at': '2025-06-02T14:30:00Z',
        'trainer': 'Trainer User',
        'trainer_name': 'Trainer User',
        'program': 'Basic Training Program',
        'overall_rating': 4.5,
        'evaluation_date': '2025-06-02T14:30:00Z',
        'description': 'Comprehensive evaluation of John Doe\'s progress',
        'competencies': [
            {
                'name': 'Communication Skills',
                'score': 4,
                'comments': 'Good communication, needs improvement in clarity'
            },
            {
                'name': 'Technical Skills',
                'score': 5,
                'comments': 'Excellent technical knowledge'
            },
            {
                'name': 'Progress',
                'score': 4,
                'comments': 'Steady progress, meeting expectations'
            },
            {
                'name': 'Engagement',
                'score': 5,
                'comments': 'Very engaged and motivated'
            }
        ],
        'categories': [
            {
                'name': 'Communication Skills',
                'rating': 4,
                'comments': 'Good communication, needs improvement in clarity'
            },
            {
                'name': 'Technical Skills',
                'rating': 5,
                'comments': 'Excellent technical knowledge'
            },
            {
                'name': 'Progress',
                'rating': 4,
                'comments': 'Steady progress, meeting expectations'
            },
            {
                'name': 'Engagement',
                'rating': 5,
                'comments': 'Very engaged and motivated'
            }
        ],
        'strengths': [
            'Strong technical skills',
            'Highly motivated',
            'Good team player'
        ],
        'areas_for_improvement': [
            'Communication clarity',
            'Time management'
        ],
        'goals_for_next_period': [
            'Improve presentation skills',
            'Complete advanced modules'
        ],
        'goals': [
            'Improve presentation skills',
            'Complete advanced modules'
        ],
        'additional_comments': 'John is making excellent progress and shows great potential'
    })

@app.route('/api/programs', methods=['GET'])
@jwt_required()
def programs():
    # Return array directly as frontend expects
    return jsonify([
        {
            'id': 1,
            'name': 'Basic Training Program',
            'description': 'Introductory training for new beneficiaries',
            'status': 'active',
            'duration': '3 months',
            'created_at': '2025-01-01T10:00:00Z',
            'participants_count': 15,
            'category': 'technical',
            'level': 'beginner',
            'instructor': 'Trainer User',
            'rating': 4.5,
            'completed_count': 45,
            'enrolled_count': 15
        },
        {
            'id': 2,
            'name': 'Advanced Training Program',
            'description': 'Advanced skills development program',
            'status': 'active',
            'duration': '6 months',
            'created_at': '2025-02-01T10:00:00Z',
            'participants_count': 8,
            'category': 'technical',
            'level': 'advanced',
            'instructor': 'Expert Trainer',
            'rating': 4.8,
            'completed_count': 23,
            'enrolled_count': 8
        }
    ])

@app.route('/api/programs/<int:id>', methods=['GET'])
@jwt_required()
def get_program(id):
    programs = [
        {
            'id': 1,
            'name': 'Basic Training Program',
            'description': 'Introductory training for new beneficiaries',
            'status': 'active',
            'duration': '3 months',
            'created_at': '2025-01-01T10:00:00Z',
            'updated_at': '2025-06-01T10:00:00Z',
            'participants_count': 15,
            'category': 'technical',
            'level': 'beginner',
            'instructor': 'Trainer User',
            'rating': 4.5,
            'completed_count': 45,
            'enrolled_count': 15,
            'objectives': [
                'Understand basic concepts',
                'Develop fundamental skills',
                'Complete practical projects'
            ],
            'modules': [
                {
                    'id': 1,
                    'name': 'Introduction Module',
                    'duration': '2 weeks',
                    'status': 'completed'
                },
                {
                    'id': 2,
                    'name': 'Core Concepts',
                    'duration': '4 weeks',
                    'status': 'in_progress'
                },
                {
                    'id': 3,
                    'name': 'Practical Application',
                    'duration': '6 weeks',
                    'status': 'pending'
                }
            ],
            'requirements': 'No prior experience required',
            'outcomes': 'Participants will gain foundational knowledge and practical skills'
        },
        {
            'id': 2,
            'name': 'Advanced Training Program',
            'description': 'Advanced skills development program',
            'status': 'active',
            'duration': '6 months',
            'created_at': '2025-02-01T10:00:00Z',
            'updated_at': '2025-06-01T10:00:00Z',
            'participants_count': 8,
            'category': 'technical',
            'level': 'advanced',
            'instructor': 'Expert Trainer',
            'rating': 4.8,
            'completed_count': 23,
            'enrolled_count': 8,
            'objectives': [
                'Master advanced concepts',
                'Develop expert-level skills',
                'Lead complex projects'
            ],
            'modules': [
                {
                    'id': 1,
                    'name': 'Advanced Theory',
                    'duration': '4 weeks',
                    'status': 'completed'
                },
                {
                    'id': 2,
                    'name': 'Specialized Topics',
                    'duration': '8 weeks',
                    'status': 'in_progress'
                },
                {
                    'id': 3,
                    'name': 'Capstone Project',
                    'duration': '12 weeks',
                    'status': 'pending'
                }
            ],
            'requirements': 'Completion of Basic Training Program or equivalent experience',
            'outcomes': 'Participants will achieve expert-level proficiency and leadership skills'
        }
    ]
    
    # Find the program by id
    program = next((p for p in programs if p['id'] == id), None)
    
    if program:
        return jsonify(program)
    else:
        return jsonify({'message': 'Program not found'}), 404

@app.route('/api/programs/<int:id>/participants', methods=['GET'])
@jwt_required()
def get_program_participants(id):
    return jsonify({
        'participants': [
            {
                'id': 1,
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'status': 'active',
                'progress': 65,
                'enrolled_date': '2025-05-01',
                'last_active': '2025-06-04'
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'email': 'jane.smith@example.com',
                'status': 'active',
                'progress': 45,
                'enrolled_date': '2025-05-15',
                'last_active': '2025-06-03'
            }
        ],
        'total': 2
    })

@app.route('/api/messages/threads', methods=['GET'])
@jwt_required()
def message_threads():
    return jsonify({
        'threads': [
            {
                'id': 1,
                'title': 'Conversation with Trainer',
                'participants': [
                    {
                        'id': 1,
                        'name': 'Admin User',
                        'avatar': None,
                        'role': 'super_admin'
                    },
                    {
                        'id': 2,
                        'name': 'Trainer User',
                        'avatar': None,
                        'role': 'trainer'
                    }
                ],
                'participant': {
                    'id': 2,
                    'name': 'Trainer User',
                    'avatar': None
                },
                'last_message': {
                    'content': 'Hello, how are you?',
                    'timestamp': '2025-06-04T10:00:00Z',
                    'created_at': '2025-06-04T10:00:00Z',
                    'is_read': True,
                    'sender_id': 2
                },
                'unread_count': 0,
                'created_at': '2025-06-01T10:00:00Z',
                'updated_at': '2025-06-04T10:00:00Z'
            }
        ],
        'total': 1
    })

@app.route('/api/messages/threads/<int:thread_id>/messages', methods=['GET'])
@jwt_required()
def get_thread_messages(thread_id):
    return jsonify({
        'messages': [
            {
                'id': 1,
                'thread_id': thread_id,
                'sender_id': 2,
                'sender': {
                    'id': 2,
                    'name': 'Trainer User',
                    'avatar': None
                },
                'content': 'Hi Admin, I wanted to discuss John Doe\'s progress.',
                'timestamp': '2025-06-04T09:00:00Z',
                'created_at': '2025-06-04T09:00:00Z',
                'is_read': True
            },
            {
                'id': 2,
                'thread_id': thread_id,
                'sender_id': 1,
                'sender': {
                    'id': 1,
                    'name': 'Admin User',
                    'avatar': None
                },
                'content': 'Hello! Sure, I\'d be happy to discuss that. How is he doing?',
                'timestamp': '2025-06-04T09:30:00Z',
                'created_at': '2025-06-04T09:30:00Z',
                'is_read': True
            },
            {
                'id': 3,
                'thread_id': thread_id,
                'sender_id': 2,
                'sender': {
                    'id': 2,
                    'name': 'Trainer User',
                    'avatar': None
                },
                'content': 'He\'s making excellent progress. His technical skills are improving rapidly.',
                'timestamp': '2025-06-04T10:00:00Z',
                'created_at': '2025-06-04T10:00:00Z',
                'is_read': True
            }
        ]
    })

@app.route('/api/users', methods=['GET'])
@jwt_required()
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    return jsonify({
        'items': [
            {
                'id': 1,
                'email': 'admin@bdc.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'super_admin',
                'is_active': True,
                'created_at': '2025-05-01T10:00:00Z',
                'last_login': '2025-06-04T14:00:00Z',
                'phone': '+1234567890',
                'department': 'Administration'
            },
            {
                'id': 2,
                'email': 'trainer@bdc.com',
                'first_name': 'Trainer',
                'last_name': 'User',
                'role': 'trainer',
                'is_active': True,
                'created_at': '2025-05-01T10:00:00Z',
                'last_login': '2025-06-04T12:00:00Z',
                'phone': '+0987654321',
                'department': 'Training'
            },
            {
                'id': 3,
                'email': 'student@bdc.com',
                'first_name': 'Student',
                'last_name': 'User',
                'role': 'student',
                'is_active': True,
                'created_at': '2025-05-15T10:00:00Z',
                'last_login': '2025-06-03T10:00:00Z',
                'phone': '+1122334455',
                'department': 'Students'
            }
        ],
        'total': 3,
        'page': page,
        'per_page': per_page,
        'total_pages': 1
    })

@app.route('/api/users/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    users = {
        1: {
            'id': 1,
            'email': 'admin@bdc.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'super_admin',
            'is_active': True,
            'created_at': '2025-05-01T10:00:00Z',
            'last_login': '2025-06-04T14:00:00Z',
            'phone': '+1234567890',
            'department': 'Administration',
            'address': '123 Admin Street, City, Country',
            'bio': 'System administrator with full access'
        },
        2: {
            'id': 2,
            'email': 'trainer@bdc.com',
            'first_name': 'Trainer',
            'last_name': 'User',
            'role': 'trainer',
            'is_active': True,
            'created_at': '2025-05-01T10:00:00Z',
            'last_login': '2025-06-04T12:00:00Z',
            'phone': '+0987654321',
            'department': 'Training',
            'address': '456 Trainer Ave, City, Country',
            'bio': 'Experienced trainer specializing in technical skills'
        },
        3: {
            'id': 3,
            'email': 'student@bdc.com',
            'first_name': 'Student',
            'last_name': 'User',
            'role': 'student',
            'is_active': True,
            'created_at': '2025-05-15T10:00:00Z',
            'last_login': '2025-06-03T10:00:00Z',
            'phone': '+1122334455',
            'department': 'Students',
            'address': '789 Student Blvd, City, Country',
            'bio': 'Enrolled in Basic Training Program'
        }
    }
    
    user = users.get(id)
    if user:
        return jsonify(user)
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/api/users/search', methods=['GET'])
@jwt_required()
def search_users():
    search_term = request.args.get('q', '')
    return jsonify({
        'users': [
            {
                'id': 2,
                'name': 'Trainer User',
                'email': 'trainer@bdc.com',
                'role': 'trainer',
                'avatar': None
            },
            {
                'id': 3,
                'name': 'Student User',
                'email': 'student@bdc.com',
                'role': 'student',
                'avatar': None
            }
        ]
    })

@app.route('/api/documents', methods=['GET'])
@jwt_required()
def documents():
    return jsonify({
        'documents': [
            {
                'id': 1,
                'name': 'Training Manual.pdf',
                'type': 'application/pdf',
                'mime_type': 'application/pdf',
                'size': 1024000,
                'created_at': '2025-06-01T10:00:00Z',
                'updated_at': '2025-06-01T10:00:00Z',
                'created_by': 'Admin User',
                'owner_id': 1,
                'category': 'Training Materials',
                'is_starred': False,
                'shared_with': []
            },
            {
                'id': 2,
                'name': 'Progress Report.docx',
                'type': 'application/docx',
                'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'size': 512000,
                'created_at': '2025-05-15T14:30:00Z',
                'updated_at': '2025-05-15T14:30:00Z',
                'created_by': 'Trainer User',
                'owner_id': 2,
                'category': 'Reports',
                'is_starred': True,
                'shared_with': [1, 3]
            }
        ],
        'folders': [
            {
                'id': 1,
                'name': 'Training Materials',
                'created_at': '2025-05-01T10:00:00Z',
                'updated_at': '2025-05-01T10:00:00Z',
                'created_by': 'Admin User',
                'document_count': 5
            },
            {
                'id': 2,
                'name': 'Reports',
                'created_at': '2025-05-01T10:00:00Z',
                'updated_at': '2025-05-01T10:00:00Z',
                'created_by': 'Admin User',
                'document_count': 3
            }
        ],
        'total': 2
    })

@app.route('/api/analytics', methods=['GET'])
@jwt_required()
def analytics():
    return jsonify({
        'overview': {
            'total_users': 50,
            'active_programs': 5,
            'completion_rate': 78.5,
            'satisfaction_score': 4.2
        },
        'charts': {
            'monthly_enrollments': [
                {'month': 'Jan', 'count': 12},
                {'month': 'Feb', 'count': 15},
                {'month': 'Mar', 'count': 18},
                {'month': 'Apr', 'count': 22},
                {'month': 'May', 'count': 20},
                {'month': 'Jun', 'count': 25}
            ]
        }
    })

@app.route('/api/analytics/trainers', methods=['GET'])
@jwt_required()
def analytics_trainers():
    return jsonify({
        'trainers': [
            {
                'id': 2,
                'name': 'Trainer User',
                'email': 'trainer@bdc.com'
            }
        ]
    })

@app.route('/api/analytics/programs', methods=['GET'])
@jwt_required()
def analytics_programs():
    return jsonify({
        'programs': [
            {
                'id': 1,
                'name': 'Basic Training Program'
            },
            {
                'id': 2,
                'name': 'Advanced Training Program'
            }
        ]
    })

@app.route('/api/reports', methods=['GET'])
@jwt_required()
def reports():
    return jsonify({
        'items': [
            {
                'id': 1,
                'title': 'Monthly Performance Report',
                'type': 'performance',
                'generated_at': '2025-06-01T00:00:00Z',
                'status': 'completed',
                'format': 'pdf'
            },
            {
                'id': 2,
                'title': 'Quarterly Summary',
                'type': 'summary',
                'generated_at': '2025-04-01T00:00:00Z',
                'status': 'completed',
                'format': 'excel'
            }
        ],
        'total': 2
    })

if __name__ == '__main__':
    logger.info("\n" + "="*60)
    logger.info("🚀 BDC Local Development Server")
    logger.info("="*60)
    logger.info("\n📍 Access URLs:")
    logger.info("   Frontend: http://localhost:5173")
    logger.info("   Backend:  http://localhost:5001")
    logger.info("\n👤 Test Users:")
    logger.info("   admin@bdc.com    / Admin123\!")
    logger.info("   trainer@bdc.com  / Trainer123\!")
    logger.info("   student@bdc.com  / Student123\!")
    logger.info("\n✅ All services ready\!")
    logger.info("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)