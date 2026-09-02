-- Least-privilege grants. Run as ADMIN after all tables exist.
WHENEVER SQLERROR EXIT SQL.SQLCODE

GRANT SELECT, INSERT, UPDATE ON zc_audit.etl_batch TO zc_ingest;
GRANT SELECT, INSERT, UPDATE ON zc_audit.extraction_watermark TO zc_ingest;
GRANT SELECT, INSERT ON zc_audit.rejected_record TO zc_ingest;
GRANT SELECT, INSERT ON zc_audit.reconciliation_result TO zc_ingest;

GRANT SELECT, INSERT ON zc_stage.stg_patient TO zc_ingest;
GRANT SELECT, INSERT ON zc_stage.stg_practitioner TO zc_ingest;
GRANT SELECT, INSERT ON zc_stage.stg_facility TO zc_ingest;
GRANT SELECT, INSERT ON zc_stage.stg_encounter TO zc_ingest;
GRANT SELECT, INSERT ON zc_stage.stg_condition TO zc_ingest;
GRANT SELECT, INSERT ON zc_stage.stg_observation TO zc_ingest;

GRANT SELECT ON zc_stage.stg_patient TO zc_dbt;
GRANT SELECT ON zc_stage.stg_practitioner TO zc_dbt;
GRANT SELECT ON zc_stage.stg_facility TO zc_dbt;
GRANT SELECT ON zc_stage.stg_encounter TO zc_dbt;
GRANT SELECT ON zc_stage.stg_condition TO zc_dbt;
GRANT SELECT ON zc_stage.stg_observation TO zc_dbt;
GRANT SELECT ON zc_audit.etl_batch TO zc_dbt;
GRANT SELECT ON zc_audit.rejected_record TO zc_dbt;
GRANT SELECT, INSERT ON zc_audit.reconciliation_result TO zc_dbt;

