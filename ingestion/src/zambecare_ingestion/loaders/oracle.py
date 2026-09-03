from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Any

import oracledb

from zambecare_ingestion.config import Settings
from zambecare_ingestion.contracts import PreparedRecord

TABLE_COLUMNS: dict[str, tuple[str, list[str]]] = {
    "Patient": ("zc_stage.stg_patient", ["external_patient_id", "first_name", "last_name",
        "date_of_birth", "sex_at_birth", "email", "phone"]),
    "Practitioner": ("zc_stage.stg_practitioner", ["practitioner_identifier", "first_name",
        "last_name", "specialty_code"]),
    "Facility": ("zc_stage.stg_facility", ["facility_name", "facility_type", "address_line_1",
        "city", "state_code", "postal_code", "latitude", "longitude"]),
    "Encounter": ("zc_stage.stg_encounter", ["source_patient_id", "source_practitioner_id",
        "source_facility_id", "encounter_type", "encounter_status", "started_at", "ended_at"]),
    "Condition": ("zc_stage.stg_condition", ["source_patient_id", "source_encounter_id",
        "condition_code", "code_system", "clinical_status", "recorded_at"]),
    "Observation": ("zc_stage.stg_observation", ["source_patient_id", "source_encounter_id",
        "observation_code", "observation_name", "numeric_value", "unit_code", "observed_at"]),
}


class OracleLoader:
    def __init__(self, settings: Settings):
        self.settings = settings

    def connect(self) -> oracledb.Connection:
        wallet = str(self.settings.oracle_wallet_dir)
        return oracledb.connect(
            user=self.settings.oracle_user,
            password=self.settings.oracle_password,
            dsn=self.settings.oracle_dsn,
            config_dir=wallet,
            wallet_location=wallet,
            wallet_password=self.settings.oracle_wallet_password,
        )

    def healthcheck(self) -> dict[str, str]:
        with self.connect() as connection:
            user, database = connection.cursor().execute(
                "SELECT USER, SYS_CONTEXT('USERENV','DB_NAME') FROM dual"
            ).fetchone()
        return {"status": "ok", "user": user, "database": database}

    @staticmethod
    def create_batch(connection: oracledb.Connection, source: str, entity: str,
                     start: datetime | None, end: datetime | None, version: str) -> int:
        cursor = connection.cursor()
        batch_var = cursor.var(oracledb.DB_TYPE_NUMBER)
        cursor.execute(
            """INSERT INTO zc_audit.etl_batch
               (source_system, entity_name, start_watermark, end_watermark,
                batch_status, code_version)
               VALUES (:source, :entity, :start_wm, :end_wm, 'STARTED', :version)
               RETURNING batch_id INTO :batch_id""",
            source=source, entity=entity, start_wm=start, end_wm=end,
            version=version, batch_id=batch_var,
        )
        connection.commit()
        return int(batch_var.getvalue()[0])

    @staticmethod
    def _insert_valid(cursor: oracledb.Cursor, batch_id: int, record: PreparedRecord) -> None:
        table, columns = TABLE_COLUMNS[record.entity]
        fixed = ["batch_id", "source_system", "source_record_id"]
        trailing = ["raw_payload", "record_hash", "validation_status"]
        all_columns = fixed + columns + trailing
        binds: dict[str, Any] = {"batch_id": batch_id, "source_system": record.source_system,
            "source_record_id": record.source_record_id, "raw_payload": record.raw_json,
            "record_hash": record.record_hash, "validation_status": "VALID"}
        binds.update({column: record.values.get(column) for column in columns})
        placeholders = ", ".join(f":{column}" for column in all_columns)
        cursor.execute(
            f"INSERT INTO {table} ({', '.join(all_columns)}) VALUES ({placeholders})", binds
        )

    @staticmethod
    def _insert_rejected(cursor: oracledb.Cursor, batch_id: int, record: PreparedRecord) -> None:
        cursor.execute(
            """INSERT INTO zc_audit.rejected_record
               (batch_id, source_entity, source_record_id, rule_code,
                rejection_reason, raw_payload, record_hash)
               VALUES (:batch_id, :entity, :source_id, :rule_code,
                       :reason, :payload, :record_hash)""",
            batch_id=batch_id, entity=record.entity, source_id=record.source_record_id,
            rule_code=record.errors[0].split(":", 1)[0], reason="; ".join(record.errors),
            payload=record.raw_json, record_hash=record.record_hash,
        )

    def load_batch(self, records: list[PreparedRecord], source: str, entity: str,
                   start: datetime | None = None, end: datetime | None = None) -> dict[str, int | str]:
        selected = [record for record in records if record.entity == entity]
        with self.connect() as connection:
            batch_id = self.create_batch(connection, source, entity, start, end,
                                         self.settings.code_version)
            accepted = rejected = 0
            try:
                cursor = connection.cursor()
                cursor.execute("UPDATE zc_audit.etl_batch SET batch_status='LOADING', "
                               "source_count=:count WHERE batch_id=:batch_id",
                               count=len(selected), batch_id=batch_id)
                for record in selected:
                    if record.valid:
                        self._insert_valid(cursor, batch_id, record)
                        accepted += 1
                    else:
                        self._insert_rejected(cursor, batch_id, record)
                        rejected += 1
                unexplained = len(selected) - accepted - rejected
                status = "PASS" if unexplained == 0 else "FAIL"
                cursor.execute(
                    """INSERT INTO zc_audit.reconciliation_result
                       (batch_id, entity_name, source_count, staged_count, rejected_count,
                        unexplained_count, reconciliation_status)
                       VALUES (:batch_id, :entity, :source_count, :staged, :rejected,
                               :unexplained, :status)""",
                    batch_id=batch_id, entity=entity, source_count=len(selected), staged=accepted,
                    rejected=rejected, unexplained=unexplained, status=status,
                )
                final_status = "COMPLETED" if status == "PASS" else "FAILED"
                cursor.execute(
                    """UPDATE zc_audit.etl_batch SET batch_status=:status,
                       staged_count=:staged, rejected_count=:rejected, completed_at=SYSTIMESTAMP
                       WHERE batch_id=:batch_id""",
                    status=final_status, staged=accepted, rejected=rejected, batch_id=batch_id,
                )
                if end and final_status == "COMPLETED":
                    cursor.execute(
                        """MERGE INTO zc_audit.extraction_watermark target
                           USING (SELECT :source source_system, :entity entity_name FROM dual) src
                           ON (target.source_system=src.source_system AND target.entity_name=src.entity_name)
                           WHEN MATCHED THEN UPDATE SET last_success_watermark=:watermark,
                             last_batch_id=:batch_id, updated_at=SYSTIMESTAMP
                           WHEN NOT MATCHED THEN INSERT
                             (source_system, entity_name, last_success_watermark, last_batch_id)
                             VALUES (:source, :entity, :watermark, :batch_id)""",
                        source=source, entity=entity, watermark=end, batch_id=batch_id,
                    )
                connection.commit()
                return {"batch_id": batch_id, "source": len(selected), "staged": accepted,
                        "rejected": rejected, "status": status}
            except Exception as exc:
                connection.rollback()
                with self.connect() as failure_connection:
                    failure_connection.cursor().execute(
                        """UPDATE zc_audit.etl_batch SET batch_status='FAILED',
                           error_message=:message, completed_at=SYSTIMESTAMP
                           WHERE batch_id=:batch_id""",
                        message=str(exc)[:2000], batch_id=batch_id,
                    )
                    failure_connection.commit()
                raise


def entity_counts(records: list[PreparedRecord]) -> Counter[str]:
    return Counter(record.entity for record in records)
