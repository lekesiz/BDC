#!/bin/bash
# Production deployment script for BDC application

set -e

# Configuration
NAMESPACE="bdc-production"
DEPLOYMENT_NAME="bdc-app"
IMAGE_TAG=${1:-latest}
TIMEOUT=600

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed"
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "docker is not installed"
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_info "Prerequisites check passed"
}

# Create namespace if it doesn't exist
create_namespace() {
    log_info "Creating namespace if it doesn't exist..."
    kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -
}

# Deploy secrets (in production, use external secret management)
deploy_secrets() {
    log_info "Deploying secrets..."
    
    # Check if secrets already exist
    if kubectl get secret bdc-secrets -n $NAMESPACE &> /dev/null; then
        log_warn "Secrets already exist. Skipping secret creation."
        log_warn "In production, ensure secrets are properly configured!"
    else
        log_warn "Creating default secrets. CHANGE THESE IN PRODUCTION!"
        kubectl apply -f k8s/secrets.yaml
    fi
}

# Deploy configuration
deploy_config() {
    log_info "Deploying configuration..."
    kubectl apply -f k8s/configmap.yaml
}

# Deploy database
deploy_database() {
    log_info "Deploying PostgreSQL database..."
    kubectl apply -f k8s/postgres.yaml
    
    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    kubectl wait --for=condition=available --timeout=${TIMEOUT}s deployment/postgres -n $NAMESPACE
}

# Deploy Redis
deploy_redis() {
    log_info "Deploying Redis..."
    kubectl apply -f k8s/redis.yaml
    
    # Wait for Redis to be ready
    log_info "Waiting for Redis to be ready..."
    kubectl wait --for=condition=available --timeout=${TIMEOUT}s deployment/redis -n $NAMESPACE
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."
    
    IMAGE_NAME="ghcr.io/your-org/bdc:${IMAGE_TAG}"
    
    # Build image
    docker build -f docker/Dockerfile --target production -t $IMAGE_NAME .
    
    # Push image
    docker push $IMAGE_NAME
    
    log_info "Image built and pushed: $IMAGE_NAME"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Create a job to run migrations
    cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-$(date +%s)
  namespace: $NAMESPACE
spec:
  template:
    spec:
      containers:
      - name: db-migration
        image: ghcr.io/your-org/bdc:${IMAGE_TAG}
        command: ['flask', 'db', 'upgrade']
        env:
        - name: FLASK_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: bdc-secrets
              key: DATABASE_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: bdc-secrets
              key: SECRET_KEY
      restartPolicy: Never
  backoffLimit: 3
EOF
    
    # Wait for migration to complete
    log_info "Waiting for database migration to complete..."
    sleep 30  # Give it time to start
}

# Deploy application
deploy_application() {
    log_info "Deploying application..."
    
    # Update image tag in deployment
    sed -i.bak "s|ghcr.io/your-org/bdc:latest|ghcr.io/your-org/bdc:${IMAGE_TAG}|g" k8s/app.yaml
    
    kubectl apply -f k8s/app.yaml
    
    # Restore original file
    mv k8s/app.yaml.bak k8s/app.yaml
    
    # Wait for deployment to be ready
    log_info "Waiting for application deployment to be ready..."
    kubectl wait --for=condition=available --timeout=${TIMEOUT}s deployment/$DEPLOYMENT_NAME -n $NAMESPACE
}

# Deploy ingress
deploy_ingress() {
    log_info "Deploying ingress..."
    kubectl apply -f k8s/ingress.yaml
}

# Deploy monitoring
deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    kubectl apply -f k8s/monitoring.yaml
    
    # Wait for monitoring to be ready
    log_info "Waiting for monitoring to be ready..."
    kubectl wait --for=condition=available --timeout=${TIMEOUT}s deployment/prometheus -n $NAMESPACE
    kubectl wait --for=condition=available --timeout=${TIMEOUT}s deployment/grafana -n $NAMESPACE
}

# Health check
health_check() {
    log_info "Performing health check..."
    
    # Get service URL
    SERVICE_URL=$(kubectl get ingress bdc-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}')
    
    if [ -z "$SERVICE_URL" ]; then
        # Fallback to port-forward for testing
        log_warn "No ingress URL found, using port-forward for health check"
        kubectl port-forward service/bdc-app-service 8080:80 -n $NAMESPACE &
        PORT_FORWARD_PID=$!
        sleep 5
        
        if curl -f http://localhost:8080/health; then
            log_info "Health check passed"
        else
            log_error "Health check failed"
            kill $PORT_FORWARD_PID
            exit 1
        fi
        
        kill $PORT_FORWARD_PID
    else
        # Check via ingress
        if curl -f https://$SERVICE_URL/health; then
            log_info "Health check passed"
        else
            log_error "Health check failed"
            exit 1
        fi
    fi
}

# Rollback function
rollback() {
    log_warn "Rolling back deployment..."
    kubectl rollout undo deployment/$DEPLOYMENT_NAME -n $NAMESPACE
    kubectl rollout status deployment/$DEPLOYMENT_NAME -n $NAMESPACE
    log_info "Rollback completed"
}

# Main deployment function
main() {
    log_info "Starting BDC production deployment..."
    
    # Trap errors and rollback if needed
    trap 'log_error "Deployment failed! Consider rollback."; exit 1' ERR
    
    check_prerequisites
    create_namespace
    deploy_secrets
    deploy_config
    deploy_database
    deploy_redis
    
    # Only build if we're not using an existing image
    if [ "$IMAGE_TAG" = "latest" ] || [ -z "$(docker images -q ghcr.io/your-org/bdc:${IMAGE_TAG})" ]; then
        build_and_push_image
    fi
    
    run_migrations
    deploy_application
    deploy_ingress
    deploy_monitoring
    
    health_check
    
    log_info "Deployment completed successfully!"
    log_info "Application URL: https://$(kubectl get ingress bdc-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}')"
    log_info "Grafana URL: http://$(kubectl get service grafana -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}'):3000"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 [deploy|rollback|health] [image_tag]"
        exit 1
        ;;
esac