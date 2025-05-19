# BDC Security Hardening Guide

## Overview
This guide provides comprehensive security hardening procedures for the BDC application in production environments.

## 1. Application Security

### Flask Security Configuration
```python
# config.py
import os
from datetime import timedelta

class ProductionConfig:
    # Security headers
    SECURITY_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'",
        'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # JWT security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_ALGORITHM = 'HS256'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_SSL_STRICT = True
    
    # Password requirements
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_NUMBERS = True
    PASSWORD_REQUIRE_SPECIAL = True
```

### Input Validation
```python
# validators.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp
import bleach

class SecureForm(FlaskForm):
    class Meta:
        csrf = True
        csrf_time_limit = None

def sanitize_input(text):
    """Sanitize user input to prevent XSS"""
    allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    allowed_attributes = {}
    return bleach.clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)

def validate_email(email):
    """Validate email format and domain"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        raise ValueError("Invalid email format")
    
    # Check against blacklisted domains
    blacklisted_domains = ['tempmail.com', 'guerrillamail.com']
    domain = email.split('@')[1]
    if domain in blacklisted_domains:
        raise ValueError("Email domain not allowed")
    
    return email

def validate_file_upload(file):
    """Validate file uploads"""
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    if file.filename == '':
        raise ValueError("No file selected")
    
    if not '.' in file.filename:
        raise ValueError("Invalid filename")
    
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} not allowed")
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds {MAX_FILE_SIZE} bytes")
    
    # Check file content matches extension
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    
    expected_mimes = {
        'pdf': 'application/pdf',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png'
    }
    
    if ext in expected_mimes and mime != expected_mimes[ext]:
        raise ValueError("File content doesn't match extension")
    
    return True
```

### SQL Injection Prevention
```python
# models.py
from sqlalchemy import text
from sqlalchemy.orm import validates

class SecureModel:
    @validates('email')
    def validate_email(self, key, email):
        # Prevent SQL injection in email
        if any(char in email for char in ["'", '"', ';', '--', '/*', '*/']):
            raise ValueError("Invalid characters in email")
        return email.lower()
    
    @classmethod
    def safe_query(cls, **kwargs):
        """Safe query method that uses parameterized queries"""
        filters = []
        for key, value in kwargs.items():
            if hasattr(cls, key):
                filters.append(getattr(cls, key) == value)
        return cls.query.filter(*filters)
    
    @staticmethod
    def execute_safe_raw_query(query, params):
        """Execute raw SQL safely with parameters"""
        return db.session.execute(text(query), params)

# Usage example
# Instead of: User.query.filter(User.email == email)
# Use: User.safe_query(email=email)

# Instead of: db.session.execute(f"SELECT * FROM users WHERE id = {user_id}")
# Use: User.execute_safe_raw_query("SELECT * FROM users WHERE id = :id", {"id": user_id})
```

### Rate Limiting
```python
# rate_limiting.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"
)

# API endpoint rate limits
@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass

@app.route('/api/auth/register', methods=['POST'])
@limiter.limit("3 per hour")
def register():
    # Registration logic
    pass

@app.route('/api/auth/reset-password', methods=['POST'])
@limiter.limit("3 per hour")
def reset_password():
    # Password reset logic
    pass

# Custom rate limit for sensitive operations
@app.route('/api/users/delete/<int:user_id>', methods=['DELETE'])
@limiter.limit("1 per minute")
@require_admin
def delete_user(user_id):
    # User deletion logic
    pass
```

### Authentication & Authorization
```python
# auth.py
import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, verify_jwt_in_request
from functools import wraps

class SecureAuth:
    @staticmethod
    def hash_password(password):
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed)
    
    @staticmethod
    def generate_tokens(user):
        """Generate JWT tokens with additional claims"""
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role,
                'tenant_id': user.tenant_id,
                'email': user.email
            }
        )
        refresh_token = create_refresh_token(identity=user.id)
        return access_token, refresh_token
    
    @staticmethod
    def revoke_token(jti):
        """Add token to blacklist"""
        redis_client.setex(f"blacklist_{jti}", 3600 * 24 * 30, "true")

def require_role(allowed_roles):
    """Decorator for role-based access control"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get('role') not in allowed_roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage
@app.route('/api/admin/users')
@require_role(['super_admin', 'tenant_admin'])
def admin_users():
    # Admin only endpoint
    pass
```

## 2. Infrastructure Security

### Linux Server Hardening
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Configure automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades

# Remove unnecessary packages
sudo apt autoremove

# Disable root login
sudo passwd -l root

