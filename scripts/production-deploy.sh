#!/bin/bash

# Production deployment script for BDC application
set -e

DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@your-domain.com"}
ENVIRONMENT=${3:-"production"}

echo "🚀 Starting BDC production deployment..."
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo "Environment: $ENVIRONMENT"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root for security reasons"
   exit 1
fi

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create application directory
APP_DIR="/opt/bdc"
echo "📁 Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Clone or update repository
if [ -d "$APP_DIR/.git" ]; then
    echo "🔄 Updating existing repository..."
    cd $APP_DIR
    git pull origin main
else
    echo "📥 Cloning repository..."
    git clone https://github.com/your-org/bdc.git $APP_DIR
    cd $APP_DIR
fi

# Copy production environment file
if [ ! -f ".env.production" ]; then
    echo "📝 Creating production environment file..."
    cp .env.production .env.production.bak 2>/dev/null || true
    
    # Generate secure passwords
    DB_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    SECRET_KEY=$(openssl rand -base64 64)
    JWT_SECRET_KEY=$(openssl rand -base64 64)
    
    # Create environment file
    cat > .env.production << EOF
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=bdc_db
DB_USER=bdc_user
DB_PASSWORD=$DB_PASSWORD

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=$REDIS_PASSWORD

# Security
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
JWT_ACCESS_TOKEN_EXPIRES=900
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Application
FLASK_ENV=production
CORS_ORIGINS=https://$DOMAIN
DOMAIN=$DOMAIN
ADMIN_EMAIL=$EMAIL

# SMTP (configure with your provider)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Rate Limiting
RATE_LIMIT_STORAGE_URL=redis://redis:6379/1
RATELIMIT_DEFAULT=1000 per hour

# Celery
CELERY_BROKER_URL=redis://redis:6379/2
CELERY_RESULT_BACKEND=redis://redis:6379/3

# File Upload
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=/app/uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/app.log
EOF

    echo "✅ Environment file created with secure passwords"
    echo "📝 Please review and update .env.production with your specific settings"
else
    echo "✅ Environment file already exists"
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p uploads logs backups

# Set up SSL certificate
echo "🔒 Setting up SSL certificate..."
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    echo "📜 Obtaining SSL certificate for $DOMAIN..."
    sudo ./scripts/ssl-setup.sh $DOMAIN $EMAIL
else
    echo "✅ SSL certificate already exists for $DOMAIN"
fi

# Build and start services
echo "🏗️ Building Docker images..."
docker-compose -f docker-compose.production.yml build

echo "🚀 Starting services..."
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are healthy
echo "🏥 Checking service health..."
MAX_ATTEMPTS=10
ATTEMPT=1

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U bdc_user -d bdc_db > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    echo "⏳ Waiting for PostgreSQL... (attempt $ATTEMPT/$MAX_ATTEMPTS)"
    sleep 10
    ATTEMPT=$((ATTEMPT + 1))
done

if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
    echo "❌ PostgreSQL failed to start within timeout"
    exit 1
fi

# Initialize database
echo "🗄️ Initializing database..."
docker-compose -f docker-compose.production.yml exec -T app flask db upgrade

# Create admin user if it doesn't exist
echo "👤 Setting up admin user..."
docker-compose -f docker-compose.production.yml exec -T app python -c "
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    admin = User.query.filter_by(email='$EMAIL').first()
    if not admin:
        admin = User(
            email='$EMAIL',
            username='admin',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print('Admin user created with email: $EMAIL and password: admin123')
        print('Please change the password after first login!')
    else:
        print('Admin user already exists')
"

# Setup monitoring
echo "📊 Setting up monitoring..."
if [ ! -d "/opt/monitoring" ]; then
    ./scripts/monitoring-setup.sh
    cd /opt/monitoring
    docker-compose -f docker-compose.monitoring.yml up -d
    cd $APP_DIR
else
    echo "✅ Monitoring already configured"
fi

# Setup backups
echo "💾 Setting up automated backups..."
CRON_JOB="0 2 * * * $APP_DIR/scripts/backup.sh"
if ! crontab -l 2>/dev/null | grep -q "$APP_DIR/scripts/backup.sh"; then
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Daily backup cron job added"
else
    echo "✅ Backup cron job already exists"
fi

# Final health check
echo "🏥 Performing final health check..."
sleep 10

if curl -f "https://$DOMAIN/health" > /dev/null 2>&1; then
    echo "✅ Application is healthy and accessible"
else
    echo "⚠️ Application health check failed, but deployment completed"
    echo "Please check the logs: docker-compose -f docker-compose.production.yml logs"
fi

# Display deployment summary
echo ""
echo "🎉 BDC Production Deployment Complete!"
echo "========================================"
echo "🌐 Application URL: https://$DOMAIN"
echo "👤 Admin Email: $EMAIL"
echo "🔑 Admin Password: admin123 (CHANGE THIS!)"
echo ""
echo "📊 Monitoring URLs:"
echo "   Prometheus: http://$DOMAIN:9090"
echo "   Grafana: http://$DOMAIN:3000 (admin/admin123)"
echo "   Alertmanager: http://$DOMAIN:9093"
echo ""
echo "📋 Important Next Steps:"
echo "1. Change admin password immediately"
echo "2. Configure SMTP settings in .env.production"
echo "3. Review and customize monitoring alerts"
echo "4. Test backup and restore procedures"
echo "5. Configure your DNS and firewall settings"
echo ""
echo "📚 For detailed documentation, see: PRODUCTION_DEPLOYMENT.md"
echo ""
echo "🔧 Useful Commands:"
echo "   View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "   Restart services: docker-compose -f docker-compose.production.yml restart"
echo "   Update application: git pull && docker-compose -f docker-compose.production.yml up -d --build"
echo "   Manual backup: ./scripts/backup.sh"
echo ""
echo "✨ Happy deploying!"