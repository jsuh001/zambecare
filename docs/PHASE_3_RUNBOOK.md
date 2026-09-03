# Phase 3 operations runbook

## Batch states

`STARTED → EXTRACTING → VALIDATING → LOADING → RECONCILING → COMPLETED`

Any exception produces `FAILED`, stores a bounded error message, and does not advance the
watermark.

## Health queries

Latest batches:

```sql
SELECT batch_id, source_system, entity_name, batch_status,
       source_count, staged_count, rejected_count, started_at, completed_at
FROM zc_audit.etl_batch
ORDER BY started_at DESC FETCH FIRST 20 ROWS ONLY;
```

Failed batches:

```sql
SELECT batch_id, source_system, entity_name, error_message, retry_count, started_at
FROM zc_audit.etl_batch
WHERE batch_status = 'FAILED'
ORDER BY started_at DESC;
```

Reconciliation failures:

```sql
SELECT batch_id, entity_name, source_count, staged_count,
       rejected_count, unexplained_count, checked_at
FROM zc_audit.reconciliation_result
WHERE reconciliation_status = 'FAIL'
ORDER BY checked_at DESC;
```

Current watermarks:

```sql
SELECT source_system, entity_name, last_success_watermark, last_batch_id, updated_at
FROM zc_audit.extraction_watermark
ORDER BY source_system, entity_name;
```

## Recovery

1. Do not manually advance a failed watermark.
2. Read the batch error and rejected-record rule codes.
3. Correct the source contract, mapping, privilege, or network problem.
4. Rerun with the same start watermark and a newly fixed upper boundary.
5. Confirm reconciliation is `PASS` before accepting the run.

Phase 4 will add packaged replay and idempotent Oracle `MERGE` processing. Phase 3 relies
on bounded PostgreSQL watermarks and a batch-specific staging primary key.

## Common failures

| Symptom | Check |
|---|---|
| `ORA-01017` | Correct database-user password, not OCI or wallet password |
| Wallet/TLS error | Extracted wallet contains `tnsnames.ora` and `ewallet.pem`; mount is read-only |
| `ORA-00942` | Run scripts 002–004 and validate grants as `ADMIN` |
| JSON constraint error | Source must be valid JSON; run validation-only first |
| PostgreSQL connection refused | Start `postgres`; use hostname `postgres` inside Compose |
| Reconciliation `FAIL` | Compare source, staged, rejected, and unexplained counts |
| Airflow resource pressure | Stop frontend/API or run the CLI without Airflow |

