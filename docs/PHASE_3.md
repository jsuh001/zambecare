# Phase 3 — Healthcare Ingestion

## Outcome

Phase 3 adds a controlled Python integration layer between the PostgreSQL application,
synthetic FHIR/CSV sources, and the Oracle Autonomous Database `DATAPRD`. It does not
diagnose patients. It moves synthetic training data, validates contracts, records rejected
records, tracks extraction watermarks, and proves record-count reconciliation.

## Scope

- PostgreSQL incremental patient extraction from `clinical.patient`
- FHIR R4-shaped Patient, Practitioner, Organization, Encounter, Condition, and Observation
- Facility CSV validation and ingestion
- Oracle schemas `ZC_STAGE` and `ZC_AUDIT`
- Oracle mTLS connectivity with `python-oracledb` Thin mode
- One auditable batch per source/entity load
- `source = staged + rejected` reconciliation
- Optional manually triggered Airflow DAG
- Tests and CI that require neither an Oracle wallet nor live Oracle

## Boundaries

- All names and clinical records are fictional synthetic training data.
- Patient data goes to `ZC_STAGE.STG_PATIENT`; facility data goes to
  `ZC_STAGE.STG_FACILITY`.
- Wallets, passwords, `.env`, and connection strings never enter Git.
- `ADMIN` provisions objects only. Runtime connections use `ZC_INGEST`.
- dbt warehouse models remain Phase 5; PL/SQL packages remain Phase 4.
- Airflow standalone mode is a low-cost learning configuration, not a production deployment.

## Flow

1. Open an ETL batch.
2. Establish a bounded extraction interval.
3. Read PostgreSQL, FHIR JSON, or facility CSV.
4. Normalize and validate each record.
5. Insert valid records into the entity-specific staging table.
6. Insert invalid records into `ZC_AUDIT.REJECTED_RECORD` with a rule code.
7. Persist reconciliation counts.
8. Complete or fail the batch.
9. Advance the watermark only after a successful PostgreSQL batch.

## Acceptance criteria

- Five least-privilege Oracle users exist.
- Four audit and six staging tables exist and are valid.
- `ZC_INGEST` can use only the explicit tables granted to it.
- FHIR and CSV validation-only runs complete without database credentials in CI.
- The invalid sample patient produces an explainable rejection.
- A registered PostgreSQL patient is loaded into `STG_PATIENT`.
- Every completed batch has zero unexplained records.
- Airflow can manually run the end-to-end DAG.

