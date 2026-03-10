with source as (
    select * from {{ source('raw', 'races') }}
),

renamed as (
    select
        race,
        year::int                                                           as race_year,
        trim(replace(replace(replace(winner, '§', ''), '*', ''), '‡', '')) as winner,
        country                                                             as winner_country,
        team,
        replace(distance, ' km', '')                                        as distance_km
    from source
)

select * from renamed
