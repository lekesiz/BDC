# BDC Deployment Checklist

## Pre-Deployment Tasks

### 1. Environment Configuration
- [ ] Create production .env file with secure values
- [ ] Configure database connection for PostgreSQL
- [ ] Set up Redis connection for production
- [ ] Configure JWT secret keys
- [ ] Set appropriate CORS origins
- [ ] Configure email service credentials
- [ ] Set up external API keys (OpenAI, Google Calendar, etc.)

### 2. Security Audit
- [ ] Review all API endpoints for proper authentication
- [ ] Ensure SQL injection protection
- [ ] Verify XSS prevention measures
- [ ] Check CSRF token implementation
- [ ] Review file upload restrictions
- [ ] Ensure passwords are properly hashed
- [ ] Configure rate limiting
- [ ] Set secure headers

### 3. Database Preparation
- [ ] Create production database
- [ ] Run all migrations
- [ ] Create indexes for performance
- [ ] Set up backup procedures
- [ ] Configure connection pooling
- [ ] Create read replicas if needed

### 4. Performance Optimization
- [ ] Enable production build optimizations
- [ ] Configure CDN for static assets
- [ ] Set up caching headers
- [ ] Enable gzip/brotli compression
- [ ] Configure load balancer
- [ ] Set up SSL/TLS certificates

### 5. Monitoring Setup
- [ ] Configure error tracking (Sentry)
- [ ] Set up performance monitoring
- [ ] Configure log aggregation
- [ ] Set up uptime monitoring
- [ ] Create alerting rules
- [ ] Configure analytics

### 6. Testing
- [ ] Run full test suite
- [ ] Perform load testing
- [ ] Security penetration testing
- [ ] Browser compatibility testing
- [ ] Mobile responsiveness testing
- [ ] Accessibility testing

## Deployment Steps

### 1. Backend Deployment
```bash
# Clone repository
git clone <repository-url>
cd BDC/server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with production values

# Run migrations
flask db upgrade

# Collect static files (if applicable)
python manage.py collectstatic

# Start application
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### 2. Frontend Deployment
```bash
# Navigate to client directory
cd BDC/client

# Install dependencies
npm install

# Build for production
npm run build

# Deploy build folder to web server/CDN
```

### 3. Docker Deployment (Alternative)
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Run migrations
docker-compose exec backend flask db upgrade
```

### 4. Server Configuration
- [ ] Configure Nginx/Apache reverse proxy
- [ ] Set up SSL with Let's Encrypt
- [ ] Configure firewall rules
- [ ] Set up systemd service files
- [ ] Configure log rotation

### 5. Post-Deployment Tasks
- [ ] Verify all services are running
- [ ] Test critical user flows
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify email sending
- [ ] Test file uploads
- [ ] Verify API integrations

## Environment Variables

### Backend (.env)
```
# Database
DATABASE_URL=postgresql://user:password@localhost/bdc_prod
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=<strong-secret-key>
JWT_SECRET_KEY=<strong-jwt-secret>

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=<email>
MAIL_PASSWORD=<password>

# External APIs
OPENAI_API_KEY=<key>
GOOGLE_CLIENT_ID=<id>
GOOGLE_CLIENT_SECRET=<secret>

# Environment
FLASK_ENV=production
```

### Frontend (.env)
```
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production
```

## Rollback Plan

### 1. Database Rollback
```bash
# Backup before deployment
pg_dump bdc_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# Rollback if needed
psql bdc_prod < backup_20250517_120000.sql
```

### 2. Application Rollback
```bash
# Tag releases
git tag -a v1.0.0 -m "Release version 1.0.0"

# Rollback to previous version
git checkout v0.9.0
```

## Monitoring Checklist

### 1. Application Health
- [ ] API endpoints responding
- [ ] Database connections stable
- [ ] Redis cache working
- [ ] Background jobs running
- [ ] Email delivery functional

### 2. Performance Metrics
- [ ] Response times < 200ms
- [ ] Error rate < 1%
- [ ] CPU usage < 70%
- [ ] Memory usage stable
- [ ] Disk space adequate

### 3. User Experience
- [ ] Login/logout working
- [ ] Core features accessible
- [ ] File uploads functional
- [ ] Search working properly
- [ ] Notifications delivering

## Support Documentation

### 1. Runbooks
- [ ] Server restart procedures
- [ ] Database backup/restore
- [ ] Cache clearing procedures
- [ ] Log analysis guide
- [ ] Common error solutions

### 2. Contact Information
- [ ] DevOps team contacts
- [ ] Database administrator
- [ ] Security team
- [ ] Business stakeholders
- [ ] External service support

## Final Verification

### 1. Functionality Tests
- [ ] User registration and login
- [ ] Role-based access control
- [ ] CRUD operations
- [ ] File uploads/downloads
- [ ] Email notifications
- [ ] API integrations
- [ ] Search functionality
- [ ] Report generation

### 2. Security Tests
- [ ] SSL certificate valid
- [ ] Headers configured correctly
- [ ] Authentication working
- [ ] Authorization enforced
- [ ] Input validation active
- [ ] Rate limiting enabled

### 3. Performance Tests
- [ ] Page load times acceptable
- [ ] API response times fast
- [ ] Database queries optimized
- [ ] Static assets cached
- [ ] Images optimized

## Sign-off

- [ ] Development team approval
- [ ] QA team approval
- [ ] Security team approval
- [ ] Business stakeholder approval
- [ ] Go-live authorization

---

**Note**: This checklist should be customized based on your specific infrastructure and deployment requirements.