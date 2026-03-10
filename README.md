# 🚴 Road Cycling Data Pipeline

A personal end-to-end data engineering project built from scratch — scraping real cycling data from the web, storing it in Snowflake, and transforming it with dbt.

> Built as a learning project to develop skills in Python, web scraping, Snowflake, dbt, and Git.

---

## 🗂️ Project Overview

This project scrapes data on the world's most famous cycling climbs, Grand Tour race winners, and stage-by-stage results, loads the raw data into Snowflake, and uses dbt to transform it into clean, analytical models.

**Questions this project aims to answer:**
- Which climbs are the hardest in the world?
- How do climbs compare across countries and regions?
- Which countries and riders have dominated the Grand Tours historically?
- Which stage types (mountain, flat, hilly) appear most in each race?
- Which finish locations appear most frequently across Grand Tour stages?

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python | Web scraping and data loading |
| BeautifulSoup | Parsing HTML from web pages |
| Pandas | Shaping and saving data |
| Snowflake | Cloud data warehouse |
| dbt | Data transformation and modeling |
| Git + GitHub | Version control |

---

## 📁 Project Structure

```
road-cycling-project/
├── scrapers/
│   ├── scrape_climbs.py        # Scrapes climb stats from ClimbFinder
│   ├── scrape_races.py         # Scrapes Grand Tour winners from Wikipedia
│   └── scrape_stages.py        # Scrapes stage-by-stage results from Wikipedia
├── loaders/
│   └── load_to_snowflake.py    # Loads all three CSVs into Snowflake
├── dbt_project/
│   ├── models/
│   │   ├── staging/            # Clean raw data
│   │   └── marts/              # Analytical models
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

---

## 🔢 Step by Step Walkthrough

### Step 1 — Set Up the Environment
Installed the required tools:
- Python 3.14, VS Code, Git

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
pip3 install "snowflake-connector-python[pandas]"
```

---

### Step 4 — Scrape Cycling Climbs

Used browser Inspect tool to identify HTML elements on ClimbFinder's ranking page. Scraped 12 pages of 25 climbs each, visiting each climb's individual page for detailed stats. Extracted country and region from breadcrumb navigation.

```python
# Get climb names and URLs from ranking pages
climbs = soup.find_all("a", class_="ranking-item-title")

# Get stats from each climb's page
table = soup.find("table", class_="table-transparant")

# Get country and region from breadcrumb
breadcrumb = soup.find("ol", class_="breadcrumb")
items = breadcrumb.find_all("li", class_="breadcrumb-item")
stats["Country"] = items[3].text.strip()
stats["Region"] = items[-2].text.strip()
```

**Sample output:**

| Name | Difficulty Points | Length | Avg Gradient | Total Ascent | Region | Country |
|---|---|---|---|---|---|---|
| Mont Ventoux | 1352 | 20.8 km | 7.7% | 1594 m | Vaucluse | France |
| Alpe d'Huez | 975 | 14 km | 8% | 1122 m | Bourg d'Oisans | France |
| Passo dello Stelvio | 1465 | 24.9 km | 7.4% | 1846 m | Bolzano | Italy |

---

### Step 5 — Scrape Grand Tour Race Winners

Scraped historical Grand Tour winners from Wikipedia (1903–2025).

**Key challenge:** ProCyclingStats and FirstCycling were blocked by Cloudflare — Wikipedia used as alternative.

```python
races = [
    ("...Tour_de_France_general_classification_winners", "Tour de France"),
    ("...Giro_d%27Italia_general_classification_winners", "Giro d'Italia"),
    ("...Vuelta_a_Espa%C3%B1a_general_classification_winners", "Vuelta a España")
]
```

---

### Step 6 — Scrape Grand Tour Stages

Scraped stage-by-stage results for 2020–2024 from Wikipedia.

**Key challenge:** Some race pages had an extra elevation column that shifted all other columns by one position. Fixed by detecting the column structure from the header row:

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

### Step 7 — Clean Data

```python
# Remove blank rows
df_clean = df.dropna(subset=['Length', 'Country', 'Region'])

# Clean special characters
df['winner'] = df['winner'].str.replace('&', '').str.strip()

# Fix encoding
df.to_csv("stages.csv", index=False, encoding='utf-8-sig')
```

---

### Step 8 — Set Up Snowflake

Created a Snowflake free trial account on AWS US West (Oregon). Set up the database structure:

```sql
CREATE DATABASE cycling_project;
USE DATABASE cycling_project;
CREATE SCHEMA raw;

CREATE TABLE climbs (
    name VARCHAR,
    difficulty_points FLOAT,
    length VARCHAR,
    average_gradient VARCHAR,
    steepest_100_metres VARCHAR,
    total_ascent VARCHAR,
    country VARCHAR,
    region VARCHAR,
    url VARCHAR
);

CREATE TABLE races (
    race VARCHAR,
    year INT,
    winner VARCHAR,
    country VARCHAR,
    team VARCHAR,
    distance VARCHAR
);

CREATE TABLE stages (
    race VARCHAR,
    year INT,
    stage VARCHAR,
    date VARCHAR,
    route VARCHAR,
    distance VARCHAR,
    stage_type VARCHAR,
    stage_winner VARCHAR
);
```

---

### Step 9 — Load Data into Snowflake

Used the Snowflake Python connector to load all three CSVs into Snowflake:

```python
conn = snowflake.connector.connect(
    user="your_username",
    password="your_password",
    account="WVAZMTZ-SSB01665",
    warehouse="COMPUTE_WH",
    database="CYCLING_PROJECT",
    schema="RAW"
)

write_pandas(conn, climbs, "CLIMBS")
write_pandas(conn, races, "RACES")
write_pandas(conn, stages, "STAGES")
```

Verified data loaded correctly:
```sql
SELECT 'climbs' AS table_name, COUNT(*) AS row_count FROM climbs
UNION ALL
SELECT 'races', COUNT(*) FROM races
UNION ALL
SELECT 'stages', COUNT(*) FROM stages;
```

Result:
```
climbs    300
races     307
stages    312
```

---

## 🚧 What's Next

- [ ] Connect dbt to Snowflake and build staging models
- [ ] Build mart models to answer analytical questions
- [ ] Visualize results in a dashboard

---

## 💡 What I Learned

- How to inspect HTML with browser developer tools to find the right elements to scrape
- How to handle Cloudflare protection and find alternative data sources
- How to loop through multiple pages to collect larger datasets
- How to extract location data from breadcrumb navigation
- How to debug scrapers by printing raw HTML to understand page structure
- How to handle inconsistent table structures using conditional logic
- How to fix character encoding issues with UTF-8
- How to clean data with pandas
- How to set up a Snowflake database, schema, and tables
- How to load CSV data into Snowflake using Python
- How Git and GitHub work together for version control

---

## 👤 Author

**David Xue**
[GitHub](https://github.com/daviddxuee/road-cycling-project)
