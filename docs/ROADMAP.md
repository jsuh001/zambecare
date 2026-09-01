# Implementation Roadmap

## Phase 1 — Foundation

Architecture, repository, local containers, initial schemas, dbt structure, CI/CD skeleton, security boundary, and documentation.

## Phase 2 — Secure transactional API

- Alembic migrations
- Patient registration and sign-in
- Argon2 password hashing
- JWT access/refresh rotation
- Patient, doctor, nurse, administrator roles
- Authorization tests
- Provider and facility APIs
- Synthetic data generator

## Phase 3 — Healthcare ingestion

- FHIR Patient, Practitioner, Organization, Encounter, Condition, Observation
- Facility CSV ingestion
- Extraction watermarks
- Airflow DAGs
- Oracle bulk stage loading
- Schema and contract validation

## Phase 4 — Oracle and PL/SQL engineering

- Batch-control package
- Validation package
- Error logging package
- Bulk loading with `FORALL`
- Idempotent `MERGE`
- Restart and replay
- utPLSQL test suite

## Phase 5 — dbt warehouse and reconciliation

- Dimensions and facts
- Incremental strategies
- SCD Type 2 history
- Generic, singular, and unit tests
- Reusable reconciliation macros
- dbt documentation and lineage
- Superset reconciliation dashboard

## Phase 6 — Care routing

- Emergency-first deterministic rules
- Specialty mapping
- Facility/location matching
- Local AI model experimentation
- Explanations and disclaimers
- Safety and bias test cases

## Phase 7 — Delivery and security

- Complete GitHub Actions gates
- Jenkins environment promotion
- Gitleaks, Bandit, Trivy, dependency scanning, OWASP ZAP
- Versioned database deployment and rollback
- Build artifacts and release notes

## Phase 8 — Operations and interview package

- Prometheus, Grafana, and Loki
- Pipeline SLA and data-freshness alerts
- Failure simulations and runbooks
- Query-tuning laboratories
- Backup/restore demonstration
- Architecture presentation and interview demo script
