# Phase 1 — Foundation and Architecture

## Objective

Establish a secure, reproducible, documented foundation for the ZambeCare Clinical Data Intelligence Platform before implementing business functionality.

## Scope delivered

1. Repository conventions and development workflow.
2. Docker-based local environment.
3. FastAPI service with a health endpoint and automated test.
4. PostgreSQL transactional healthcare schema.
5. Oracle staging, audit, and dimensional warehouse objects.
6. dbt Core project with staging, incremental fact, and reconciliation models.
7. GitHub Actions and Jenkins pipeline definitions.
8. Security and synthetic-data boundaries.
9. Living technical documentation and phased roadmap.

## Functional requirements established

- Patients will register and manage their accounts.
- Authorized clinical users will record encounters, diagnoses, and observations.
- Patients will be matched to providers and facilities by symptoms, specialty, location, and availability.
- Emergency warning rules will execute before AI-assisted suggestions.
- Clinical data will be ingested into Oracle for analytics and operational reporting.
- Every batch will be explainable: source count equals accepted plus rejected count.
- Sensitive record access will be auditable.

## Non-functional requirements

| Category | Phase 1 decision |
|---|---|
| Cost | Local-first; free/open-source tools; optional cloud later |
| Privacy | Synthetic data only in all portfolio environments |
| Security | Least privilege, secrets outside source, no PHI in logs |
| Reliability | Idempotent batches, validation, rejected records, restartability |
| Performance | Partition-ready facts, index exercises, measurable execution plans |
| Observability | Health endpoint now; metrics and structured logs in later phases |
| Maintainability | Versioned SQL, migrations, dbt tests/docs, ADRs |

## Acceptance criteria

- [x] Repository contains documented architecture and roadmap.
- [x] API image can be built from `api/Dockerfile`.
- [x] `/health` endpoint has an automated test.
- [x] PostgreSQL schema defines patients, providers, facilities, encounters, diagnoses, vitals, and audit events.
- [x] Oracle scripts define staging, audit, reconciliation, dimension, and partitioned fact objects.
- [x] dbt defines sources, staging models, an incremental model, reconciliation, and data tests.
- [x] GitHub Actions and Jenkins definitions exist.
- [x] Static validation rejects common leaked credential patterns.
- [x] Documentation clearly prohibits real PHI.

## Deferred to Phase 2

- User registration and login
- Password hashing and JWT issuance
- Role-based authorization
- Alembic migrations
- CRUD APIs
- Synthetic data generator
- Database integration tests

## Phase 1 design review questions

Before Phase 2 is finalized, confirm:

1. Whether the public UI will be React or server-rendered templates.
2. Whether initial provider search should use postal-code distance or exact city/state matching.
3. Which clinical roles are required in the first demonstration: patient, doctor, nurse, and administrator are proposed.

These choices do not prevent starting the backend authentication foundation.
