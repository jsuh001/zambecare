import csv
from pathlib import Path

from zambecare_ingestion.contracts import PreparedRecord, decimal_or_none

REQUIRED = {"facility_id", "facility_name", "facility_type", "address_line_1", "city",
            "state_code", "postal_code"}


def extract_facilities(path: Path) -> list[PreparedRecord]:
    records: list[PreparedRecord] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Facility CSV missing columns: {', '.join(sorted(missing))}")
        for row_number, row in enumerate(reader, start=2):
            source_id = (row.get("facility_id") or f"row-{row_number}").strip()
            errors = [f"{name} is required" for name in REQUIRED if not (row.get(name) or "").strip()]
            try:
                latitude = decimal_or_none(row.get("latitude"))
                longitude = decimal_or_none(row.get("longitude"))
            except ValueError:
                latitude = longitude = None
                errors.append("latitude and longitude must be numeric")
            values = {**row, "latitude": latitude, "longitude": longitude}
            records.append(PreparedRecord("Facility", "FACILITY_CSV", source_id, row, values, errors))
    return records

