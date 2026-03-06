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
│   └── load_to_snowflake.py    # Loads CSV data into Snowflake
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
Installed the required tools on my machine:
- Python 3.14
- VS Code
- Git

Verified everything was working by running:
```bash
python3 --version
git --version
```

Configured Git with my identity so commits are properly credited:
```bash
git config --global user.name "David Xue"
git config --global user.email "youremail@gmail.com"
```

---

### Step 2 — Create GitHub Repo and Clone Locally
Created a new repository on GitHub, cloned it to my Desktop, and opened it in VS Code:
```bash
git clone https://github.com/daviddxuee/road-cycling-project.git
cd road-cycling-project
code .
```

---

### Step 3 — Install Python Libraries
```bash
pip3 install requests beautifulsoup4 pandas lxml
```

| Library | Purpose |
|---|---|
| `requests` | Fetch web pages |
| `beautifulsoup4` | Parse HTML |
| `pandas` | Organize data into tables |
| `lxml` | HTML parser (more stable than default on Python 3.14) |

---

### Step 4 — Scrape Cycling Climbs

Used the browser's **Inspect** tool to identify HTML elements on ClimbFinder's ranking page.

**Phase 1** — Extract climb names and URLs from ranking pages:
```python
climbs = soup.find_all("a", class_="ranking-item-title")
for climb in climbs:
    name = climb.text.strip()
    link = "https://climbfinder.com/" + climb["href"]
```

**Phase 2** — Visit each climb page and extract stats:
```python
table = soup.find("table", class_="table-transparant")
# Extract country and region from breadcrumb navigation
# Structure: Home > World > Europe > Country > ... > Region > Climb Name
breadcrumb = soup.find("ol", class_="breadcrumb")
items = breadcrumb.find_all("li", class_="breadcrumb-item")
stats["Country"] = items[3].text.strip()
stats["Region"] = items[-2].text.strip()
```

**Phase 3** — Loop through 12 pages to collect 300 climbs:
```python
for page_num in range(1, 13):
    page_url = f"https://climbfinder.com/en/ranking?s=popular&p={page_num}"
    links = get_climb_links(page_url)
    all_climb_links.extend(links)
    time.sleep(1)
```

**Sample output:**

| Name | Difficulty Points | Length | Avg Gradient | Total Ascent | Region | Country |
|---|---|---|---|---|---|---|
| Mont Ventoux | 1352 | 20.8 km | 7.7% | 1594 m | Vaucluse | France |
| Alpe d'Huez | 975 | 14 km | 8% | 1122 m | Bourg d'Oisans | France |
| Passo dello Stelvio | 1465 | 24.9 km | 7.4% | 1846 m | Bolzano | Italy |

---

### Step 5 — Scrape Grand Tour Race Winners

Scraped historical Grand Tour winners from Wikipedia for all three races.

**Key challenge:** ProCyclingStats and FirstCycling were blocked by Cloudflare protection — Wikipedia was used as an alternative with clean, structured HTML tables.

```python
races = [
    ("https://en.wikipedia.org/wiki/List_of_Tour_de_France_general_classification_winners", "Tour de France"),
    ("https://en.wikipedia.org/wiki/List_of_Giro_d%27Italia_general_classification_winners", "Giro d'Italia"),
    ("https://en.wikipedia.org/wiki/List_of_Vuelta_a_Espa%C3%B1a_general_classification_winners", "Vuelta a España")
]
```

**Sample output:**

| Race | Year | Winner | Country | Team |
|---|---|---|---|---|
| Tour de France | 2024 | Tadej Pogačar | Slovenia | UAE Team Emirates |
| Giro d'Italia | 2024 | Tadej Pogačar | Slovenia | UAE Team Emirates |
| Vuelta a España | 2024 | Primož Roglič | Slovenia | Red Bull - Bora - Hansgrohe |

---

### Step 6 — Scrape Grand Tour Stages

Scraped stage-by-stage results for 2020–2024 from Wikipedia.

**Key challenge:** Different race pages had different table structures — the 2023 Tour de France and 2024 Giro d'Italia had an extra elevation gain column that shifted all other columns by one position. Fixed by detecting the column structure from the header row:

```python
header_text = header_row.text.lower()
has_elevation = "elevation" in header_text

if has_elevation:
    stage_type = tds[5].text.strip()
    winner = tds[6].text.strip()
else:
    stage_type = tds[4].text.strip()
    winner = tds[5].text.strip()
```

**Sample output:**

| Race | Year | Stage | Route | Stage Type | Winner |
|---|---|---|---|---|---|
| Tour de France | 2024 | 1 | Florence to Rimini | Hilly stage | Romain Bardet |
| Giro d'Italia | 2024 | 1 | Venaria Reale to Torino | Flat stage | Jonathan Milan |
| Vuelta a España | 2024 | 1 | Lisbon to Oeiras | Flat stage | Sam Welsford |

---

### Step 7 — Clean Data

After scraping, data was cleaned using pandas:
```python
# Remove blank rows from climbs
df_clean = df.dropna(subset=['Length', 'Country', 'Region'])

# Clean special characters from race winner names
df['winner'] = df['winner'].str.replace('&', '').str.strip()

# Fix encoding issues in stages data
df.to_csv("stages.csv", index=False, encoding='utf-8-sig')
```

---

### Step 8 — Push to GitHub

All changes were version controlled with descriptive commit messages:
```bash
git add .
git commit -m "add climbs scraper and CSV"
git push

git add .
git commit -m "add country and region columns to climbs scraper"
git push

git add .
git commit -m "add grand tour race results scraper with 307 results"
git push

git add .
git commit -m "add grand tour stages scraper with 312 stages"
git push
```

---

## 🚧 What's Next

- [ ] Load all three CSVs into Snowflake tables
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
- How to handle inconsistent table structures across pages using conditional logic
- How to fix character encoding issues with UTF-8
- How to clean data by removing blank rows and special characters with pandas
- How Git and GitHub work together for version control

---

## 👤 Author

**David Xue**
[GitHub](https://github.com/daviddxuee/road-cycling-project)