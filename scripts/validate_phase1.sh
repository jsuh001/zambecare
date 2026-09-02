#!/usr/bin/env sh
set -eu

required_files="
README.md
docker-compose.yml
api/app/main.py
api/alembic.ini
api/alembic/versions/20260902_01_phase2_identity.py
frontend/package.json
frontend/src/App.jsx
db/postgres/init/001_oltp_schema.sql
db/oracle/init/001_create_users.sql
db/oracle/init/002_core_objects.sql
dbt_zambecare/dbt_project.yml
dbt_zambecare/models/reconciliation/recon_encounter_batch.sql
docs/PROJECT_DOCUMENTATION.md
docs/PHASE_1.md
docs/PHASE_1_IMPLEMENTATION.md
docs/PHASE_2.md
docs/PHASE_2_IMPLEMENTATION.md
docs/AWS_EC2_IMPLEMENTATION.md
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
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=target \
    --exclude='validate_phase1.sh'; then
    echo "Potential credential material detected." >&2
    exit 1
fi

echo "ZambeCare project static validation passed."
