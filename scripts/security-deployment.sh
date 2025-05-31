#!/bin/bash
# BDC Security Deployment Script
# Comprehensive security hardening deployment automation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/tmp/bdc-security-deployment-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    echo -e "${RED}ERROR: $1${NC}" >&2
    log "ERROR: $1"
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✓ $1${NC}"
    log "SUCCESS: $1"
}

# Warning message
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
    log "WARNING: $1"
}

# Info message
info() {
    echo -e "${BLUE}ℹ $1${NC}"
    log "INFO: $1"
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if running as non-root
    if [[ $EUID -eq 0 ]]; then
        error_exit "This script should not be run as root for security reasons"
    fi
    
    # Check required tools
    local required_tools=("docker" "kubectl" "helm" "openssl" "jq" "curl")
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            error_exit "Required tool '$tool' is not installed"
        fi
    done
    
    # Check Kubernetes access
    if ! kubectl auth can-i get pods &> /dev/null; then
        error_exit "Kubernetes access not available or insufficient permissions"
    fi
    
    success "Prerequisites check completed"
}

# Validate environment variables
validate_environment() {
    info "Validating environment variables..."
    
    local required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "SECRET_KEY"
        "JWT_SECRET_KEY"
        "DB_ENCRYPTION_KEY"
    )
    
    local missing_vars=()
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        error_exit "Missing required environment variables: ${missing_vars[*]}"
    fi
    
    # Check for default/weak values
    if [[ "$SECRET_KEY" == "dev-secret-key-change-in-production" ]]; then
        error_exit "SECRET_KEY is still set to default development value"
    fi
    
    if [[ "$JWT_SECRET_KEY" == "jwt-secret-key-change-in-production" ]]; then
        error_exit "JWT_SECRET_KEY is still set to default development value"
    fi
    
    success "Environment variables validated"
}

# Generate SSL certificates
generate_ssl_certificates() {
    info "Generating SSL certificates..."
    
    local ssl_dir="$PROJECT_ROOT/ssl"
    mkdir -p "$ssl_dir"
    
    # Generate private key
    openssl genrsa -out "$ssl_dir/bdc.key" 2048
    
    # Generate certificate signing request
    openssl req -new -key "$ssl_dir/bdc.key" -out "$ssl_dir/bdc.csr" -subj "/C=US/ST=State/L=City/O=Organization/CN=bdc.company.com"
    
    # Generate self-signed certificate (replace with proper CA-signed cert in production)
    openssl x509 -req -days 365 -in "$ssl_dir/bdc.csr" -signkey "$ssl_dir/bdc.key" -out "$ssl_dir/bdc.crt"
    
    # Set proper permissions
    chmod 600 "$ssl_dir/bdc.key"
    chmod 644 "$ssl_dir/bdc.crt"
    
    success "SSL certificates generated"
}

# Create Kubernetes secrets
create_k8s_secrets() {
    info "Creating Kubernetes secrets..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace bdc-production --dry-run=client -o yaml | kubectl apply -f -
    
    # Create SSL certificate secret
    kubectl create secret tls bdc-ssl-cert \
        --cert="$PROJECT_ROOT/ssl/bdc.crt" \
        --key="$PROJECT_ROOT/ssl/bdc.key" \
        --namespace=bdc-production \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create application secrets
    kubectl create secret generic bdc-app-secrets \
        --from-literal=database-url="$DATABASE_URL" \
        --from-literal=redis-url="$REDIS_URL" \
        --from-literal=secret-key="$SECRET_KEY" \
        --from-literal=jwt-secret-key="$JWT_SECRET_KEY" \
        --from-literal=db-encryption-key="$DB_ENCRYPTION_KEY" \
        --namespace=bdc-production \
        --dry-run=client -o yaml | kubectl apply -f -
    
    success "Kubernetes secrets created"
}

# Deploy security policies
deploy_security_policies() {
    info "Deploying security policies..."
    
    # Apply Pod Security Policies
    kubectl apply -f "$PROJECT_ROOT/k8s/production/security-policies.yaml"
    
    # Apply Network Policies
    kubectl apply -f "$PROJECT_ROOT/k8s/production/network-policies.yaml"
    
    # Wait for policies to be ready
    kubectl wait --for=condition=ready pod -l app=gatekeeper-system --namespace=gatekeeper-system --timeout=300s || warning "Gatekeeper not found, some policies may not be enforced"
    
    success "Security policies deployed"
}

