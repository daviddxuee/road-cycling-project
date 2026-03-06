# 🚴 Road Cycling Data Pipeline

A personal end-to-end data engineering project built from scratch — scraping real cycling data from the web, storing it in Snowflake, and transforming it with dbt.

> Built as a learning project to develop skills in Python, web scraping, Snowflake, dbt, and Git.

---

## 🗂️ Project Overview

This project scrapes data on the world's most famous cycling climbs from [ClimbFinder](https://climbfinder.com), loads the raw data into Snowflake, and uses dbt to transform it into clean, analytical models.

**Questions this project aims to answer:**
- Which climbs are the hardest in the world?
- How do climbs compare across countries?
- Which climbs appear most in famous races like the Tour de France and Giro d'Italia?
- What makes a climb "legendary" — length, gradient, or elevation?

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
│   └── scrape_races.py         # Scrapes pro race results (coming soon)
├── loaders/
│   └── load_to_snowflake.py    # Loads CSV data into Snowflake
├── dbt_project/
│   ├── models/
│   │   ├── staging/            # Clean raw data
│   │   └── marts/              # Analytical models
└── README.md
```

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
git config --global user.name "daviddxuee"
git config --global user.email "davidxue0908@gmail.com"
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
Installed the libraries needed for scraping and data handling:
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

### Step 4 — Build the Web Scraper

Used the browser's **Inspect** tool to identify the HTML elements containing climb data on ClimbFinder's ranking page.

**Phase 1** — Fetch the ranking page and extract climb names + URLs:
```python
import requests
from bs4 import BeautifulSoup

url = "https://climbfinder.com/en/ranking?s=popular&p=1"
headers = {"User-Agent": "Mozilla/5.0 ..."}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "lxml")

climbs = soup.find_all("a", class_="ranking-item-title")
for climb in climbs:
    name = climb.text.strip()
    link = "https://climbfinder.com/" + climb["href"]
    print(name, "→", link)
```

**Phase 2** — Visit each climb's individual page and extract detailed stats:
```python
def get_climb_stats(climb_url):
    response = requests.get(climb_url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    
    stats = {}

    # Get stats table
    table = soup.find("table", class_="table-transparant")
    if table:
        rows = table.find_all("tr")
        for row in rows:
            label = row.find("th")
            value = row.find("td", class_="text-end")
            if label and value:
                stats[label.text.strip()] = value.text.strip()

    # Get country and region from breadcrumb
    # Structure: Home > World > Europe > Country > ... > Region > Climb Name
    breadcrumb = soup.find("ol", class_="breadcrumb")
    if breadcrumb:
        items = breadcrumb.find_all("li", class_="breadcrumb-item")
        if len(items) >= 4:
            stats["Country"] = items[3].text.strip()
        if len(items) >= 2:
            stats["Region"] = items[-2].text.strip()

    return stats
```

**Phase 3** — Loop through 12 pages to collect 300 climbs:
```python
all_climb_links = []
for page_num in range(1, 13):
    print(f"Fetching page {page_num} of 12...")
    page_url = f"https://climbfinder.com/en/ranking?s=popular&p={page_num}"
    links = get_climb_links(page_url)
    all_climb_links.extend(links)
    time.sleep(1)  # be polite, wait 1 second between requests
```

**Key learning:** Added a 1 second delay between requests (`time.sleep(1)`) to be respectful to the website's server and avoid getting blocked.

---

### Step 5 — Clean and Save Data to CSV

After scraping, 12 out of 312 rows were blank (climb pages with no stats table). These were removed using pandas:

```python
df = pd.read_csv('climbs.csv')
df_clean = df.dropna(subset=['Length', 'Country', 'Region'])
df_clean.to_csv('climbs.csv', index=False)
print(f'Removed blank rows. Climbs remaining: {len(df_clean)}')
```

Final result: **300 clean climbs** saved to `climbs.csv`.

**Sample output:**

| Name | Difficulty Points | Length | Avg Gradient | Steepest 100m | Total Ascent | Region | Country |
|---|---|---|---|---|---|---|---|
| Mont Ventoux | 1352 | 20.8 km | 7.7% | 13.3% | 1594 m | Vaucluse | France |
| Alpe d'Huez | 975 | 14 km | 8% | 11.3% | 1122 m | Bourg d'Oisans | France |
| Passo dello Stelvio | 1465 | 24.9 km | 7.4% | 10.3% | 1846 m | Bolzano | Italy |
| Col du Galibier | 1556 | 34.8 km | 6% | 10.6% | 2085 m | Bourg d'Oisans | France |
| Eyserbosweg | 42 | 1.2 km | 6.8% | 10.1% | 82 m | South Limburg | Netherlands |

---

### Step 6 — Push to GitHub

Used Git to version control and publish the project:
```bash
git init
git remote add origin https://github.com/daviddxuee/road-cycling-project.git
git add .
git commit -m "add climbs scraper and CSV"
git push -u origin main
```

Subsequent updates were pushed with descriptive commit messages:
```bash
git add .
git commit -m "add country and region columns to climbs scraper"
git push

git add .
git commit -m "clean blank rows from climbs data"
git push
```

---

## 🚧 What's Next

- [ ] Load `climbs.csv` into a Snowflake table
- [ ] Scrape pro race results from ProCyclingStats
- [ ] Connect dbt to Snowflake and build staging models
- [ ] Build mart models to answer analytical questions
- [ ] Visualize results in a dashboard

---

## 💡 What I Learned

- How to inspect HTML with browser developer tools to find the right elements to scrape
- How to handle common scraping issues like 403 errors (blocked requests) and 404 errors (wrong URLs)
- How to loop through multiple pages to collect larger datasets
- How to extract data from breadcrumb navigation for location context (country and region)
- How to clean data by removing blank rows with pandas
- How Git and GitHub work together for version control
- The importance of going step by step and debugging errors one at a time

---

## 👤 Author

**David Xue**
[GitHub](https://github.com/daviddxuee/road-cycling-project)