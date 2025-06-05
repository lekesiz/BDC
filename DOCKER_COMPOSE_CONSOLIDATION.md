# Docker Compose Consolidation

## Current Structure (After Cleanup)

### Main Files Kept:
1. **docker-compose.yml** - Base configuration
2. **docker-compose.dev.yml** - Development overrides
3. **docker-compose.prod.yml** - Production configuration
4. **docker-compose.production.yml** - Alternative production (to be merged)
5. **docker-compose.monitoring.yml** - Monitoring stack (Prometheus, Grafana)
6. **docker-compose.elk.yml** - ELK stack for logging
7. **docker-compose.jaeger.yml** - Distributed tracing

### Files Archived:
- docker-compose.api.yml
- docker-compose.app.yml
- docker-compose.custom.yml
- docker-compose.frontend.yml
- docker-compose.html.yml
- docker-compose.local-test.yml
- docker-compose.portable.yml
- docker-compose.test.yml

## Recommended Final Structure:

```
docker/
├── docker-compose.yml          # Base configuration
├── docker-compose.dev.yml      # Development overrides
├── docker-compose.prod.yml     # Production configuration
└── monitoring/
    ├── docker-compose.monitoring.yml  # Prometheus + Grafana
    ├── docker-compose.elk.yml         # ELK Stack
    └── docker-compose.jaeger.yml      # Tracing
```

## Usage:

### Development:
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Production with Monitoring:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f monitoring/docker-compose.monitoring.yml up -d
```