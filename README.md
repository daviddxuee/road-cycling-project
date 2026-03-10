# 🚴 Road Cycling Data Pipeline

A personal end-to-end data engineering project built from scratch — scraping real cycling data from the web, storing it in Snowflake, and transforming it with dbt.

> Built as a learning project to develop skills in Python, web scraping, Snowflake, dbt, and Git.

---

## 🗂️ Project Overview

This project scrapes data on the world's most famous cycling climbs, Grand Tour race winners, stage-by-stage results, and climb appearances in races, loads the raw data into Snowflake, and uses dbt to transform it into clean, analytical models.

**Questions this project aims to answer:**
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
│   │   ├── staging/              # Clean raw data
│   │   └── marts/                # Analytical models
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
| url | Source URL |

### 2. Grand Tour Winners (`races.csv`) — 307 rows
Historical race winners across all three Grand Tours scraped from Wikipedia (1903–2025).

| Column | Description |
|---|---|
| race | Race name (Tour de France, Giro d'Italia, Vuelta a España) |
| year | Year of the race |
| winner | Name of the winner |
| country | Winner's country |
| team | Winner's team |
| distance | Total race distance |

### 3. Grand Tour Stages (`stages.csv`) — 312 rows
Stage-by-stage results for 2020–2024 across all three Grand Tours scraped from Wikipedia.

| Column | Description |
|---|---|
| race | Race name |
| year | Year of the race |
| stage | Stage number |
| date | Date of the stage |
| route | Start and finish locations |
| distance | Stage distance |
| stage_type | Type of stage (Flat, Mountain, Hilly, Time trial) |
| stage_winner | Name and nationality of stage winner |

### 4. Race Climbs (`race_climbs.csv`) — 120 rows
Most frequently visited climbs per Grand Tour scraped from [ProCyclingStats](https://www.procyclingstats.com).

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
```bash
python3 --version
git --version
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
pip3 install requests beautifulsoup4 pandas lxml
pip3 install cloudscraper procyclingstats
pip3 install "snowflake-connector-python[pandas]"
```

---

### Step 4 — Scrape Cycling Climbs
Scraped 12 pages of 25 climbs each from ClimbFinder, visiting each climb's individual page for detailed stats. Extracted country and region from breadcrumb navigation.

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
Scraped historical Grand Tour winners from Wikipedia (1903–2025).

**Key challenge:** ProCyclingStats and FirstCycling were blocked by Cloudflare — Wikipedia used as alternative.

---

### Step 6 — Scrape Grand Tour Stages
Scraped stage-by-stage results for 2020–2024 from Wikipedia.

**Key challenge:** Some pages had an extra elevation column shifting all other columns by one. Fixed by detecting column structure from the header:

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
Scraped the most frequently visited climbs per Grand Tour from ProCyclingStats using `cloudscraper` to bypass Cloudflare protection.

```python
import cloudscraper

scraper = cloudscraper.create_scraper()

races = [
    ("https://www.procyclingstats.com/race/tour-de-france/route/climbs", "Tour de France"),
    ("https://www.procyclingstats.com/race/giro-d-italia/route/climbs", "Giro d'Italia"),
    ("https://www.procyclingstats.com/race/vuelta-a-espana/route/climbs", "Vuelta a España")
]
```

**Sample output:**

| Race | Position | Climb | Stages | Editions | First Year |
|---|---|---|---|---|---|
| Tour de France | 1 | Col du Tourmalet | 62 | 61 | 1910 |
| Tour de France | 2 | Col du Galibier | 39 | 37 | 1923 |
| Tour de France | 4 | L'Alpe d'Huez | 34 | 31 | 1952 |

---

### Step 8 — Set Up Snowflake
Created a Snowflake free trial account on AWS US West (Oregon) and set up the database structure:

```sql
CREATE DATABASE cycling_project;
USE DATABASE cycling_project;
CREATE SCHEMA raw;

CREATE TABLE climbs (...);
CREATE TABLE races (...);
CREATE TABLE stages (...);
CREATE TABLE race_climbs (...);
```

---

### Step 9 — Load Data into Snowflake
Used the Snowflake Python connector to load all four CSVs. Added truncation before each load to prevent duplicate data:

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

Verified data loaded correctly:
```sql
SELECT 'climbs' AS table_name, COUNT(*) AS row_count FROM climbs
UNION ALL
SELECT 'races', COUNT(*) FROM races
UNION ALL
SELECT 'stages', COUNT(*) FROM stages
UNION ALL
SELECT 'race_climbs', COUNT(*) FROM race_climbs;
```

Result:
```
climbs        300
races         307
stages        312
race_climbs   120
```

---

## 🚧 What's Next

- [ ] Connect dbt to Snowflake and build staging models
- [ ] Build mart models to answer analytical questions
- [ ] Visualize results in a dashboard

---

## 💡 What I Learned

- How to inspect HTML with browser developer tools to find the right elements to scrape
- How to handle Cloudflare protection using cloudscraper
- How to loop through multiple pages to collect larger datasets
- How to extract location data from breadcrumb navigation
- How to debug scrapers by printing raw HTML to understand page structure
- How to handle inconsistent table structures using conditional logic
- How to fix character encoding issues with UTF-8
- How to clean data with pandas
- How to set up a Snowflake database, schema, and tables
- How to load CSV data into Snowflake using Python
- How to prevent duplicate data by truncating tables before loading
- How Git and GitHub work together for version control

---

## 👤 Author

**David Xue**
[GitHub](https://github.com/daviddxuee/road-cycling-project)