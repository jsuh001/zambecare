# Phase 1 Implementation Guide

## 1. Goal

Phase 1 proves that the ZambeCare foundation can be reproduced from source. At the end, the API responds, PostgreSQL initializes, Oracle is available for data-engineering exercises, dbt can connect, automated tests pass, and the project documentation matches the implementation.

No real patient or medical data may be used.

## 2. Recommended implementation strategy

Use a local-first workflow:

1. Develop and test FastAPI and PostgreSQL locally.
2. Run GitHub Actions when code is pushed.
3. Start Oracle locally only for Oracle/dbt exercises.
4. Add Jenkins locally after the lightweight foundation works.
5. Use EC2 as an optional deployment laboratory, not as a daily development requirement.

This is the least expensive approach and provides faster troubleshooting. It also separates application problems from AWS networking and IAM problems.

## 3. Workstation capacity

| Workload | Suggested available memory | Services |
|---|---:|---|
| Lightweight | 4 GB | FastAPI and PostgreSQL |
| Analytics practice | 8 GB or more | FastAPI, PostgreSQL, Oracle and dbt |
| Full DevOps lab | 12–16 GB | Application, Oracle, Jenkins and monitoring |

Do not run Oracle, Jenkins, SonarQube, Airflow, and Grafana simultaneously on a small computer. Start only the profile being practiced.

## 4. Local installation

### Step 1 — Install prerequisites

Install:

- Git
- Docker Desktop on macOS/Windows, or Docker Engine plus the Compose plugin on Linux
- A code editor such as Visual Studio Code

Verify:

```bash
git --version
docker --version
docker compose version
```

### Step 2 — Open the project

Extract the ZambeCare archive, enter the directory, and inspect the current phase:

```bash
cd zambecare
sed -n '1,220p' docs/PHASE_1.md
```

### Step 3 — Create local configuration

```bash
cp .env.example .env
```

Edit `.env` and replace every example secret. Generate a development secret without copying it into chat or Git:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Place the result in `SECRET_KEY`. Confirm `.env` is ignored:

```bash
git check-ignore .env
```

Expected result: `.env`.

### Step 4 — Validate the repository

```bash
make validate
docker compose config --quiet
```

Both commands should exit without an error.

### Step 5 — Start the lightweight stack

```bash
docker compose up --build -d postgres api
docker compose ps
```

Both containers should become healthy.

### Step 6 — Test the API

```bash
curl http://localhost:8000/health
```

Expected fields:

```json
{
  "status": "healthy",
  "service": "zambecare-api",
  "timestamp": "..."
}
```

Open `http://localhost:8000/docs` to view FastAPI Swagger documentation.

### Step 7 — Verify PostgreSQL

```bash
docker compose exec postgres psql \
  -U zambecare_app \
  -d zambecare \
  -c "select table_schema, table_name from information_schema.tables where table_schema in ('clinical','security') order by 1,2;"
```

Confirm the patient, facility, provider, encounter, diagnosis, vital-sign, and audit tables exist.

### Step 8 — Run the API test

```bash
docker compose run --rm api pytest -q
```

Expected result: `1 passed` for the Phase 1 baseline.

### Step 9 — Start Oracle only when needed

Oracle Container Registry may require one-time sign-in and license acceptance.

```bash
docker login container-registry.oracle.com
docker compose --profile oracle up -d oracle
docker compose ps
docker compose logs -f oracle
```

Wait until Oracle reports healthy. Do not expose port 1521 outside your workstation or EC2 host.

### Step 10 — Create Oracle schemas and objects

Run the numbered scripts as a privileged local-development account:

```bash
docker compose exec -it oracle sqlplus system@FREEPDB1
```

At the SQL prompt, run:

```sql
@/path/available/in/container/001_create_users.sql
@/path/available/in/container/002_core_objects.sql
@/path/available/in/container/003_object_grants.sql
```

If the project directory is not mounted into the Oracle container, copy the scripts first:

```bash
oracle_container_id="$(docker compose ps -q oracle)"
docker cp db/oracle/init/. "$oracle_container_id":/tmp/zambecare-init/
docker compose exec -it oracle sqlplus system@FREEPDB1
```

Then use `/tmp/zambecare-init/001_create_users.sql` and the remaining numbered paths. Script 001 prompts securely for four schema passwords.

### Step 11 — Configure and validate dbt

Ensure the `ORACLE_DBT_PASSWORD` in `.env` matches the password entered for `ZC_DBT`.

```bash
docker compose --profile analytics run --rm dbt debug
docker compose --profile analytics run --rm dbt parse
```

After the Oracle source tables and grants are present:

```bash
docker compose --profile analytics run --rm dbt build
docker compose --profile analytics run --rm dbt docs generate
```

The first empty build may create models but will not contain business data until Phase 3 ingestion.

### Step 12 — Verify CI

Push the repository to GitHub and open a pull request. Confirm these jobs pass:

- API tests
- Static validation
- API container build

### Step 13 — Phase 1 completion checklist

- [ ] `.env` contains unique local secrets and is ignored by Git.
- [ ] Static validation passes.
- [ ] Compose configuration is valid.
- [ ] API and PostgreSQL are healthy.
- [ ] `/health` responds.
- [ ] API tests pass.
- [ ] PostgreSQL tables exist.
- [ ] Oracle schemas and objects exist.
- [ ] `dbt debug` succeeds.
- [ ] GitHub Actions succeeds.
- [ ] No real PHI is present.
- [ ] Implementation notes and failures are recorded.

## 5. Common problems

| Problem | Likely cause | Check |
|---|---|---|
| Compose refuses to start | `.env` missing or placeholder required value | `docker compose config` |
| API unhealthy | PostgreSQL not ready or invalid database URL | `docker compose logs api postgres` |
| Port already allocated | Another PostgreSQL/API instance is running | Change the host port in `.env` |
| Oracle exits | Insufficient memory, registry terms, or architecture mismatch | Oracle logs and Docker resource allocation |
| dbt cannot connect | Oracle not ready, password mismatch, wrong service | `dbt debug`; verify `FREEPDB1` |
| dbt authorization error | Object grants not applied | Run `003_object_grants.sql` |

## 6. Daily cost-saving workflow

Run only FastAPI and PostgreSQL during normal application development. Start Oracle for scheduled practice sessions, and stop all services afterward:

```bash
docker compose --profile oracle --profile analytics down
```

Named volumes retain local database data until explicitly deleted. Do not add `-v` unless you intentionally want to erase the local databases.
