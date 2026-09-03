# Phase 3 manual implementation guide

This is the authoritative hands-on procedure. Execute each checkpoint manually and save
sanitized evidence. Never paste passwords, wallet files, full service strings, or `.env`.

## 1. Prerequisites

- Phase 2 is merged and `feature/phase-3-ingestion` is checked out.
- Docker Desktop and Compose work.
- PostgreSQL, API, and frontend passed Phase 2 verification.
- DATAPRD is Available, Always Free, and reachable from desktop SQL Developer.
- `Wallet_DATAPRD.zip` is extracted under `secrets/oracle_wallet/`.
- `.env` and `secrets/` are ignored by Git.

Verify the wallet is not tracked:

```bash
git check-ignore -v secrets/oracle_wallet/
git ls-files secrets/
```

The second command must print nothing.

## 2. Script catalog

Run SQL scripts in numeric order from `db/oracle/cloud/`.

| Script | Purpose | Writes data? |
|---|---|---|
| `001_create_zambecare_users.sql` | Schema owners and runtime users | Creates users/grants |
| `002_create_audit_objects.sql` | Batch, watermark, rejection, reconciliation | Creates tables/indexes |
| `003_create_stage_objects.sql` | Six healthcare staging tables | Creates tables/indexes |
| `004_grant_object_privileges.sql` | Least-privilege runtime/dbt grants | Grants privileges |
| `005_validate_phase3.sql` | Users, objects, grants, invalid-object checks | No |
| `006_smoke_test.sql` | Inserts one fictional patient and reconciliation | Rolls back |

The scripts intentionally contain no real passwords. Script 001 prompts using hidden input.
If the five users already exist, begin at script 002; do not rerun script 001 and do not drop
working accounts.

## 3. Apply Oracle scripts in SQL Developer

Connect as `ADMIN` using the `dataprd_low` service. Run each with F5:

```sql
@/absolute/path/to/zambecare/db/oracle/cloud/002_create_audit_objects.sql
@/absolute/path/to/zambecare/db/oracle/cloud/003_create_stage_objects.sql
@/absolute/path/to/zambecare/db/oracle/cloud/004_grant_object_privileges.sql
@/absolute/path/to/zambecare/db/oracle/cloud/005_validate_phase3.sql
@/absolute/path/to/zambecare/db/oracle/cloud/006_smoke_test.sql
```

For a completely new environment, run script 001 first. On John's current DATAPRD setup,
the accounts already exist, so start with 002.

Expected validation: five users, four audit tables, six stage tables, no invalid objects.
The smoke test must show a passing batch and end with a rollback message.

## 4. Configure local secrets

Add these entries privately to `.env`; preserve existing Phase 2 entries:

```dotenv
ORACLE_INGEST_USER=ZC_INGEST
ORACLE_INGEST_PASSWORD=<private database password>
ORACLE_DSN=dataprd_low
ORACLE_WALLET_DIR=/opt/oracle/wallet
ORACLE_WALLET_PASSWORD=<private wallet password>
INGEST_POSTGRES_URL=postgresql://zambecare_app:<private-postgres-password>@postgres:5432/zambecare
CODE_VERSION=phase3-local
AIRFLOW_PORT=8080
```

Do not put quotes around values unless the value intentionally contains them. If a password
contains URL-reserved characters, percent-encode it in `INGEST_POSTGRES_URL`; the separate
Oracle password variable does not require URL encoding.

## 5. Run source validation without Oracle

Build the ingestion image:

```bash
docker build -t zambecare-ingestion:phase3 ./ingestion
```

FHIR contract check:

```bash
docker run --rm -v "$PWD/data:/opt/zambecare/data:ro" \
  zambecare-ingestion:phase3 fhir \
  --file /opt/zambecare/data/fhir/sample_bundle.json --validate-only
```

Facility CSV contract check:

```bash
docker run --rm -v "$PWD/data:/opt/zambecare/data:ro" \
  zambecare-ingestion:phase3 facility-csv \
  --file /opt/zambecare/data/csv/facilities.csv --validate-only
```

The FHIR sample expects 7 valid records across six entity types. The CSV expects three valid
facility records. The invalid patient fixture must report one rejected record.

## 6. Test Oracle mTLS as the runtime account

```bash
docker compose --profile ingestion run --rm ingestion oracle-check
```

Expected output contains `status: ok` and `user: ZC_INGEST`. It must not use `ADMIN`.

## 7. Load FHIR and CSV

```bash
docker compose --profile ingestion run --rm ingestion fhir \
  --file /opt/zambecare/data/fhir/sample_bundle.json

docker compose --profile ingestion run --rm ingestion facility-csv \
  --file /opt/zambecare/data/csv/facilities.csv
```

Each entity produces its own batch. Validate with script 005 and the runbook health queries.

## 8. Load registered PostgreSQL patients

Start PostgreSQL if necessary:

```bash
docker compose up -d postgres
```

Use an explicit UTC lower watermark for the first training run:

```bash
docker compose --profile ingestion run --rm ingestion postgres-patient \
  --start 1970-01-01T00:00:00+00:00
```

Then verify that the records are in the patient staging table:

```sql
SELECT batch_id, source_system, source_record_id, first_name, last_name,
       date_of_birth, validation_status, loaded_at
FROM zc_stage.stg_patient
WHERE source_system = 'POSTGRES'
ORDER BY loaded_at DESC;
```

Do not query or screenshot password hashes. Use only fictional patients.

## 9. Run automated tests

```bash
python3 -m venv ingestion/.venv
source ingestion/.venv/bin/activate
python -m pip install -r ingestion/requirements.txt
cd ingestion
ruff check src tests
pytest -q
cd ..
./scripts/validate_phase3.sh
```

## 10. Run Airflow only after CLI success

```bash
docker compose --profile airflow up --build -d postgres airflow
docker compose logs airflow --tail=100
```

Open `http://localhost:8080`. Airflow standalone prints a local administrator credential in
its startup logs; keep it private. Trigger `zambecare_phase3_ingestion` manually and use the
default `start_watermark` parameter for the first run.

Stop the heavy profile afterward:

```bash
docker compose --profile airflow stop airflow
```

## 11. Git and CI checkpoint

```bash
git status --short
git diff --check
git add .
git status --short
git commit -m "feat: add Phase 3 healthcare ingestion pipeline"
git push -u origin feature/phase-3-ingestion
```

Review the staged file list before committing. It must not contain `.env`, `secrets/`, wallet
files, generated logs, or actual patient information. Open a pull request only after API,
frontend, ingestion, static validation, and container-build jobs pass.

## 12. Evidence checklist

- SQL Developer connection as ADMIN (no endpoint/password visible)
- Script 005 object counts
- Script 006 rollback confirmation
- FHIR and CSV validation summaries
- Oracle check as ZC_INGEST
- PostgreSQL patient batch reconciliation PASS
- Airflow DAG success graph
- GitHub Actions success

