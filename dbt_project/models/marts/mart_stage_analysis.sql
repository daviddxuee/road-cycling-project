with stages as (
    select * from {{ ref('stg_stages') }}
)

select
    race,
    race_year,
    stage_type,
    count(*) as num_stages
from stages
where stage_type != ''
group by race, race_year, stage_type
order by race, race_year, num_stages desc
