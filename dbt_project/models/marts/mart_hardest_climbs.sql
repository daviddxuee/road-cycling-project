with climbs as (
    select * from {{ ref('stg_climbs') }}
)

select
    climb_name,
    country,
    region,
    difficulty_points,
    length_km,
    average_gradient_pct,
    total_ascent_m,
    rank() over (order by difficulty_points desc) as difficulty_rank
from climbs
where difficulty_points is not null
order by difficulty_points desc
