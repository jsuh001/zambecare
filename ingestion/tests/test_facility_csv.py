from pathlib import Path

from zambecare_ingestion.extractors.csv_facility import extract_facilities

ROOT = Path(__file__).parents[2]


def test_facility_csv_is_valid_and_separate_from_patients():
    records = extract_facilities(ROOT / "data/csv/facilities.csv")
    assert len(records) == 3
    assert all(record.entity == "Facility" for record in records)
    assert all(record.valid for record in records)

