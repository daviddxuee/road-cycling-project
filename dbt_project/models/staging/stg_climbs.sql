with source as (
    select * from {{ source('raw', 'climbs') }}
),

renamed as (
    select
        name                                                as climb_name,
        difficulty_points,
        replace(length, ' km', '')::float                  as length_km,
        replace(average_gradient, '%', '')::float          as average_gradient_pct,
        replace(steepest_100_metres, '%', '')::float       as steepest_100m_pct,
        replace(total_ascent, ' m', '')::float             as total_ascent_m,
        country,
        region,
        url
    from source
)

select * from renamed