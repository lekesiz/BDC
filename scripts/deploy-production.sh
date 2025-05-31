#!/bin/bash

# BDC Production Deployment Script
# This script handles complete production deployment with safety checks

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_ENV="${1:-production}"
SKIP_TESTS="${SKIP_TESTS:-false}"
DRY_RUN="${DRY_RUN:-false}"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if required commands exist
    local required_commands=("docker" "docker-compose" "kubectl" "git")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "$cmd is required but not installed"
        fi
    done
    
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        error "Not in a git repository"
    fi
    
    # Check if environment file exists
    if [[ ! -f "$PROJECT_ROOT/.env.$DEPLOYMENT_ENV" ]]; then
        error "Environment file .env.$DEPLOYMENT_ENV not found"
    fi
    
    success "Prerequisites check passed"
}

# Pre-deployment checks
pre_deployment_checks() {
    log "Running pre-deployment checks..."
    
    # Check if we're on the correct branch
    local current_branch=$(git branch --show-current)
    if [[ "$DEPLOYMENT_ENV" == "production" && "$current_branch" != "main" ]]; then
        error "Production deployments must be from main branch (current: $current_branch)"
    fi
    
    # Check if working directory is clean
    if [[ -n "$(git status --porcelain)" ]]; then
        error "Working directory is not clean. Commit or stash changes first."
    fi
    
    # Check if we're up to date with remote
    git fetch origin
    local local_commit=$(git rev-parse HEAD)
    local remote_commit=$(git rev-parse origin/$(git branch --show-current))
    if [[ "$local_commit" != "$remote_commit" ]]; then
        error "Local branch is not up to date with remote. Pull latest changes first."
    fi
    
    success "Pre-deployment checks passed"
}

# Run tests
run_tests() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        warning "Skipping tests (SKIP_TESTS=true)"
        return 0
    fi
    
    log "Running tests..."
    
    # Backend tests
    log "Running backend tests..."
    cd "$PROJECT_ROOT/server"
    python -m pytest --cov=app --cov-fail-under=80
    
    # Frontend tests
    log "Running frontend tests..."
    cd "$PROJECT_ROOT/client"
    npm test -- --coverage --watchAll=false
    
    # Security checks
    log "Running security checks..."
    cd "$PROJECT_ROOT/server"
    safety check
    bandit -r app/
    
    cd "$PROJECT_ROOT/client"
    npm audit --audit-level=high
    
    success "All tests passed"
}

# Build images
build_images() {
    log "Building Docker images..."
    
    local timestamp=$(date +%Y%m%d-%H%M%S)
    local git_commit=$(git rev-parse --short HEAD)
    local image_tag="${DEPLOYMENT_ENV}-${timestamp}-${git_commit}"
    
    # Build backend image
    log "Building backend image..."
    docker build -t "bdc-backend:${image_tag}" -f "$PROJECT_ROOT/server/Dockerfile.prod" "$PROJECT_ROOT/server"
    docker tag "bdc-backend:${image_tag}" "bdc-backend:latest"
    
    # Build frontend image
    log "Building frontend image..."
    docker build -t "bdc-frontend:${image_tag}" -f "$PROJECT_ROOT/client/Dockerfile.prod" "$PROJECT_ROOT/client"
    docker tag "bdc-frontend:${image_tag}" "bdc-frontend:latest"
    
    # Security scan
    log "Running security scan on images..."
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy image "bdc-backend:${image_tag}"
    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy image "bdc-frontend:${image_tag}"
    
    success "Images built successfully"
    echo "Backend image: bdc-backend:${image_tag}"
    echo "Frontend image: bdc-frontend:${image_tag}"
}

