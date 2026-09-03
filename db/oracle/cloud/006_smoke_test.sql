-- Transactional smoke test: inserts, reconciles, then rolls everything back.
WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK
SET SERVEROUTPUT ON
VARIABLE smoke_batch NUMBER

INSERT INTO zc_audit.etl_batch
  (source_system, entity_name, batch_status, source_count, staged_count, rejected_count, code_version)
VALUES ('PHASE3_SMOKE', 'Patient', 'LOADING', 1, 1, 0, 'manual-smoke-test')
RETURNING batch_id INTO :smoke_batch;

INSERT INTO zc_stage.stg_patient
  (batch_id, source_system, source_record_id, external_patient_id, first_name, last_name,
   date_of_birth, sex_at_birth, email, raw_payload, record_hash, validation_status)
VALUES
  (:smoke_batch, 'PHASE3_SMOKE', 'patient-smoke-001', 'patient-smoke-001',
   'Amina', 'Cole', DATE '1992-04-16', 'female', 'amina.cole@example.test',
   '{"resourceType":"Patient","id":"patient-smoke-001"}',
   STANDARD_HASH('{"resourceType":"Patient","id":"patient-smoke-001"}', 'SHA256'), 'VALID');

INSERT INTO zc_audit.reconciliation_result
  (batch_id, entity_name, source_count, staged_count, rejected_count,
   unexplained_count, reconciliation_status)
VALUES (:smoke_batch, 'Patient', 1, 1, 0, 0, 'PASS');

UPDATE zc_audit.etl_batch SET batch_status='COMPLETED', completed_at=SYSTIMESTAMP
WHERE batch_id=:smoke_batch;

SELECT batch_id, batch_status, source_count, staged_count, rejected_count
FROM zc_audit.etl_batch WHERE batch_id=:smoke_batch;
SELECT batch_id, source_record_id, validation_status
FROM zc_stage.stg_patient WHERE batch_id=:smoke_batch;
ROLLBACK;
PROMPT Smoke test rolled back; no test patient was retained.
