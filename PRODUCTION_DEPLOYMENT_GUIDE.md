# BDC Production Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the BDC (Business Development Center) application to production environments. The application includes a React frontend, Flask backend, PostgreSQL database, Redis cache, and comprehensive monitoring stack.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Docker Deployment](#docker-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Monitoring Setup](#monitoring-setup)
6. [SSL/TLS Configuration](#ssltls-configuration)
7. [Database Management](#database-management)
8. [Backup and Recovery](#backup-and-recovery)
9. [Security Configuration](#security-configuration)
10. [Troubleshooting](#troubleshooting)
11. [Maintenance](#maintenance)

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: Minimum 4 cores (8+ recommended for production)
- **Memory**: Minimum 8GB RAM (16GB+ recommended for production)
- **Storage**: Minimum 100GB SSD (500GB+ recommended for production)
- **Network**: Static IP address and domain name

### Software Requirements

```bash
# Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install docker-compose-plugin

# Kubernetes (if using K8s deployment)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Additional tools
sudo apt-get update
sudo apt-get install -y git curl wget nginx certbot
```

### Domain and DNS Setup

1. Register a domain name (e.g., `yourdomain.com`)
2. Set up DNS records:
   ```
   A    yourdomain.com        -> your-server-ip
   A    api.yourdomain.com    -> your-server-ip
   A    monitoring.yourdomain.com -> your-server-ip
   ```

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/bdc-application.git
cd bdc-application
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.production.template .env.production

# Edit configuration
nano .env.production
```

**Required Configuration Variables:**

```bash
# Database
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgresql://bdc_user:your-secure-password@postgres:5432/bdc_production

# Application Security
SECRET_KEY=your-very-long-and-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# External Services
OPENAI_API_KEY=your-openai-key
SENTRY_DSN=your-sentry-dsn
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret

# Domain Configuration
VITE_API_URL=https://api.yourdomain.com
FRONTEND_URL=https://yourdomain.com
```

### 3. SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificates
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com

# Certificates will be stored in /etc/letsencrypt/live/
```

#### Option B: Custom Certificates

```bash
# Create SSL directory
sudo mkdir -p /etc/ssl/bdc

# Copy your certificates
sudo cp your-cert.pem /etc/ssl/bdc/cert.pem
sudo cp your-key.pem /etc/ssl/bdc/key.pem

# Set permissions
sudo chmod 600 /etc/ssl/bdc/key.pem
sudo chmod 644 /etc/ssl/bdc/cert.pem
```

## Docker Deployment

### 1. Production Deployment with Docker Compose

```bash
# Build and deploy
./scripts/deploy-production.sh production

# Or manually:
docker-compose -f docker-compose.production.yml up -d
```

### 2. Verify Deployment

```bash
# Check container status
docker-compose -f docker-compose.production.yml ps

# Check logs
docker-compose -f docker-compose.production.yml logs -f backend
docker-compose -f docker-compose.production.yml logs -f frontend

# Health checks
curl https://yourdomain.com/health
curl https://api.yourdomain.com/health
```

### 3. Scaling Services

```bash
# Scale backend
docker-compose -f docker-compose.production.yml up -d --scale backend=3

# Scale frontend
docker-compose -f docker-compose.production.yml up -d --scale frontend=2
```

## Kubernetes Deployment

### 1. Cluster Setup

```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Create namespace
kubectl apply -f k8s/production/namespace.yaml
```

### 2. Configure Secrets

```bash
# Edit secrets file with your actual values
nano k8s/production/secrets.yaml

# Apply secrets
kubectl apply -f k8s/production/secrets.yaml
```

### 3. Deploy Application

```bash
# Deploy all components
kubectl apply -f k8s/production/

# Check deployment status
kubectl get deployments -n bdc-production
kubectl get pods -n bdc-production
kubectl get services -n bdc-production
```

### 4. Configure Ingress

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Apply ingress configuration
kubectl apply -f k8s/production/ingress.yaml

# Get external IP
kubectl get ingress -n bdc-production
```

## Monitoring Setup

### 1. Deploy Monitoring Stack

```bash
# Create monitoring namespace
kubectl create namespace bdc-monitoring

# Deploy Prometheus
kubectl apply -f monitoring/prometheus/ -n bdc-monitoring

# Deploy Grafana
kubectl apply -f monitoring/grafana/ -n bdc-monitoring

# Deploy AlertManager
kubectl apply -f monitoring/alertmanager/ -n bdc-monitoring
```

### 2. Access Monitoring Dashboards

- **Prometheus**: `http://monitoring.yourdomain.com:9090`
- **Grafana**: `http://monitoring.yourdomain.com:3000`
  - Default credentials: admin / (see GRAFANA_ADMIN_PASSWORD)
- **AlertManager**: `http://monitoring.yourdomain.com:9093`

### 3. Configure Alerts

```bash
# Edit alert rules
nano monitoring/prometheus/rules/bdc-alerts.yml

# Update AlertManager configuration
nano monitoring/alertmanager/alertmanager.yml

# Apply changes
kubectl apply -f monitoring/prometheus/rules/ -n bdc-monitoring
kubectl rollout restart deployment/prometheus -n bdc-monitoring
```

## Database Management

### 1. Database Initialization

```bash
# Run initial migration
kubectl exec -it deployment/bdc-backend -n bdc-production -- flask db upgrade

# Create admin user
kubectl exec -it deployment/bdc-backend -n bdc-production -- python create_admin.py
```

### 2. Database Backup

```bash
# Manual backup
kubectl exec deployment/postgres -n bdc-production -- pg_dump -U bdc_user bdc_production > backup-$(date +%Y%m%d).sql

# Automated backup (runs daily)
kubectl create -f k8s/production/backup-cronjob.yaml
```

### 3. Database Restore

```bash
# Restore from backup
kubectl exec -i deployment/postgres -n bdc-production -- psql -U bdc_user -d bdc_production < backup-20240101.sql
```

## Security Configuration

### 1. Network Security

```bash
# Apply network policies
kubectl apply -f k8s/production/network-policies.yaml

# Configure firewall (Ubuntu/Debian)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

### 2. Application Security

- **HTTPS Enforcement**: All traffic redirected to HTTPS
- **Security Headers**: CSP, HSTS, X-Frame-Options configured
- **Rate Limiting**: API endpoints protected with rate limits
- **Authentication**: JWT-based authentication with secure tokens
- **Input Validation**: All inputs validated and sanitized

### 3. Regular Security Updates

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Update Docker images
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

# Security scanning
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image bdc-backend:latest
```

## Backup and Recovery

### 1. Automated Backups

The system includes automated backup for:
- **Database**: Daily PostgreSQL dumps to S3
- **File Uploads**: Daily sync to S3
- **Configuration**: Weekly backup of environment configs

### 2. Disaster Recovery Plan

#### RTO (Recovery Time Objective): 4 hours
#### RPO (Recovery Point Objective): 24 hours

**Recovery Steps:**

1. **Infrastructure Recovery**:
   ```bash
   # Deploy to new infrastructure
   ./scripts/deploy-production.sh production
   ```

2. **Database Recovery**:
   ```bash
   # Restore latest backup
   aws s3 cp s3://your-backup-bucket/database/latest.sql ./
   kubectl exec -i deployment/postgres -n bdc-production -- psql -U bdc_user -d bdc_production < latest.sql
   ```

3. **File Recovery**:
   ```bash
   # Restore file uploads
   aws s3 sync s3://your-backup-bucket/files/ /path/to/uploads/
   ```

### 3. Backup Verification

```bash
# Test backup restoration (automated weekly)
./scripts/test-backup-restore.sh
```

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

```bash
# Check logs
kubectl logs deployment/bdc-backend -n bdc-production
kubectl logs deployment/bdc-frontend -n bdc-production

# Check resource usage
kubectl top pods -n bdc-production

# Check configuration
kubectl get configmap bdc-backend-config -n bdc-production -o yaml
```

#### 2. Database Connection Issues

```bash
# Test database connectivity
kubectl exec deployment/bdc-backend -n bdc-production -- python -c "
import psycopg2
conn = psycopg2.connect('postgresql://bdc_user:password@postgres:5432/bdc_production')
print('Connection successful')
"

# Check PostgreSQL logs
kubectl logs deployment/postgres -n bdc-production
```

#### 3. SSL/TLS Issues

```bash
# Verify certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check certificate expiration
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates
```

#### 4. Performance Issues

```bash
# Check resource usage
kubectl top pods -n bdc-production
kubectl top nodes

# Check database performance
kubectl exec deployment/postgres -n bdc-production -- psql -U bdc_user -d bdc_production -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
"
```

### Monitoring and Alerts

#### Key Metrics to Monitor

1. **Application Metrics**:
   - Response time (< 2 seconds)
   - Error rate (< 1%)
   - Throughput (requests/second)

2. **Infrastructure Metrics**:
   - CPU usage (< 80%)
   - Memory usage (< 85%)
   - Disk usage (< 90%)
   - Network latency

3. **Database Metrics**:
   - Connection count
   - Query performance
   - Database size
   - Replication lag (if applicable)

#### Alert Thresholds

- **Critical**: Service down, error rate > 5%, response time > 10s
- **Warning**: High resource usage, error rate > 1%, response time > 2s
- **Info**: Deployment notifications, backup status

## Maintenance

### Regular Maintenance Tasks

#### Daily
- Monitor system health and alerts
- Review application logs for errors
- Check backup completion
- Verify SSL certificate status

#### Weekly
- Update system packages
- Review performance metrics
- Test backup restoration
- Security scan of Docker images

#### Monthly
- Review and update dependencies
- Performance optimization review
- Disaster recovery plan testing
- Security audit and penetration testing

### Scaling Guidelines

#### Horizontal Scaling

```bash
# Scale backend based on CPU/Memory usage
kubectl scale deployment bdc-backend --replicas=5 -n bdc-production

# Configure HPA for automatic scaling
kubectl apply -f k8s/production/hpa.yaml
```

#### Vertical Scaling

```bash
# Update resource requests/limits
kubectl patch deployment bdc-backend -n bdc-production -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "bdc-backend",
          "resources": {
            "requests": {"memory": "1Gi", "cpu": "1000m"},
            "limits": {"memory": "2Gi", "cpu": "2000m"}
          }
        }]
      }
    }
  }
}'
```

### Performance Optimization

1. **Database Optimization**:
   - Regular VACUUM and ANALYZE
   - Index optimization
   - Connection pooling
   - Query optimization

2. **Application Optimization**:
   - Caching strategies
   - Code optimization
   - Asset compression
   - CDN integration

3. **Infrastructure Optimization**:
   - Load balancing
   - Auto-scaling
   - Resource allocation
   - Network optimization

## Support and Contact

For technical support and questions:

- **Documentation**: [Internal Documentation Portal]
- **Issues**: Create GitHub issue in the repository
- **Emergency**: Contact on-call engineer via PagerDuty
- **Email**: devops@yourdomain.com

---

**Last Updated**: 2025-05-30
**Version**: 1.0.0
**Maintainer**: DevOps Team