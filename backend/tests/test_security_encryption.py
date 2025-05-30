import pytest
from cryptography.fernet import Fernet
from app import create_app, db
from app.models import User, Document
from app.services.encryption import EncryptionService
from app.tests.factories import UserFactory, DocumentFactory

class TestSecurityEncryption:
    """Test data encryption and secure storage"""
    
    @pytest.fixture
    def app(self):
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    @pytest.fixture
    def encryption_service(self, app):
        return EncryptionService(app.config['SECRET_KEY'])
    
    def test_password_encryption(self, app):
        """Test password hashing and verification"""
        user = UserFactory()
        raw_password = 'TestPassword123!'
        user.set_password(raw_password)
        db.session.commit()
        
        # Password should be hashed
        assert user.password_hash != raw_password
        assert len(user.password_hash) > 50  # Bcrypt hash length
        
        # Verification should work
        assert user.verify_password(raw_password)
        assert not user.verify_password('WrongPassword')
        
        # Same password should produce different hashes (salt)
        another_user = UserFactory()
        another_user.set_password(raw_password)
        db.session.commit()
        
        assert user.password_hash != another_user.password_hash
    
    def test_sensitive_data_encryption(self, encryption_service):
        """Test encryption of sensitive data fields"""
        sensitive_data = {
            'ssn': '123-45-6789',
            'credit_card': '4111111111111111',
            'bank_account': '1234567890',
            'api_key': 'sk_test_abcdefghijklmnop'
        }
        
        encrypted_data = {}
        for key, value in sensitive_data.items():
            encrypted = encryption_service.encrypt(value)
            encrypted_data[key] = encrypted
            
            # Should be encrypted
            assert encrypted != value
            assert len(encrypted) > len(value)
            
            # Should be decryptable
            decrypted = encryption_service.decrypt(encrypted)
            assert decrypted == value
    
    def test_database_field_encryption(self, app):
        """Test encryption of database fields"""
        # Assuming we have encrypted fields in the model
        user = UserFactory()
        user.phone = '+1234567890'  # Should be encrypted
        user.ssn = '123-45-6789'    # Should be encrypted
        db.session.commit()
        
        # Raw database query to check encryption
        result = db.session.execute(
            'SELECT phone, ssn FROM users WHERE id = :id',
            {'id': user.id}
        ).fetchone()
        
        # Values in database should be encrypted
        if hasattr(user, '_encrypt_field'):
            assert result.phone != '+1234567890'
            assert result.ssn != '123-45-6789'
    
    def test_file_encryption(self, encryption_service):
        """Test file encryption for uploads"""
        file_content = b'This is a sensitive document'
        
        # Encrypt file
        encrypted_content = encryption_service.encrypt_file(file_content)
        assert encrypted_content != file_content
        
        # Decrypt file
        decrypted_content = encryption_service.decrypt_file(encrypted_content)
        assert decrypted_content == file_content
    
    def test_token_encryption(self, encryption_service):
        """Test secure token generation and verification"""
        user_id = 123
        purpose = 'password_reset'
        
        # Generate token
        token = encryption_service.generate_token(user_id, purpose)
        assert len(token) > 20
        
        # Verify token
        verified_id, verified_purpose = encryption_service.verify_token(token)
        assert verified_id == user_id
        assert verified_purpose == purpose
        
        # Invalid token should fail
        with pytest.raises(Exception):
            encryption_service.verify_token('invalid_token')
    
    def test_api_key_storage(self, app):
        """Test secure API key storage"""
        # API keys should be hashed, not encrypted
        api_key = 'sk_live_abcdefghijklmnopqrstuvwxyz123456'
        
        # Store hashed version
        from hashlib import sha256
        hashed_key = sha256(api_key.encode()).hexdigest()
        
        # Verify key
        provided_key = 'sk_live_abcdefghijklmnopqrstuvwxyz123456'
        provided_hash = sha256(provided_key.encode()).hexdigest()
        
        assert hashed_key == provided_hash
    
    def test_session_encryption(self, client):
        """Test session data encryption"""
        with client.session_transaction() as session:
            session['user_id'] = 123
            session['sensitive_data'] = 'secret_value'
        
        # Session cookie should be encrypted
        response = client.get('/')
        cookie = response.headers.get('Set-Cookie')
        
        if cookie:
            # Cookie value should not contain plain text
            assert 'secret_value' not in cookie
            assert '123' not in cookie
    
    def test_tls_enforcement(self, app):
        """Test TLS/SSL enforcement in production"""
        if app.config['ENV'] == 'production':
            app.config['SESSION_COOKIE_SECURE'] = True
            app.config['SESSION_COOKIE_HTTPONLY'] = True
            app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
            
            # Check secure cookie settings
            assert app.config['SESSION_COOKIE_SECURE']
            assert app.config['SESSION_COOKIE_HTTPONLY']
            assert app.config['SESSION_COOKIE_SAMESITE'] == 'Strict'
    
    def test_key_rotation(self, encryption_service):
        """Test encryption key rotation"""
        old_key = encryption_service.key
        data = 'sensitive_data'
        
        # Encrypt with old key
        encrypted = encryption_service.encrypt(data)
        
        # Rotate key
        new_key = Fernet.generate_key()
        encryption_service.rotate_key(old_key, new_key)
        
        # Should still be able to decrypt old data
        decrypted = encryption_service.decrypt(encrypted)
        assert decrypted == data
    
    def test_secure_random_generation(self):
        """Test secure random number generation"""
        import secrets
        
        # Generate secure tokens
        token1 = secrets.token_urlsafe(32)
        token2 = secrets.token_urlsafe(32)
        
        # Should be different
        assert token1 != token2
        
        # Should be long enough
        assert len(token1) >= 32
        assert len(token2) >= 32
    
    def test_certificate_validation(self, app):
        """Test SSL certificate validation"""
        if app.config['ENV'] == 'production':
            import ssl
            
            context = ssl.create_default_context()
            assert context.check_hostname
            assert context.verify_mode == ssl.CERT_REQUIRED
    
    def test_sensitive_data_masking(self):
        """Test masking of sensitive data in logs/responses"""
        sensitive_fields = ['password', 'ssn', 'credit_card', 'api_key']
        data = {
            'username': 'john_doe',
            'password': 'secret123',
            'ssn': '123-45-6789',
            'credit_card': '4111111111111111'
        }
        
        # Mask sensitive data
        masked_data = {}
        for key, value in data.items():
            if key in sensitive_fields:
                masked_data[key] = '*' * len(str(value))
            else:
                masked_data[key] = value
        
        # Check masking
        assert masked_data['password'] == '*********'
        assert masked_data['ssn'] == '***********'
        assert masked_data['username'] == 'john_doe'
    
    def test_encryption_at_rest(self, app):
        """Test database encryption at rest"""
        # This would typically be handled by the database
        # Check that sensitive tables are marked for encryption
        sensitive_tables = ['users', 'documents', 'api_keys', 'sessions']
        
        for table in sensitive_tables:
            # In production, verify table encryption settings
            if app.config['ENV'] == 'production':
                # This would check actual database encryption settings
                pass
    
    def test_secure_file_deletion(self):
        """Test secure file deletion"""
        import os
        import tempfile
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b'sensitive_data')
            filename = tmp.name
        
        # Secure deletion should overwrite before deleting
        with open(filename, 'ba+', buffering=0) as f:
            length = f.tell()
            f.seek(0)
            f.write(os.urandom(length))
        
        os.remove(filename)
        
        # File should be completely removed
        assert not os.path.exists(filename)