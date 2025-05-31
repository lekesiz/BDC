#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import datetime
import uuid
import time

app = Flask(__name__)
CORS(app)

# In-memory database
db = {
    "users": [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@bdc.com",
            "password": "Admin123!",
            "role": "super_admin",
            "first_name": "Admin",
            "last_name": "User"
        },
        {
            "id": 2,
            "username": "tenant",
            "email": "tenant@bdc.com",
            "password": "Tenant123!",
            "role": "tenant_admin",
            "first_name": "Tenant",
            "last_name": "Admin"
        },
        {
            "id": 3,
            "username": "trainer",
            "email": "trainer@bdc.com",
            "password": "Trainer123!",
            "role": "trainer",
            "first_name": "Trainer",
            "last_name": "User"
        },
        {
            "id": 4,
            "username": "student",
            "email": "student@bdc.com",
            "password": "Student123!",
            "role": "student",
            "first_name": "Student",
            "last_name": "User"
        }
    ],
    "beneficiaries": [
        {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+33612345678",
            "status": "active",
            "trainer_id": 3
        },
        {
            "id": 2,
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "+33687654321",
            "status": "active",
            "trainer_id": 3
        },
        {
            "id": 3,
            "first_name": "Alice",
            "last_name": "Johnson",
            "email": "alice.johnson@example.com",
            "phone": "+33698765432",
            "status": "inactive",
            "trainer_id": 3
        }
    ],
    "programs": [
        {
            "id": 1,
            "name": "Career Development",
            "description": "A comprehensive program for career development",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "status": "active"
        },
        {
            "id": 2,
            "name": "Leadership Skills",
            "description": "Program to develop leadership skills",
            "start_date": "2025-02-01",
            "end_date": "2025-08-31",
            "status": "active"
        }
    ],
    "evaluations": [
        {
            "id": 1,
            "title": "Initial Assessment",
            "description": "Assessment of initial skills",
            "beneficiary_id": 1,
            "trainer_id": 3,
            "date": "2025-01-15",
            "status": "completed",
            "score": 85
        },
        {
            "id": 2,
            "title": "Mid-term Evaluation",
            "description": "Evaluation of progress",
            "beneficiary_id": 1,
            "trainer_id": 3,
            "date": "2025-06-15",
            "status": "pending",
            "score": None
        }
    ],
    "documents": [
        {
            "id": 1,
            "title": "Resume",
            "beneficiary_id": 1,
            "file_type": "pdf",
            "created_at": "2025-01-10",
            "updated_at": "2025-01-10",
            "size": 256
        },
        {
            "id": 2,
            "title": "Cover Letter",
            "beneficiary_id": 1,
            "file_type": "docx",
            "created_at": "2025-01-10",
            "updated_at": "2025-01-15",
            "size": 128
        },
        {
            "id": 3,
            "title": "Personal Statement",
            "beneficiary_id": 2,
            "file_type": "pdf",
            "created_at": "2025-01-20",
            "updated_at": "2025-01-20",
            "size": 512
        },
        {
            "id": 4,
            "title": "GDPR Consent Form",
            "beneficiary_id": 1,
            "file_type": "pdf",
            "created_at": "2025-01-05",
            "updated_at": "2025-01-05",
            "size": 64
        },
        {
            "id": 5,
            "title": "ID Document",
            "beneficiary_id": 3,
            "file_type": "jpg",
            "created_at": "2025-01-18",
            "updated_at": "2025-01-18",
            "size": 1024
        },
        {
            "id": 6,
            "title": "Reference Letter",
            "beneficiary_id": 2,
            "file_type": "pdf",
            "created_at": "2025-01-12",
            "updated_at": "2025-01-12",
            "size": 384
        },
        {
            "id": 7,
            "title": "Diploma",
            "beneficiary_id": 3,
            "file_type": "pdf",
            "created_at": "2025-01-08",
            "updated_at": "2025-01-08",
            "size": 768
        },
        {
            "id": 8,
            "title": "Work Certificate",
            "beneficiary_id": 1,
            "file_type": "pdf",
            "created_at": "2025-01-22",
            "updated_at": "2025-01-22",
            "size": 192
        },
        {
            "id": 9,
            "title": "Assessment Results",
            "beneficiary_id": 2,
            "file_type": "xlsx",
            "created_at": "2025-01-25",
            "updated_at": "2025-01-25",
            "size": 320
        },
        {
            "id": 10,
            "title": "Skills Certificate",
            "beneficiary_id": 3,
            "file_type": "pdf",
            "created_at": "2025-01-30",
            "updated_at": "2025-01-30",
            "size": 256
        },
        {
            "id": 11,
            "title": "Motivation Letter",
            "beneficiary_id": 1,
            "file_type": "docx",
            "created_at": "2025-02-05",
            "updated_at": "2025-02-05",
            "size": 224
        },
        {
            "id": 12,
            "title": "Language Test Results",
            "beneficiary_id": 2,
            "file_type": "pdf",
            "created_at": "2025-02-10",
            "updated_at": "2025-02-10",
            "size": 288
        }
    ],
    "appointments": [
        {
            "id": 1,
            "title": "Progress Review Meeting",
            "beneficiary_id": 1,
            "trainer_id": 3,
            "date": "2025-05-25",
            "time": "10:00",
            "notes": "Monthly review of career progress",
            "status": "scheduled",
            "beneficiary_name": "John Doe"
        },
        {
            "id": 2,
            "title": "Career Assessment Session",
            "beneficiary_id": 2,
            "trainer_id": 3,
            "date": "2025-05-27",
            "time": "14:00",
            "notes": "Initial career assessment",
            "status": "scheduled",
            "beneficiary_name": "Jane Smith"
        },
        {
            "id": 3,
            "title": "Monthly Status Review",
            "beneficiary_id": 3,
            "trainer_id": 3,
            "date": "2025-06-01",
            "time": "11:00",
            "notes": "Review of monthly progress and goals",
            "status": "scheduled",
            "beneficiary_name": "Alice Johnson"
        },
        {
            "id": 4,
            "title": "Resume Workshop",
            "beneficiary_id": 1,
            "trainer_id": 3,
            "date": "2025-06-10",
            "time": "15:30",
            "notes": "Workshop to improve resume content and formatting",
            "status": "scheduled",
            "beneficiary_name": "John Doe"
        },
        {
            "id": 5,
            "title": "Interview Preparation",
            "beneficiary_id": 2,
            "trainer_id": 3,
            "date": "2025-06-15",
            "time": "09:00",
            "notes": "Mock interview and feedback session",
            "status": "scheduled",
            "beneficiary_name": "Jane Smith"
        }
    ],
    "reports": [],
    "tokens": {}
}

