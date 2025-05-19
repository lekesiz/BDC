# BDC Monitoring & Alerting Setup Guide

## Overview
This guide covers the setup of comprehensive monitoring and alerting for the BDC application in production.

## 1. Application Performance Monitoring (APM)

### Sentry Setup (Error Tracking)
```bash
# Install Sentry SDK
pip install sentry-sdk[flask]
```

Backend integration:
```python
# In your Flask app
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[FlaskIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

Frontend integration:
```javascript
// Install Sentry
npm install @sentry/react @sentry/tracing

// In your main App.jsx
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
  integrations: [new BrowserTracing()],
  tracesSampleRate: 0.1,
  environment: "production"
});
```

### New Relic Setup (Performance Monitoring)
```bash
# Install New Relic agent
pip install newrelic
```

Configure New Relic:
```ini
# newrelic.ini
[newrelic]
license_key = YOUR_LICENSE_KEY
app_name = BDC Production
monitor_mode = true
log_level = info
ssl = true
high_security = true
transaction_tracer.enabled = true
error_collector.enabled = true
browser_monitoring.auto_instrument = true
```

Start with New Relic:
```bash
NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn app:app
```

## 2. Infrastructure Monitoring

### Prometheus + Grafana Setup

Install Prometheus:
```bash
# Download and install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.37.0/prometheus-2.37.0.linux-amd64.tar.gz
tar xvf prometheus-2.37.0.linux-amd64.tar.gz
sudo mv prometheus-2.37.0.linux-amd64 /opt/prometheus
```

Prometheus configuration:
```yaml
# /opt/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bdc-backend'
    static_configs:
      - targets: ['localhost:5000']
  
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']
  
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['localhost:9187']
  
  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['localhost:9121']
```

Install Grafana:
```bash
# Add Grafana repository
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl enable grafana-server
sudo systemctl start grafana-server
```

### Node Exporter (System Metrics)
```bash
# Download and install
wget https://github.com/prometheus/node_exporter/releases/download/v1.3.1/node_exporter-1.3.1.linux-amd64.tar.gz
tar xvf node_exporter-1.3.1.linux-amd64.tar.gz
sudo mv node_exporter-1.3.1.linux-amd64/node_exporter /usr/local/bin/

# Create systemd service
sudo nano /etc/systemd/system/node_exporter.service
```

Service file:
```ini
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
```

### PostgreSQL Exporter
```bash
# Install postgres_exporter
wget https://github.com/prometheus-community/postgres_exporter/releases/download/v0.11.1/postgres_exporter-0.11.1.linux-amd64.tar.gz
tar xvf postgres_exporter-0.11.1.linux-amd64.tar.gz
sudo mv postgres_exporter-0.11.1.linux-amd64/postgres_exporter /usr/local/bin/

# Set connection string
export DATA_SOURCE_NAME="postgresql://postgres:password@localhost:5432/bdc_production?sslmode=disable"
```

### Redis Exporter
```bash
# Install redis_exporter
wget https://github.com/oliver006/redis_exporter/releases/download/v1.43.0/redis_exporter-v1.43.0.linux-amd64.tar.gz
tar xvf redis_exporter-v1.43.0.linux-amd64.tar.gz
sudo mv redis_exporter-v1.43.0.linux-amd64/redis_exporter /usr/local/bin/
```

## 3. Log Management

### ELK Stack Setup (Elasticsearch, Logstash, Kibana)

Install Elasticsearch:
```bash
# Add Elastic repository
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
sudo apt-get update
sudo apt-get install elasticsearch

# Configure Elasticsearch
sudo nano /etc/elasticsearch/elasticsearch.yml
```

Configuration:
```yaml
cluster.name: bdc-cluster
node.name: bdc-node-1
network.host: localhost
http.port: 9200
```

Install Logstash:
```bash
sudo apt-get install logstash

