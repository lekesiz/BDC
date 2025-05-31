# BDC Production Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying the BDC (Başkent Development Center) application to production.

## Prerequisites
- Ubuntu 20.04+ or similar Linux distribution
- Docker & Docker Compose
- Git
- Domain name with DNS configured
- SSL certificate (Let's Encrypt recommended)

## Quick Start

### 1. Server Setup
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
```

### 2. Application Deployment
```bash
# Clone repository
git clone https://github.com/your-org/bdc.git
cd bdc

# Copy and configure environment
cp .env.production.example .env.production
nano .env.production  # Edit with your settings

# SSL Setup (replace with your domain)
sudo ./scripts/ssl-setup.sh your-domain.com admin@your-domain.com

# Deploy application
docker-compose -f docker-compose.production.yml up -d

# Initialize database
docker-compose -f docker-compose.production.yml exec app flask db upgrade
docker-compose -f docker-compose.production.yml exec app python seed_database.py
```

### 3. Monitoring Setup
```bash
# Setup monitoring stack
./scripts/monitoring-setup.sh

# Start monitoring
cd /opt/monitoring
docker-compose -f docker-compose.monitoring.yml up -d
```

## Configuration Files

### Environment Variables (.env.production)
```bash
# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=bdc_db
DB_USER=bdc_user
DB_PASSWORD=your-secure-password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET_KEY=your-jwt-secret

# Application
FLASK_ENV=production
CORS_ORIGINS=https://your-domain.com
```

### SSL Configuration
The application includes automatic SSL setup using Let's Encrypt:
```bash
./scripts/ssl-setup.sh your-domain.com admin@your-domain.com
```

## Docker Deployment

### Using Docker Compose
```bash
# Production deployment
docker-compose -f docker-compose.production.yml up -d

# View logs
docker-compose -f docker-compose.production.yml logs -f

# Update application
git pull
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

### Using Docker Swarm
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.production.yml bdc
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (v1.20+)
- kubectl configured
- Ingress controller (nginx recommended)

### Deployment Steps
```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets (edit with your values first)
kubectl apply -f k8s/secrets.yaml

# Create configmap
kubectl apply -f k8s/configmap.yaml

# Deploy database
kubectl apply -f k8s/postgres-deployment.yaml

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml

# Deploy application
kubectl apply -f k8s/bdc-deployment.yaml

# Check status
kubectl get pods -n bdc-production
```

## Monitoring & Logging

### Prometheus & Grafana
- Prometheus: http://your-domain.com:9090
- Grafana: http://your-domain.com:3000 (admin/admin123)
- Alertmanager: http://your-domain.com:9093

### Health Checks
```bash
# Application health
curl https://your-domain.com/health

# Database health
docker exec bdc-postgres-prod pg_isready

# Redis health
docker exec bdc-redis-prod redis-cli ping
```

## Backup & Recovery

### Automated Backups
```bash
# Setup daily backups
sudo crontab -e
# Add: 0 2 * * * /path/to/bdc/scripts/backup.sh
```

### Manual Backup
```bash
./scripts/backup.sh
```

### Restore from Backup
```bash
# Stop application
docker-compose -f docker-compose.production.yml down

# Restore database
gunzip < backup_file.sql.gz | docker exec -i bdc-postgres-prod psql -U bdc_user -d bdc_db

# Restore files
tar -xzf files_backup.tar.gz -C /path/to/uploads

# Start application
docker-compose -f docker-compose.production.yml up -d
```

## Security Considerations

### Network Security
- Use firewall (ufw recommended)
- Restrict database access
- Enable fail2ban for SSH protection

### Application Security
- JWT tokens with expiration
- Rate limiting enabled
- CORS properly configured
- Security headers implemented

### SSL/TLS
- Strong cipher suites
- HSTS enabled
- Certificate auto-renewal

## Performance Optimization

### Database
- Connection pooling enabled
- Query optimization
- Regular VACUUM and ANALYZE

### Caching
- Redis for session storage
- Static file caching
- API response caching

### Load Balancing
For high availability, use multiple app instances:
```yaml
services:
  app:
    deploy:
      replicas: 3
```

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker-compose -f docker-compose.production.yml logs app

# Check dependencies
docker-compose -f docker-compose.production.yml ps
```

#### Database Connection Issues
```bash
# Test connection
docker exec bdc-app-prod python -c "from app import db; print(db.engine.execute('SELECT 1').scalar())"
```

#### SSL Certificate Issues
```bash
# Renew certificate
certbot renew --dry-run

# Check certificate status
openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Check database performance
docker exec bdc-postgres-prod psql -U bdc_user -d bdc_db -c "SELECT * FROM pg_stat_activity;"
```

## Maintenance

### Regular Tasks
- Monitor disk space
- Review logs weekly
- Update dependencies monthly
- Security patches as needed

### Updates
```bash
# Update application
git pull
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Update database schema
docker-compose -f docker-compose.production.yml exec app flask db upgrade
```

## CI/CD Pipeline

The application includes GitHub Actions workflow for automated deployment:
- Runs tests on pull requests
- Builds Docker images on main branch
- Deploys to production automatically

Configure deployment by setting up these secrets in GitHub:
- `DOCKER_REGISTRY_TOKEN`
- `PRODUCTION_SERVER_SSH_KEY`
- `PRODUCTION_SERVER_HOST`

## Support

For production support:
1. Check application logs
2. Review monitoring dashboards
3. Check system resources
4. Contact development team if needed

## Checklist

- [ ] Server prepared and secured
- [ ] Domain and DNS configured
- [ ] SSL certificate installed
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] Application deployed
- [ ] Monitoring setup
- [ ] Backup configured
- [ ] Health checks verified
- [ ] Performance optimized
- [ ] Security hardened

## Version Information
- Application Version: 1.0.0
- Docker Image: bdc:latest
- Database: PostgreSQL 15
- Cache: Redis 7
- Web Server: Nginx
- WSGI Server: Gunicorn