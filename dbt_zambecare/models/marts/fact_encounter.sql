{{
    config(
        materialized='incremental',
        unique_key=['batch_id', 'source_encounter_id'],
        incremental_strategy='merge'
    )
}}

select
    e.batch_id,
    e.source_encounter_id,
    p.source_patient_id,
    e.encounter_type,
    e.encounter_status,
    e.started_at,
    e.ended_at,
    e.load_timestamp
from {{ ref('stg_valid_encounter') }} e
join {{ ref('stg_valid_patient') }} p
  on p.source_patient_id = e.source_patient_id
{% if is_incremental() %}
where e.load_timestamp > (
    select coalesce(max(load_timestamp), timestamp '1900-01-01 00:00:00') from {{ this }}
)
{% endif %}
