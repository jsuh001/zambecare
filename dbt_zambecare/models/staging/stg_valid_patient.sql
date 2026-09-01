select
    batch_id,
    source_record_id as source_patient_id,
    source_system,
    extract(year from date_of_birth) as birth_year,
    load_timestamp
from {{ source('zc_stage', 'stg_patient') }}
where validation_status = 'VALID'
