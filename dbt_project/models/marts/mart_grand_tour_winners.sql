with races as (
    select * from {{ ref('stg_races') }}
),

wins_by_rider as (
    select
        winner,
        winner_country,
        race,
        count(*) as total_wins,
        min(race_year) as first_win,
        max(race_year) as last_win
    from races
    group by winner, winner_country, race
),

wins_by_country as (
    select
        winner_country,
        count(*) as total_wins
    from races
    group by winner_country
)

select
    r.winner,
    r.winner_country,
    r.race,
    r.total_wins,
    r.first_win,
    r.last_win
from wins_by_rider r
order by total_wins desc