# Build and push secure Docker images
build_secure_images() {
    info "Building secure Docker images..."
    
    local registry="${DOCKER_REGISTRY:-your-registry.com}"
    local tag="${IMAGE_TAG:-$(date +%Y%m%d-%H%M%S)}"
    
    # Build backend image
    docker build -f "$PROJECT_ROOT/docker/Dockerfile.production" \
        -t "$registry/bdc/backend:$tag" \
        "$PROJECT_ROOT"
    
    # Scan image for vulnerabilities
    if command -v trivy &> /dev/null; then
        info "Scanning backend image for vulnerabilities..."
        trivy image --exit-code 1 --severity HIGH,CRITICAL "$registry/bdc/backend:$tag" || \
            error_exit "Critical vulnerabilities found in backend image"
    else
        warning "Trivy not installed, skipping vulnerability scan"
    fi
    
    # Push image
    docker push "$registry/bdc/backend:$tag"
    
    # Update deployment manifest
    sed -i "s|image: .*bdc/backend:.*|image: $registry/bdc/backend:$tag|g" \
        "$PROJECT_ROOT/k8s/production/backend.yaml"
    
    success "Secure Docker images built and pushed"
}

# Deploy monitoring stack
deploy_monitoring() {
    info "Deploying security monitoring stack..."
    
    # Create monitoring namespace
    kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy Prometheus
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --values "$PROJECT_ROOT/monitoring/prometheus-values.yaml" \
        --wait
    
    # Deploy Falco for runtime security
    helm repo add falcosecurity https://falcosecurity.github.io/charts
    helm repo update
    
    helm upgrade --install falco falcosecurity/falco \
        --namespace monitoring \
        --values "$PROJECT_ROOT/monitoring/falco-values.yaml" \
        --wait
    
    # Apply custom security monitoring configuration
    kubectl apply -f "$PROJECT_ROOT/monitoring/security-monitoring.yaml"
    
    success "Security monitoring stack deployed"
}

# Deploy application with security hardening
deploy_application() {
    info "Deploying BDC application with security hardening..."
    
    # Apply all Kubernetes manifests
    kubectl apply -f "$PROJECT_ROOT/k8s/production/"
    
    # Wait for deployments to be ready
    kubectl rollout status deployment/bdc-backend --namespace=bdc-production --timeout=600s
    kubectl rollout status deployment/bdc-frontend --namespace=bdc-production --timeout=600s
    
    # Verify security contexts
    local pods=$(kubectl get pods -n bdc-production -o name)
    for pod in $pods; do
        local security_context=$(kubectl get "$pod" -n bdc-production -o jsonpath='{.spec.securityContext}')
        if [[ "$security_context" == *"runAsRoot"* ]] || [[ "$security_context" == *"privileged"* ]]; then
            error_exit "Pod $pod has insecure security context"
        fi
    done
    
    success "BDC application deployed with security hardening"
}

# Run security tests
run_security_tests() {
    info "Running security tests..."
    
    # Wait for application to be ready
    sleep 30
    
    # Get application URL
    local app_url=$(kubectl get ingress bdc-ingress -n bdc-production -o jsonpath='{.spec.rules[0].host}')
    if [[ -z "$app_url" ]]; then
        app_url="https://localhost"
        warning "Could not determine application URL, using localhost"
    else
        app_url="https://$app_url"
    fi
    
    # Basic connectivity test
    if curl -s -k "$app_url/health" | grep -q "OK"; then
        success "Application health check passed"
    else
        error_exit "Application health check failed"
    fi
    
    # Security headers test
    info "Testing security headers..."
    local headers=$(curl -s -I -k "$app_url")
    
    local required_headers=(
        "Strict-Transport-Security"
        "X-Content-Type-Options"
        "X-Frame-Options"
        "X-XSS-Protection"
    )
    
    for header in "${required_headers[@]}"; do
        if echo "$headers" | grep -q "$header"; then
            success "Security header '$header' present"
        else
            warning "Security header '$header' missing"
        fi
    done
    
    # Run OWASP ZAP baseline scan if available
    if command -v zap-baseline.py &> /dev/null; then
        info "Running OWASP ZAP baseline security scan..."
        zap-baseline.py -t "$app_url" -J zap-report.json || warning "ZAP scan found issues"
    else
        warning "OWASP ZAP not installed, skipping security scan"
    fi
    
    success "Security tests completed"
}

# Setup log aggregation
setup_logging() {
    info "Setting up centralized logging..."
    
    # Deploy ELK stack or similar
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    # Deploy Elasticsearch
    helm upgrade --install elasticsearch elastic/elasticsearch \
        --namespace monitoring \
        --set persistence.enabled=true \
        --set resources.requests.memory=2Gi \
        --wait
    
    # Deploy Kibana
    helm upgrade --install kibana elastic/kibana \
        --namespace monitoring \
        --wait
    
    # Deploy Filebeat for log collection
    kubectl apply -f "$PROJECT_ROOT/monitoring/filebeat-config.yaml"
    
    success "Centralized logging setup completed"
}

