select
    batch_id,
    source_record_id as source_encounter_id,
    source_patient_id,
    encounter_type,
    encounter_status,
    started_at,
    ended_at,
    load_timestamp
from {{ source('zc_stage', 'stg_encounter') }}
where validation_status = 'VALID'
