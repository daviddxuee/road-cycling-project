import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_race_winners(url, race_name):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    tables = soup.find_all("table", class_="wikitable")
    table = tables[1]
    rows = table.find("tbody").find_all("tr")

    results = []
    for row in rows:
        tds = row.find_all("td")
        winner_tag = row.find("th", scope="row")

        if not winner_tag or len(tds) < 4:
            continue

        year = tds[0].text.strip()
        country = tds[1].text.strip()
        winner = winner_tag.text.strip().replace("*", "").replace("†", "").replace("#", "").strip()
        team = tds[2].text.strip()
        distance = tds[3].text.strip()

        results.append({
            "race": race_name,
            "year": year,
            "winner": winner,
            "country": country,
            "team": team,
            "distance": distance
        })
    return results

# Scrape all three Grand Tours
all_results = []

races = [
    ("https://en.wikipedia.org/wiki/List_of_Tour_de_France_general_classification_winners", "Tour de France"),
    ("https://en.wikipedia.org/wiki/List_of_Giro_d%27Italia_general_classification_winners", "Giro d'Italia"),
    ("https://en.wikipedia.org/wiki/List_of_Vuelta_a_Espa%C3%B1a_general_classification_winners", "Vuelta a España")
]

for url, race_name in races:
    print(f"Scraping {race_name}...")
    results = scrape_race_winners(url, race_name)
    all_results.extend(results)
    print(f"Found {len(results)} results")
    time.sleep(1)

# Save to CSV
df = pd.DataFrame(all_results)
df.to_csv("races.csv", index=False)
print(f"Done! Saved {len(df)} results to races.csv")
