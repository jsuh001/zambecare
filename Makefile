.PHONY: validate validate-phase3 test ingestion-test ingestion-validate-fhir \
	ingestion-load-fhir airflow-up up down logs frontend-build dbt-debug dbt-build dbt-docs

validate:
	./scripts/validate_phase1.sh

validate-phase3:
	./scripts/validate_phase3.sh

ingestion-test:
	docker build -t zambecare-ingestion-test ./ingestion
	docker run --rm --entrypoint python zambecare-ingestion-test -m pytest -q

ingestion-validate-fhir:
	docker compose --profile ingestion run --rm ingestion fhir \
		--file /opt/zambecare/data/fhir/sample_bundle.json --validate-only

ingestion-load-fhir:
	docker compose --profile ingestion run --rm ingestion fhir \
		--file /opt/zambecare/data/fhir/sample_bundle.json

airflow-up:
	docker compose --profile airflow up --build -d postgres airflow

test:
	docker compose run --rm api pytest -q

up:
	docker compose up --build -d postgres api frontend

down:
	docker compose --profile oracle down

logs:
	docker compose logs -f frontend api postgres

frontend-build:
	cd frontend && npm install && npm run build

dbt-debug:
	docker compose --profile analytics run --rm dbt debug

dbt-build:
	docker compose --profile analytics run --rm dbt build

dbt-docs:
	docker compose --profile analytics run --rm dbt docs generate
