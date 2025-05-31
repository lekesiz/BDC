#!/bin/bash
# Performance tuning script for BDC production server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "Please run as root"
        exit 1
    fi
}

# Optimize Linux kernel parameters
optimize_kernel() {
    log_info "Optimizing kernel parameters..."
    
    cat >> /etc/sysctl.conf << 'EOF'

# BDC Production Optimizations
# Network optimizations
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 65536 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# File descriptor limits
fs.file-max = 2097152

# Virtual memory
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5

# Security
kernel.randomize_va_space = 2
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.secure_redirects = 0
net.ipv4.conf.default.secure_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Connection tracking
net.netfilter.nf_conntrack_max = 1000000
net.netfilter.nf_conntrack_tcp_timeout_established = 600

EOF
    
    # Apply immediately
    sysctl -p
    
    log_info "Kernel parameters optimized"
}

# Optimize file system
optimize_filesystem() {
    log_info "Optimizing file system..."
    
    # Create optimized mount options
    if ! grep -q "noatime" /etc/fstab; then
        log_warn "Consider adding 'noatime' to your filesystem mount options in /etc/fstab"
        log_warn "Example: /dev/sda1 / ext4 defaults,noatime 0 1"
    fi
    
    # Optimize ext4 filesystems
    if command -v tune2fs &> /dev/null; then
        log_info "Optimizing ext4 filesystems..."
        for fs in $(mount | grep ext4 | awk '{print $1}'); do
            tune2fs -o journal_data_writeback $fs 2>/dev/null || true
        done
    fi
    
    log_info "File system optimization completed"
}

# Optimize PostgreSQL
optimize_postgresql() {
    log_info "Optimizing PostgreSQL configuration..."
    
    PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oP '\d+\.\d+' | head -1)
    PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
    
    if [ -f "$PG_CONF" ]; then
        # Backup original configuration
        cp "$PG_CONF" "$PG_CONF.backup.$(date +%Y%m%d)"
        
        # Calculate memory settings based on available RAM
        TOTAL_RAM=$(free -m | awk 'NR==2{print $2}')
        SHARED_BUFFERS=$((TOTAL_RAM / 4))
        EFFECTIVE_CACHE_SIZE=$((TOTAL_RAM * 3 / 4))
        WORK_MEM=$((TOTAL_RAM / 100))
        MAINTENANCE_WORK_MEM=$((TOTAL_RAM / 16))
        
        cat >> "$PG_CONF" << EOF

# BDC Production Optimizations
# Memory settings
shared_buffers = ${SHARED_BUFFERS}MB
effective_cache_size = ${EFFECTIVE_CACHE_SIZE}MB
work_mem = ${WORK_MEM}MB
maintenance_work_mem = ${MAINTENANCE_WORK_MEM}MB

# Checkpoint settings
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
max_wal_size = 4GB
min_wal_size = 1GB

# Connection settings
max_connections = 200
max_prepared_transactions = 200

# Performance settings
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
max_parallel_maintenance_workers = 4

# Logging
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0

# Autovacuum
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min
autovacuum_vacuum_threshold = 50
autovacuum_analyze_threshold = 50
autovacuum_vacuum_scale_factor = 0.2
autovacuum_analyze_scale_factor = 0.1
autovacuum_vacuum_cost_delay = 20ms
autovacuum_vacuum_cost_limit = 200

EOF
        
        systemctl restart postgresql
        log_info "PostgreSQL configuration optimized"
    else
        log_warn "PostgreSQL configuration file not found"
    fi
}

# Optimize Redis
optimize_redis() {
    log_info "Optimizing Redis configuration..."
    
    REDIS_CONF="/etc/redis/redis.conf"
    
    if [ -f "$REDIS_CONF" ]; then
        # Backup original configuration
        cp "$REDIS_CONF" "$REDIS_CONF.backup.$(date +%Y%m%d)"
        
        # Calculate memory settings
        TOTAL_RAM=$(free -m | awk 'NR==2{print $2}')
        REDIS_MEMORY=$((TOTAL_RAM / 8))  # Use 1/8 of total RAM for Redis
        
        cat >> "$REDIS_CONF" << EOF

# BDC Production Optimizations
# Memory settings
maxmemory ${REDIS_MEMORY}mb
maxmemory-policy allkeys-lru

# Persistence settings
save 900 1
save 300 10
save 60 10000

# Network settings
tcp-keepalive 300
tcp-backlog 511
timeout 0

# Performance settings
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
list-compress-depth 0
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000

# Security
protected-mode yes
bind 127.0.0.1

EOF
        
        systemctl restart redis
        log_info "Redis configuration optimized"
    else
        log_warn "Redis configuration file not found"
    fi
}

