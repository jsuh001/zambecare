# Phase 3 source-to-target mapping

## FHIR resources

| Source | Key mappings | Oracle target |
|---|---|---|
| Patient | `id`, `name`, `birthDate`, `gender`, `telecom` | `ZC_STAGE.STG_PATIENT` |
| Practitioner | `id`, identifier, name, qualification code | `ZC_STAGE.STG_PRACTITIONER` |
| Organization | `id`, name, type, address | `ZC_STAGE.STG_FACILITY` |
| Encounter | subject, participant, organization, type, status, period | `ZC_STAGE.STG_ENCOUNTER` |
| Condition | subject, encounter, clinical status, ICD-10-CM-shaped code | `ZC_STAGE.STG_CONDITION` |
| Observation | subject, encounter, LOINC-shaped code, value, UCUM-shaped unit | `ZC_STAGE.STG_OBSERVATION` |

FHIR references such as `Patient/pt-7a241` are normalized to the source identifier
`pt-7a241`. Original resources are retained as JSON in `raw_payload` for lineage. A SHA-256
`record_hash` is calculated from canonical JSON.

## PostgreSQL patient

| PostgreSQL | Oracle |
|---|---|
| `external_patient_id` | `source_record_id`, `external_patient_id` |
| `first_name`, `last_name` | Same named staging columns |
| `date_of_birth` | `date_of_birth` |
| `sex_at_birth` | `sex_at_birth` |
| `email`, `phone` | Same named staging columns |
| `updated_at` | Extraction watermark boundary and raw lineage value |

The extraction predicate is `updated_at > start_watermark AND updated_at <= end_watermark`.
The upper boundary is fixed before extraction to prevent records arriving mid-run from being
lost.

## Facility CSV

Required columns are `facility_id`, `facility_name`, `facility_type`, `address_line_1`,
`city`, `state_code`, and `postal_code`. Latitude and longitude are optional numeric fields.
Facility rows never enter the patient table.

## Initial rule codes

| Rule | Meaning |
|---|---|
| `FHIR_ID_REQUIRED` | Resource has no stable source ID |
| `PATIENT_NAME_AND_BIRTH_DATE_REQUIRED` | Required patient identity fields are absent |
| `PRACTITIONER_NAME_REQUIRED` | Practitioner name is incomplete |
| `FACILITY_NAME_REQUIRED` | Organization/facility name is missing |
| `ENCOUNTER_PATIENT_AND_START_REQUIRED` | Encounter lacks patient or start time |
| `CONDITION_PATIENT_AND_CODE_REQUIRED` | Condition lacks patient or clinical code |
| `OBSERVATION_PATIENT_CODE_VALUE_REQUIRED` | Vital sign lacks patient, code, or value |
| `UNSUPPORTED_FHIR_RESOURCE` | Resource is outside the Phase 3 contract |