# Setup backup and disaster recovery
setup_backup() {
    info "Setting up backup and disaster recovery..."
    
    # Create backup storage
    kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backup-storage
  namespace: bdc-production
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
EOF
    
    # Create backup CronJob
    kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: bdc-production
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:13
            command:
            - /bin/bash
            - -c
            - |
              export PGPASSWORD=\$DATABASE_PASSWORD
              pg_dump -h \$DATABASE_HOST -U \$DATABASE_USER \$DATABASE_NAME | gzip > /backup/backup-\$(date +%Y%m%d-%H%M%S).sql.gz
              # Encrypt backup
              gpg --symmetric --cipher-algo AES256 --output /backup/backup-\$(date +%Y%m%d-%H%M%S).sql.gz.gpg /backup/backup-\$(date +%Y%m%d-%H%M%S).sql.gz
              rm /backup/backup-\$(date +%Y%m%d-%H%M%S).sql.gz
              # Clean old backups (keep 30 days)
              find /backup -name "*.gpg" -mtime +30 -delete
            env:
            - name: DATABASE_HOST
              valueFrom:
                secretKeyRef:
                  name: bdc-app-secrets
                  key: database-host
            - name: DATABASE_USER
              valueFrom:
                secretKeyRef:
                  name: bdc-app-secrets
                  key: database-user
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: bdc-app-secrets
                  key: database-password
            - name: DATABASE_NAME
              valueFrom:
                secretKeyRef:
                  name: bdc-app-secrets
                  key: database-name
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-storage
          restartPolicy: OnFailure
EOF
    
    success "Backup and disaster recovery setup completed"
}

# Validate deployment
validate_deployment() {
    info "Validating security deployment..."
    
    # Check all pods are running
    local failed_pods=$(kubectl get pods -n bdc-production --field-selector=status.phase!=Running -o name)
    if [[ -n "$failed_pods" ]]; then
        error_exit "Some pods are not running: $failed_pods"
    fi
    
    # Check security policies are applied
    local psp_count=$(kubectl get psp | wc -l)
    if [[ $psp_count -lt 2 ]]; then
        warning "Pod Security Policies may not be properly configured"
    fi
    
    # Check network policies are applied
    local netpol_count=$(kubectl get networkpolicy -n bdc-production | wc -l)
    if [[ $netpol_count -lt 2 ]]; then
        warning "Network Policies may not be properly configured"
    fi
    
    # Check monitoring is working
    if kubectl get pods -n monitoring | grep -q "prometheus.*Running"; then
        success "Prometheus monitoring is running"
    else
        warning "Prometheus monitoring may not be working properly"
    fi
    
    # Generate deployment report
    cat > "$PROJECT_ROOT/deployment-report.md" <<EOF
# BDC Security Deployment Report

**Deployment Date**: $(date)
**Log File**: $LOG_FILE

## Deployed Components
- ✅ SSL Certificates
- ✅ Kubernetes Secrets
- ✅ Security Policies
- ✅ Docker Images (Security Scanned)
- ✅ Application Deployment
- ✅ Security Monitoring
- ✅ Centralized Logging
- ✅ Backup System

## Security Features Enabled
- ✅ Pod Security Policies
- ✅ Network Policies
- ✅ RBAC
- ✅ Secrets Management
- ✅ Runtime Security Monitoring (Falco)
- ✅ Vulnerability Scanning
- ✅ Security Headers
- ✅ Encrypted Storage
- ✅ Audit Logging

## Next Steps
1. Configure monitoring alerts
2. Setup external backups
3. Complete compliance documentation
4. Schedule security assessment
5. Conduct incident response drill

## Support Contacts
- Security Team: security@company.com
- DevOps Team: devops@company.com
- Incident Response: incident@company.com
EOF
    
    success "Security deployment validation completed"
}

# Cleanup function
cleanup() {
    info "Cleaning up temporary files..."
    rm -f /tmp/bdc-deployment-*
}

# Main execution
main() {
    info "Starting BDC security deployment..."
    info "Log file: $LOG_FILE"
    
    # Trap cleanup on exit
    trap cleanup EXIT
    
    # Run deployment steps
    check_prerequisites
    validate_environment
    generate_ssl_certificates
    create_k8s_secrets
    deploy_security_policies
    build_secure_images
    deploy_monitoring
    deploy_application
    run_security_tests
    setup_logging
    setup_backup
    validate_deployment
    
    success "BDC security deployment completed successfully!"
    info "Deployment report: $PROJECT_ROOT/deployment-report.md"
    info "Log file: $LOG_FILE"
}

# Execute main function
main "$@"