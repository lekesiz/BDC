# BDC Deployment Guide

## Overview

This guide covers the deployment process for the BDC (Beneficiary Development Center) application, including both development and production environments. The application consists of a Flask backend and React frontend, deployed using Docker containers.

## Prerequisites

### System Requirements

- Ubuntu 20.04 LTS or later (Production)
- Docker 20.10+ and Docker Compose 2.0+
- Python 3.9+ (Development)
- Node.js 16+ and npm 8+ (Development)
- PostgreSQL 13+ (Production)
- Redis 6+ (Production)
- Nginx (Production)
- Git

### Domain and SSL

- Domain name configured with DNS
- SSL certificate (Let's Encrypt recommended)
- Mail server for notifications (optional)

## Development Environment

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/your-org/bdc.git
cd bdc
```

2. **Backend setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

4. **Initialize database**
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
flask seed-db  # Optional: Seed with sample data
```

5. **Run backend server**
```bash
flask run
# or
python run.py
```

6. **Frontend setup**
```bash
cd ../client
npm install
cp .env.example .env
# Edit .env file
```

7. **Run frontend development server**
```bash
npm run dev
```

### Docker Development

1. **Build and run with Docker Compose**
```bash
docker-compose -f docker-compose.dev.yml up --build
```

2. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api

## Production Deployment

### Server Preparation

1. **Update system packages**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Install required software**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y
```

3. **Create application user**
```bash
sudo useradd -m -s /bin/bash bdc
sudo usermod -aG docker bdc
```

4. **Create directory structure**
```bash
sudo mkdir -p /opt/bdc
sudo chown bdc:bdc /opt/bdc
```

### Application Deployment

1. **Clone repository to server**
```bash
sudo -u bdc git clone https://github.com/your-org/bdc.git /opt/bdc
cd /opt/bdc
```

2. **Create production environment file**
```bash
sudo -u bdc cp .env.production.example .env
sudo -u bdc nano .env
```

Example production `.env`:
```env
# Application
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://bdc_user:password@postgres:5432/bdc_prod
REDIS_URL=redis://redis:6379/0

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Frontend
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

3. **Build and start containers**
```bash
sudo -u bdc docker-compose -f docker-compose.prod.yml up -d --build
```

### Nginx Configuration

1. **Create Nginx server block**
```bash
sudo nano /etc/nginx/sites-available/bdc
```

```nginx
# API server
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Frontend server
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

2. **Enable the site**
```bash
sudo ln -s /etc/nginx/sites-available/bdc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL Certificate Setup

1. **Obtain SSL certificate**
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

2. **Configure auto-renewal**
```bash
sudo crontab -e
# Add this line:
0 3 * * * /usr/bin/certbot renew --quiet
```

### Database Setup

1. **Create PostgreSQL database and user**
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE bdc_prod;
CREATE USER bdc_user WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE bdc_prod TO bdc_user;
\q
```

2. **Run migrations**
```bash
sudo -u bdc docker-compose -f docker-compose.prod.yml exec backend flask db upgrade
```

3. **Create admin user**
```bash
sudo -u bdc docker-compose -f docker-compose.prod.yml exec backend flask create-admin
```

### Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      - FLASK_ENV=production
    env_file:
      - .env
    volumes:
      - ./backend:/app
      - static_volume:/app/static
      - media_volume:/app/media
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./client
      dockerfile: Dockerfile.prod
      args:
        - REACT_APP_API_URL=${REACT_APP_API_URL}
    volumes:
      - ./client/nginx.conf:/etc/nginx/conf.d/default.conf
    restart: unless-stopped

  postgres:
    image: postgres:13-alpine
    environment:
      - POSTGRES_DB=bdc_prod
      - POSTGRES_USER=bdc_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/static
      - media_volume:/media
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### Environment Variables

Complete list of environment variables:

```bash
# Application Settings
SECRET_KEY=              # Flask secret key
JWT_SECRET_KEY=          # JWT signing key
FLASK_ENV=production     # Flask environment

# Database
DATABASE_URL=            # PostgreSQL connection string
DB_POOL_SIZE=10         # Connection pool size
DB_MAX_OVERFLOW=20      # Max overflow connections

# Redis
REDIS_URL=              # Redis connection string
REDIS_POOL_SIZE=10      # Connection pool size

# Email
MAIL_SERVER=            # SMTP server
MAIL_PORT=              # SMTP port
MAIL_USE_TLS=          # Use TLS (true/false)
MAIL_USERNAME=          # SMTP username
MAIL_PASSWORD=          # SMTP password
MAIL_DEFAULT_SENDER=    # Default sender email

# Frontend
REACT_APP_API_URL=      # API base URL
REACT_APP_GOOGLE_CLIENT_ID=  # Google OAuth client ID
REACT_APP_SENTRY_DSN=   # Sentry DSN for frontend

# File Storage
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216  # 16MB max file size

# Security
CORS_ORIGINS=*          # Allowed CORS origins
SESSION_LIFETIME=86400  # Session lifetime in seconds
PASSWORD_MIN_LENGTH=8   # Minimum password length

# Monitoring
SENTRY_DSN=            # Sentry DSN for backend
LOG_LEVEL=INFO         # Logging level
PROMETHEUS_ENABLED=true # Enable Prometheus metrics

# External Services
OPENAI_API_KEY=        # OpenAI API key
GOOGLE_CALENDAR_CREDENTIALS=  # Google Calendar creds
TWILIO_ACCOUNT_SID=    # Twilio account SID
TWILIO_AUTH_TOKEN=     # Twilio auth token
```

## Monitoring and Logging

### Application Monitoring

1. **Prometheus setup**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'bdc'
    static_configs:
      - targets: ['backend:5000']
```

2. **Grafana dashboard**
```bash
docker run -d \
  -p 3001:3000 \
  --name grafana \
  -v grafana_data:/var/lib/grafana \
  grafana/grafana
```

### Log Management

1. **Application logs**
```bash
# View backend logs
docker-compose logs -f backend

# View all logs
docker-compose logs -f

# Export logs
docker-compose logs > logs_$(date +%Y%m%d).txt
```

2. **Nginx logs**
```bash
# Access logs
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log
```

3. **Log rotation**
```bash
# /etc/logrotate.d/bdc
/opt/bdc/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 bdc bdc
    sharedscripts
    postrotate
        docker-compose -f /opt/bdc/docker-compose.prod.yml restart backend
    endscript
}
```

### Health Checks

1. **Docker health checks**
```dockerfile
# backend/Dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
```

2. **Monitoring endpoints**
```python
# app/api/monitoring.py
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': app.config['VERSION']
    }

@app.route('/metrics')
def metrics():
    # Return Prometheus metrics
    return Response(prometheus_client.generate_latest(), 
                   mimetype='text/plain')
```

## Backup and Recovery

### Database Backup

1. **Automated backups**
```bash
#!/bin/bash
# /opt/bdc/scripts/backup.sh

BACKUP_DIR="/opt/bdc/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="bdc_prod"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U bdc_user $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-backup-bucket/
```

2. **Schedule backups**
```bash
# Add to crontab
0 2 * * * /opt/bdc/scripts/backup.sh
```

### File Backup

```bash
#!/bin/bash
# Backup uploaded files
tar -czf /opt/bdc/backups/files_$(date +%Y%m%d).tar.gz /opt/bdc/uploads/
```

### Restore Procedures

1. **Database restore**
```bash
# Stop application
docker-compose down

# Restore database
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U bdc_user bdc_prod

# Start application
docker-compose up -d
```

2. **File restore**
```bash
tar -xzf files_backup.tar.gz -C /
```

## Updates and Maintenance

### Application Updates

1. **Pull latest changes**
```bash
cd /opt/bdc
git pull origin main
```

2. **Update containers**
```bash
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

3. **Run migrations**
```bash
docker-compose exec backend flask db upgrade
```

### Zero-Downtime Deployment

1. **Blue-Green deployment**
```bash
# Deploy to staging
docker-compose -f docker-compose.staging.yml up -d

# Test staging
curl https://staging.yourdomain.com/health

# Switch traffic to staging
# Update Nginx configuration

# Stop old version
docker-compose -f docker-compose.prod.yml down
```

2. **Rolling updates**
```bash
# Update one service at a time
docker-compose up -d --no-deps --build backend
# Wait for health check
docker-compose up -d --no-deps --build frontend
```

### Maintenance Mode

```nginx
# maintenance.html
<!DOCTYPE html>
<html>
<head>
    <title>Maintenance</title>
</head>
<body>
    <h1>Site Under Maintenance</h1>
    <p>We'll be back shortly.</p>
</body>
</html>

# nginx.conf
location / {
    if (-f /opt/bdc/maintenance.html) {
        return 503;
    }
    proxy_pass http://localhost:3000;
}

error_page 503 /maintenance.html;
location = /maintenance.html {
    root /opt/bdc;
}
```

## Security Hardening

### Server Security

1. **Configure firewall**
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

2. **SSH hardening**
```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
```

3. **Fail2ban setup**
```bash
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
```

### Application Security

1. **Environment variables**
```bash
# Never commit .env files
echo ".env" >> .gitignore

# Use strong secrets
openssl rand -hex 32  # Generate secret keys
```

2. **Docker security**
```dockerfile
# Run as non-root user
RUN useradd -m appuser
USER appuser

# Minimize image size
FROM python:3.9-slim
```

3. **Network isolation**
```yaml
# docker-compose.yml
networks:
  frontend:
  backend:
  
services:
  backend:
    networks:
      - backend
  postgres:
    networks:
      - backend
```

## Troubleshooting

### Common Issues

1. **Container won't start**
```bash
# Check logs
docker-compose logs backend

# Check container status
docker ps -a

# Rebuild containers
docker-compose build --no-cache
```

2. **Database connection errors**
```bash
# Test database connection
docker-compose exec postgres psql -U bdc_user -d bdc_prod

# Check environment variables
docker-compose exec backend env | grep DATABASE_URL
```

3. **Permission issues**
```bash
# Fix file permissions
sudo chown -R bdc:bdc /opt/bdc
sudo chmod -R 755 /opt/bdc
```

### Performance Issues

1. **Slow queries**
```sql
-- Enable query logging
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();

-- Check slow queries
SELECT query, calls, mean_time, max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

2. **High memory usage**
```bash
# Check container resources
docker stats

# Limit container resources
docker-compose.yml:
  backend:
    mem_limit: 512m
    cpus: '0.5'
```

### Debug Mode

```bash
# Enable debug mode temporarily
docker-compose exec backend flask shell
>>> app.config['DEBUG'] = True
```

## Rollback Procedures

1. **Application rollback**
```bash
# Tag current version
git tag -a v1.0.0 -m "Version 1.0.0"

# Rollback to previous version
git checkout v0.9.0
docker-compose build
docker-compose up -d
```

2. **Database rollback**
```bash
# Rollback last migration
docker-compose exec backend flask db downgrade

# Restore from backup
docker-compose exec -T postgres psql -U bdc_user bdc_prod < backup.sql
```

## Scaling

### Horizontal Scaling

1. **Load balancer setup**
```nginx
upstream backend {
    server backend1:5000;
    server backend2:5000;
    server backend3:5000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

2. **Database replication**
```yaml
# Master-slave replication
services:
  postgres-master:
    image: postgres:13
    environment:
      - POSTGRES_REPLICATION_MODE=master
      
  postgres-slave:
    image: postgres:13
    environment:
      - POSTGRES_REPLICATION_MODE=slave
      - POSTGRES_MASTER_HOST=postgres-master
```

### Vertical Scaling

```bash
# Upgrade server resources
# Update docker-compose limits
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
```

## Disaster Recovery

### Backup Strategy

1. **3-2-1 Rule**
   - 3 copies of data
   - 2 different storage types
   - 1 offsite backup

2. **Recovery Time Objective (RTO)**
   - Database: < 1 hour
   - Application: < 30 minutes
   - Full recovery: < 2 hours

3. **Recovery Point Objective (RPO)**
   - Database: < 1 hour (hourly backups)
   - Files: < 24 hours (daily backups)

### Disaster Recovery Plan

1. **Infrastructure failure**
   - Switch to backup server
   - Restore from latest backup
   - Update DNS records

2. **Data corruption**
   - Stop application
   - Restore from known good backup
   - Run integrity checks

3. **Security breach**
   - Isolate affected systems
   - Reset all credentials
   - Audit access logs
   - Notify users if necessary

## Support and Resources

### Documentation

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)

### Monitoring Services

- [Sentry](https://sentry.io/) - Error tracking
- [Prometheus](https://prometheus.io/) - Metrics collection
- [Grafana](https://grafana.com/) - Metrics visualization
- [Datadog](https://www.datadoghq.com/) - Full-stack monitoring

### Support Channels

- GitHub Issues: https://github.com/your-org/bdc/issues
- Email: support@yourdomain.com
- Slack: #bdc-support
- Documentation: https://docs.yourdomain.com