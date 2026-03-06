import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_stages(url, race_name, year):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    stages_table = soup.find("table", class_="wikitable")

    if not stages_table:
        print(f"  No stages table found for {race_name} {year}")
        return []

    # Check header to see if elevation gain column exists
    header_row = stages_table.find("tr")
    header_text = header_row.text.lower() if header_row else ""
    has_elevation = "elevation" in header_text

    rows = stages_table.find("tbody").find_all("tr")
    results = []

    for row in rows:
        stage_tag = row.find("th", scope="row")
        tds = row.find_all("td")

        if not stage_tag or len(tds) < 5:
            continue

        stage = stage_tag.text.strip()
        date = tds[0].text.strip()
        route = tds[1].text.strip()
        distance = tds[2].text.strip()

        if has_elevation:
            # Extra elevation column shifts everything by 1
            stage_type = tds[5].text.strip() if len(tds) > 5 else ""
            winner = tds[6].text.strip() if len(tds) > 6 else ""
        else:
            stage_type = tds[4].text.strip() if len(tds) > 4 else ""
            winner = tds[5].text.strip() if len(tds) > 5 else ""

        results.append({
            "race": race_name,
            "year": year,
            "stage": stage,
            "date": date,
            "route": route,
            "distance": distance,
            "stage_type": stage_type,
            "stage_winner": winner
        })

    return results


# Scrape last 5 years of each Grand Tour
all_stages = []

races = [
    ("Tour_de_France", "Tour de France"),
    ("Giro_d%27Italia", "Giro d'Italia"),
    ("Vuelta_a_Espa%C3%B1a", "Vuelta a España")
]

years = [2020, 2021, 2022, 2023, 2024]

for race_slug, race_name in races:
    for year in years:
        url = f"https://en.wikipedia.org/wiki/{year}_{race_slug}"
        print(f"Scraping {race_name} {year}...")
        stages = scrape_stages(url, race_name, year)
        all_stages.extend(stages)
        print(f"  Found {len(stages)} stages")
        time.sleep(1)

# Save to CSV
df = pd.DataFrame(all_stages)
df.to_csv("stages.csv", index=False, encoding='utf-8-sig')
print(f"\nDone! Saved {len(df)} stages to stages.csv")
