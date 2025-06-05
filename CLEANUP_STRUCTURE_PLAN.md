# BDC Project Structure Cleanup Plan

## Current Issues
1. **200+ duplicate files** causing confusion
2. **Multiple implementations** of same services
3. **Redundant test files** (150+ test files)
4. **Multiple entry points** for server
5. **Scattered configuration** files

## Cleanup Strategy

### Phase 1: Server Cleanup ✅ IN PROGRESS

#### Entry Points (Keep only essential)
- ✅ Keep: `wsgi.py` (production)
- ✅ Keep: `run_local.py` (development)
- ✅ Archive: `run_app.py`, `run_server.py`, `run_flask.py`, `simple_app.py`

#### Services Consolidation
**Auth Service:**
- Keep: `app/services/v2/auth_service.py` → rename to `app/services/auth_service.py`
- Remove: auth_service_refactored.py, auth_service_2fa.py, improved_auth_service.py

**Other Services:**
- Keep v2 versions where available
- Merge features from "improved" versions
- Remove all "_refactored" versions

#### API Endpoints
- Keep: One endpoint per resource
- Remove: simple_, improved_, enhanced_ variants
- Consolidate v1 and v2 into single versions

#### Repositories
- Keep: v2 repositories
- Remove: "improved" variants
- Standardize interfaces

### Phase 2: Test Cleanup

#### Consolidate Tests by Domain
From 150+ test files to ~30:
- `tests/test_auth.py` - All auth tests
- `tests/test_users.py` - All user tests
- `tests/test_beneficiaries.py` - All beneficiary tests
- Remove all "coverage_boost" tests

### Phase 3: Frontend Cleanup

#### Remove Duplicate Components
- Consolidate multiple implementations
- Remove unused components
- Standardize component structure

### Phase 4: Configuration

#### Single Config Structure
```
config/
├── __init__.py
├── base.py          # Base configuration
├── development.py   # Dev overrides
├── production.py    # Prod overrides
└── testing.py       # Test overrides
```

### Phase 5: Docker Cleanup

#### Single Dockerfile
- Multi-stage build
- Development and production targets
- Remove all duplicate Dockerfiles

## Expected Results

### Before:
- 500+ files in server
- 150+ test files
- Multiple versions of same code
- Confusing structure

### After:
- ~200 files in server
- ~30 focused test files
- Single implementation per feature
- Clear, maintainable structure

## File Count Reduction

| Category | Before | After | Reduction |
|----------|--------|-------|-----------|
| Services | 60+ | 15 | 75% |
| Tests | 150+ | 30 | 80% |
| API | 40+ | 20 | 50% |
| Config | 10+ | 4 | 60% |
| Total | 500+ | 200 | 60% |

## Implementation Steps

1. **Backup current state**
2. **Archive old files** (don't delete immediately)
3. **Consolidate services** (v2 → main)
4. **Merge test files**
5. **Clean configuration**
6. **Update imports**
7. **Test everything**
8. **Remove archive after verification**