with source as (
    select * from {{ source('raw', 'stages') }}
),

renamed as (
    select
        race,
        year::int                                    as race_year,
        stage,
        date,
        route,
        distance,
        stage_type,
        stage_winner
    from source
)

select * from renamed