select *
from {{ ref('fact_encounter') }}
where ended_at is not null
  and ended_at < started_at
