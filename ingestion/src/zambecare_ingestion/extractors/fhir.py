import json
from pathlib import Path
from typing import Any

from zambecare_ingestion.contracts import (
    PreparedRecord,
    decimal_or_none,
    parse_iso_date,
    parse_iso_datetime,
)


def _reference(value: dict[str, Any] | None) -> str | None:
    reference = (value or {}).get("reference")
    return reference.split("/")[-1] if reference else None


def _coding(concept: dict[str, Any] | None) -> tuple[str | None, str | None, str | None]:
    coding = ((concept or {}).get("coding") or [{}])[0]
    return coding.get("code"), coding.get("system"), coding.get("display")


def _name(resource: dict[str, Any]) -> tuple[str | None, str | None]:
    name = (resource.get("name") or [{}])[0]
    return " ".join(name.get("given") or []) or None, name.get("family")


def _normalize(resource: dict[str, Any], source_system: str) -> PreparedRecord:
    entity = resource.get("resourceType", "Unknown")
    source_id = resource.get("id") or "missing-id"
    errors = []
    if source_id == "missing-id":
        errors.append("FHIR_ID_REQUIRED")

    values: dict[str, Any] = {}
    try:
        if entity == "Patient":
            first, last = _name(resource)
            telecom = {item.get("system"): item.get("value") for item in resource.get("telecom", [])}
            values = {"external_patient_id": source_id, "first_name": first, "last_name": last,
                      "date_of_birth": parse_iso_date(resource.get("birthDate")),
                      "sex_at_birth": resource.get("gender"), "email": telecom.get("email"),
                      "phone": telecom.get("phone")}
            if not first or not last or not values["date_of_birth"]:
                errors.append("PATIENT_NAME_AND_BIRTH_DATE_REQUIRED")
        elif entity == "Practitioner":
            first, last = _name(resource)
            specialty, _, _ = _coding(((resource.get("qualification") or [{}])[0]).get("code"))
            identifier = ((resource.get("identifier") or [{}])[0]).get("value")
            values = {"practitioner_identifier": identifier, "first_name": first,
                      "last_name": last, "specialty_code": specialty}
            if not first or not last:
                errors.append("PRACTITIONER_NAME_REQUIRED")
        elif entity == "Organization":
            address = (resource.get("address") or [{}])[0]
            facility_type, _, _ = _coding((resource.get("type") or [{}])[0])
            values = {"facility_name": resource.get("name"), "facility_type": facility_type,
                      "address_line_1": " ".join(address.get("line") or []), "city": address.get("city"),
                      "state_code": address.get("state"), "postal_code": address.get("postalCode"),
                      "latitude": None, "longitude": None}
            entity = "Facility"
            if not values["facility_name"]:
                errors.append("FACILITY_NAME_REQUIRED")
        elif entity == "Encounter":
            period = resource.get("period") or {}
            encounter_type, _, _ = _coding((resource.get("type") or [{}])[0])
            participant = (resource.get("participant") or [{}])[0]
            values = {"source_patient_id": _reference(resource.get("subject")),
                      "source_practitioner_id": _reference(participant.get("individual")),
                      "source_facility_id": _reference(resource.get("serviceProvider") or {}),
                      "encounter_type": encounter_type, "encounter_status": resource.get("status"),
                      "started_at": parse_iso_datetime(period.get("start")),
                      "ended_at": parse_iso_datetime(period.get("end"))}
            if not values["source_patient_id"] or not values["started_at"]:
                errors.append("ENCOUNTER_PATIENT_AND_START_REQUIRED")
        elif entity == "Condition":
            code, system, _ = _coding(resource.get("code"))
            clinical, _, _ = _coding(resource.get("clinicalStatus"))
            values = {"source_patient_id": _reference(resource.get("subject")),
                      "source_encounter_id": _reference(resource.get("encounter")),
                      "condition_code": code, "code_system": system, "clinical_status": clinical,
                      "recorded_at": parse_iso_datetime(resource.get("recordedDate"))}
            if not values["source_patient_id"] or not code:
                errors.append("CONDITION_PATIENT_AND_CODE_REQUIRED")
        elif entity == "Observation":
            code, _, display = _coding(resource.get("code"))
            quantity = resource.get("valueQuantity") or {}
            values = {"source_patient_id": _reference(resource.get("subject")),
                      "source_encounter_id": _reference(resource.get("encounter")),
                      "observation_code": code, "observation_name": display,
                      "numeric_value": decimal_or_none(quantity.get("value")),
                      "unit_code": quantity.get("code") or quantity.get("unit"),
                      "observed_at": parse_iso_datetime(resource.get("effectiveDateTime"))}
            if not values["source_patient_id"] or not code or values["numeric_value"] is None:
                errors.append("OBSERVATION_PATIENT_CODE_VALUE_REQUIRED")
        else:
            errors.append("UNSUPPORTED_FHIR_RESOURCE")
    except (TypeError, ValueError, IndexError) as exc:
        errors.append(f"FHIR_PARSE_ERROR: {exc}")
    return PreparedRecord(entity, source_system, source_id, resource, values, errors)


def extract_fhir(path: Path, source_system: str = "FHIR_FILE") -> list[PreparedRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    resources = ([entry.get("resource", {}) for entry in payload.get("entry", [])]
                 if payload.get("resourceType") == "Bundle" else [payload])
    return [_normalize(resource, source_system) for resource in resources]

