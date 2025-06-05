# Security Fixes Required - Hardcoded Credentials

## Critical Security Issues Found

### 1. Database Credentials
**Files to fix:**
- `seed_evaluations_demo.py` - Lines 27-29
- `docker-compose.yml` - Lines 18, 49-50
- `.env.local` and `server/.env` - Multiple database passwords

**Action Required:**
- Use environment variables for all database connections
- Remove hardcoded passwords from docker-compose files
- Use `.env` files only for local development, never commit them

### 2. Default User Passwords
**File:** `server/app/core/database_manager.py`
- Admin: `Admin123!` (lines 144, 322)
- Tenant: `Tenant123!` (line 152)
- Trainer: `Trainer123!` (line 160)
- Student: `Student123!` (line 168)

**Action Required:**
- Generate random passwords for initial users
- Force password change on first login
- Store hashed passwords only

### 3. API Keys
**Files to fix:**
- `server/app/services/ai/report_synthesis.py` - Line 54
- `server/app/services/ai/recommendations.py` - Line 56
- `server/app/services/ai/note_analysis.py` - Line 44
- `server/app/services/alert_service.py` - Line 379

**Action Required:**
- Remove all placeholder API keys
- Use environment variables: `os.getenv('OPENAI_API_KEY')`
- Fail gracefully if API key is not configured

### 4. Secret Keys
**Files to fix:**
- `server/config.py` - Lines 9, 24
- `.env.local` and `server/.env` - SECRET_KEY and JWT_SECRET_KEY

**Action Required:**
- Generate strong random keys for production
- Never use default/development keys in production
- Document key generation process

### 5. SMTP Credentials
**File:** `alertmanager/alertmanager.yml` - Line 6

**Action Required:**
- Use environment variable substitution in YAML
- Never commit SMTP passwords

### 6. Redis Credentials
**Files:** `.env.local` and `server/.env`

**Action Required:**
- Use strong passwords for Redis in production
- Configure Redis ACL for better security

## Recommended Environment Variables

Create a `.env.example` file with these variables (without values):

```bash
# Database
DATABASE_URL=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=

# Redis
REDIS_URL=
REDIS_PASSWORD=

# Security
SECRET_KEY=
JWT_SECRET_KEY=

# External Services
OPENAI_API_KEY=
SMTP_PASSWORD=
SENTRY_DSN=

# Default Admin (for initial setup only)
ADMIN_EMAIL=
ADMIN_PASSWORD=
```

## Security Best Practices

1. **Never commit .env files** - Already in .gitignore
2. **Use strong, random passwords** - Minimum 32 characters for keys
3. **Rotate credentials regularly**
4. **Use different credentials for each environment**
5. **Implement proper secret management** (e.g., HashiCorp Vault, AWS Secrets Manager)
6. **Audit access logs regularly**
7. **Use encrypted connections** for all services

## Priority Actions

1. **HIGH**: Remove hardcoded credentials from source code
2. **HIGH**: Update docker-compose files to use env variables
3. **MEDIUM**: Implement secure password generation for default users
4. **MEDIUM**: Add credential validation on startup
5. **LOW**: Document security procedures

---
*This file should be addressed immediately before any production deployment*