#!/bin/bash
# Production readiness validation script for BDC application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

log_info() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_CHECKS++))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_CHECKS++))
}

log_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

check_item() {
    ((TOTAL_CHECKS++))
    if eval "$2"; then
        log_info "$1"
        return 0
    else
        log_error "$1"
        return 1
    fi
}

# Check environment variables
check_environment() {
    log_header "Environment Configuration"
    
    check_item "SECRET_KEY is set and strong" "[ ! -z \"\$SECRET_KEY\" ] && [ \${#SECRET_KEY} -ge 32 ]"
    check_item "JWT_SECRET_KEY is set and strong" "[ ! -z \"\$JWT_SECRET_KEY\" ] && [ \${#JWT_SECRET_KEY} -ge 32 ]"
    check_item "DATABASE_URL is configured" "[ ! -z \"\$DATABASE_URL\" ]"
    check_item "REDIS_URL is configured" "[ ! -z \"\$REDIS_URL\" ]"
    check_item "FLASK_ENV is set to production" "[ \"\$FLASK_ENV\" = 'production' ]"
}

# Check file structure
check_files() {
    log_header "File Structure"
    
    check_item "Production config exists" "[ -f 'config/production.py' ]"
    check_item "Docker files exist" "[ -f 'docker/Dockerfile' ] && [ -f 'docker-compose.production.yml' ]"
    check_item "Kubernetes manifests exist" "[ -d 'k8s' ] && [ -f 'k8s/app.yaml' ]"
    check_item "SSL setup script exists" "[ -f 'scripts/ssl-setup.sh' ] && [ -x 'scripts/ssl-setup.sh' ]"
    check_item "Deployment script exists" "[ -f 'scripts/deploy.sh' ] && [ -x 'scripts/deploy.sh' ]"
    check_item "Performance tuning script exists" "[ -f 'scripts/performance-tuning.sh' ] && [ -x 'scripts/performance-tuning.sh' ]"
    check_item "Backup scripts exist" "[ -f 'docker/scripts/backup.py' ] && [ -f 'docker/scripts/backup.sh' ]"
}

# Check security middleware
check_security() {
    log_header "Security Configuration"
    
    check_item "Security middleware exists" "[ -f 'app/middleware/security_middleware.py' ]"
    check_item "Health checker exists" "[ -f 'app/utils/health_checker.py' ]"
    check_item "Backup manager exists" "[ -f 'app/utils/backup_manager.py' ]"
    check_item "WSGI entry point configured" "[ -f 'wsgi.py' ]"
    check_item "Gunicorn config exists" "[ -f 'docker/gunicorn.conf.py' ]"
}

# Check Docker configuration
check_docker() {
    log_header "Docker Configuration"
    
    check_item "Production Dockerfile exists" "[ -f 'docker/Dockerfile' ]"
    check_item "Production requirements exist" "[ -f 'requirements-production.txt' ]"
    check_item "Docker compose production file exists" "[ -f 'docker-compose.production.yml' ]"
    check_item "Nginx configuration exists" "[ -f 'docker/nginx.conf' ]"
    check_item "Prometheus config exists" "[ -f 'docker/prometheus.yml' ]"
}

# Check Kubernetes configuration
check_kubernetes() {
    log_header "Kubernetes Configuration"
    
    check_item "Namespace manifest exists" "[ -f 'k8s/namespace.yaml' ]"
    check_item "ConfigMap manifest exists" "[ -f 'k8s/configmap.yaml' ]"
    check_item "Secrets template exists" "[ -f 'k8s/secrets.yaml' ]"
    check_item "PostgreSQL manifest exists" "[ -f 'k8s/postgres.yaml' ]"
    check_item "Redis manifest exists" "[ -f 'k8s/redis.yaml' ]"
    check_item "Application manifest exists" "[ -f 'k8s/app.yaml' ]"
    check_item "Ingress manifest exists" "[ -f 'k8s/ingress.yaml' ]"
    check_item "Monitoring manifest exists" "[ -f 'k8s/monitoring.yaml' ]"
}

# Check CI/CD configuration
check_cicd() {
    log_header "CI/CD Configuration"
    
    check_item "GitHub Actions workflow exists" "[ -f '.github/workflows/deploy.yml' ]"
    check_item "Gitignore configured properly" "[ -f '.gitignore' ]"
}