# Optimize Nginx
optimize_nginx() {
    log_info "Optimizing Nginx configuration..."
    
    NGINX_CONF="/etc/nginx/nginx.conf"
    
    if [ -f "$NGINX_CONF" ]; then
        # Backup original configuration
        cp "$NGINX_CONF" "$NGINX_CONF.backup.$(date +%Y%m%d)"
        
        # Get number of CPU cores
        CPU_CORES=$(nproc)
        
        cat > "$NGINX_CONF" << EOF
user www-data;
worker_processes $CPU_CORES;
worker_rlimit_nofile 65535;
pid /run/nginx.pid;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Buffer settings
    client_body_buffer_size 128k;
    client_max_body_size 10m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;
    
    # Timeout settings
    client_header_timeout 3m;
    client_body_timeout 3m;
    send_timeout 3m;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # File cache
    open_file_cache max=200000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;
    
    # Include mime types and other configs
    include /etc/nginx/mime.types;
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
EOF
        
        # Test configuration and restart
        nginx -t && systemctl restart nginx
        log_info "Nginx configuration optimized"
    else
        log_warn "Nginx configuration file not found"
    fi
}

# Set system limits
optimize_limits() {
    log_info "Optimizing system limits..."
    
    cat >> /etc/security/limits.conf << 'EOF'

# BDC Production Limits
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
root soft nofile 65535
root hard nofile 65535
root soft nproc 65535
root hard nproc 65535

EOF
    
    # Update systemd limits
    cat > /etc/systemd/system.conf.d/limits.conf << 'EOF'
[Manager]
DefaultLimitNOFILE=65535
DefaultLimitNPROC=65535
EOF
    
    systemctl daemon-reload
    
    log_info "System limits optimized"
}

# Optimize application server (Gunicorn)
optimize_gunicorn() {
    log_info "Creating optimized Gunicorn configuration..."
    
    mkdir -p /etc/bdc
    
    cat > /etc/bdc/gunicorn.conf.py << 'EOF'
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5

# Restart workers
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "/var/log/bdc/gunicorn_access.log"
errorlog = "/var/log/bdc/gunicorn_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'bdc_app'

# Server mechanics
preload_app = True
daemon = False
pidfile = '/var/run/gunicorn.pid'
tmp_upload_dir = '/tmp'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

EOF
    
    mkdir -p /var/log/bdc
    chown www-data:www-data /var/log/bdc
    
    log_info "Gunicorn configuration created"
}

# Setup monitoring and alerts
setup_monitoring() {
    log_info "Setting up basic monitoring..."
    
    # Install basic monitoring tools
    apt-get update
    apt-get install -y htop iotop nethogs sysstat
    
    # Enable sysstat
    systemctl enable sysstat
    systemctl start sysstat
    
    # Create performance monitoring script
    cat > /usr/local/bin/bdc-monitor.sh << 'EOF'
#!/bin/bash
# BDC Performance Monitoring Script

LOG_FILE="/var/log/bdc/performance.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Performance Check" >> $LOG_FILE

# CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "CPU Usage: ${CPU_USAGE}%" >> $LOG_FILE

# Memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
echo "Memory Usage: ${MEMORY_USAGE}%" >> $LOG_FILE

# Disk usage
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}')
echo "Disk Usage: $DISK_USAGE" >> $LOG_FILE

# Load average
LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}')
echo "Load Average:$LOAD_AVG" >> $LOG_FILE

# Check if any service is down
systemctl is-active --quiet nginx || echo "WARNING: Nginx is down" >> $LOG_FILE
systemctl is-active --quiet postgresql || echo "WARNING: PostgreSQL is down" >> $LOG_FILE
systemctl is-active --quiet redis || echo "WARNING: Redis is down" >> $LOG_FILE

echo "" >> $LOG_FILE
EOF
    
    chmod +x /usr/local/bin/bdc-monitor.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/bdc-monitor.sh") | crontab -
    
    log_info "Basic monitoring setup completed"
}

# Main function
main() {
    check_root
    
    log_info "Starting BDC production performance tuning..."
    
    optimize_kernel
    optimize_filesystem
    optimize_limits
    optimize_nginx
    optimize_postgresql
    optimize_redis
    optimize_gunicorn
    setup_monitoring
    
    log_info "Performance tuning completed!"
    log_info "Please reboot the system to ensure all changes take effect."
    log_info "Monitor the system with: tail -f /var/log/bdc/performance.log"
}

main "$@"