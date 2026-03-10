with race_climbs as (
    select * from {{ ref('stg_race_climbs') }}
),

climbs as (
    select * from {{ ref('stg_climbs') }}
)

select
    rc.race,
    rc.position,
    rc.climb_name,
    rc.num_stages,
    rc.num_editions,
    rc.first_year,
    c.country,
    c.region,
    c.difficulty_points,
    c.length_km,
    c.average_gradient_pct,
    c.total_ascent_m
from race_climbs rc
left join climbs c
    on lower(trim(rc.climb_name)) = lower(trim(c.climb_name))
order by rc.race, rc.position
