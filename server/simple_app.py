#!/usr/bin/env python3
"""Simple Flask app for testing."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Create Flask app
app = Flask(__name__)

# Basic configuration
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bdc_simple.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app, origins=['http://localhost:3000', 'http://localhost:5173', 'http://127.0.0.1:3000', 'http://127.0.0.1:5173'])

# Simple User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Simple Beneficiary model
class Beneficiary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), default='active')

# Routes
@app.route('/')
def index():
    return jsonify({'message': 'BDC Backend Server is running!', 'status': 'healthy'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

@app.route('/api/users')
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': u.id,
        'email': u.email,
        'username': u.username,
        'role': u.role,
        'is_active': u.is_active
    } for u in users])

@app.route('/api/beneficiaries')
def get_beneficiaries():
    beneficiaries = Beneficiary.query.all()
    return jsonify([{
        'id': b.id,
        'name': b.name,
        'email': b.email,
        'phone': b.phone,
        'status': b.status
    } for b in beneficiaries])

@app.route('/api/test')
def test():
    return jsonify({'message': 'API test successful', 'cors': 'enabled'})

# Create tables and sample data
with app.app_context():
    db.create_all()
    
    # Create sample users if they don't exist
    if User.query.count() == 0:
        users_data = [
            {'email': 'admin@bdc.com', 'username': 'admin', 'password': 'admin123', 'role': 'admin'},
            {'email': 'student@bdc.com', 'username': 'student', 'password': 'student123', 'role': 'student'},
            {'email': 'trainer@bdc.com', 'username': 'trainer', 'password': 'trainer123', 'role': 'trainer'},
        ]
        
        for user_data in users_data:
            user = User(
                email=user_data['email'],
                username=user_data['username'],
                role=user_data['role']
            )
            user.set_password(user_data['password'])
            db.session.add(user)
        
        db.session.commit()
        print(f"Created {len(users_data)} sample users")
    
    # Create sample beneficiaries if they don't exist
    if Beneficiary.query.count() == 0:
        beneficiaries_data = [
            {'name': 'John Doe', 'email': 'john@example.com', 'phone': '555-0001'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'phone': '555-0002'},
            {'name': 'Bob Johnson', 'email': 'bob@example.com', 'phone': '555-0003'},
        ]
        
        for ben_data in beneficiaries_data:
            beneficiary = Beneficiary(
                name=ben_data['name'],
                email=ben_data['email'],
                phone=ben_data['phone']
            )
            db.session.add(beneficiary)
        
        db.session.commit()
        print(f"Created {len(beneficiaries_data)} sample beneficiaries")

if __name__ == '__main__':
    print("Starting simple BDC server...")
    print("Backend: http://localhost:5001")
    print("Health check: http://localhost:5001/health")
    print("API test: http://localhost:5001/api/test")
    print("Users: http://localhost:5001/api/users")
    print("Beneficiaries: http://localhost:5001/api/beneficiaries")
    app.run(host='0.0.0.0', port=5001, debug=True)