# Configure Logstash
sudo nano /etc/logstash/conf.d/bdc.conf
```

Logstash configuration:
```ruby
input {
  file {
    path => "/var/log/bdc/*.log"
    start_position => "beginning"
    type => "bdc-app"
  }
  
  file {
    path => "/var/log/nginx/*.log"
    start_position => "beginning"
    type => "nginx"
  }
}

filter {
  if [type] == "bdc-app" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }
  
  if [type] == "nginx" {
    grok {
      match => { "message" => "%{COMBINEDAPACHELOG}" }
    }
  }
  
  date {
    match => [ "timestamp", "ISO8601" ]
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "bdc-%{+YYYY.MM.dd}"
  }
}
```

Install Kibana:
```bash
sudo apt-get install kibana
sudo systemctl enable kibana
sudo systemctl start kibana
```

### Centralized Logging with Fluentd
```bash
# Install Fluentd
curl -L https://toolbelt.treasuredata.com/sh/install-ubuntu-focal-td-agent4.sh | sh

# Configure Fluentd
sudo nano /etc/td-agent/td-agent.conf
```

Configuration:
```ruby
<source>
  @type tail
  path /var/log/bdc/app.log
  pos_file /var/log/td-agent/bdc.log.pos
  tag bdc.app
  <parse>
    @type json
  </parse>
</source>

<match bdc.**>
  @type elasticsearch
  host localhost
  port 9200
  logstash_format true
  logstash_prefix bdc
  buffer_type memory
  flush_interval 10s
</match>
```

## 4. Alerts Configuration

### AlertManager Setup (Prometheus)
```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@yourdomain.com'
  smtp_auth_username: 'alerts@yourdomain.com'
  smtp_auth_password: 'your-password'

route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-emails'
  routes:
  - match:
      severity: critical
    receiver: 'pagerduty'

receivers:
- name: 'team-emails'
  email_configs:
  - to: 'team@yourdomain.com'
    require_tls: true

- name: 'pagerduty'
  pagerduty_configs:
  - service_key: 'YOUR_PAGERDUTY_KEY'
```

### Prometheus Alert Rules
```yaml
# alerts.yml
groups:
- name: bdc_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(flask_http_request_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is above 10% for 5 minutes"
  
  - alert: HighResponseTime
    expr: histogram_quantile(0.95, flask_http_request_duration_seconds_bucket) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High response time"
      description: "95th percentile response time is above 500ms"
  
  - alert: DatabaseDown
    expr: up{job="postgres-exporter"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Database is down"
      description: "PostgreSQL database is not responding"
  
  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is above 90%"
  
  - alert: DiskSpaceLow
    expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Low disk space"
      description: "Disk space is below 10%"
```

## 5. Custom Dashboards

### Grafana Dashboard JSON
```json
{
  "dashboard": {
    "title": "BDC Production Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(flask_http_request_total[5m])"
          }
        ]
      },
      {
        "title": "Response Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, flask_http_request_duration_seconds_bucket)"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(flask_http_request_total{status=~\"5..\"}[5m])"
          }
        ]
      },
      {
        "title": "Active Users",
        "targets": [
          {
            "expr": "bdc_active_users"
          }
        ]
      }
    ]
  }
}
```

## 6. Health Check Endpoints

Backend health checks:
```python
from flask import jsonify
import psutil
import redis

@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/health/detailed')
def detailed_health():
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'disk_space': check_disk_space(),
        'memory': check_memory()
    }
    
    status = 'healthy' if all(checks.values()) else 'unhealthy'
    
    return jsonify({
        'status': status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    })

def check_database():
    try:
        db.session.execute('SELECT 1')
        return True
    except:
        return False

def check_redis():
    try:
        r = redis.Redis.from_url(app.config['REDIS_URL'])
        r.ping()
        return True
    except:
        return False

def check_disk_space():
    usage = psutil.disk_usage('/')
    return usage.percent < 90

def check_memory():
    memory = psutil.virtual_memory()
    return memory.percent < 90
