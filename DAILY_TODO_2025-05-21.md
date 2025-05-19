# DAILY TODO - 2025-05-21

## Session Goals
1. Program Management API refactor to modular v2 package
2. Add Prometheus monitoring exporter to Flask backend
3. Start S3 document storage POC
4. Increase backend coverage to ≥ 70 % with ProgramService tests

## Task List
- [x] 1. Create this daily TODO file
- [x] 2. Extract program endpoints to `app/api/programs_v2/` (list endpoint)
- [x] 3. Register new blueprint and migrate tests
- [x] 4. Integrate `prometheus_flask_exporter` and expose `/metrics`
- [x] 5. Add env config and update docker-compose.dev.yml
- [~] 6. Implement minimal S3 storage adapter in `storage_service.py` (feature flag added)
- [~] 7. Add Program model test; coverage increment
- [ ] 8. Update PROJECT_MEMORY.md with progress summary