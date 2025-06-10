# BDC Platform - Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [Deployment Options](#deployment-options)
3. [Prerequisites](#prerequisites)
4. [Docker Deployment](#docker-deployment)
5. [Manual Deployment](#manual-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [Configuration](#configuration)
8. [SSL/TLS Setup](#ssltls-setup)
9. [Database Setup](#database-setup)
10. [Monitoring Setup](#monitoring-setup)
11. [Backup & Recovery](#backup--recovery)
12. [Scaling](#scaling)
13. [Troubleshooting](#troubleshooting)
14. [Maintenance](#maintenance)

---

## Overview

This guide provides comprehensive instructions for deploying the BDC Platform in various environments. The platform supports multiple deployment methods to suit different needs and infrastructures.

### Deployment Architecture

```
┌─────────────────────┐
│   Load Balancer     │
│   (Nginx/HAProxy)   │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │             │
┌───▼───┐    ┌───▼───┐
│ Web   │    │ Web   │
│ Server│    │ Server│
│   1   │    │   2   │
└───┬───┘    └───┬───┘
    │             │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │             │
┌───▼───┐    ┌───▼───┐
│  API  │    │  API  │
│Server │    │Server │
│   1   │    │   2   │
└───┬───┘    └───┬───┘
    │             │
    └──────┬──────┘
           │
    ┌──────▼──────────┐
    │                 │
┌───▼───┐        ┌───▼───┐
│Postgres│        │ Redis │
│Primary │        │Cluster│
└────────┘        └───────┘
```

---

## Deployment Options

### 1. Docker Deployment (Recommended)
- **Best for**: Quick setup, consistency, portability
- **Time**: 5-10 minutes
- **Complexity**: Low

### 2. Manual Deployment
- **Best for**: Custom environments, specific requirements
- **Time**: 30-60 minutes
- **Complexity**: Medium

### 3. Cloud Deployment
- **Best for**: Production, scalability
- **Time**: 1-2 hours
- **Complexity**: High

---

## Prerequisites

### System Requirements

#### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 20 GB
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 11+

#### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 50+ GB SSD
- **OS**: Ubuntu 22.04 LTS

### Software Requirements

```bash
# Docker deployment
- Docker 20.10+
- Docker Compose 2.0+

# Manual deployment
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Nginx 1.18+
```

### Network Requirements
- Ports: 80, 443 (web), 5000 (API), 5432 (PostgreSQL), 6379 (Redis)
- Domain name (for SSL)
- Static IP (recommended)

---

## Docker Deployment

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/your-org/bdc-platform.git
cd bdc-platform
```

2. **Configure environment**
```bash
cp .env.production.template .env
nano .env  # Edit configuration
```

3. **Run deployment script**
```bash
# Basic deployment
./scripts/docker-deploy.sh

# With monitoring
./scripts/docker-deploy.sh --monitoring

# Development mode
./scripts/docker-deploy.sh --mode development
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./server
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@postgres:5432/${DATABASE_NAME}
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./data/uploads:/app/uploads

  frontend:
    build:
      context: ./client
      dockerfile: Dockerfile
    environment:
      VITE_API_URL: ${API_URL}
    depends_on:
      - backend
    ports:
      - "80:80"
      - "443:443"

volumes:
  postgres_data:
  redis_data:
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove everything
docker-compose down -v

# Update images
docker-compose pull
docker-compose up -d
```

---

## Manual Deployment

### Backend Setup

1. **Install system dependencies**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.11 python3.11-dev python3-pip postgresql-15 redis-server nginx

# CentOS/RHEL
sudo yum install -y python311 python311-devel postgresql15-server redis nginx
```

2. **Setup Python environment**
```bash
cd server
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Configure database**
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE bdc_production;
CREATE USER bdc_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE bdc_production TO bdc_user;
\q

# Run migrations
flask db upgrade
```

4. **Configure application**
```bash
cp .env.example .env
nano .env  # Edit configuration
```

5. **Setup systemd service**
```bash
sudo nano /etc/systemd/system/bdc-backend.service
```

```ini
[Unit]
Description=BDC Backend API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/bdc/server
Environment="PATH=/opt/bdc/server/venv/bin"
ExecStart=/opt/bdc/server/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/tmp/bdc-backend.sock \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app:create_app()
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

6. **Start backend service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable bdc-backend
sudo systemctl start bdc-backend
```

### Frontend Setup

1. **Install Node.js**
```bash
# Using NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

2. **Build frontend**
```bash
cd client
npm install
npm run build
```

3. **Configure Nginx**
```bash
sudo nano /etc/nginx/sites-available/bdc-frontend
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL configuration
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Frontend files
    root /opt/bdc/client/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api {
        proxy_pass http://unix:/tmp/bdc-backend.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket proxy
    location /socket.io {
        proxy_pass http://unix:/tmp/bdc-backend.sock;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

4. **Enable site**
```bash
sudo ln -s /etc/nginx/sites-available/bdc-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Cloud Deployment

### AWS Deployment

1. **Infrastructure setup**
```bash
# Install AWS CLI
pip install awscli
aws configure

# Deploy with CloudFormation
aws cloudformation create-stack \
  --stack-name bdc-platform \
  --template-body file://aws/cloudformation.yaml \
  --parameters file://aws/parameters.json
```

2. **RDS setup**
```bash
# Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier bdc-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.2 \
  --master-username bdc_admin \
  --master-user-password $DB_PASSWORD \
  --allocated-storage 100
```

3. **ECS deployment**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name bdc-cluster

# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://aws/task-definition.json

# Create service
aws ecs create-service \
  --cluster bdc-cluster \
  --service-name bdc-service \
  --task-definition bdc-app:1
```

### Google Cloud Deployment

```bash
# Setup gcloud
gcloud init
gcloud config set project YOUR_PROJECT_ID

# Deploy to Cloud Run
gcloud run deploy bdc-backend \
  --image gcr.io/YOUR_PROJECT_ID/bdc-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Deploy to GKE
gcloud container clusters create bdc-cluster \
  --num-nodes=3 \
  --zone=us-central1-a

kubectl apply -f k8s/
```

### Azure Deployment

```bash
# Login to Azure
az login
az account set --subscription YOUR_SUBSCRIPTION_ID

# Create resource group
az group create --name bdc-rg --location eastus

# Deploy with ARM template
az deployment group create \
  --resource-group bdc-rg \
  --template-file azure/template.json \
  --parameters @azure/parameters.json
```

---

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/bdc
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://localhost:6379
REDIS_POOL_SIZE=10

# Security
SECRET_KEY=your-very-secure-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-also-32-chars-min
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Application
APP_NAME=BDC Platform
APP_ENV=production
DEBUG=false
LOG_LEVEL=info

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=notifications@your-domain.com
SMTP_PASSWORD=your-email-password
SMTP_USE_TLS=true

# Storage
UPLOAD_FOLDER=/data/uploads
MAX_UPLOAD_SIZE=16777216
ALLOWED_EXTENSIONS=pdf,doc,docx,jpg,jpeg,png

# External Services
OPENAI_API_KEY=sk-your-openai-api-key
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# Performance
CACHE_TYPE=redis
CACHE_REDIS_URL=redis://localhost:6379/1
CACHE_DEFAULT_TIMEOUT=300

# Security
CORS_ORIGINS=https://your-domain.com
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
```

### Application Configuration

```python
# config.py
class ProductionConfig:
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Performance
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # Monitoring
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
```

---

## SSL/TLS Setup

### Let's Encrypt (Certbot)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Manual SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # SSL Optimization
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

---

## Database Setup

### PostgreSQL Configuration

```bash
# postgresql.conf
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_beneficiaries_tenant_id ON beneficiaries(tenant_id);
CREATE INDEX idx_beneficiaries_created_at ON beneficiaries(created_at);
CREATE INDEX idx_programs_status ON programs(status);
CREATE INDEX idx_evaluations_program_id ON evaluations(program_id);

-- Analyze tables
ANALYZE beneficiaries;
ANALYZE programs;
ANALYZE evaluations;
```

### Backup Configuration

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
DB_NAME="bdc_production"

pg_dump -U bdc_user -h localhost $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

---

## Monitoring Setup

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bdc-backend'
    static_configs:
      - targets: ['localhost:5000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']

  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

### Grafana Dashboards

1. **Import dashboards**
```bash
# Application dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana/dashboards/application.json

# System dashboard
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @grafana/dashboards/system.json
```

2. **Configure alerts**
```yaml
# Alert rules
groups:
  - name: bdc_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(flask_http_request_exceptions_total[5m]) > 0.05
        for: 5m
        annotations:
          summary: "High error rate detected"
          
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
        for: 1m
        annotations:
          summary: "PostgreSQL is down"
```

---

## Backup & Recovery

### Automated Backup

```bash
# Create backup script
sudo nano /opt/bdc/scripts/backup.sh
```

```bash
#!/bin/bash
# BDC Platform Backup Script

BACKUP_ROOT="/backups/bdc"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$DATE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U bdc_user -h localhost bdc_production | \
  gzip > $BACKUP_DIR/database.sql.gz

# Backup uploads
tar -czf $BACKUP_DIR/uploads.tar.gz /data/uploads/

# Backup configuration
tar -czf $BACKUP_DIR/config.tar.gz /opt/bdc/server/.env

# Create manifest
cat > $BACKUP_DIR/manifest.json <<EOF
{
  "timestamp": "$DATE",
  "version": "$(cat /opt/bdc/VERSION)",
  "components": ["database", "uploads", "config"]
}
EOF

# Upload to S3 (optional)
aws s3 sync $BACKUP_DIR s3://bdc-backups/$DATE/

# Cleanup old backups (keep 30 days)
find $BACKUP_ROOT -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;
```

### Recovery Procedure

```bash
# 1. Stop services
sudo systemctl stop bdc-backend
sudo systemctl stop nginx

# 2. Restore database
gunzip < /backups/bdc/20240101_120000/database.sql.gz | \
  psql -U bdc_user -h localhost bdc_production

# 3. Restore uploads
tar -xzf /backups/bdc/20240101_120000/uploads.tar.gz -C /

# 4. Restore configuration
tar -xzf /backups/bdc/20240101_120000/config.tar.gz -C /

# 5. Start services
sudo systemctl start bdc-backend
sudo systemctl start nginx
```

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  backend:
    deploy:
      replicas: 4
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/load-balancer.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

### Load Balancer Configuration

```nginx
# nginx/load-balancer.conf
upstream backend_servers {
    least_conn;
    server backend_1:5000 weight=1;
    server backend_2:5000 weight=1;
    server backend_3:5000 weight=1;
    server backend_4:5000 weight=1;
}

server {
    listen 80;
    
    location /api {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Scaling

```bash
# Setup read replica
pg_basebackup -h primary-db -D /var/lib/postgresql/data -U replicator -W

# Configure streaming replication
echo "standby_mode = 'on'
primary_conninfo = 'host=primary-db port=5432 user=replicator'
" > /var/lib/postgresql/data/recovery.conf
```

---

## Troubleshooting

### Common Issues

#### Backend Won't Start

```bash
# Check logs
sudo journalctl -u bdc-backend -n 100

# Common fixes
# 1. Database connection
psql -U bdc_user -h localhost -d bdc_production -c "SELECT 1;"

# 2. Redis connection
redis-cli ping

# 3. Permission issues
sudo chown -R www-data:www-data /opt/bdc/server

# 4. Python dependencies
source venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

#### Frontend Build Fails

```bash
# Clear cache
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# Check Node version
node --version  # Should be 18+

# Memory issues
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

#### Database Performance

```sql
-- Check slow queries
SELECT query, calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT
    schemaname AS table_schema,
    tablename AS table_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Vacuum and analyze
VACUUM ANALYZE;
```

### Performance Tuning

```bash
# System tuning
sudo sysctl -w vm.swappiness=10
sudo sysctl -w net.core.somaxconn=65535
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=65535

# PostgreSQL tuning
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET work_mem = '16MB';
SELECT pg_reload_conf();
```

---

## Maintenance

### Regular Tasks

#### Daily
- Check application logs
- Monitor system resources
- Verify backup completion

#### Weekly
- Review error logs
- Update dependencies
- Check disk usage

#### Monthly
- Security updates
- Performance review
- Database maintenance

### Update Procedure

```bash
# 1. Backup current version
./scripts/backup.sh

# 2. Pull latest code
git pull origin main

# 3. Update backend
cd server
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade

# 4. Update frontend
cd ../client
npm install
npm run build

# 5. Restart services
sudo systemctl restart bdc-backend
sudo systemctl reload nginx

# 6. Verify
curl https://your-domain.com/health
```

### Security Updates

```bash
# Check for vulnerabilities
# Python
pip install safety
safety check

# Node.js
npm audit
npm audit fix

# System packages
sudo apt update
sudo apt list --upgradable
```

---

## Appendix

### Useful Commands

```bash
# Service management
sudo systemctl status bdc-backend
sudo systemctl restart bdc-backend
sudo journalctl -u bdc-backend -f

# Database
psql -U bdc_user -d bdc_production
pg_dump -U bdc_user bdc_production > backup.sql

# Docker
docker-compose ps
docker-compose logs -f backend
docker exec -it bdc_postgres psql -U bdc_user

# Performance
htop
iotop
pg_top
redis-cli monitor
```

### References

- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)

---

*Last Updated: January 2025*
*Version: 1.0.0*