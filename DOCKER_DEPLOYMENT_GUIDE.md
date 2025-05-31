# 🐳 BDC Docker Portable Deployment Guide

## Overview

This guide explains how to deploy the BDC (Beneficiary Development Center) application using Docker on any system that supports Docker. The deployment is designed to be completely portable and can run on local machines, cloud servers, or any Docker-compatible environment.

## 🚀 Quick Start

### Prerequisites

- Docker 20.10+ with Compose V2
- At least 4GB RAM available
- At least 10GB free disk space
- Internet connection for initial setup

### 1. Clone or Copy the Project

```bash
# If using git
git clone <repository-url> bdc-app
cd bdc-app

# Or extract the project files to a directory
```

### 2. Configure Environment

```bash
# Copy the environment template
cp .env.production.template .env

# Edit the environment file with your settings
nano .env  # or use your preferred editor
```

### 3. Deploy

```bash
# Basic deployment
./scripts/docker-deploy.sh

# With monitoring (Prometheus + Grafana)
./scripts/docker-deploy.sh --monitoring

# Development mode
./scripts/docker-deploy.sh --mode development
```

### 4. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **Grafana** (if monitoring enabled): http://localhost:3000

## 📋 Detailed Configuration

### Environment Variables

The `.env` file contains all configuration options. Key variables to configure:

#### Required (Security Critical)
```bash
# Database credentials
DATABASE_PASSWORD=your-very-secure-db-password-here
REDIS_PASSWORD=your-secure-redis-password-here

# Application secrets
SECRET_KEY=your-super-secret-flask-key-change-this-32-chars-minimum
JWT_SECRET_KEY=your-jwt-secret-key-change-this-as-well-32-chars-min
```

#### Optional Services
```bash
# Email configuration
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password

# OpenAI integration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Monitoring
GRAFANA_ADMIN_PASSWORD=your-secure-grafana-password
```

#### Domain Configuration
```bash
# For production deployment
VITE_API_URL=https://yourdomain.com/api
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SSL_DOMAIN=yourdomain.com
```

### Port Configuration

Default ports can be customized in `.env`:

```bash
# Frontend
FRONTEND_HTTP_PORT=80
FRONTEND_HTTPS_PORT=443

# Backend
BACKEND_PORT=5000

# Database
DATABASE_PORT=5432
REDIS_PORT=6379

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

## 🔧 Deployment Options

### Basic Production Deployment

```bash
# Standard production deployment
./scripts/docker-deploy.sh
```

Features included:
- PostgreSQL database
- Redis cache
- Flask backend
- React frontend with Nginx
- Health checks
- Security hardening
- Resource limits

### Development Deployment

```bash
# Development mode with hot reload
./scripts/docker-deploy.sh --mode development
```

Additional features:
- Hot reload for both frontend and backend
- Development debugging tools
- Relaxed security settings
- Development dependencies

### Full Monitoring Stack

```bash
# Production with comprehensive monitoring
./scripts/docker-deploy.sh --monitoring
```

Additional services:
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **Alerting**: Built-in alert rules

### Custom Deployment

```bash
# Force rebuild and recreate everything
./scripts/docker-deploy.sh --force-recreate --monitoring

# Skip building (use existing images)
./scripts/docker-deploy.sh --skip-build

# Dry run (see what would be done)
./scripts/docker-deploy.sh --dry-run --monitoring
```

## 📁 Data Persistence

All application data is stored in the `./data/` directory:

```
data/
├── postgres/          # Database files
├── redis/            # Redis persistence
├── uploads/          # User uploaded files
├── logs/             # Application logs
├── nginx-logs/       # Web server logs
├── prometheus/       # Metrics data
└── grafana/          # Dashboard configurations
```

### Backup Strategy

```bash
# Backup all data
tar -czf bdc-backup-$(date +%Y%m%d).tar.gz data/

# Backup only database
docker compose --file docker-compose.portable.yml exec postgres pg_dump -U bdc_user bdc_production > backup.sql

