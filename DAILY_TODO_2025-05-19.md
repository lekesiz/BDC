# DAILY TODO - 2025-05-19

## Session Goals
Establish CI quality gates (tests, lint, pre-commit, workflow) and begin modular backend refactor.

## Task List
- [x] 1. Record session plan in PROJECT_MEMORY.md
- [x] 2. Create this daily TODO file
- [~] 3. Run baseline tests (backend & frontend) to ensure green state (blocked locally by Python 3.13 deps; will rely on CI run)
- [x] 4. Add pre-commit configuration (black, isort, flake8, bandit, eslint, prettier) and install hooks (config file added)
- [x] 5. Configure GitHub Actions CI workflow (tests + lint on push/PR) (workflow file created)
- [x] 6. Backend refactor step 1: extract beneficiaries endpoints into sub-package `server/app/api/beneficiaries_v2/`
- [x] 7. Update blueprint imports & ensure server passes healthcheck (register_blueprints updated)
- [~] 8. Re-run backend tests to verify no regressions (will rely on CI)
- [ ] 9. Commit & push changes to remote
- [ ] 10. Update PROJECT_MEMORY.md with summary and next steps 