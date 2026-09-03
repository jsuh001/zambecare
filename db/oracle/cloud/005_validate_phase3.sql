-- Read-only validation. Run as ADMIN after scripts 001-004.
SET PAGESIZE 100
SET LINESIZE 220

PROMPT === ZambeCare users ===
SELECT username, account_status, authentication_type, default_tablespace
FROM dba_users WHERE username LIKE 'ZC\_%' ESCAPE '\' ORDER BY username;

PROMPT === Audit tables (expect 4) ===
SELECT owner, table_name FROM dba_tables
WHERE owner = 'ZC_AUDIT' ORDER BY table_name;

PROMPT === Stage tables (expect 6) ===
SELECT owner, table_name FROM dba_tables
WHERE owner = 'ZC_STAGE' ORDER BY table_name;

PROMPT === ZC_INGEST object grants ===
SELECT owner, table_name, privilege FROM dba_tab_privs
WHERE grantee = 'ZC_INGEST' ORDER BY owner, table_name, privilege;

PROMPT === Invalid objects (expect no rows) ===
SELECT owner, object_name, object_type, status FROM dba_objects
WHERE owner IN ('ZC_STAGE','ZC_AUDIT','ZC_DW','ZC_DBT') AND status <> 'VALID';

PROMPT === Reconciliation health ===
SELECT batch_id, entity_name, source_count, staged_count, rejected_count,
       unexplained_count, reconciliation_status, checked_at
FROM zc_audit.reconciliation_result ORDER BY checked_at DESC FETCH FIRST 20 ROWS ONLY;