# Helper functions
def get_user_by_credentials(email, password):
    for user in db["users"]:
        if user["email"] == email and user["password"] == password:
            return user
    return None

def get_user_by_id(user_id):
    for user in db["users"]:
        if user["id"] == user_id:
            return user
    return None

def create_token(user_id):
    token = str(uuid.uuid4())
    expiry = datetime.datetime.now() + datetime.timedelta(hours=1)
    db["tokens"][token] = {
        "user_id": user_id,
        "expiry": expiry
    }
    return token

def validate_token(token):
    if token not in db["tokens"]:
        return None
    
    token_data = db["tokens"][token]
    if token_data["expiry"] < datetime.datetime.now():
        del db["tokens"][token]
        return None
    
    return get_user_by_id(token_data["user_id"])

def user_to_response(user):
    user_copy = user.copy()
    user_copy.pop("password", None)
    return user_copy

# Basic routes
@app.route('/')
def hello():
    return """
    <h1>BDC Test API</h1>
    <p>Welcome to the BDC Test API server. The following endpoints are available:</p>
    <ul>
        <li><a href="/health">GET /health</a> - Health check</li>
        <li>POST /api/auth/login - Login with email and password</li>
        <li>GET /api/auth/me - Get current user info (requires token)</li>
        <li>GET /api/users - Get all users</li>
        <li>GET /api/beneficiaries - Get all beneficiaries</li>
        <li>POST /api/beneficiaries - Create new beneficiary</li>
        <li>GET /api/programs - Get all programs</li>
        <li>GET /api/evaluations - Get all evaluations</li>
        <li>POST /api/evaluations - Create new evaluation</li>
        <li>GET /api/documents - Get all documents</li>
        <li>GET /api/appointments - Get all appointments</li>
        <li>POST /api/appointments - Schedule new appointment</li>
        <li>POST /api/reports - Generate report</li>
    </ul>
    """

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

# Auth routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = get_user_by_credentials(email, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = create_token(user["id"])
    
    return jsonify({
        "token": token,
        "user": user_to_response(user)
    })

@app.route('/api/auth/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Authorization header missing or invalid"}), 401
    
    token = auth_header.split(' ')[1]
    user = validate_token(token)
    
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    return jsonify(user_to_response(user))

# User routes
@app.route('/api/users', methods=['GET'])
def get_users():
    users = [user_to_response(user) for user in db["users"]]
    return jsonify({"users": users})

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user_to_response(user))

# Beneficiary routes
@app.route('/api/beneficiaries', methods=['GET'])
def get_beneficiaries():
    return jsonify({"beneficiaries": db["beneficiaries"]})

@app.route('/api/beneficiaries/<int:beneficiary_id>', methods=['GET'])
def get_beneficiary(beneficiary_id):
    beneficiary = next((b for b in db["beneficiaries"] if b["id"] == beneficiary_id), None)
    if not beneficiary:
        return jsonify({"error": "Beneficiary not found"}), 404
    
    return jsonify(beneficiary)

