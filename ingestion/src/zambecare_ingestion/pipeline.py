from datetime import UTC, datetime
from pathlib import Path

from zambecare_ingestion.config import Settings
from zambecare_ingestion.contracts import PreparedRecord
from zambecare_ingestion.extractors.csv_facility import extract_facilities
from zambecare_ingestion.extractors.fhir import extract_fhir
from zambecare_ingestion.extractors.postgres import extract_patients
from zambecare_ingestion.loaders.oracle import OracleLoader, entity_counts


def validate_summary(records: list[PreparedRecord]) -> dict[str, object]:
    counts = entity_counts(records)
    return {"total": len(records), "valid": sum(record.valid for record in records),
            "rejected": sum(not record.valid for record in records), "entities": dict(counts)}


def run_file(path: Path, source_type: str, settings: Settings | None,
             validate_only: bool = False) -> list[dict[str, object]]:
    records = extract_fhir(path) if source_type == "fhir" else extract_facilities(path)
    if validate_only:
        return [validate_summary(records)]
    if not records:
        raise ValueError(f"No records found in {path}")
    if settings is None:
        raise ValueError("Oracle settings are required for loading")
    loader = OracleLoader(settings)
    return [loader.load_batch(records, records[0].source_system, entity)
            for entity in sorted(entity_counts(records))]


def run_postgres(settings: Settings, start: datetime, end: datetime | None = None,
                 validate_only: bool = False) -> list[dict[str, object]]:
    upper = end or datetime.now(UTC)
    records = extract_patients(settings.postgres_url, start, upper)
    if validate_only:
        return [validate_summary(records)]
    return [OracleLoader(settings).load_batch(records, "POSTGRES", "Patient", start, upper)]
