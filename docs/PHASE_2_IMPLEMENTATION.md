# Phase 2 Implementation and Testing Guide

## 1. Pull or copy the Phase 2 source

If your GitHub repository contains Phase 1 changes that are not in this package, commit them first. Apply Phase 2 on a new branch instead of overwriting `main`:

```bash
git switch -c feature/phase-2
```

Copy or merge the Phase 2 files, then inspect changes:

```bash
git status
git diff --stat
```

## 2. Update environment configuration

Compare `.env.example` with `.env`. Add:

```text
REFRESH_TOKEN_EXPIRE_DAYS=7
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
FRONTEND_PORT=3000
VITE_API_URL=http://localhost:8000/api/v1
```

Generate a unique secret of at least 32 characters:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Place it in `SECRET_KEY`. Never commit `.env`.

## 3. Decide whether to preserve Phase 1 local data

Phase 1 data must be synthetic. If you have no records to preserve, the cleanest local upgrade is:

```bash
docker compose down
docker volume ls | grep zambecare
```

To retain the existing PostgreSQL volume, simply start Phase 2; Alembic adds the new structures. Do not delete a volume unless you have deliberately confirmed its contents are disposable.

## 4. Build and start Phase 2

```bash
docker compose config --quiet
docker compose up --build -d postgres api frontend
docker compose ps
```

The API container automatically runs:

```bash
alembic upgrade head
```

before starting FastAPI.

## 5. Confirm database migration

```bash
docker compose exec api alembic current
```

Expected revision:

```text
20260902_01 (head)
```

Inspect the new tables:

```bash
docker compose exec postgres psql \
  -U zambecare_app \
  -d zambecare \
  -c "select table_schema, table_name from information_schema.tables where table_schema in ('clinical','security') order by 1,2;"
```

## 6. Open the application

- Patient portal: `http://localhost:3000`
- FastAPI documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

Use fictional names, addresses, dates, phone numbers, and medical information.

## 7. Test the patient journey

1. Open the patient portal.
2. Select **Create patient account**.
3. Enter synthetic information.
4. Use a 12+ character password containing upper, lower, number, and symbol characters.
5. Sign in.
6. Confirm the dashboard loads your profile.
7. Change the preferred language and save.
8. Open **Find care** and search Dallas or `PRIMARY_CARE`.
9. Sign out.
10. Confirm the protected dashboard is no longer accessible.

## 8. Run automated tests

```bash
docker compose run --rm api pytest -q
```

Expected baseline:

```text
9 passed
```

## 9. Build the frontend independently

```bash
cd frontend
npm ci
npm run build
cd ..
```

## 10. Verify the CI pipeline

Commit on the feature branch:

```bash
git add .
git commit -m "Implement ZambeCare Phase 2 application"
git push -u origin feature/phase-2
```

Open a pull request into `main`. Confirm:

- API tests pass.
- Alembic migration test passes against PostgreSQL.
- Static validation passes.
- Frontend production build passes.
- API and frontend container builds pass.

Merge only after all required jobs succeed.

## 11. Docker Hub publishing

Your existing Docker Hub publishing job can continue publishing the API image. Add a second build/push step for the frontend when you want both images in Docker Hub:

```yaml
- name: Build and push frontend image
  uses: docker/build-push-action@v7
  with:
    context: ./frontend
    push: true
    tags: |
      ${{ vars.DOCKERHUB_USERNAME }}/zambecare-frontend:latest
      ${{ vars.DOCKERHUB_USERNAME }}/zambecare-frontend:${{ github.sha }}
```

## 12. Troubleshooting

| Symptom | Check |
|---|---|
| API exits during startup | `docker compose logs api postgres`; check Alembic error |
| Migration reports patient table missing | Confirm Phase 1 PostgreSQL init scripts ran |
| Browser shows network error | Confirm API health and `VITE_API_URL` |
| Browser shows CORS error | Confirm the frontend origin is in `ALLOWED_ORIGINS` |
| Login returns 401 | Check password, account state, and lockout interval |
| Directory is empty | Confirm `002_synthetic_directory.sql` ran on a new database |
| Old PostgreSQL volume lacks seed data | Apply the seed SQL manually or recreate only disposable synthetic data |
| `npm ci` fails | Confirm `frontend/package-lock.json` is committed |

## 13. Phase completion evidence

Keep screenshots or logs showing:

- Successful GitHub Actions run
- Patient portal landing page
- Successful synthetic registration and dashboard
- Provider/facility search
- `alembic current`
- Nine passing backend tests
- Docker Hub image tags

Do not capture passwords, tokens, `.env`, or real personal information.
