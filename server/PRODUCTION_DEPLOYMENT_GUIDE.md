# BDC Production Deployment Guide

This comprehensive guide covers the complete production deployment of the BDC (Behavioral Development Center) application with enterprise-grade security, performance, and reliability.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Security Configuration](#security-configuration)
3. [Environment Setup](#environment-setup)
4. [Database Setup](#database-setup)
5. [SSL/HTTPS Configuration](#ssl-https-configuration)
6. [Docker Deployment](#docker-deployment)
7. [Kubernetes Deployment](#kubernetes-deployment)
8. [Monitoring & Logging](#monitoring--logging)
9. [Backup & Recovery](#backup--recovery)
10. [Performance Optimization](#performance-optimization)
11. [Health Checks](#health-checks)
12. [Load Balancing](#load-balancing)
13. [CI/CD Pipeline](#ci-cd-pipeline)
14. [Security Hardening](#security-hardening)
15. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04 LTS or CentOS 8+ (recommended)
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 100GB SSD minimum (500GB+ recommended)
- **Network**: Stable internet connection with static IP

### Required Software
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Kubernetes (optional)
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubectl

# Install monitoring tools
sudo apt install -y htop iotop nethogs sysstat
```

## 🔒 Security Configuration

### 1. Environment Variables Setup

**Copy and configure production environment:**
```bash
cp .env.production .env
```

**Required environment variables (update with secure values):**
```bash
# Security Keys (MUST be changed)
SECRET_KEY="your-super-secure-secret-key-here"
JWT_SECRET_KEY="your-jwt-secret-key-here"

# Database
DATABASE_URL="postgresql://username:password@localhost:5432/bdc_production"

# Redis
REDIS_URL="redis://localhost:6379/0"
REDIS_PASSWORD="your-redis-password"

# Email Configuration
MAIL_SERVER="smtp.sendgrid.net"
MAIL_USERNAME="apikey"
MAIL_PASSWORD="your-sendgrid-api-key"

# Domain Configuration
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"
TRUSTED_HOSTS="yourdomain.com,www.yourdomain.com"

# AWS (for file storage and backups)
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_S3_BUCKET="your-s3-bucket"

# Monitoring
SENTRY_DSN="your-sentry-dsn"
```

### 2. Generate Secure Keys
```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# Generate backup encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## 🗄️ Database Setup

### PostgreSQL Production Setup

**1. Install PostgreSQL:**
```bash
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**2. Create production database:**
```bash
sudo -u postgres psql << EOF
CREATE DATABASE bdc_production;
CREATE USER bdc_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE bdc_production TO bdc_user;
ALTER USER bdc_user CREATEDB;
\q
EOF
```

**3. Configure PostgreSQL for production:**
```bash
sudo nano /etc/postgresql/13/main/postgresql.conf
```

Add optimizations:
```
# Memory settings
shared_buffers = 2GB
effective_cache_size = 6GB
work_mem = 16MB
maintenance_work_mem = 512MB

# Connection settings
max_connections = 200

# Performance settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
```

**4. Run database migrations:**
```bash
export FLASK_ENV=production
export DATABASE_URL="postgresql://bdc_user:password@localhost:5432/bdc_production"
flask db upgrade
```

## 🔐 SSL/HTTPS Configuration

### Option 1: Let's Encrypt (Recommended)
```bash
# Run SSL setup script
sudo ./scripts/ssl-setup.sh yourdomain.com admin@yourdomain.com letsencrypt
```

### Option 2: Manual Certificate Setup
```bash
# If you have your own certificates
sudo mkdir -p /etc/ssl/bdc
sudo cp your-cert.pem /etc/ssl/bdc/cert.pem
sudo cp your-key.pem /etc/ssl/bdc/key.pem
sudo chmod 600 /etc/ssl/bdc/key.pem
sudo chmod 644 /etc/ssl/bdc/cert.pem
```

## 🐳 Docker Deployment

### 1. Production Docker Deployment

**Build and deploy with Docker Compose:**
```bash
# Set environment variables
export DB_PASSWORD="your-database-password"
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret-key"
export REDIS_PASSWORD="your-redis-password"
export GRAFANA_PASSWORD="your-grafana-password"

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f app
```

### 2. Initialize Application Data
```bash
# Create admin user
docker-compose -f docker-compose.production.yml exec app python create_admin.py

# Run any additional setup scripts
docker-compose -f docker-compose.production.yml exec app python seed_db.py
```

## ☸️ Kubernetes Deployment

### 1. Deploy to Kubernetes
```bash
# Deploy using the deployment script
./scripts/deploy.sh

# Or deploy manually:
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml  # Update with real secrets first
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/app.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/monitoring.yaml
```

### 2. Verify Deployment
```bash
# Check pod status
kubectl get pods -n bdc-production

# Check services
kubectl get services -n bdc-production

# Check ingress
kubectl get ingress -n bdc-production

# View logs
kubectl logs -f deployment/bdc-app -n bdc-production
```

## 📊 Monitoring & Logging

### 1. Access Monitoring Dashboards

**Prometheus:** `http://your-domain:9090`
**Grafana:** `http://your-domain:3000` (admin/your-grafana-password)

### 2. Configure Alerts

**Slack notifications (optional):**
```bash
# Set webhook URL in environment
export SLACK_WEBHOOK_URL="your-slack-webhook-url"
```

### 3. Log Management
```bash
# View application logs
tail -f logs/bdc_production.log

# View access logs
tail -f /var/log/nginx/access.log

# View error logs
tail -f /var/log/nginx/error.log
```

## 💾 Backup & Recovery

### 1. Automated Backups

**Configure backup settings:**
```bash
export BACKUP_S3_BUCKET="your-backup-bucket"
export BACKUP_ENCRYPTION_KEY="your-encryption-key"
```

**Manual backup:**
```bash
# Database backup
docker-compose exec backup python backup.py once

# Or using script
./docker/scripts/backup.sh
```

### 2. Restore from Backup
```bash
# List available backups
aws s3 ls s3://your-backup-bucket/database_backups/

# Restore database
docker-compose exec app python -c "
from app.utils.backup_manager import BackupManager
backup_manager = BackupManager()
backup_manager.restore_database_backup('s3://bucket/backup_file.sql.gz.encrypted')
"
```

## 🚀 Performance Optimization

### 1. System Performance Tuning
```bash
# Run performance optimization script
sudo ./scripts/performance-tuning.sh
```

### 2. Application Performance

**Enable caching:**
```bash
# Redis is automatically configured for caching
# Monitor cache hit rates in Grafana dashboard
```

**Database optimization:**
```bash
# Run database analysis
sudo -u postgres psql bdc_production -c "ANALYZE;"

# Check slow queries
sudo -u postgres psql bdc_production -c "
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

## 🏥 Health Checks

### 1. Application Health Endpoints

- **Basic health:** `https://yourdomain.com/health`
- **Detailed health:** `https://yourdomain.com/health/detailed`
- **Readiness probe:** `https://yourdomain.com/ready`
- **Liveness probe:** `https://yourdomain.com/live`

### 2. Monitor Health Status
```bash
# Check application health
curl -f https://yourdomain.com/health

# Check all services
./scripts/health-check.sh
```

## ⚖️ Load Balancing

### 1. Nginx Load Balancing (Multi-server)

**Configure upstream servers:**
```nginx
upstream app_backend {
    least_conn;
    server app1:8000 max_fails=3 fail_timeout=30s;
    server app2:8000 max_fails=3 fail_timeout=30s;
    server app3:8000 max_fails=3 fail_timeout=30s;
}
```

### 2. Horizontal Pod Autoscaling (Kubernetes)
```bash
# HPA is automatically configured in k8s/app.yaml
# Monitor scaling:
kubectl get hpa -n bdc-production
```

## 🔄 CI/CD Pipeline

### 1. GitHub Actions Setup

**Required secrets in GitHub repository:**
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DATABASE_URL`
- `REDIS_URL`
- `SLACK_WEBHOOK_URL`

### 2. Manual Deployment
```bash
# Build and push new version
docker build -f docker/Dockerfile --target production -t ghcr.io/your-org/bdc:v1.0.0 .
docker push ghcr.io/your-org/bdc:v1.0.0

# Deploy new version
./scripts/deploy.sh v1.0.0
```

## 🛡️ Security Hardening

### 1. Firewall Configuration
```bash
# UFW firewall setup
sudo ufw enable
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 5432/tcp   # PostgreSQL (only internal)
sudo ufw deny 6379/tcp   # Redis (only internal)
```

### 2. Security Headers
```bash
# Security headers are automatically configured in nginx.conf
# Verify with:
curl -I https://yourdomain.com
```

### 3. Regular Security Updates
```bash
# Set up automatic security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```

## 🔧 Troubleshooting

### Common Issues

**1. Application won't start:**
```bash
# Check logs
docker-compose logs app
kubectl logs deployment/bdc-app -n bdc-production

# Check environment variables
docker-compose exec app env | grep -E "(SECRET_KEY|DATABASE_URL)"
```

**2. Database connection failed:**
```bash
# Test database connection
docker-compose exec app python -c "
from app.extensions import db
from app import create_app
app = create_app()
with app.app_context():
    db.engine.execute('SELECT 1')
print('Database connection successful')
"
```

**3. High memory usage:**
```bash
# Check memory usage
docker stats
kubectl top pods -n bdc-production

# Restart services if needed
docker-compose restart app
kubectl rollout restart deployment/bdc-app -n bdc-production
```

**4. SSL certificate issues:**
```bash
# Check certificate validity
openssl x509 -in /etc/ssl/bdc/cert.pem -text -noout

# Renew Let's Encrypt certificate
sudo certbot renew
```

### Performance Issues

**1. Slow database queries:**
```bash
# Enable query logging
sudo -u postgres psql bdc_production -c "
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
"

# Check slow queries log
sudo tail -f /var/log/postgresql/postgresql-13-main.log
```

**2. High CPU usage:**
```bash
# Check top processes
htop

# Scale application
docker-compose up --scale app=3
kubectl scale deployment bdc-app --replicas=5 -n bdc-production
```

## 📞 Support and Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor application health
- Check error logs
- Verify backup completion

**Weekly:**
- Review performance metrics
- Update security patches
- Clean up old logs

**Monthly:**
- Review and rotate SSL certificates
- Database maintenance (VACUUM, ANALYZE)
- Review and update dependencies

### Emergency Procedures

**Application Down:**
1. Check health endpoints
2. Review recent deployments
3. Check resource usage
4. Rollback if necessary: `kubectl rollout undo deployment/bdc-app -n bdc-production`

**Database Issues:**
1. Check PostgreSQL logs
2. Verify disk space
3. Check connection limits
4. Restore from backup if needed

## 📝 Production Checklist

### Pre-Deployment
- [ ] All environment variables configured with production values
- [ ] SSL certificates installed and verified
- [ ] Database optimized and backed up
- [ ] Monitoring and alerting configured
- [ ] Security headers and firewalls configured
- [ ] Performance tuning applied
- [ ] Backup and recovery procedures tested

### Post-Deployment
- [ ] Health checks passing
- [ ] Monitoring dashboards accessible
- [ ] SSL/HTTPS working correctly
- [ ] Application functionality verified
- [ ] Performance metrics within acceptable ranges
- [ ] Backup system operational
- [ ] Error tracking and logging working

### Security Verification
- [ ] All default passwords changed
- [ ] Unnecessary services disabled
- [ ] Access logs monitoring configured
- [ ] Rate limiting active
- [ ] Input validation working
- [ ] CSRF protection enabled
- [ ] Security headers present

---

## 🎉 Congratulations!

Your BDC application is now deployed and ready for production use with:

✅ **Enterprise Security** - Comprehensive security measures and monitoring  
✅ **High Availability** - Load balancing and auto-scaling capabilities  
✅ **Performance Optimized** - Database tuning and caching  
✅ **Monitoring & Alerts** - Full observability stack  
✅ **Automated Backups** - Reliable backup and recovery procedures  
✅ **CI/CD Ready** - Automated deployment pipeline  

For ongoing support and updates, refer to this guide and monitor the application through the configured dashboards and alerts.

**Important:** Remember to regularly update your security configurations, monitor performance metrics, and keep your system dependencies up to date.