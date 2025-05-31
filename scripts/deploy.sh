#!/bin/bash
# Deployment script for BDC application

set -e

# Set default values
ENVIRONMENT=${1:-"development"}
TAG=${2:-"latest"}
GH_REPO=${GITHUB_REPOSITORY:-"organization/bdc"}
REPO="ghcr.io/${GH_REPO}"

# Configuration based on environment
if [ "$ENVIRONMENT" == "production" ]; then
    TARGET_HOST=${PROD_HOST:-""}
    TARGET_USER=${PROD_USER:-""}
    TARGET_DIR=${PROD_DIR:-"/opt/bdc"}
    COMPOSE_FILE="docker-compose.prod.yml"
elif [ "$ENVIRONMENT" == "development" ]; then
    TARGET_HOST=${DEV_HOST:-""}
    TARGET_USER=${DEV_USER:-""}
    TARGET_DIR=${DEV_DIR:-"/opt/bdc-dev"}
    COMPOSE_FILE="docker-compose.dev.yml"
elif [ "$ENVIRONMENT" == "staging" ]; then
    TARGET_HOST=${STAGING_HOST:-""}
    TARGET_USER=${STAGING_USER:-""}
    TARGET_DIR=${STAGING_DIR:-"/opt/bdc-staging"}
    COMPOSE_FILE="docker-compose.staging.yml"
else
    echo "Unknown environment: $ENVIRONMENT"
    echo "Usage: $0 [development|staging|production] [tag]"
    exit 1
fi

# Ensure host is specified
if [ -z "$TARGET_HOST" ]; then
    echo "Error: Target host not specified."
    echo "Set the appropriate environment variable (DEV_HOST, STAGING_HOST, or PROD_HOST)."
    exit 1
fi

echo "========================================="
echo "BDC Deployment"
echo "========================================="
echo "Environment: $ENVIRONMENT"
echo "Target Host: $TARGET_HOST"
echo "Target Dir: $TARGET_DIR"
echo "Tag: $TAG"
echo "========================================="

# Create target directory if it doesn't exist
ssh "$TARGET_USER@$TARGET_HOST" "mkdir -p $TARGET_DIR"

# Copy docker-compose file to target
echo "📋 Copying docker-compose file..."
scp "docker/$COMPOSE_FILE" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/docker-compose.yml"

# Copy environment file if it exists
if [ -f ".env.$ENVIRONMENT" ]; then
    echo "📋 Copying environment file..."
    scp ".env.$ENVIRONMENT" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/.env"
fi

# Copy nginx config if exists
if [ -f "nginx/$ENVIRONMENT.conf" ]; then
    echo "📋 Copying nginx configuration..."
    ssh "$TARGET_USER@$TARGET_HOST" "mkdir -p $TARGET_DIR/nginx"
    scp "nginx/$ENVIRONMENT.conf" "$TARGET_USER@$TARGET_HOST:$TARGET_DIR/nginx/"
fi

# SSH to target and update the application
echo "🚀 Deploying application..."
ssh "$TARGET_USER@$TARGET_HOST" "cd $TARGET_DIR && \
    echo \"📦 Pulling latest images...\" && \
    export TAG=$TAG && \
    export GITHUB_REPOSITORY=$GH_REPO && \
    docker pull $REPO/bdc-server:$TAG && \
    docker pull $REPO/bdc-client:$TAG && \
    echo \"🛑 Stopping old containers...\" && \
    docker-compose down && \
    echo \"🔄 Starting new containers...\" && \
    docker-compose up -d && \
    echo \"📊 Running database migrations...\" && \
    docker-compose exec -T server flask db upgrade && \
    echo \"🧹 Cleaning up old images...\" && \
    docker image prune -f && \
    echo \"⏳ Waiting for services to be healthy...\" && \
    sleep 15 && \
    echo \"📊 Container status:\" && \
    docker-compose ps"

echo "✅ Deployment completed successfully."

# Run health checks
echo "🏥 Running health checks..."
./scripts/health_check.sh "$TARGET_HOST"

# Run smoke tests for production
if [ "$ENVIRONMENT" == "production" ]; then
    echo "🧪 Running smoke tests..."
    ./scripts/smoke_test.sh "$PROD_URL"
fi

echo "========================================="
echo "✅ Deployment complete!"
echo "========================================="