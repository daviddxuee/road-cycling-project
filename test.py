import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import time

scraper = cloudscraper.create_scraper()

def scrape_race_climbs(url, race_name):
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, "lxml")
    
    table = soup.find("table", class_="basic")
    if not table:
        print(f"No table found for {race_name}")
        return []
    
    rows = table.find("tbody").find_all("tr")
    results = []
    
    for row in rows:
        tds = row.find_all("td")
        climb_link = row.find("a")
        
        if not climb_link or len(tds) < 5:
            continue
        
        results.append({
            "race": race_name,
            "position": tds[0].text.strip(),
            "climb_name": climb_link.text.strip(),
            "num_stages": tds[2].text.strip(),
            "num_editions": tds[3].text.strip(),
            "first_year": tds[4].text.strip()
        })
    
    return results

# Scrape all three Grand Tours
all_results = []

races = [
    ("https://www.procyclingstats.com/race/tour-de-france/route/climbs", "Tour de France"),
    ("https://www.procyclingstats.com/race/giro-d-italia/route/climbs", "Giro d'Italia"),
    ("https://www.procyclingstats.com/race/vuelta-a-espana/route/climbs", "Vuelta a España")
]

for url, race_name in races:
    print(f"Scraping {race_name}...")
    results = scrape_race_climbs(url, race_name)
    all_results.extend(results)
    print(f"Found {len(results)} climbs")
    time.sleep(2)

# Save to CSV
df = pd.DataFrame(all_results)
df.to_csv("race_climbs.csv", index=False)
print(f"\nDone! Saved {len(df)} rows to race_climbs.csv")
