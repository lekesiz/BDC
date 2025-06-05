# BDC Comprehensive Monitoring Stack

A complete monitoring solution for the BDC application providing real-time system metrics, alerting, and observability.

## 🚀 Features

### Core Monitoring Components
- **Prometheus** - Metrics collection and storage
- **Grafana** - Visualization and dashboards
- **AlertManager** - Alert handling and routing
- **Node Exporter** - System metrics
- **cAdvisor** - Container metrics
- **Blackbox Exporter** - External service monitoring

### Database & Cache Monitoring
- **PostgreSQL Exporter** - Database performance metrics
- **Redis Exporter** - Cache performance metrics

### Log Management
- **Loki** - Log aggregation and storage
- **Promtail** - Log collection and shipping

### Custom Application Metrics
- **BDC Metrics Exporter** - Application-specific metrics
- User activity tracking
- Business metrics (beneficiaries, programs, evaluations)
- Performance monitoring

## 📊 Monitoring Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                BDC Monitoring Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  BDC App    │    │ PostgreSQL  │    │   Redis     │     │
│  │ (Backend)   │    │ (Database)  │    │  (Cache)    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                    │                    │        │
│         └────────────────────┼────────────────────┘        │
│                              │                             │
│  ┌─────────────┐    ┌─────────▼─────────┐    ┌─────────────┐│
│  │   System    │    │   Exporters       │    │   Logs      ││
│  │ (Node/cAdv) │    │ (App/DB/Redis)    │    │(Loki/Promtail)││
│  └─────────────┘    └─────────┬─────────┘    └─────────────┘│
│         │                    │                    │        │
│         └────────────────────┼────────────────────┘        │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │   Prometheus      │                   │
│                    │ (Metrics Storage) │                   │
│                    └─────────┬─────────┘                   │
│                              │                             │
│         ┌────────────────────┼────────────────────┐        │
│         │                    │                    │        │
│  ┌──────▼──────┐    ┌────────▼────────┐    ┌──────▼──────┐ │
│  │  Grafana    │    │ AlertManager    │    │   React     │ │
│  │(Dashboards) │    │   (Alerts)      │    │ Dashboard   │ │
│  └─────────────┘    └─────────────────┘    └─────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Quick Start

### 1. Deploy Monitoring Stack

```bash
# Deploy the complete monitoring stack
./scripts/deploy-monitoring-stack.sh

# Deploy with logs
./scripts/deploy-monitoring-stack.sh --logs
```

### 2. Access Monitoring Tools

Once deployed, access the monitoring tools:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **AlertManager**: http://localhost:9093
- **BDC System Dashboard**: http://localhost:5173/admin/monitoring

### 3. Configure Environment

Update your `.env.production` file with monitoring settings:

```bash
# Monitoring Configuration
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
GRAFANA_ADMIN_PASSWORD=your-secure-password
GRAFANA_SECRET_KEY=your-grafana-secret-key
ALERTMANAGER_PORT=9093

# Alert Channels
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
ADMIN_EMAILS=admin@yourcompany.com
ALERT_WEBHOOK_URL=https://your-webhook-endpoint.com/alerts
```

## 📈 Metrics Collected

### System Metrics
- **CPU Usage** - Per-core and overall CPU utilization
- **Memory Usage** - RAM usage, available memory, swap
- **Disk Usage** - Disk space, I/O operations
- **Network** - Network traffic, connections
- **Load Average** - System load over time

### Application Metrics
- **Request Metrics** - Request count, response times, error rates
- **User Activity** - Active users, sessions, login activity
- **Business Metrics** - Beneficiaries, programs, evaluations, documents
- **Database Performance** - Connections, query times, slow queries
- **Cache Performance** - Hit rates, memory usage, evictions

### Container Metrics
- **Resource Usage** - CPU, memory, network per container
- **Container Health** - Restart counts, status, uptime
- **Docker Metrics** - Image sizes, build times

## 🚨 Alerting Rules

### System Alerts
- **High CPU Usage** - > 80% for 5 minutes
- **High Memory Usage** - > 85% for 5 minutes
- **High Disk Usage** - > 85% for 5 minutes
- **High Load Average** - > 2 for 10 minutes

### Application Alerts
- **Application Down** - Service unavailable for 1 minute
- **High Response Time** - 95th percentile > 2 seconds for 5 minutes
- **High Error Rate** - > 10% error rate for 5 minutes
- **Critical Error Rate** - > 20% error rate for 2 minutes

### Database Alerts
- **Database Down** - PostgreSQL unavailable for 1 minute
- **High Connection Usage** - > 80% of max connections for 5 minutes
- **Slow Queries** - Average query time > 1 second for 5 minutes

### Security Alerts
- **High Auth Failures** - > 10 failures per second for 5 minutes
- **Potential Brute Force** - > 50 failures per second for 2 minutes
- **SSL Certificate Expiry** - Certificate expires in < 7 days