# Program routes
@app.route('/api/programs', methods=['GET'])
def get_programs():
    return jsonify({"programs": db["programs"]})

@app.route('/api/programs/<int:program_id>', methods=['GET'])
def get_program(program_id):
    program = next((p for p in db["programs"] if p["id"] == program_id), None)
    if not program:
        return jsonify({"error": "Program not found"}), 404
    
    return jsonify(program)

# Evaluation routes
@app.route('/api/evaluations', methods=['GET'])
def get_evaluations():
    return jsonify({"evaluations": db["evaluations"]})

@app.route('/api/evaluations', methods=['POST'])
def create_evaluation():
    data = request.json
    
    # Simple validation
    required_fields = ["title", "beneficiary_id", "date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create new evaluation
    new_id = max([e["id"] for e in db["evaluations"]], default=0) + 1
    
    evaluation = {
        "id": new_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "beneficiary_id": data["beneficiary_id"],
        "trainer_id": data.get("trainer_id", None),
        "date": data["date"],
        "status": data.get("status", "pending"),
        "score": data.get("score", None)
    }
    
    db["evaluations"].append(evaluation)
    
    return jsonify(evaluation), 201

@app.route('/api/evaluations/<int:evaluation_id>', methods=['GET'])
def get_evaluation(evaluation_id):
    evaluation = next((e for e in db["evaluations"] if e["id"] == evaluation_id), None)
    if not evaluation:
        return jsonify({"error": "Evaluation not found"}), 404
    
    return jsonify(evaluation)

# Document routes
@app.route('/api/documents', methods=['GET'])
def get_documents():
    return jsonify({"documents": db["documents"]})

@app.route('/api/documents/<int:document_id>', methods=['GET'])
def get_document(document_id):
    document = next((d for d in db["documents"] if d["id"] == document_id), None)
    if not document:
        return jsonify({"error": "Document not found"}), 404
    
    return jsonify(document)

# Appointment routes
@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    return jsonify({"appointments": db["appointments"]})

@app.route('/api/appointments', methods=['POST'])
def create_appointment():
    data = request.json
    
    # Simple validation
    required_fields = ["title", "beneficiary_id", "date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create new appointment
    new_id = max([a["id"] for a in db["appointments"]], default=0) + 1
    
    # Find beneficiary name for display
    beneficiary = next((b for b in db["beneficiaries"] if b["id"] == data["beneficiary_id"]), None)
    beneficiary_name = f"{beneficiary['first_name']} {beneficiary['last_name']}" if beneficiary else "Unknown"
    
    appointment = {
        "id": new_id,
        "title": data["title"],
        "beneficiary_id": data["beneficiary_id"],
        "trainer_id": data.get("trainer_id", None),
        "date": data["date"],
        "time": data.get("time", "00:00"),
        "notes": data.get("notes", ""),
        "status": data.get("status", "scheduled"),
        "beneficiary_name": beneficiary_name
    }
    
    db["appointments"].append(appointment)
    
    return jsonify(appointment), 201

@app.route('/api/appointments/<int:appointment_id>', methods=['GET'])
def get_appointment(appointment_id):
    appointment = next((a for a in db["appointments"] if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    
    return jsonify(appointment)

# Report routes
@app.route('/api/reports', methods=['POST'])
def generate_report():
    data = request.json
    
    # Simple validation
    required_fields = ["title", "type", "start_date", "end_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create new report
    new_id = max([r["id"] for r in db["reports"]], default=0) + 1
    
    report = {
        "id": new_id,
        "title": data["title"],
        "type": data["type"],
        "beneficiary_id": data.get("beneficiary_id"),
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "format": data.get("format", "pdf"),
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        "url": f"/files/reports/report_{new_id}.{data.get('format', 'pdf')}"
    }
    
    db["reports"].append(report)
    
    return jsonify(report), 201

# Post a beneficiary
@app.route('/api/beneficiaries', methods=['POST'])
def create_beneficiary():
    data = request.json
    
    # Simple validation
    required_fields = ["first_name", "last_name", "email"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create new beneficiary
    new_id = max([b["id"] for b in db["beneficiaries"]], default=0) + 1
    
    beneficiary = {
        "id": new_id,
        "first_name": data["first_name"],
        "last_name": data["last_name"],
        "email": data["email"],
        "phone": data.get("phone", ""),
        "status": data.get("status", "active"),
        "trainer_id": data.get("trainer_id", None)
    }
    
    db["beneficiaries"].append(beneficiary)
    
    return jsonify(beneficiary), 201

# Introduce artificial delay to simulate network latency
@app.before_request
def before_request():
    time.sleep(0.1)

if __name__ == '__main__':
    print("Starting complete test API server on port 8888...")
    app.run(host='0.0.0.0', port=8888, debug=True)