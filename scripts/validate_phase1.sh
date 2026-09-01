#!/usr/bin/env sh
set -eu

required_files="
README.md
docker-compose.yml
api/app/main.py
db/postgres/init/001_oltp_schema.sql
db/oracle/init/001_create_users.sql
db/oracle/init/002_core_objects.sql
dbt_zambecare/dbt_project.yml
dbt_zambecare/models/reconciliation/recon_encounter_batch.sql
docs/PROJECT_DOCUMENTATION.md
docs/PHASE_1.md
docs/DATA_DICTIONARY.md
docs/SECURITY_AND_HIPAA.md
docs/VALIDATION.md
Jenkinsfile
.github/workflows/ci.yml
"

for path in $required_files; do
    if [ ! -f "$path" ]; then
        echo "Missing required Phase 1 file: $path" >&2
        exit 1
    fi
done

if grep -R -n -E '(BEGIN (RSA|OPENSSH) PRIVATE KEY|AKIA[0-9A-Z]{16})' . \
    --exclude-dir=.git --exclude='validate_phase1.sh'; then
    echo "Potential credential material detected." >&2
    exit 1
fi

echo "Phase 1 static validation passed."