## 📊 Grafana Dashboards

### Pre-configured Dashboards
1. **BDC System Overview** - High-level system health
2. **Application Performance** - Request metrics and response times
3. **Database Performance** - PostgreSQL metrics and queries
4. **Infrastructure Monitoring** - System resources and containers
5. **Business Metrics** - User activity and application usage

### Custom Dashboard Features
- **Real-time Updates** - 30-second refresh intervals
- **Interactive Charts** - Drill-down capabilities
- **Alert Integration** - Visual alert indicators
- **Mobile Responsive** - Optimized for mobile viewing

## 🔍 Log Management

### Log Sources
- **Application Logs** - BDC backend application logs
- **System Logs** - Operating system logs
- **Container Logs** - Docker container logs
- **Access Logs** - Web server access logs
- **Database Logs** - PostgreSQL logs

### Log Processing
- **Structured Logging** - JSON format with consistent fields
- **Log Parsing** - Automatic parsing of log levels and messages
- **Log Retention** - Configurable retention policies
- **Log Search** - Full-text search capabilities

## 🛠️ Configuration

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'bdc-backend'
    static_configs:
      - targets: ['app-exporter:8000']
    scrape_interval: 15s
```

### AlertManager Configuration
```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'default'
```

### Grafana Provisioning
- **Datasources** - Automatically configured Prometheus and Loki
- **Dashboards** - Pre-loaded BDC-specific dashboards
- **Plugins** - Essential visualization plugins

## 🔧 Maintenance

### Regular Tasks
1. **Update Retention Policies** - Adjust based on storage capacity
2. **Review Alert Thresholds** - Fine-tune based on application behavior
3. **Dashboard Updates** - Add new metrics and visualizations
4. **Security Updates** - Keep monitoring tools updated

### Backup and Recovery
- **Prometheus Data** - Backup time-series data
- **Grafana Configuration** - Export dashboards and settings
- **AlertManager Config** - Backup alert routing rules

### Scaling Considerations
- **Horizontal Scaling** - Multiple Prometheus instances
- **Federation** - Aggregate metrics from multiple sources
- **Remote Storage** - Long-term storage solutions
- **Load Balancing** - Distribute monitoring load

## 📞 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check service status
docker-compose -f docker-compose.monitoring.yml ps

# View service logs
docker-compose -f docker-compose.monitoring.yml logs prometheus
```

#### No Metrics Data
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify metrics endpoint
curl http://localhost:8000/metrics
```

#### Grafana Connection Issues
```bash
# Check Grafana logs
docker logs bdc-grafana

# Verify datasource configuration
curl http://localhost:3000/api/datasources
```

### Performance Optimization
- **Reduce Scrape Intervals** - For high-cardinality metrics
- **Metric Filtering** - Remove unnecessary metrics
- **Storage Optimization** - Configure appropriate retention
- **Query Optimization** - Optimize dashboard queries

## 🚀 Advanced Features

### Custom Metrics
```python
# Add custom application metrics
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter('bdc_custom_requests_total', 'Custom requests')
PROCESSING_TIME = Histogram('bdc_processing_seconds', 'Processing time')
```

### Alert Integrations
- **Slack Integration** - Real-time alert notifications
- **Email Alerts** - Critical alert notifications
- **Webhook Integration** - Custom alert handling
- **PagerDuty Integration** - On-call alerting

### Monitoring Best Practices
1. **Monitor What Matters** - Focus on user-impacting metrics
2. **Set Meaningful Alerts** - Avoid alert fatigue
3. **Document Runbooks** - Clear incident response procedures
4. **Regular Reviews** - Continuously improve monitoring

## 📈 Metrics Reference

### Application Metrics
| Metric | Type | Description |
|--------|------|-------------|
| `bdc_requests_total` | Counter | Total HTTP requests |
| `bdc_request_duration_seconds` | Histogram | Request latency |
| `bdc_active_users` | Gauge | Current active users |
| `bdc_total_beneficiaries` | Gauge | Total beneficiaries |
| `bdc_error_rate` | Gauge | Application error rate |

### System Metrics
| Metric | Type | Description |
|--------|------|-------------|
| `node_cpu_seconds_total` | Counter | CPU time spent |
| `node_memory_MemAvailable_bytes` | Gauge | Available memory |
| `node_filesystem_avail_bytes` | Gauge | Available disk space |
| `node_load1` | Gauge | 1-minute load average |

## 🔗 External Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [AlertManager Guide](https://prometheus.io/docs/alerting/latest/alertmanager/)
- [BDC Monitoring Best Practices](./monitoring-best-practices.md)

## 📝 License

This monitoring configuration is part of the BDC project and follows the same licensing terms.