# DAILY TODO - 2025-05-22

## Session Goals
1. Complete Program Management V2 CRUD refactor
2. Increase backend coverage ≥ 75 % via ProgramService tests
3. Add S3 storage upload tests
4. Add frontend Program component tests, raise coverage ≥ 65 %
5. Bump CI coverage thresholds (backend 65 %, frontend 60 %)

## Task List
- [x] 1. Create this daily TODO file
- [ ] 2. Move create/update/delete/enrollment/session endpoints to `app/api/programs_v2/`
- [x] 3. Update blueprint & migrate tests (401 + authorized CRUD)
- [x] 4. Add ProgramService unit tests (coverage target)
- [x] 5. Add S3 upload tests (when STORAGE_BACKEND=s3)
- [x] 6. Add frontend Program page tests (Vitest)
- [x] 7. Update CI coverage fail-under in run_tests.py & vitest config
- [ ] 8. Update PROJECT_MEMORY.md with session summary 