# Check documentation
check_documentation() {
    log_header "Documentation"
    
    check_item "Production deployment guide exists" "[ -f 'PRODUCTION_DEPLOYMENT_GUIDE.md' ]"
    check_item "Production checklist exists" "[ -f 'PRODUCTION_CHECKLIST.md' ]"
    check_item "Validation script exists" "[ -f 'scripts/validate-production.sh' ]"
}

# Check Python dependencies
check_dependencies() {
    log_header "Dependencies"
    
    if [ -f "requirements-production.txt" ]; then
        log_info "Production requirements file found"
        
        # Check for critical production packages
        if grep -q "gunicorn" requirements-production.txt; then
            log_info "Gunicorn (WSGI server) included"
        else
            log_error "Gunicorn not found in production requirements"
        fi
        
        if grep -q "psycopg2-binary" requirements-production.txt; then
            log_info "PostgreSQL driver included"
        else
            log_error "PostgreSQL driver not found"
        fi
        
        if grep -q "redis" requirements-production.txt; then
            log_info "Redis client included"
        else
            log_error "Redis client not found"
        fi
        
        if grep -q "prometheus-flask-exporter" requirements-production.txt; then
            log_info "Prometheus metrics exporter included"
        else
            log_error "Prometheus metrics exporter not found"
        fi
        
        if grep -q "sentry-sdk" requirements-production.txt; then
            log_info "Sentry error tracking included"
        else
            log_warn "Sentry error tracking not found (optional)"
        fi
        
        if grep -q "cryptography" requirements-production.txt; then
            log_info "Cryptography library included"
        else
            log_error "Cryptography library not found"
        fi
    else
        log_error "Production requirements file not found"
    fi
}

# Test basic application import
test_application() {
    log_header "Application Validation"
    
    if python3 -c "from app import create_app; app = create_app(); print('Application import successful')" 2>/dev/null; then
        log_info "Application imports successfully"
    else
        log_error "Application import failed"
    fi
    
    if python3 -c "import wsgi; print('WSGI module import successful')" 2>/dev/null; then
        log_info "WSGI module imports successfully"
    else
        log_error "WSGI module import failed"
    fi
}

# Check for common security issues
check_security_issues() {
    log_header "Security Validation"
    
    # Check for default passwords in config files
    if grep -r "CHANGE_ME" . --exclude-dir=.git --exclude="*.md" 2>/dev/null; then
        log_error "Default passwords found - must be changed for production"
    else
        log_info "No default passwords found"
    fi
    
    # Check for debug mode
    if grep -r "DEBUG.*=.*True" . --exclude-dir=.git 2>/dev/null; then
        log_error "Debug mode enabled - must be disabled for production"
    else
        log_info "Debug mode properly disabled"
    fi
    
    # Check for hardcoded secrets
    if grep -r "password.*=.*['\"]" . --exclude-dir=.git --exclude="*.md" --exclude="validate-production.sh" 2>/dev/null | grep -v "os.getenv\|os.environ"; then
        log_warn "Possible hardcoded passwords found - review for security"
    else
        log_info "No obvious hardcoded passwords found"
    fi
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "================================================="
    echo "    BDC Production Readiness Validation"
    echo "================================================="
    echo -e "${NC}\n"
    
    # Load environment if .env.production exists
    if [ -f ".env.production" ]; then
        log_info "Loading production environment variables"
        export $(grep -v '^#' .env.production | xargs)
    else
        log_warn "No .env.production file found"
    fi
    
    # Run all checks
    check_environment
    check_files
    check_security
    check_docker
    check_kubernetes
    check_cicd
    check_documentation
    check_dependencies
    test_application
    check_security_issues
    
    # Summary
    log_header "Validation Summary"
    echo -e "Total Checks: ${BLUE}$TOTAL_CHECKS${NC}"
    echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
    echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All checks passed! Your BDC application is ready for production deployment.${NC}"
        echo -e "\nNext steps:"
        echo -e "1. Review and update environment variables in .env.production"
        echo -e "2. Configure SSL certificates using ./scripts/ssl-setup.sh"
        echo -e "3. Deploy using Docker Compose or Kubernetes"
        echo -e "4. Run performance tuning with ./scripts/performance-tuning.sh"
        echo -e "5. Set up monitoring and backup systems"
        return 0
    else
        echo -e "\n${RED}❌ Some checks failed. Please address the issues above before deploying to production.${NC}"
        echo -e "\nRefer to PRODUCTION_DEPLOYMENT_GUIDE.md for detailed instructions."
        return 1
    fi
}

# Run main function
main "$@"