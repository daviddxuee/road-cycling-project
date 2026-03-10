# 🚴 Road Cycling Data Pipeline

A personal end-to-end data engineering project built from scratch — scraping real cycling data from the web, storing it in Snowflake, and transforming it with dbt.

> Built as a learning project to develop skills in Python, web scraping, Snowflake, dbt, and Git — with Claude (Anthropic's AI) as a collaborative coding partner throughout the entire project.

---

## 🤖 How I Used AI in This Project

This project was built in close collaboration with **Claude (Anthropic)**, an AI assistant. Rather than simply copying and pasting code, I used Claude as an interactive coding partner to:

- **Make architectural decisions** — Claude helped me scope the project, choose data sources, and decide what datasets to build
- **Debug errors in real time** — every error was pasted into Claude, which diagnosed the issue and explained why it happened
- **Learn while building** — Claude walked me through each concept line by line, gave exercises to test my understanding, and explained the "why" behind every decision
- **Navigate blockers** — when ProCyclingStats and FirstCycling were blocked by Cloudflare, Claude suggested alternative sources and tools like `cloudscraper`
- **Write and iterate on code** — Claude generated the initial scripts, but I ran every command, interpreted every result, and made decisions about what data to collect and how to clean it

This approach reflects how modern data professionals work — knowing how to effectively leverage AI tools to accelerate development, debug faster, and make better decisions is a core skill in today's data engineering landscape.

---

## 🗂️ Project Overview

This project scrapes data on the world's most famous cycling climbs, Grand Tour race winners, stage-by-stage results, and climb appearances in races, loads the raw data into Snowflake, and uses dbt to transform it into clean, analytical models.

**Questions this project answers:**
- Which climbs are the hardest in the world?
- How do climbs compare across countries and regions?
- Which countries and riders have dominated the Grand Tours historically?
- Which climbs appear most frequently in the Tour de France, Giro d'Italia, and Vuelta a España?
- Which stage types (mountain, flat, hilly) appear most in each race?

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Web scraping and data loading |
| BeautifulSoup | Parsing HTML from web pages |
| cloudscraper | Bypassing Cloudflare protection |
| Pandas | Shaping and saving data |
| Snowflake | Cloud data warehouse |
| dbt | Data transformation and modeling |
| Git + GitHub | Version control |
| Claude (Anthropic) | AI coding partner and debugging assistant |

---

## 📁 Project Structure

```
road-cycling-project/
├── scrapers/
│   ├── scrape_climbs.py          # Scrapes climb stats from ClimbFinder
│   ├── scrape_races.py           # Scrapes Grand Tour winners from Wikipedia
│   ├── scrape_stages.py          # Scrapes stage-by-stage results from Wikipedia
│   └── scrape_race_climbs.py     # Scrapes climb appearances per race from ProCyclingStats
├── loaders/
│   └── load_to_snowflake.py      # Loads all four CSVs into Snowflake
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   ├── stg_climbs.sql
│   │   │   ├── stg_races.sql
│   │   │   ├── stg_stages.sql
│   │   │   └── stg_race_climbs.sql
│   │   └── marts/
│   │       ├── mart_hardest_climbs.sql
│   │       ├── mart_grand_tour_winners.sql
│   │       ├── mart_climb_appearances.sql
│   │       └── mart_stage_analysis.sql
└── README.md
```

---

## 📊 Datasets

### 1. Cycling Climbs (`climbs.csv`) — 300 rows
The world's most popular cycling climbs scraped from [ClimbFinder](https://climbfinder.com).

| Column | Description |
|---|---|
| name | Name of the climb |
| difficulty_points | Overall difficulty score |
| length | Length of the climb |
| average_gradient | Average gradient (%) |
| steepest_100_metres | Steepest 100m section (%) |
| total_ascent | Total elevation gain |
| region | Region where the climb is located |
| country | Country where the climb is located |

### 2. Grand Tour Winners (`races.csv`) — 307 rows
Historical race winners across all three Grand Tours scraped from Wikipedia (1903–2025).

| Column | Description |
|---|---|
| race | Race name |
| year | Year of the race |
| winner | Name of the winner |
| country | Winner's country |
| team | Winner's team |
| distance | Total race distance |

### 3. Grand Tour Stages (`stages.csv`) — 312 rows
Stage-by-stage results for 2020–2024 across all three Grand Tours.

| Column | Description |
|---|---|
| race | Race name |
| year | Year of the race |
| stage | Stage number |
| route | Start and finish locations |
| stage_type | Type of stage (Flat, Mountain, Hilly, Time trial) |
| stage_winner | Name and nationality of stage winner |

### 4. Race Climbs (`race_climbs.csv`) — 120 rows
Most frequently visited climbs per Grand Tour from [ProCyclingStats](https://www.procyclingstats.com).

| Column | Description |
|---|---|
| race | Race name |
| position | Ranking position |
| climb_name | Name of the climb |
| num_stages | Number of stages the climb has appeared in |
| num_editions | Number of race editions the climb has appeared in |
| first_year | First year the climb appeared in the race |

---

## 🔢 Step by Step Walkthrough

### Step 1 — Set Up the Environment
Installed Python 3.11 (via pyenv), VS Code, Git, and Homebrew. Configured Git identity for version control.

> **AI collaboration:** Claude helped diagnose that dbt is incompatible with Python 3.14 and guided the installation of pyenv and Python 3.11 as a fix.

```bash
brew install pyenv
pyenv install 3.11
pyenv local 3.11
git config --global user.name "David Xue"
git config --global user.email "youremail@gmail.com"
```

---

### Step 2 — Create GitHub Repo and Clone Locally
```bash
git clone https://github.com/daviddxuee/road-cycling-project.git
cd road-cycling-project
code .
```

---

### Step 3 — Install Python Libraries
```bash
pip install requests beautifulsoup4 pandas lxml
pip install cloudscraper procyclingstats
pip install "snowflake-connector-python[pandas]"
pip install dbt-snowflake
```

---

### Step 4 — Scrape Cycling Climbs

> **AI collaboration:** Claude suggested ClimbFinder as a data source, helped identify the correct HTML elements using browser Inspect tool screenshots, and debugged multiple issues including 403 errors, wrong table classes, and Python 3.14 BeautifulSoup compatibility issues.

Scraped 12 pages of 25 climbs each from ClimbFinder, visiting each individual climb page for detailed stats. Extracted country and region from breadcrumb navigation.

```python
# Get stats from each climb's page
table = soup.find("table", class_="table-transparant")

# Get country and region from breadcrumb
# Structure: Home > World > Europe > Country > ... > Region > Climb Name
breadcrumb = soup.find("ol", class_="breadcrumb")
items = breadcrumb.find_all("li", class_="breadcrumb-item")
stats["Country"] = items[3].text.strip()
stats["Region"] = items[-2].text.strip()
```

---

### Step 5 — Scrape Grand Tour Race Winners

> **AI collaboration:** Claude identified that ProCyclingStats and FirstCycling were protected by Cloudflare and suggested Wikipedia as a reliable alternative. Claude also helped debug the table selection issue by printing raw HTML to understand the page structure.

```python
tables = soup.find_all("table", class_="wikitable")
table = tables[1]  # First table is a legend key, second is the actual data
```

---

### Step 6 — Scrape Grand Tour Stages

> **AI collaboration:** Claude identified that some race pages had an extra elevation column that shifted all other columns by one position, and implemented a conditional fix based on the header row.

```python
has_elevation = "elevation" in header_text
if has_elevation:
    stage_type = tds[5].text.strip()
    winner = tds[6].text.strip()
else:
    stage_type = tds[4].text.strip()
    winner = tds[5].text.strip()
```

---

### Step 7 — Scrape Race Climbs from ProCyclingStats

> **AI collaboration:** I identified the ProCyclingStats climb frequency pages as a valuable data source. Claude suggested using `cloudscraper` to bypass Cloudflare protection after the standard requests library was blocked.

```python
import cloudscraper
scraper = cloudscraper.create_scraper()
response = scraper.get("https://www.procyclingstats.com/race/tour-de-france/route/climbs")
```

---

### Step 8 — Set Up Snowflake

> **AI collaboration:** Claude guided the Snowflake setup step by step, including creating the database, schema, and tables with appropriate data types.

```sql
CREATE DATABASE cycling_project;
CREATE SCHEMA raw;
CREATE TABLE climbs (...);
CREATE TABLE races (...);
CREATE TABLE stages (...);
CREATE TABLE race_climbs (...);
```

---

### Step 9 — Load Data into Snowflake

> **AI collaboration:** Claude identified a duplicate data issue when the loader was run multiple times and implemented a truncation step to prevent it.

```python
cursor.execute("TRUNCATE TABLE climbs")
cursor.execute("TRUNCATE TABLE races")
cursor.execute("TRUNCATE TABLE stages")
cursor.execute("TRUNCATE TABLE race_climbs")

write_pandas(conn, climbs, "CLIMBS")
write_pandas(conn, races, "RACES")
write_pandas(conn, stages, "STAGES")
write_pandas(conn, race_climbs, "RACE_CLIMBS")
```

---

### Step 10 — Build dbt Staging Models

> **AI collaboration:** Claude explained the dbt staging/mart architecture, helped fix column name mismatches between the scraper output and Snowflake, and guided the setup of the sources.yml configuration file.

Built 4 staging models to clean raw data — fixing column names, casting data types, and stripping units:

```sql
-- Example: stg_climbs.sql
select
    name                                          as climb_name,
    difficulty_points,
    replace(length, ' km', '')::float             as length_km,
    replace(average_gradient, '%', '')::float     as average_gradient_pct,
    country,
    region
from {{ source('raw', 'climbs') }}
```

---

### Step 11 — Build dbt Mart Models

> **AI collaboration:** Claude identified that special characters like `§` and `‡` in winner names were causing incorrect win counts in the grand tour winners model, and implemented a fix to strip them in the staging layer. This caught that Eddy Merckx and Tadej Pogačar's wins were being undercounted.

Built 4 mart models to answer analytical questions:

- **mart_hardest_climbs** — top climbs ranked by difficulty with country and region
- **mart_grand_tour_winners** — most successful riders and countries across Grand Tours
- **mart_climb_appearances** — climb frequency data enriched with difficulty stats
- **mart_stage_analysis** — breakdown of stage types per race per year

**Sample insight — most dominant riders:**

| Rider | Country | Race | Wins |
|---|---|---|---|
| Eddy Merckx | Belgium | Tour de France | 5 |
| Eddy Merckx | Belgium | Giro d'Italia | 5 |
| Tadej Pogačar | Slovenia | Tour de France | 4 |
| Fausto Coppi | Italy | Giro d'Italia | 5 |

---

## 💡 What I Learned

**Technical skills:**
- How to inspect HTML with browser developer tools to find scrapeable elements
- How to handle Cloudflare protection using cloudscraper
- How to loop through multiple pages to collect larger datasets
- How to extract location data from breadcrumb navigation
- How to debug scrapers by printing raw HTML
- How to handle inconsistent table structures using conditional logic
- How to fix character encoding issues with UTF-8
- How to set up a Snowflake database and load data with Python
- How to build a dbt pipeline with staging and mart layers
- How Git and GitHub work together for version control

**AI collaboration skills:**
- How to effectively communicate errors and context to an AI assistant
- How to use AI to make architectural and data source decisions
- How to iterate quickly by combining AI suggestions with hands-on testing
- How to learn from AI explanations rather than just copying code
- How to use AI as a debugging partner by sharing raw output and error messages

---

## 👤 Author

**David Xue**
[GitHub](https://github.com/daviddxuee/road-cycling-project)