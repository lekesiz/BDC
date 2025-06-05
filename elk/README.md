# BDC ELK Stack Implementation

## Overview

This directory contains the complete ELK (Elasticsearch, Logstash, Kibana) stack implementation for the BDC application, providing centralized logging, metrics collection, and comprehensive observability.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BDC ELK Stack                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Filebeat   │    │ Metricbeat  │    │ Application │     │
│  │   (Logs)    │    │ (Metrics)   │    │    Logs     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                    │                    │        │
│         └────────────────────┼────────────────────┘        │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │     Logstash      │                   │
│                    │   (Processing)    │                   │
│                    └─────────┬─────────┘                   │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │   Elasticsearch   │                   │
│                    │    (Storage)      │                   │
│                    └─────────┬─────────┘                   │
│                              │                             │
│                    ┌─────────▼─────────┐                   │
│                    │     Kibana        │                   │
│                    │ (Visualization)   │                   │
│                    └───────────────────┘                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Directory Structure

```
elk/
├── elasticsearch/
│   └── config/
│       └── elasticsearch.yml      # Elasticsearch configuration
├── logstash/
│   ├── config/
│   │   └── logstash.yml          # Logstash configuration
│   └── pipeline/
│       └── bdc-logs.conf         # Log processing pipeline
├── kibana/
│   ├── config/
│   │   └── kibana.yml            # Kibana configuration
│   └── dashboards/               # Pre-built dashboards
├── filebeat/
│   └── config/
│       └── filebeat.yml          # Log shipping configuration
├── metricbeat/
│   └── config/
│       └── metricbeat.yml        # Metrics collection configuration
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Deploy ELK Stack
```bash
# Basic ELK deployment
./scripts/deploy-elk-stack.sh

# With monitoring (Prometheus + Grafana)
./scripts/deploy-elk-stack.sh --monitoring

# Dry run to see what would be deployed
./scripts/deploy-elk-stack.sh --dry-run
```

### 2. Access Services
- **Kibana**: http://localhost:5601
- **Elasticsearch**: http://localhost:9200
- **Logstash**: http://localhost:9600

### 3. Configure Index Patterns in Kibana
1. Open Kibana at http://localhost:5601
2. Go to Stack Management → Index Patterns
3. Create patterns:
   - `filebeat-bdc-*` for application logs
   - `metricbeat-bdc-*` for system metrics
   - `bdc-*` for processed logs

## 📊 Data Collection

### Application Logs
- **Flask application logs**: JSON formatted with request context
- **Security audit logs**: Comprehensive security events
- **Nginx access/error logs**: Web server monitoring
- **Docker container logs**: Container-level logging

### System Metrics
- **System metrics**: CPU, memory, disk, network
- **Docker metrics**: Container performance
- **PostgreSQL metrics**: Database performance
- **Redis metrics**: Cache performance
- **HTTP metrics**: API endpoint monitoring

## 🔧 Configuration

### Environment Variables
Copy `.env.elk.template` to your `.env` file and configure:

```bash
# Memory allocation (adjust based on your system)
ELK_ELASTICSEARCH_MEMORY=1G
ELK_LOGSTASH_MEMORY=1G
ELK_KIBANA_MEMORY=512M

# Security
KIBANA_ENCRYPTION_KEY=your-32-character-secret-key-here

# Application context
BDC_ENVIRONMENT=production
BDC_VERSION=1.0.0
```

### System Requirements
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk**: 10GB free space for logs and indices
- **Linux kernel**: `vm.max_map_count >= 262144` for Elasticsearch

### Set vm.max_map_count (Linux/macOS)
```bash
# Temporary
sudo sysctl -w vm.max_map_count=262144

