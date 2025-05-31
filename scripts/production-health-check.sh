#!/bin/bash

# BDC Production Health Check Script
# Comprehensive health monitoring for production deployment

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:5000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:80}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
TIMEOUT=30
HEALTH_LOG="/tmp/bdc_health_check.log"

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}✗${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
    esac
}

# Function to check HTTP endpoint
check_endpoint() {
    local url=$1
    local name=$2
    local expected_code=${3:-200}
    
    print_status "INFO" "Checking $name at $url..."
    
    if response=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$url" 2>/dev/null); then
        if [ "$response" = "$expected_code" ]; then
            print_status "OK" "$name is healthy (HTTP $response)"
            return 0
        else
            print_status "ERROR" "$name returned HTTP $response (expected $expected_code)"
            return 1
        fi
    else
        print_status "ERROR" "$name is not responding"
        return 1
    fi
}

# Function to check Docker container health
check_container_health() {
    local container_name=$1
    
    if docker ps --filter "name=$container_name" --filter "status=running" --format "{{.Names}}" | grep -q "$container_name"; then
        local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-health-check")
        
        case $health_status in
            "healthy")
                print_status "OK" "Container $container_name is healthy"
                return 0
                ;;
            "unhealthy")
                print_status "ERROR" "Container $container_name is unhealthy"
                return 1
                ;;
            "starting")
                print_status "WARN" "Container $container_name is starting"
                return 1
                ;;
            "no-health-check")
                print_status "WARN" "Container $container_name has no health check configured"
                return 0
                ;;
            *)
                print_status "ERROR" "Container $container_name has unknown health status: $health_status"
                return 1
                ;;
        esac
    else
        print_status "ERROR" "Container $container_name is not running"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    print_status "INFO" "Checking database connectivity..."
    
    if check_container_health "bdc-postgres"; then
        # Try to connect to the database
        if docker exec bdc-postgres pg_isready -U "${POSTGRES_USER:-bdc_user}" -d "${POSTGRES_DB:-bdc_production}" >/dev/null 2>&1; then
            print_status "OK" "Database is accepting connections"
            return 0
        else
            print_status "ERROR" "Database is not accepting connections"
            return 1
        fi
    else
        return 1
    fi
}

# Function to check Redis connectivity
check_redis() {
    print_status "INFO" "Checking Redis connectivity..."
    
    if check_container_health "bdc-redis"; then
        # Try to ping Redis
        if docker exec bdc-redis redis-cli ping >/dev/null 2>&1; then
            print_status "OK" "Redis is responding to ping"
            return 0
        else
            print_status "ERROR" "Redis is not responding to ping"
            return 1
        fi
    else
        return 1
    fi
}

# Function to check disk space
check_disk_space() {
    print_status "INFO" "Checking disk space..."
    
    local threshold=80
    local usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$usage" -lt "$threshold" ]; then
        print_status "OK" "Disk usage is $usage% (threshold: $threshold%)"
        return 0
    else
        print_status "WARN" "Disk usage is $usage% (threshold: $threshold%)"
        return 1
    fi
}

# Function to check memory usage
check_memory() {
    print_status "INFO" "Checking memory usage..."
    
    local threshold=80
    local usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    
    if [ "$usage" -lt "$threshold" ]; then
        print_status "OK" "Memory usage is $usage% (threshold: $threshold%)"
        return 0
    else
        print_status "WARN" "Memory usage is $usage% (threshold: $threshold%)"
        return 1
    fi
}

