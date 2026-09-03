from pathlib import Path

from zambecare_ingestion.extractors.fhir import extract_fhir
from zambecare_ingestion.pipeline import validate_summary

ROOT = Path(__file__).parents[2]


def test_bundle_maps_supported_healthcare_entities():
    records = extract_fhir(ROOT / "data/fhir/sample_bundle.json")
    assert len(records) == 7
    assert {record.entity for record in records} == {
        "Patient", "Practitioner", "Facility", "Encounter", "Condition", "Observation"
    }
    assert all(record.valid for record in records)


def test_invalid_patient_is_rejected_with_explainable_rule():
    records = extract_fhir(ROOT / "data/fhir/invalid_patient.json")
    summary = validate_summary(records)
    assert summary["rejected"] == 1
    assert records[0].errors == ["PATIENT_NAME_AND_BIRTH_DATE_REQUIRED"]