```

## 7. Monitoring Scripts

### Daily health report script
```bash
#!/bin/bash
# daily-health-report.sh

REPORT_FILE="/var/log/bdc/health-report-$(date +%Y%m%d).log"

echo "BDC Daily Health Report - $(date)" > $REPORT_FILE
echo "=================================" >> $REPORT_FILE

# Check services
echo -e "\nService Status:" >> $REPORT_FILE
systemctl status bdc >> $REPORT_FILE
systemctl status postgresql >> $REPORT_FILE
systemctl status redis >> $REPORT_FILE
systemctl status nginx >> $REPORT_FILE

# Check disk space
echo -e "\nDisk Usage:" >> $REPORT_FILE
df -h >> $REPORT_FILE

# Check memory
echo -e "\nMemory Usage:" >> $REPORT_FILE
free -h >> $REPORT_FILE

# Check database size
echo -e "\nDatabase Size:" >> $REPORT_FILE
sudo -u postgres psql -d bdc_production -c "SELECT pg_database_size('bdc_production');" >> $REPORT_FILE

# Check error logs
echo -e "\nRecent Errors:" >> $REPORT_FILE
grep ERROR /var/log/bdc/app.log | tail -20 >> $REPORT_FILE

# Send email
mail -s "BDC Daily Health Report" admin@yourdomain.com < $REPORT_FILE
```

## 8. Uptime Monitoring

### UptimeRobot Configuration
1. Add monitor for https://yourdomain.com
2. Set check interval: 5 minutes
3. Configure alerts:
   - Email
   - SMS
   - Webhook

### Pingdom Setup
1. Create transaction check
2. Monitor critical user flows:
   - Login
   - Dashboard load
   - API response

## 9. Performance Benchmarking

### Load testing with Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class BDCUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/api/dashboard", 
            headers={"Authorization": f"Bearer {self.token}"})
    
    @task(2)
    def list_beneficiaries(self):
        self.client.get("/api/beneficiaries",
            headers={"Authorization": f"Bearer {self.token}"})
    
    @task(1)
    def create_beneficiary(self):
        self.client.post("/api/beneficiaries",
            json={"name": "Test User", "email": "test@test.com"},
            headers={"Authorization": f"Bearer {self.token}"})
```

Run load test:
```bash
locust -f locustfile.py --host=https://yourdomain.com --users=100 --spawn-rate=10
```

## 10. Incident Response

### On-call rotation
```yaml
# pagerduty.yml
schedules:
  - name: "BDC On-Call"
    time_zone: "America/New_York"
    layers:
      - name: "Primary"
        start: "2023-01-01T09:00:00"
        rotation_virtual_start: "2023-01-01T09:00:00"
        users:
          - email: "engineer1@company.com"
          - email: "engineer2@company.com"
        rotation_turn_length_seconds: 604800  # 1 week
```

### Incident response playbook
1. **Acknowledge alert** within 5 minutes
2. **Assess severity**:
   - P1: Service down
   - P2: Performance degraded
   - P3: Non-critical issue
3. **Initial response**:
   - Check monitoring dashboards
   - Review recent deployments
   - Check error logs
4. **Escalation path**:
   - P1: Notify team lead immediately
   - P2: Update status page
   - P3: Create ticket for next business day
5. **Resolution**:
   - Fix issue
   - Monitor for 30 minutes
   - Create post-mortem document

## Monitoring Checklist

### Daily
- [ ] Check error rates
- [ ] Review performance metrics
- [ ] Monitor disk space
- [ ] Check backup status

### Weekly
- [ ] Review security logs
- [ ] Check SSL certificate expiry
- [ ] Analyze slow queries
- [ ] Update monitoring thresholds

### Monthly
- [ ] Performance trending
- [ ] Capacity planning
- [ ] Security audit
- [ ] Disaster recovery test

---

This comprehensive monitoring setup ensures the BDC application runs smoothly in production with proactive alerting and detailed visibility into system health.