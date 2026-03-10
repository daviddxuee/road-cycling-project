import snowflake.connector
import pandas as pd
from snowflake.connector.pandas_tools import write_pandas

# Connect to Snowflake
conn = snowflake.connector.connect(
    user="x",
    password="x",
    account="x",
    warehouse="x",
    database="CYCLING_PROJECT",
    schema="RAW"
)

print("Connected to Snowflake!")

print("Truncating tables...")
cursor = conn.cursor()
cursor.execute("TRUNCATE TABLE climbs")
cursor.execute("TRUNCATE TABLE races")
cursor.execute("TRUNCATE TABLE stages")
cursor.execute("TRUNCATE TABLE race_climbs")
print("Tables truncated!")

# Load climbs
print("Loading climbs...")
climbs = pd.read_csv("climbs.csv")
climbs.columns = [c.upper().replace(" ", "_") for c in climbs.columns]
write_pandas(conn, climbs, "CLIMBS")
print(f"Loaded {len(climbs)} climbs!")

# Load races
print("Loading races...")
races = pd.read_csv("races.csv")
races.columns = [c.upper().replace(" ", "_") for c in races.columns]
write_pandas(conn, races, "RACES")
print(f"Loaded {len(races)} races!")

# Load stages
print("Loading stages...")
stages = pd.read_csv("stages.csv", encoding="utf-8-sig")
stages.columns = [c.upper().replace(" ", "_") for c in stages.columns]
write_pandas(conn, stages, "STAGES")
print(f"Loaded {len(stages)} stages!")

# Load race climbs
print("Loading race climbs...")
race_climbs = pd.read_csv("race_climbs.csv")
race_climbs.columns = [c.upper().replace(" ", "_") for c in race_climbs.columns]
write_pandas(conn, race_climbs, "RACE_CLIMBS")
print(f"Loaded {len(race_climbs)} race climbs!")

print("All done!")
conn.close()
