#!/bin/bash
# Advanced deployment script with staging and rollback support

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "info")
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        "warn")
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        "error")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac
}

# Parse command line arguments
ENVIRONMENT=${1:-"staging"}
TAG=${2:-"latest"}
ACTION=${3:-"deploy"}  # deploy, rollback, status
REPO="${GITHUB_REPOSITORY:-"ghcr.io/organization/bdc"}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(staging|production)$ ]]; then
    print_status "error" "Invalid environment: $ENVIRONMENT"
    echo "Usage: $0 [staging|production] [tag] [deploy|rollback|status]"
    exit 1
fi

# Load environment configuration
case $ENVIRONMENT in
    "staging")
        TARGET_HOST=${STAGING_HOST:-""}
        TARGET_USER=${STAGING_USER:-""}
        TARGET_DIR=${STAGING_DIR:-"/opt/bdc-staging"}
        COMPOSE_FILE="docker-compose.staging.yml"
        BACKUP_DIR="/opt/bdc-backups/staging"
        ;;
    "production")
        TARGET_HOST=${PROD_HOST:-""}
        TARGET_USER=${PROD_USER:-""}
        TARGET_DIR=${PROD_DIR:-"/opt/bdc"}
        COMPOSE_FILE="docker-compose.prod.yml"
        BACKUP_DIR="/opt/bdc-backups/production"
        ;;
esac

# Ensure required variables are set
if [ -z "$TARGET_HOST" ] || [ -z "$TARGET_USER" ]; then
    print_status "error" "Missing environment variables for $ENVIRONMENT"
    exit 1
fi

# Function to create backup
create_backup() {
    print_status "info" "Creating backup before deployment..."
    
    ssh "$TARGET_USER@$TARGET_HOST" "
        cd $TARGET_DIR
        
        # Create backup directory
        mkdir -p $BACKUP_DIR
        
        # Backup database
        docker-compose exec -T postgres pg_dump -U \$POSTGRES_USER \$POSTGRES_DB > $BACKUP_DIR/db_$(date +%Y%m%d_%H%M%S).sql
        
        # Save current image tags
        docker images | grep 'bdc-' | awk '{print \$1\":\"\$2}' > $BACKUP_DIR/images_$(date +%Y%m%d_%H%M%S).txt
        
        # Backup config files
        tar czf $BACKUP_DIR/config_$(date +%Y%m%d_%H%M%S).tar.gz .env docker-compose.yml
    "
    
    print_status "info" "Backup completed"
}

# Function to deploy
deploy() {
    print_status "info" "Starting deployment to $ENVIRONMENT with tag $TAG"
    
    # Create backup first
    create_backup
    
    # Copy docker-compose file
    print_status "info" "Copying docker-compose configuration..."
    scp "$COMPOSE_FILE" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/docker-compose.yml"
    
    # Deploy
    print_status "info" "Deploying application..."
    ssh "$TARGET_USER@$TARGET_HOST" "
        cd $TARGET_DIR
        
        # Set deployment timestamp
        export DEPLOY_TIME=$(date +%Y%m%d_%H%M%S)
        
        # Pull new images
        echo 'Pulling latest images...'
        docker pull $REPO/bdc-server:$TAG || exit 1
        docker pull $REPO/bdc-client:$TAG || exit 1
        
        # Stop current containers
        echo 'Stopping current containers...'
        docker-compose down
        
        # Run database migrations
        echo 'Running database migrations...'
        docker-compose run --rm backend flask db upgrade
        
        # Start new containers
        echo 'Starting new containers...'
        docker-compose up -d
        
        # Cleanup old images
        echo 'Cleaning up old images...'
        docker image prune -f
        
        # Wait for services to be ready
        echo 'Waiting for services to be ready...'
        sleep 20
        
        # Check health
        docker-compose ps
    "
    
    print_status "info" "Deployment completed"
    
    # Run health checks
    print_status "info" "Running health checks..."
    if [ -f "./scripts/health_check.sh" ]; then
        TARGET_URL="https://$TARGET_HOST"
        ./scripts/health_check.sh "$TARGET_URL"
    fi
}

# Function to rollback
rollback() {
    print_status "warn" "Starting rollback for $ENVIRONMENT"
    
    # Get last backup
    last_backup=$(ssh "$TARGET_USER@$TARGET_HOST" "ls -t $BACKUP_DIR/images_*.txt | head -1")
    
    if [ -z "$last_backup" ]; then
        print_status "error" "No backup found for rollback"
        exit 1
    fi
    
    print_status "info" "Rolling back to: $last_backup"
    
    ssh "$TARGET_USER@$TARGET_HOST" "
        cd $TARGET_DIR
        
        # Stop current containers
        docker-compose down
        
        # Restore database
        db_backup=\$(ls -t $BACKUP_DIR/db_*.sql | head -1)
        if [ -n \"\$db_backup\" ]; then
            echo 'Restoring database...'
            docker-compose run --rm postgres psql -U \$POSTGRES_USER \$POSTGRES_DB < \$db_backup
        fi
        
        # Restore config
        config_backup=\$(ls -t $BACKUP_DIR/config_*.tar.gz | head -1)
        if [ -n \"\$config_backup\" ]; then
            echo 'Restoring configuration...'
            tar xzf \$config_backup
        fi
        
        # Restore images and start containers
        echo 'Restoring containers...'
        docker-compose up -d
    "
    
    print_status "info" "Rollback completed"
}

# Function to check status
check_status() {
    print_status "info" "Checking status of $ENVIRONMENT deployment"
    
    ssh "$TARGET_USER@$TARGET_HOST" "
        cd $TARGET_DIR
        
        echo '=== Container Status ==='
        docker-compose ps
        
        echo -e '\n=== Container Logs (last 10 lines) ==='
        docker-compose logs --tail=10
        
        echo -e '\n=== System Resources ==='
        docker stats --no-stream
        
        echo -e '\n=== Disk Usage ==='
        df -h | grep -E '(Filesystem|docker|/opt/bdc)'
    "
}

# Main execution
case $ACTION in
    "deploy")
        deploy
        
        # If staging, optionally promote to production
        if [ "$ENVIRONMENT" == "staging" ]; then
            print_status "info" "Deployment to staging successful"
            echo -n "Promote to production? (y/N): "
            read -r promote
            if [[ $promote =~ ^[Yy]$ ]]; then
                print_status "info" "Promoting to production..."
                $0 production $TAG deploy
            fi
        fi
        ;;
    "rollback")
        rollback
        ;;
    "status")
        check_status
        ;;
    *)
        print_status "error" "Unknown action: $ACTION"
        echo "Usage: $0 [staging|production] [tag] [deploy|rollback|status]"
        exit 1
        ;;
esac