# Restore database
docker compose --file docker-compose.portable.yml exec -T postgres psql -U bdc_user bdc_production < backup.sql
```

## 🔒 Security Considerations

### Production Security Checklist

- [ ] **Change all default passwords** in `.env`
- [ ] **Configure SSL certificates** for HTTPS
- [ ] **Set proper CORS origins** for your domain
- [ ] **Use strong secrets** (32+ characters)
- [ ] **Restrict database access** to internal network only
- [ ] **Enable firewall** on host system
- [ ] **Regular security updates** of base images
- [ ] **Monitor access logs** for suspicious activity

### SSL/HTTPS Setup

For production with SSL:

1. **Obtain SSL certificates** (Let's Encrypt, CloudFlare, etc.)
2. **Place certificates** in `./ssl/` directory:
   ```
   ssl/
   ├── cert.pem
   └── key.pem
   ```
3. **Update environment**:
   ```bash
   SSL_DOMAIN=yourdomain.com
   VITE_API_URL=https://yourdomain.com/api
   ```

### Network Security

The deployment uses two networks:
- **bdc_internal**: Database and cache (isolated)
- **bdc_external**: Frontend and API (internet-facing)

## 📊 Monitoring and Maintenance

### Health Checks

All services include health checks:
- **Database**: Connection and query tests
- **Cache**: Redis ping tests
- **Backend**: API endpoint tests
- **Frontend**: HTTP response tests

### Monitoring with Grafana

When monitoring is enabled:

1. **Access Grafana**: http://localhost:3000
2. **Default credentials**: admin / (see GRAFANA_ADMIN_PASSWORD in .env)
3. **Pre-configured dashboards** for:
   - Application performance
   - Database metrics
   - System resources
   - Error tracking

### Log Management

```bash
# View all logs
docker compose --file docker-compose.portable.yml logs -f

# View specific service logs
docker compose --file docker-compose.portable.yml logs -f backend

# View recent logs only
docker compose --file docker-compose.portable.yml logs --tail=100 -f
```

## 🛠️ Troubleshooting

### Common Issues

#### Services Not Starting

```bash
# Check service status
docker compose --file docker-compose.portable.yml ps

# Check specific service logs
docker compose --file docker-compose.portable.yml logs backend

# Restart specific service
docker compose --file docker-compose.portable.yml restart backend
```

#### Database Connection Issues

```bash
# Check database health
docker compose --file docker-compose.portable.yml exec postgres pg_isready -U bdc_user

# Access database directly
docker compose --file docker-compose.portable.yml exec postgres psql -U bdc_user bdc_production
```

#### Frontend Build Issues

```bash
# Rebuild frontend only
docker compose --file docker-compose.portable.yml build frontend

# Force rebuild without cache
docker compose --file docker-compose.portable.yml build --no-cache frontend
```

#### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER ./data/
chmod -R 755 ./data/
chmod 700 ./data/postgres  # PostgreSQL requires restrictive permissions
```

### Performance Tuning

#### Resource Limits

Adjust in `.env`:
```bash
# Backend resources
BACKEND_MEMORY_LIMIT=2G
BACKEND_CPU_LIMIT=2.0
GUNICORN_WORKERS=8

# Frontend resources
FRONTEND_MEMORY_LIMIT=1G
FRONTEND_CPU_LIMIT=1.0
```

#### Database Optimization

```bash
# Connect to database
docker compose --file docker-compose.portable.yml exec postgres psql -U bdc_user bdc_production

# Check database size
SELECT pg_size_pretty(pg_database_size('bdc_production'));

# Analyze query performance
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';
```

## 🔄 Updates and Maintenance

### Updating the Application

```bash
# Pull latest images
docker compose --file docker-compose.portable.yml pull

# Restart with new images
docker compose --file docker-compose.portable.yml up -d

# Or use the deployment script
./scripts/docker-deploy.sh --force-recreate
```

### Database Migrations

Database migrations run automatically on backend startup. To run manually:

```bash
docker compose --file docker-compose.portable.yml exec backend flask db upgrade
```

### Cleanup Old Data

```bash
# Remove unused Docker resources
docker system prune -a

# Remove old application logs (keep last 30 days)
find ./data/logs/ -name "*.log" -mtime +30 -delete

# Clean up old backups
find . -name "bdc-backup-*.tar.gz" -mtime +90 -delete
```

## 📞 Support and Help

### Get Help

```bash
# Show deployment script help
./scripts/docker-deploy.sh --help

# Check system requirements
docker --version
docker compose version

# Show service status
docker compose --file docker-compose.portable.yml ps
```

### Useful Commands

```bash
# Start services
docker compose --file docker-compose.portable.yml up -d

# Stop services
docker compose --file docker-compose.portable.yml down

# Restart services
docker compose --file docker-compose.portable.yml restart

# View real-time logs
docker compose --file docker-compose.portable.yml logs -f

# Execute commands in containers
docker compose --file docker-compose.portable.yml exec backend bash
docker compose --file docker-compose.portable.yml exec postgres psql -U bdc_user bdc_production

# Update and restart
docker compose --file docker-compose.portable.yml pull && docker compose --file docker-compose.portable.yml up -d
```

---

## 🎉 Success!

Once deployed successfully, you'll have a fully functional BDC application running with:

- ✅ **High availability** with health checks
- ✅ **Data persistence** with proper backups
- ✅ **Security hardening** with best practices
- ✅ **Performance optimization** with resource limits
- ✅ **Monitoring capabilities** (if enabled)
- ✅ **Easy maintenance** with simple commands

The application is now ready to serve users and can be accessed through your configured domain or localhost!