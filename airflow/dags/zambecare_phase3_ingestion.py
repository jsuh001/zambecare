from datetime import UTC, datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

with DAG(
    dag_id="zambecare_phase3_ingestion",
    description="Validate and ingest synthetic ZambeCare healthcare data",
    start_date=datetime(2026, 9, 1, tzinfo=UTC),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    params={"start_watermark": "1970-01-01T00:00:00+00:00"},
    tags=["zambecare", "phase3", "synthetic-data"],
) as dag:
    validate_fhir = BashOperator(
        task_id="validate_fhir_contract",
        bash_command=("zambecare-ingest fhir --file /opt/zambecare/data/fhir/sample_bundle.json "
                      "--validate-only"),
    )
    validate_facilities = BashOperator(
        task_id="validate_facility_contract",
        bash_command=("zambecare-ingest facility-csv --file "
                      "/opt/zambecare/data/csv/facilities.csv --validate-only"),
    )
    load_fhir = BashOperator(
        task_id="load_fhir_to_oracle",
        bash_command="zambecare-ingest fhir --file /opt/zambecare/data/fhir/sample_bundle.json",
    )
    load_facilities = BashOperator(
        task_id="load_facilities_to_oracle",
        bash_command=("zambecare-ingest facility-csv --file "
                      "/opt/zambecare/data/csv/facilities.csv"),
    )
    load_postgres_patients = BashOperator(
        task_id="load_postgres_patients_to_oracle",
        bash_command=("zambecare-ingest postgres-patient "
                      "--start '{{ params.start_watermark }}'"),
    )

    [validate_fhir, validate_facilities] >> load_fhir >> load_facilities >> load_postgres_patients