# Function to check SSL certificates
check_ssl_certificates() {
    print_status "INFO" "Checking SSL certificates..."
    
    local ssl_dir="./nginx/ssl"
    local cert_file="$ssl_dir/cert.pem"
    local key_file="$ssl_dir/key.pem"
    
    if [ -f "$cert_file" ] && [ -f "$key_file" ]; then
        # Check certificate expiration
        local expiry_date=$(openssl x509 -enddate -noout -in "$cert_file" | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
        local current_epoch=$(date +%s)
        local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        if [ "$days_until_expiry" -gt 30 ]; then
            print_status "OK" "SSL certificate expires in $days_until_expiry days"
            return 0
        elif [ "$days_until_expiry" -gt 0 ]; then
            print_status "WARN" "SSL certificate expires in $days_until_expiry days"
            return 1
        else
            print_status "ERROR" "SSL certificate has expired"
            return 1
        fi
    else
        print_status "WARN" "SSL certificates not found in $ssl_dir"
        return 1
    fi
}

# Function to check API endpoints
check_api_endpoints() {
    print_status "INFO" "Checking API endpoints..."
    
    local endpoints=(
        "$BACKEND_URL/api/health"
        "$BACKEND_URL/api/auth/status"
    )
    
    local failed=0
    for endpoint in "${endpoints[@]}"; do
        if ! check_endpoint "$endpoint" "API $(basename "$endpoint")"; then
            ((failed++))
        fi
    done
    
    if [ $failed -eq 0 ]; then
        print_status "OK" "All API endpoints are healthy"
        return 0
    else
        print_status "ERROR" "$failed API endpoint(s) failed"
        return 1
    fi
}

# Function to check application performance
check_performance() {
    print_status "INFO" "Checking application performance..."
    
    # Check response time
    local response_time=$(curl -o /dev/null -s -w "%{time_total}" --max-time $TIMEOUT "$BACKEND_URL/api/health" 2>/dev/null || echo "0")
    local response_time_ms=$(echo "$response_time * 1000" | bc)
    
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        print_status "OK" "API response time: ${response_time_ms}ms"
        return 0
    else
        print_status "WARN" "API response time: ${response_time_ms}ms (threshold: 2000ms)"
        return 1
    fi
}

# Function to check logs for errors
check_logs() {
    print_status "INFO" "Checking recent logs for errors..."
    
    local error_count=0
    local containers=("bdc-backend" "bdc-frontend" "bdc-postgres" "bdc-redis")
    
    for container in "${containers[@]}"; do
        if docker ps --filter "name=$container" --format "{{.Names}}" | grep -q "$container"; then
            local errors=$(docker logs --since=10m "$container" 2>&1 | grep -i "error\|exception\|fatal" | wc -l)
            if [ "$errors" -gt 0 ]; then
                print_status "WARN" "Container $container has $errors error(s) in the last 10 minutes"
                ((error_count += errors))
            fi
        fi
    done
    
    if [ $error_count -eq 0 ]; then
        print_status "OK" "No recent errors found in logs"
        return 0
    else
        print_status "WARN" "Found $error_count error(s) in recent logs"
        return 1
    fi
}

# Function to generate health report
generate_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "# BDC Production Health Check Report" > "$HEALTH_LOG"
    echo "Generated: $timestamp" >> "$HEALTH_LOG"
    echo "" >> "$HEALTH_LOG"
    
    echo "## System Information" >> "$HEALTH_LOG"
    echo "- Hostname: $(hostname)" >> "$HEALTH_LOG"
    echo "- OS: $(uname -s) $(uname -r)" >> "$HEALTH_LOG"
    echo "- Uptime: $(uptime)" >> "$HEALTH_LOG"
    echo "" >> "$HEALTH_LOG"
    
    echo "## Container Status" >> "$HEALTH_LOG"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" >> "$HEALTH_LOG"
    echo "" >> "$HEALTH_LOG"
    
    echo "## Resource Usage" >> "$HEALTH_LOG"
    echo "### Memory" >> "$HEALTH_LOG"
    free -h >> "$HEALTH_LOG"
    echo "" >> "$HEALTH_LOG"
    echo "### Disk" >> "$HEALTH_LOG"
    df -h >> "$HEALTH_LOG"
    echo "" >> "$HEALTH_LOG"
    
    print_status "INFO" "Health report generated: $HEALTH_LOG"
}

# Main health check function
main() {
    echo "=================================="
    echo "🏥 BDC Production Health Check"
    echo "=================================="
    echo ""
    
    local total_checks=0
    local failed_checks=0
    
    # Run all health checks
    checks=(
        "check_disk_space"
        "check_memory"
        "check_container_health bdc-postgres"
        "check_container_health bdc-redis"
        "check_container_health bdc-backend"
        "check_container_health bdc-frontend"
        "check_database"
        "check_redis"
        "check_endpoint $FRONTEND_URL Frontend"
        "check_api_endpoints"
        "check_performance"
        "check_ssl_certificates"
        "check_logs"
    )
    
    for check in "${checks[@]}"; do
        ((total_checks++))
        if ! eval "$check"; then
            ((failed_checks++))
        fi
        echo ""
    done
    
    # Generate report
    generate_report
    
    # Summary
    echo "=================================="
    echo "📊 Health Check Summary"
    echo "=================================="
    echo "Total checks: $total_checks"
    echo "Failed checks: $failed_checks"
    echo "Success rate: $(( (total_checks - failed_checks) * 100 / total_checks ))%"
    echo ""
    
    if [ $failed_checks -eq 0 ]; then
        print_status "OK" "All health checks passed! System is healthy 🎉"
        exit 0
    elif [ $failed_checks -le 2 ]; then
        print_status "WARN" "Some non-critical issues detected. System is partially healthy ⚠️"
        exit 1
    else
        print_status "ERROR" "Multiple critical issues detected. System needs attention! 🚨"
        exit 2
    fi
}

# Check dependencies
if ! command -v curl >/dev/null 2>&1; then
    print_status "ERROR" "curl is required but not installed"
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    print_status "ERROR" "docker is required but not installed"
    exit 1
fi

if ! command -v bc >/dev/null 2>&1; then
    print_status "ERROR" "bc is required but not installed"
    exit 1
fi

# Run main function
main "$@"