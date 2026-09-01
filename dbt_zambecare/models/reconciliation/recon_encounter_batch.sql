with source_counts as (
    select batch_id, count(*) as source_count
    from {{ source('zc_stage', 'stg_encounter') }}
    group by batch_id
),
target_counts as (
    select batch_id, count(*) as target_count
    from {{ ref('fact_encounter') }}
    group by batch_id
),
reject_counts as (
    select batch_id, count(*) as rejected_count
    from {{ source('zc_audit', 'rejected_record') }}
    where upper(source_entity) = 'ENCOUNTER'
    group by batch_id
)
select
    s.batch_id,
    s.source_count,
    coalesce(t.target_count, 0) as target_count,
    coalesce(r.rejected_count, 0) as rejected_count,
    s.source_count - coalesce(t.target_count, 0) - coalesce(r.rejected_count, 0)
        as unexplained_count,
    case
        when s.source_count = coalesce(t.target_count, 0) + coalesce(r.rejected_count, 0)
            then 'PASS'
        else 'FAIL'
    end as reconciliation_status
from source_counts s
left join target_counts t on t.batch_id = s.batch_id
left join reject_counts r on r.batch_id = s.batch_id
