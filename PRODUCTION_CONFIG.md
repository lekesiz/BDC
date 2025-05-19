# BDC Production Configuration Guide

## Overview
This guide provides comprehensive instructions for configuring the BDC application for production deployment.

## Server Requirements

### Minimum Hardware
- **CPU**: 4 cores
- **RAM**: 8GB
- **Storage**: 50GB SSD
- **Network**: 100Mbps

### Recommended Hardware
- **CPU**: 8+ cores
- **RAM**: 16GB+
- **Storage**: 100GB+ SSD
- **Network**: 1Gbps

### Software Requirements
- **OS**: Ubuntu 20.04 LTS or newer
- **Python**: 3.9+
- **Node.js**: 16+
- **PostgreSQL**: 13+
- **Redis**: 6+
- **Nginx**: Latest stable
- **Docker**: 20.10+ (optional)

## Production Environment Setup

### 1. System Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql redis-server nginx git curl

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2. PostgreSQL Configuration
```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE bdc_production;
CREATE USER bdc_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE bdc_production TO bdc_user;
\q

# Configure PostgreSQL for production
sudo nano /etc/postgresql/13/main/postgresql.conf
```

Add these settings:
```
# Performance tuning
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
max_connections = 200
```

### 3. Redis Configuration
```bash
sudo nano /etc/redis/redis.conf
```

Update these settings:
```
# Persistence
save 900 1
save 300 10
save 60 10000

# Security
requirepass your_redis_password

# Memory
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 4. Application Deployment

#### Backend Deployment
```bash
# Create application directory
sudo mkdir -p /var/www/bdc
sudo chown $USER:$USER /var/www/bdc

# Clone repository
cd /var/www/bdc
git clone <repository-url> .

# Set up Python environment
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create production config
cp .env.example .env.production
nano .env.production
```

Production environment variables:
```
# Flask
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=<generate-secure-key>

# Database
DATABASE_URL=postgresql://bdc_user:secure_password@localhost/bdc_production
SQLALCHEMY_DATABASE_URI=${DATABASE_URL}

# Redis
REDIS_URL=redis://:your_redis_password@localhost:6379/0

# JWT
JWT_SECRET_KEY=<generate-secure-jwt-key>
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
LOG_TO_STDOUT=false

# Security
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
WTF_CSRF_ENABLED=true

# Rate Limiting
RATELIMIT_STORAGE_URL=redis://:your_redis_password@localhost:6379/1

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/var/www/bdc/uploads
```

#### Frontend Deployment
```bash
cd /var/www/bdc/client

# Install dependencies
npm install

# Create production environment
cp .env.example .env.production
nano .env.production
```

Frontend environment variables:
```
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production
VITE_SENTRY_DSN=your-sentry-dsn
VITE_GOOGLE_ANALYTICS_ID=your-ga-id
```

Build for production:
```bash
npm run build
```

### 5. Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/bdc
```

Nginx configuration:
```nginx
# API server
upstream bdc_api {
    server localhost:5000;
}

# Main server block
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS server block
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend files
    root /var/www/bdc/client/dist;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API routes
    location /api {
        proxy_pass http://bdc_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # WebSocket support
    location /socket.io {
        proxy_pass http://bdc_api;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Static files
    location /static {
        alias /var/www/bdc/client/dist/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Uploads
    location /uploads {
        alias /var/www/bdc/uploads;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    gzip_disable "MSIE [1-6]\.";
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/bdc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. SystemD Service
```bash
sudo nano /etc/systemd/system/bdc.service
```

Service configuration:
```ini
[Unit]
Description=BDC Application
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/bdc/server
Environment="PATH=/var/www/bdc/server/venv/bin"
ExecStart=/var/www/bdc/server/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind 0.0.0.0:5000 \
    --timeout 120 \
    --log-level info \
    --log-file /var/log/bdc/gunicorn.log \
    --access-logfile /var/log/bdc/access.log \
    --error-logfile /var/log/bdc/error.log \
    wsgi:app

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
# Create log directory
sudo mkdir -p /var/log/bdc
sudo chown www-data:www-data /var/log/bdc

