#!/usr/bin/env bash
set -euo pipefail

required=(
  db/oracle/cloud/001_create_zambecare_users.sql
  db/oracle/cloud/002_create_audit_objects.sql
  db/oracle/cloud/003_create_stage_objects.sql
  db/oracle/cloud/004_grant_object_privileges.sql
  db/oracle/cloud/005_validate_phase3.sql
  db/oracle/cloud/006_smoke_test.sql
  ingestion/pyproject.toml
  airflow/dags/zambecare_phase3_ingestion.py
  data/fhir/sample_bundle.json
  data/csv/facilities.csv
  docs/PHASE_3_IMPLEMENTATION.md
)

for file in "${required[@]}"; do
  test -f "$file" || { echo "Missing required Phase 3 file: $file"; exit 1; }
done

if rg -n '(Wallet_.*\.zip|cwallet\.sso|ewallet\.pem|BEGIN PRIVATE KEY)' \
  --glob '!scripts/validate_phase3.sh' --glob '!docs/**' --glob '!*.md' .; then
  echo "Possible wallet or private key material found in tracked project content."
  exit 1
fi

python -m json.tool data/fhir/sample_bundle.json >/dev/null
python -m json.tool data/fhir/invalid_patient.json >/dev/null
echo "Phase 3 static validation passed."

