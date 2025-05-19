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
- [x] 9. Commit & push changes to remote (git push completed)
- [x] 10. Update PROJECT_MEMORY.md with summary and next steps
- [x] 11. Bring over beneficiary detail/update/delete endpoints to v2 package
- [x] 12. Migrate trainer endpoints (list & assign) to v2 package
- [x] 13. Migrate notes endpoints to v2 package
- [x] 14. Migrate documents list & profile-picture upload endpoints to v2 package
- [x] 15. Migrate evaluations/sessions/progress/skills/comparison/report endpoints to v2 package
- [x] 16. Mark legacy beneficiaries.py as DEPRECATED
- [x] 17. Add initial unit test for v2 blueprint registration
- [x] 18. Add parametric unauthorized (401) tests for all v2 endpoints
- [x] 19. Add authorized happy-path test for beneficiaries list endpoint
- [x] 20. Add beneficiary creation + notes flow test
- [x] 21. Add authorized tests for documents, progress, skills endpoints
- [x] 22. Enforce minimum 50% coverage in run_tests.py
- [x] 23. Set frontend coverage thresholds in vitest config (≥50%) 