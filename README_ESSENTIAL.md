# BDC (Bilan de Compétence) - Essential Documentation

## Project Overview
BDC is a comprehensive competency assessment platform built with modern web technologies. It provides tools for trainers to evaluate students, manage programs, and track progress.

## Tech Stack
- **Backend**: Flask 3.0.0, SQLAlchemy 2.0.25, PostgreSQL
- **Frontend**: React 18.2.0, Vite 6.3.5, Tailwind CSS
- **Deployment**: Docker, Docker Compose
- **Security**: JWT Authentication, CORS, Rate Limiting

## Quick Start

### Docker Deployment (Recommended)
```bash
# 1. Clone repository
git clone <repository-url> bdc && cd bdc

# 2. Copy environment template
cp .env.production.template .env

# 3. Edit environment variables
nano .env

# 4. Deploy with Docker
./scripts/docker-deploy.sh

# 5. Optional: Deploy with monitoring
./scripts/docker-deploy.sh --monitoring
```

### Local Development
```bash
# Backend
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
python run_app.py

# Frontend
cd client
npm install
npm run dev
```

## Default Credentials
- **Admin**: admin@bdc.com / Admin123!
- **Tenant Admin**: tenant@bdc.com / Tenant123!
- **Trainer**: trainer@bdc.com / Trainer123!
- **Student**: student@bdc.com / Student123!

## Service URLs
- **Frontend**: http://localhost:5173 (dev) or http://localhost (prod)
- **Backend API**: http://localhost:5001 (dev) or http://localhost:5000 (prod)
- **Grafana**: http://localhost:3000 (if monitoring enabled)
- **Prometheus**: http://localhost:9090 (if monitoring enabled)

## Key Features
- Multi-tenant support
- Role-based access control (RBAC)
- Real-time notifications via WebSocket
- Document management with versioning
- Calendar and appointment scheduling
- Evaluation and test management
- Performance monitoring
- AI-powered features (optional)

## Project Structure
```
BDC/
├── client/                 # React frontend
├── server/                # Flask backend
├── docker/                # Docker configurations
├── scripts/               # Deployment scripts
├── docs/                  # Documentation
└── data/                  # Persistent data (Docker)
```

## Documentation
- [API Documentation](./API_DOCUMENTATION_2025.md)
- [Docker Deployment Guide](./DOCKER_DEPLOYMENT_GUIDE.md)
- [Development Guide](./DEVELOPING.md)
- [Security Guide](./docs/security/SECURITY_OVERVIEW.md)

## Maintenance

### Backup
```bash
# Full backup
tar -czf bdc-backup-$(date +%Y%m%d).tar.gz data/

# Database only
docker compose exec postgres pg_dump -U bdc_user bdc_production > backup.sql
```

### Update
```bash
# Pull latest changes
git pull origin main

# Rebuild and deploy
./scripts/docker-deploy.sh --force-recreate
```

### Monitoring
- **Logs**: `docker compose logs -f [service-name]`
- **Health**: `./scripts/production-health-check.sh`
- **Metrics**: Access Grafana at http://localhost:3000

## Troubleshooting
See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common issues and solutions.

## License
See [LICENSE](./LICENSE) file for details.

---
*Last updated: January 2025*