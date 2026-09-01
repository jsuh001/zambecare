.PHONY: validate test up down logs dbt-debug dbt-build dbt-docs

validate:
	./scripts/validate_phase1.sh

test:
	docker compose run --rm api pytest -q

up:
	docker compose up --build -d postgres api

down:
	docker compose --profile oracle down

logs:
	docker compose logs -f api postgres

dbt-debug:
	docker compose --profile analytics run --rm dbt debug

dbt-build:
	docker compose --profile analytics run --rm dbt build

dbt-docs:
	docker compose --profile analytics run --rm dbt docs generate