# Permanent
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
```

## 📈 Monitoring and Alerting

### Pre-configured Dashboards
- **System Overview**: CPU, memory, disk usage
- **Application Performance**: Response times, error rates
- **Security Events**: Authentication, access attempts
- **Database Performance**: Query performance, connections

### Alert Configuration
Edit `elk/logstash/pipeline/bdc-logs.conf` to configure alerts:

```yaml
# High-risk security events trigger alerts
if [risk_level] == "critical" or [risk_level] == "high" {
  mutate {
    add_tag => [ "security_alert" ]
  }
}
```

## 🔍 Log Analysis

### Search Examples

#### Application Errors
```
level:ERROR AND service:flask
```

#### Security Events
```
type:bdc-security AND risk_level:high
```

#### Performance Issues
```
response_time:>5000 AND service:nginx
```

#### User Activity
```
user_id:* AND event_type:LOGIN_SUCCESS
```

### Useful Queries
1. **Top Error Messages**: `level:ERROR | top 10 message.keyword`
2. **Response Time Distribution**: `service:nginx | percentiles response_time`
3. **Security Event Trends**: `type:bdc-security | date_histogram @timestamp interval:1h`
4. **Database Performance**: `service:postgresql | avg query_time`

## 🛠️ Maintenance

### Index Management
Logstash automatically creates time-based indices:
- `bdc-application-YYYY.MM.DD`
- `bdc-security-YYYY.MM.DD`
- `filebeat-bdc-YYYY.MM.DD`
- `metricbeat-bdc-YYYY.MM.DD`

### Cleanup Old Indices
```bash
# Delete indices older than 30 days
curl -X DELETE "localhost:9200/bdc-*-$(date -d '30 days ago' '+%Y.%m.%d')"
```

### Backup Configuration
```bash
# Backup Elasticsearch indices
docker exec bdc-elasticsearch \
  curl -X PUT "localhost:9200/_snapshot/backup_repo/snapshot_$(date +%Y%m%d)" \
  -H 'Content-Type: application/json' \
  -d '{"indices": "bdc-*,filebeat-*,metricbeat-*"}'
```

## 🔧 Troubleshooting

### Common Issues

#### Elasticsearch Won't Start
```bash
# Check vm.max_map_count
sysctl vm.max_map_count

# Check disk space
df -h

# Check logs
docker logs bdc-elasticsearch
```

#### High Memory Usage
```bash
# Reduce memory allocation in docker-compose.elk.yml
ELK_ELASTICSEARCH_MEMORY=512M
ELK_LOGSTASH_MEMORY=512M
```

#### No Data in Kibana
```bash
# Check if indices exist
curl http://localhost:9200/_cat/indices?v

# Check Filebeat status
docker logs bdc-filebeat

# Check Logstash pipeline
docker logs bdc-logstash
```

### Performance Tuning

#### Elasticsearch
- Increase `indices.memory.index_buffer_size` for heavy indexing
- Adjust `refresh_interval` based on search vs. indexing needs
- Use Index Lifecycle Management (ILM) for automatic cleanup

#### Logstash
- Increase `pipeline.workers` for higher throughput
- Adjust `pipeline.batch.size` based on memory
- Use persistent queues for reliability

#### Kibana
- Enable caching for dashboards
- Use date math in index patterns
- Optimize visualizations and queries

## 📝 Index Templates

### Application Logs Template
```json
{
  "index_patterns": ["bdc-application-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "refresh_interval": "30s"
  },
  "mappings": {
    "properties": {
      "timestamp": {"type": "date"},
      "level": {"type": "keyword"},
      "message": {"type": "text"},
      "request_id": {"type": "keyword"},
      "user_id": {"type": "keyword"}
    }
  }
}
```

## 🚨 Security Considerations

1. **Network Security**: ELK services run on internal Docker network
2. **Authentication**: Consider enabling X-Pack security for production
3. **SSL/TLS**: Configure SSL for external access
4. **Data Privacy**: Implement field-level security for sensitive data
5. **Audit Logging**: All ELK actions are logged for compliance

## 🔄 Updates and Upgrades

### Update ELK Stack
```bash
# Pull latest images
docker compose -f docker-compose.portable.yml -f docker-compose.elk.yml pull

# Recreate containers
./scripts/deploy-elk-stack.sh --force-recreate
```

### Configuration Changes
1. Update configuration files in `elk/` directory
2. Restart specific services:
```bash
docker compose -f docker-compose.portable.yml -f docker-compose.elk.yml restart logstash
```

## 📊 Capacity Planning

### Storage Requirements
- **Application logs**: ~100MB/day (estimated)
- **Security logs**: ~50MB/day (estimated)
- **Metrics**: ~200MB/day (estimated)
- **Total**: ~350MB/day (~10GB/month)

### Resource Recommendations

| Environment | CPU | Memory | Storage |
|-------------|-----|--------|---------|
| Development | 2 cores | 4GB | 50GB |
| Staging | 4 cores | 8GB | 100GB |
| Production | 8 cores | 16GB | 500GB+ |

## 🎯 Next Steps

1. **Configure Dashboards**: Import pre-built dashboards
2. **Set Up Alerts**: Configure alerting for critical events
3. **Optimize Performance**: Tune based on your data volume
4. **Implement Security**: Enable authentication and SSL
5. **Monitor Usage**: Track resource utilization and performance

## 📞 Support

For issues and questions:
1. Check container logs: `docker logs <container-name>`
2. Review Elasticsearch cluster health: `curl http://localhost:9200/_cluster/health`
3. Verify service status: `docker compose ps`
4. Check system resources: `docker stats`