# Enable and start service
sudo systemctl enable bdc
sudo systemctl start bdc
sudo systemctl status bdc
```

### 7. SSL Certificate
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### 8. Firewall Configuration
```bash
# Allow necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 9. Monitoring Setup

#### Log Rotation
```bash
sudo nano /etc/logrotate.d/bdc
```

```
/var/log/bdc/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload bdc >/dev/null 2>&1
    endscript
}
```

#### Application Monitoring
```bash
# Install monitoring tools
pip install flower  # For Celery monitoring
pip install prometheus-flask-exporter  # For metrics

# Add to your Flask app
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)
```

### 10. Backup Configuration
```bash
# Create backup script
sudo nano /opt/bdc-backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/bdc"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -U bdc_user bdc_production | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/bdc/uploads

# Keep only last 7 days
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

# Optional: Upload to S3
# aws s3 sync $BACKUP_DIR s3://your-backup-bucket/bdc/
```

Make it executable and schedule:
```bash
sudo chmod +x /opt/bdc-backup.sh
sudo crontab -e
# Add: 0 3 * * * /opt/bdc-backup.sh
```

## Performance Tuning

### 1. Database Optimization
```sql
-- Create indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_beneficiaries_tenant ON beneficiaries(tenant_id);
CREATE INDEX idx_evaluations_beneficiary ON evaluations(beneficiary_id);

-- Analyze tables
ANALYZE;
```

### 2. Redis Optimization
```python
# In your Flask app
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Use caching
@cache.cached(timeout=300)
def expensive_function():
    return compute_something()
```

### 3. Frontend Optimization
```javascript
// Use the optimized Vite config
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import compression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [
    react(),
    compression({
      algorithm: 'gzip',
      ext: '.gz'
    }),
    compression({
      algorithm: 'brotliCompress',
      ext: '.br'
    })
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          utils: ['axios', 'date-fns', 'lodash-es']
        }
      }
    }
  }
});
```

## Security Hardening

### 1. Application Security
```python
# Add security headers
from flask_talisman import Talisman

Talisman(app, force_https=True)

# Rate limiting
from flask_limiter import Limiter
limiter = Limiter(
    app,
    key_func=lambda: get_remote_address(),
    default_limits=["200 per day", "50 per hour"]
)

# CORS configuration
from flask_cors import CORS
CORS(app, origins=['https://yourdomain.com'])
```

### 2. Server Security
```bash
# Disable root SSH
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Configure fail2ban
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Maintenance

### 1. Regular Updates
```bash
# Monthly maintenance script
#!/bin/bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /var/www/bdc/server
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Update Node packages
cd /var/www/bdc/client
npm update
npm audit fix

# Restart services
sudo systemctl restart bdc
sudo systemctl restart nginx
```

### 2. Monitoring Checklist
- Check disk space
- Monitor CPU/Memory usage
- Review error logs
- Check backup status
- Verify SSL certificate
- Test critical paths

## Troubleshooting

### Common Issues

1. **502 Bad Gateway**
   - Check if BDC service is running
   - Review Gunicorn logs
   - Verify Nginx proxy settings

2. **Database Connection Errors**
   - Check PostgreSQL status
   - Verify connection string
   - Check firewall rules

3. **Redis Connection Issues**
   - Verify Redis is running
   - Check authentication
   - Monitor memory usage

4. **Slow Performance**
   - Check database queries
   - Monitor server resources
   - Review caching strategy

## Support Contacts

- **System Administrator**: admin@yourdomain.com
- **Database Admin**: dba@yourdomain.com
- **Emergency**: +1-xxx-xxx-xxxx

---

This configuration guide should be customized based on your specific requirements and infrastructure setup.