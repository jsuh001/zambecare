# Project Validation Report

Validation date: 2026-09-01

Phase 2 validation date: 2026-09-02

## Passed

- Repository-required-file validation
- Common credential-pattern scan
- Docker Compose, GitHub Actions, and dbt YAML parsing
- FastAPI automated test: 1 passed
- dbt Core project parsing with dbt Core 1.12.3 and Oracle adapter 1.12.0
- Local and AWS EC2 implementation guides included in repository validation
- Phase 2 Python test suite: 9 passed
- Phase 2 Alembic migration rendered as PostgreSQL SQL successfully
- React/Vite production build completed successfully
- Phase 2 frontend, migration, security, and implementation documentation present

## Environment limitation

Docker was not installed in the build workspace, so container startup, live PostgreSQL migration execution, and Oracle SQL execution were not performed here. These are workstation integration checks:

1. `docker compose config`
2. `docker compose up --build -d postgres api`
3. `curl http://localhost:8000/health`
4. Confirm `alembic current` reports `20260902_01`.
5. Complete the synthetic registration/login/dashboard workflow.
6. Start the Oracle profile and apply numbered Oracle scripts when beginning Oracle work.
7. `dbt debug` followed by `dbt build` when beginning analytical work.

No claim is made that the Oracle DDL has run until those integration checks pass against the selected Oracle Free image.

## Phase 3 validation

Phase 3 adds `scripts/validate_phase3.sh`, ingestion unit tests, FHIR/CSV validation-only
runs, Oracle script `005_validate_phase3.sql`, and rollback-only smoke script
`006_smoke_test.sql`. CI does not receive an Oracle wallet. Live mTLS and database writes are
manual acceptance tests against DATAPRD using synthetic data.
