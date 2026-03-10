with source as (
    select * from {{ source('raw', 'race_climbs') }}
),

renamed as (
    select
        race,
        position::int       as position,
        climb_name,
        num_stages::int     as num_stages,
        num_editions::int   as num_editions,
        first_year::int     as first_year
    from source
)

select * from renamed