# Deploy with Docker Compose
deploy_docker_compose() {
    log "Deploying with Docker Compose..."
    
    cd "$PROJECT_ROOT"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would execute: docker-compose -f docker-compose.production.yml up -d"
        return 0
    fi
    
    # Create backup of current deployment
    if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
        log "Creating backup of current deployment..."
        docker-compose -f docker-compose.production.yml exec postgres pg_dump -U bdc_user bdc_production > "backup-$(date +%Y%m%d-%H%M%S).sql"
    fi
    
    # Deploy new version
    docker-compose -f docker-compose.production.yml pull
    docker-compose -f docker-compose.production.yml up -d --remove-orphans
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    local max_attempts=30
    local attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker-compose -f docker-compose.production.yml ps | grep -q "unhealthy"; then
            attempt=$((attempt + 1))
            log "Waiting for services to be healthy (attempt $attempt/$max_attempts)..."
            sleep 10
        else
            break
        fi
    done
    
    if [[ $attempt -eq $max_attempts ]]; then
        error "Services failed to become healthy within expected time"
    fi
    
    success "Docker Compose deployment completed"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    log "Deploying to Kubernetes..."
    
    cd "$PROJECT_ROOT"
    
    # Check kubectl context
    local current_context=$(kubectl config current-context)
    log "Current kubectl context: $current_context"
    
    if [[ "$DEPLOYMENT_ENV" == "production" && "$current_context" != *"production"* ]]; then
        error "Kubectl context does not appear to be production environment"
    fi
    
    if [[ "$DRY_RUN" == "true" ]]; then
        log "DRY RUN: Would apply Kubernetes manifests"
        kubectl apply --dry-run=client -f "k8s/$DEPLOYMENT_ENV/"
        return 0
    fi
    
    # Apply manifests
    kubectl apply -f "k8s/$DEPLOYMENT_ENV/"
    
    # Wait for rollout
    log "Waiting for deployment rollout..."
    kubectl rollout status deployment/bdc-backend -n "bdc-$DEPLOYMENT_ENV" --timeout=600s
    kubectl rollout status deployment/bdc-frontend -n "bdc-$DEPLOYMENT_ENV" --timeout=600s
    
    success "Kubernetes deployment completed"
}

# Health checks
health_checks() {
    log "Running health checks..."
    
    local max_attempts=10
    local attempt=0
    local base_url="https://yourdomain.com"
    
    if [[ "$DEPLOYMENT_ENV" != "production" ]]; then
        base_url="https://staging.yourdomain.com"
    fi
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f "$base_url/health" > /dev/null 2>&1 && \
           curl -f "$base_url/api/health" > /dev/null 2>&1; then
            success "Health checks passed"
            return 0
        fi
        
        attempt=$((attempt + 1))
        log "Health check failed (attempt $attempt/$max_attempts), retrying in 30 seconds..."
        sleep 30
    done
    
    error "Health checks failed after $max_attempts attempts"
}

# Smoke tests
smoke_tests() {
    log "Running smoke tests..."
    
    local base_url="https://yourdomain.com"
    if [[ "$DEPLOYMENT_ENV" != "production" ]]; then
        base_url="https://staging.yourdomain.com"
    fi
    
    # Test critical endpoints
    local endpoints=(
        "/health"
        "/api/health"
        "/api/auth/status"
        "/api/health/database"
        "/api/health/cache"
    )
    
    for endpoint in "${endpoints[@]}"; do
        log "Testing endpoint: $endpoint"
        if ! curl -f "$base_url$endpoint" > /dev/null 2>&1; then
            error "Smoke test failed for endpoint: $endpoint"
        fi
    done
    
    success "Smoke tests passed"
}

# Post-deployment tasks
post_deployment() {
    log "Running post-deployment tasks..."
    
    # Update monitoring dashboards
    if command -v kubectl &> /dev/null; then
        kubectl create configmap grafana-dashboards \
            --from-file="$PROJECT_ROOT/monitoring/grafana/dashboards/" \
            -n bdc-monitoring \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
    
    # Send deployment notification
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚀 BDC $DEPLOYMENT_ENV deployment completed successfully!\"}" \
            "$SLACK_WEBHOOK_URL"
    fi
    
    success "Post-deployment tasks completed"
}

# Rollback function
rollback() {
    error "Deployment failed. Initiating rollback..."
    
    if command -v kubectl &> /dev/null; then
        kubectl rollout undo deployment/bdc-backend -n "bdc-$DEPLOYMENT_ENV"
        kubectl rollout undo deployment/bdc-frontend -n "bdc-$DEPLOYMENT_ENV"
    else
        # Docker Compose rollback
        cd "$PROJECT_ROOT"
        docker-compose -f docker-compose.production.yml down
        # Restore from backup if available
        local latest_backup=$(ls -t backup-*.sql 2>/dev/null | head -n1)
        if [[ -n "$latest_backup" ]]; then
            warning "Restoring from backup: $latest_backup"
            docker-compose -f docker-compose.production.yml up -d postgres
            sleep 30
            docker-compose -f docker-compose.production.yml exec -T postgres psql -U bdc_user -d bdc_production < "$latest_backup"
        fi
    fi
}

# Main deployment flow
main() {
    log "Starting BDC $DEPLOYMENT_ENV deployment..."
    
    # Set trap for cleanup on error
    trap rollback ERR
    
    check_prerequisites
    pre_deployment_checks
    run_tests
    build_images
    
    # Choose deployment method
    if command -v kubectl &> /dev/null && kubectl config current-context &> /dev/null; then
        deploy_kubernetes
    else
        deploy_docker_compose
    fi
    
    health_checks
    smoke_tests
    post_deployment
    
    success "BDC $DEPLOYMENT_ENV deployment completed successfully!"
    
    # Remove trap
    trap - ERR
}

# Script entry point
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi