-- Run as a privileged account after 002_core_objects.sql.
WHENEVER SQLERROR EXIT SQL.SQLCODE;
ALTER SESSION SET CONTAINER = FREEPDB1;

GRANT SELECT ON zc_stage.stg_patient TO zc_dbt;
GRANT SELECT ON zc_stage.stg_encounter TO zc_dbt;
GRANT SELECT ON zc_audit.rejected_record TO zc_dbt;
GRANT SELECT ON zc_audit.etl_batch TO zc_dbt;
GRANT SELECT, INSERT ON zc_audit.reconciliation_result TO zc_dbt;

GRANT SELECT, INSERT, UPDATE, DELETE ON zc_dw.dim_patient TO zc_dbt;
GRANT SELECT, INSERT, UPDATE, DELETE ON zc_dw.fact_encounter TO zc_dbt;
