# Phase 1 Data Dictionary

This dictionary describes the initial foundation. It will expand with every migration.

## PostgreSQL operational entities

| Entity | Primary key | Purpose | Sensitive fields |
|---|---|---|---|
| `clinical.patient` | `patient_id` | Patient identity and account-linked demographics | Name, DOB, email, phone |
| `clinical.facility` | `facility_id` | Healthcare facility and location | Generally non-PHI |
| `clinical.provider` | `provider_id` | Doctor/provider and specialty | Provider identifiers |
| `clinical.encounter` | `encounter_id` | Actual healthcare interaction | Patient/provider relationship and timing |
| `clinical.diagnosis` | `diagnosis_id` | Encounter-linked diagnosis | Clinical PHI |
| `clinical.vital_sign` | `vital_sign_id` | Encounter observation or measurement | Clinical PHI |
| `security.phi_access_audit` | `audit_id` | Metadata about sensitive-record access | Security-sensitive; no clinical payload |

## Oracle staging entities

| Entity | Grain | Purpose |
|---|---|---|
| `ZC_STAGE.STG_PATIENT` | One source patient per batch | Raw/source-aligned patient load and validation state |
| `ZC_STAGE.STG_ENCOUNTER` | One source encounter per batch | Raw/source-aligned encounter load and validation state |

## Oracle audit entities

| Entity | Grain | Purpose |
|---|---|---|
| `ZC_AUDIT.ETL_BATCH` | One entity extraction batch | Lifecycle, counts, and operational state |
| `ZC_AUDIT.REJECTED_RECORD` | One failed rule per source record | Explainable data-quality rejection |
| `ZC_AUDIT.RECONCILIATION_RESULT` | One entity reconciliation per batch | Source-to-target accounting result |

## Oracle analytical entities

| Entity | Grain | Purpose |
|---|---|---|
| `ZC_DW.DIM_PATIENT` | One patient version | De-identified slowly changing patient context |
| `ZC_DW.FACT_ENCOUNTER` | One healthcare encounter | Partitioned encounter analytics |

## Classification

| Classification | Examples | Handling |
|---|---|---|
| Restricted PHI | Patient name plus diagnosis, vitals, encounter | Operational access only; encrypt; audit |
| Direct identifier | Name, email, phone, exact DOB | Exclude from analytics unless justified |
| Internal sensitive | Audit metadata, rejection messages | Restrict and retain per policy |
| Public/reference | Specialty codes, facility types | Normal integrity controls |

No real records are permitted in the portfolio environment.