# Configure SSH
sudo nano /etc/ssh/sshd_config
```

SSH configuration:
```
Port 2222  # Non-standard port
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
MaxSessions 2
ClientAliveInterval 300
ClientAliveCountMax 2
AllowUsers bdc-admin
Protocol 2
X11Forwarding no
```

### Firewall Configuration
```bash
# Install and configure UFW
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow specific ports
sudo ufw allow 2222/tcp  # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Enable firewall
sudo ufw enable

# Advanced iptables rules
# Rate limit SSH connections
sudo iptables -A INPUT -p tcp --dport 2222 -m state --state NEW -m recent --set
sudo iptables -A INPUT -p tcp --dport 2222 -m state --state NEW -m recent --update --seconds 60 --hitcount 3 -j DROP

# Block invalid packets
sudo iptables -A INPUT -m conntrack --ctstate INVALID -j DROP

# Prevent SYN flood
sudo iptables -A INPUT -p tcp ! --syn -m state --state NEW -j DROP
sudo iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
```

### Fail2ban Configuration
```bash
# Install fail2ban
sudo apt install fail2ban

# Configure fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

Fail2ban configuration:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
destemail = admin@yourdomain.com
action = %(action_mwl)s

[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log

[bdc-app]
enabled = true
filter = bdc-app
port = http,https
logpath = /var/log/bdc/app.log
maxretry = 5
bantime = 1800
```

Custom fail2ban filter:
```ini
# /etc/fail2ban/filter.d/bdc-app.conf
[Definition]
failregex = ^.*Failed login attempt from <HOST>.*$
            ^.*Unauthorized access attempt from <HOST>.*$
            ^.*Invalid API key from <HOST>.*$
ignoreregex =
```

## 3. Database Security

### PostgreSQL Hardening
```sql
-- Revoke default permissions
REVOKE ALL ON DATABASE bdc_production FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Create separate user for application
CREATE USER bdc_app WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE bdc_production TO bdc_app;
GRANT USAGE ON SCHEMA public TO bdc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO bdc_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO bdc_app;

-- Enable SSL
ALTER SYSTEM SET ssl = on;

-- Configure authentication
-- In pg_hba.conf:
# TYPE  DATABASE        USER            ADDRESS                 METHOD
host    bdc_production  bdc_app         127.0.0.1/32           scram-sha-256
host    bdc_production  bdc_app         ::1/128                scram-sha-256

-- Enable logging
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;

-- Set password encryption
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
```

### Database Access Monitoring
```python
# db_audit.py
from datetime import datetime
import logging

class DatabaseAudit:
    @staticmethod
    def log_query(query, user_id, ip_address):
        """Log database queries for audit"""
        audit_log = AuditLog(
            user_id=user_id,
            action='database_query',
            details=str(query),
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.session.add(audit_log)
        db.session.commit()
    
    @staticmethod
    def log_sensitive_access(table_name, user_id, action):
        """Log access to sensitive tables"""
        sensitive_tables = ['users', 'payments', 'audit_logs']
        
        if table_name in sensitive_tables:
            logging.warning(f"Sensitive access: User {user_id} performed {action} on {table_name}")
            # Send alert to security team
            send_security_alert(f"Sensitive database access: {table_name}")
```

## 4. API Security

### API Authentication
```python
# api_security.py
import hmac
import hashlib
from datetime import datetime, timedelta

class APIKeySecurity:
    @staticmethod
    def generate_api_key(client_id):
        """Generate secure API key"""
        secret = os.environ.get('API_SECRET')
        timestamp = datetime.utcnow().isoformat()
        message = f"{client_id}:{timestamp}"
        
        signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"{client_id}:{timestamp}:{signature}"
    
    @staticmethod
    def verify_api_key(api_key):
        """Verify API key validity"""
        try:
            client_id, timestamp, signature = api_key.split(':')
            
            # Check timestamp (key valid for 24 hours)
            key_time = datetime.fromisoformat(timestamp)
            if datetime.utcnow() - key_time > timedelta(hours=24):
                return False
            
            # Verify signature
            expected_signature = APIKeySecurity.generate_api_key(client_id).split(':')[2]
            return hmac.compare_digest(signature, expected_signature)
        except:
            return False

# API endpoint security
@app.before_request
def verify_api_request():
    if request.path.startswith('/api/'):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not APIKeySecurity.verify_api_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
```

### CORS Configuration
```python
# cors_config.py
from flask_cors import CORS

# Restrictive CORS configuration
cors = CORS(app, resources={
    r"/api/*": {
        "origins": ["https://app.yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
        "expose_headers": ["Content-Range", "X-Content-Range"],
        "supports_credentials": True,
        "max_age": 3600
    }
})

# Custom CORS headers for specific endpoints
@app.after_request
def after_request(response):
    # Only allow specific origins for sensitive endpoints
    if request.path.startswith('/api/admin/'):
        response.headers['Access-Control-Allow-Origin'] = 'https://admin.yourdomain.com'
    
    return response
```

## 5. File Upload Security

### Secure File Upload Handler
```python
# file_security.py
import os
import hashlib
import magic
from PIL import Image
from werkzeug.utils import secure_filename

class SecureFileUpload:
    UPLOAD_FOLDER = '/var/www/bdc/uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_file(file):
        """Comprehensive file validation"""
        if not file or file.filename == '':
            raise ValueError("No file provided")
        
        # Secure filename
        filename = secure_filename(file.filename)
        
        # Check extension
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
        if not ext or ext not in SecureFileUpload.ALLOWED_EXTENSIONS:
            raise ValueError(f"File type not allowed: {ext}")
        
        # Check file size
        file.seek(0, 2)
        size = file.tell()
        file.seek(0)
        
        if size > SecureFileUpload.MAX_FILE_SIZE:
            raise ValueError(f"File too large: {size} bytes")
        
        # Verify file type with python-magic
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
        
        allowed_mimes = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        
        if ext in allowed_mimes and mime != allowed_mimes[ext]:
            raise ValueError(f"File content doesn't match extension")
        
        # Additional checks for images
        if ext in ['jpg', 'jpeg', 'png']:
            try:
                img = Image.open(file)
                img.verify()
                file.seek(0)
                
                # Check image dimensions
                if img.width > 4000 or img.height > 4000:
                    raise ValueError("Image dimensions too large")
            except:
                raise ValueError("Invalid image file")
        
        return True
    
    @staticmethod
    def save_file(file, user_id):
        """Save file securely with unique name"""
        if not SecureFileUpload.validate_file(file):
            return None
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        random_string = hashlib.md5(os.urandom(32)).hexdigest()[:8]
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{user_id}_{timestamp}_{random_string}.{ext}"
        
        # Create user directory
        user_dir = os.path.join(SecureFileUpload.UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        # Save file
        filepath = os.path.join(user_dir, filename)
        file.save(filepath)
        
        # Set file permissions
        os.chmod(filepath, 0o644)
        
        # Scan for viruses (optional)
        # if not SecureFileUpload.scan_virus(filepath):
        #     os.remove(filepath)
        #     raise ValueError("Virus detected in file")
        
        return filepath
```

## 6. Session Security

### Secure Session Management
```python
# session_security.py
import uuid
from datetime import datetime, timedelta

class SecureSession:
    @staticmethod
    def create_session(user_id):
        """Create secure session"""
        session_id = str(uuid.uuid4())
        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'last_activity': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
        
        # Store in Redis with expiration
        redis_client.setex(
            f"session:{session_id}",
            timedelta(hours=24),
            json.dumps(session_data)
        )
        
        return session_id
    
    @staticmethod
    def validate_session(session_id):
        """Validate and update session"""
        session_data = redis_client.get(f"session:{session_id}")
        
        if not session_data:
            return None
        
        data = json.loads(session_data)
        
        # Check session timeout (30 minutes of inactivity)
        last_activity = datetime.fromisoformat(data['last_activity'])
        if datetime.utcnow() - last_activity > timedelta(minutes=30):
            SecureSession.destroy_session(session_id)
            return None
        
        # Check IP address change
        if data['ip_address'] != request.remote_addr:
            logging.warning(f"IP address mismatch for session {session_id}")
            SecureSession.destroy_session(session_id)
            return None
        
        # Update last activity
        data['last_activity'] = datetime.utcnow().isoformat()
        redis_client.setex(
            f"session:{session_id}",
            timedelta(hours=24),
            json.dumps(data)
        )
        
        return data
    
    @staticmethod
    def destroy_session(session_id):
        """Destroy session"""
        redis_client.delete(f"session:{session_id}")
```

## 7. Logging & Auditing

### Comprehensive Audit Logging
```python
# audit_logging.py
import json
from datetime import datetime

class AuditLogger:
    @staticmethod
    def log_authentication(user_id, action, success, ip_address):
        """Log authentication events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'action': action,  # login, logout, password_change
            'success': success,
            'ip_address': ip_address,
            'user_agent': request.headers.get('User-Agent'),
            'session_id': session.get('session_id')
        }
        
        # Log to file
        with open('/var/log/bdc/auth.log', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Log to database
        audit = AuthAuditLog(**log_entry)
        db.session.add(audit)
        db.session.commit()
        
        # Alert on suspicious activity
        if action == 'login' and not success:
            AuditLogger.check_failed_attempts(user_id, ip_address)
    
    @staticmethod
    def log_data_access(user_id, resource, action, details=None):
        """Log data access events"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'resource': resource,
            'action': action,  # create, read, update, delete
            'details': details,
            'ip_address': request.remote_addr
        }
        
        # Sensitive resources trigger alerts
        sensitive_resources = ['users', 'payments', 'audit_logs']
        if resource in sensitive_resources:
            send_security_alert(f"Sensitive data access: {resource}")
        
        # Log to database
        audit = DataAuditLog(**log_entry)
        db.session.add(audit)
        db.session.commit()
```

## 8. Security Headers

### Nginx Security Headers
```nginx
# /etc/nginx/sites-available/bdc
server {
    # ... other configuration ...
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.yourdomain.com;" always;
    
    # Hide server version
    server_tokens off;
    
    # Prevent clickjacking
    add_header X-Frame-Options "SAMEORIGIN" always;
}
```

## 9. Dependency Security

### Package Security Scanning
```bash
# Python dependencies
pip install safety
safety check

# JavaScript dependencies
npm audit
npm audit fix

# Automated dependency updates
pip install pip-tools
pip-compile --upgrade requirements.in

# GitHub Dependabot configuration
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/server"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    
  - package-ecosystem: "npm"
    directory: "/client"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

## 10. Security Testing

### Automated Security Testing
```python
# security_tests.py
import pytest
from sqlalchemy import text

class TestSecurity:
    def test_sql_injection(self, client):
        """Test SQL injection prevention"""
        malicious_inputs = [
            "' OR '1'='1",
            "1; DROP TABLE users;",
            "' UNION SELECT * FROM users--"
        ]
        
        for payload in malicious_inputs:
            response = client.post('/api/auth/login', json={
                'email': payload,
                'password': 'test'
            })
            assert response.status_code in [400, 401]
            
            # Verify database is intact
            user_count = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
            assert user_count > 0
    
    def test_xss_prevention(self, client):
        """Test XSS prevention"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')"
        ]
        
        for payload in xss_payloads:
            response = client.post('/api/comments', json={
                'content': payload
            })
            
            # Verify payload is escaped in response
            assert '<script>' not in response.get_data(as_text=True)
    
    def test_authentication_required(self, client):
        """Test authentication requirements"""
        protected_endpoints = [
            '/api/users',
            '/api/beneficiaries',
            '/api/admin/settings'
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
    
    def test_rate_limiting(self, client):
        """Test rate limiting"""
        # Make multiple requests
        for i in range(10):
            response = client.post('/api/auth/login', json={
                'email': 'test@test.com',
                'password': 'wrong'
            })
        
        # Should be rate limited
        assert response.status_code == 429
```

### Penetration Testing Checklist
1. **Authentication Testing**
   - [ ] Password brute force protection
   - [ ] Session hijacking prevention
   - [ ] JWT token security
   - [ ] Password reset security

2. **Authorization Testing**
   - [ ] Privilege escalation
   - [ ] Access control bypass
   - [ ] Direct object references
   - [ ] Path traversal

3. **Input Validation**
   - [ ] SQL injection
   - [ ] XSS attacks
   - [ ] Command injection
   - [ ] XXE injection

4. **API Security**
   - [ ] Rate limiting
   - [ ] API key validation
   - [ ] CORS configuration
   - [ ] Method validation

5. **Infrastructure Security**
   - [ ] SSL/TLS configuration
   - [ ] Security headers
   - [ ] Server hardening
   - [ ] Firewall rules

## Security Monitoring Dashboard

### Key Security Metrics
```python
# security_metrics.py
class SecurityMetrics:
    @staticmethod
    def get_dashboard_data():
        return {
            'failed_login_attempts': get_failed_login_count(),
            'suspicious_activities': get_suspicious_activity_count(),
            'blocked_ips': get_blocked_ip_count(),
            'security_alerts': get_recent_alerts(),
            'vulnerability_scan_results': get_last_scan_results(),
            'ssl_certificate_expiry': get_ssl_expiry_days(),
            'password_policy_violations': get_policy_violations(),
            'api_abuse_attempts': get_api_abuse_count()
        }
```

---

This comprehensive security hardening guide ensures the BDC application is protected against common vulnerabilities and follows security best practices.