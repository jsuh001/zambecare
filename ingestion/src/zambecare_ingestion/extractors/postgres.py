from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row

from zambecare_ingestion.contracts import PreparedRecord

PATIENT_SQL = """
SELECT external_patient_id::text AS source_record_id, first_name, last_name,
       date_of_birth, sex_at_birth, email, phone, updated_at
FROM clinical.patient
WHERE updated_at > %(start_watermark)s
  AND updated_at <= %(end_watermark)s
  AND is_active = TRUE
ORDER BY updated_at, patient_id
"""


def extract_patients(
    postgres_url: str, start_watermark: datetime, end_watermark: datetime
) -> list[PreparedRecord]:
    with psycopg.connect(postgres_url, row_factory=dict_row) as connection:
        rows: list[dict[str, Any]] = connection.execute(
            PATIENT_SQL,
            {"start_watermark": start_watermark, "end_watermark": end_watermark},
        ).fetchall()

    records = []
    for row in rows:
        raw = {key: value for key, value in row.items()}
        source_id = raw.pop("source_record_id")
        values = {
            "external_patient_id": source_id,
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "date_of_birth": row["date_of_birth"],
            "sex_at_birth": row["sex_at_birth"],
            "email": row["email"],
            "phone": row["phone"],
        }
        records.append(PreparedRecord("Patient", "POSTGRES", source_id, raw, values))
    return records

