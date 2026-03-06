import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_climb_links(page_url):
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    climbs = soup.find_all("a", class_="ranking-item-title")
    links = []
    for climb in climbs:
        links.append({
            "name": climb.text.strip(),
            "url": "https://climbfinder.com/" + climb["href"]
        })
    return links

def get_climb_stats(climb_url):
    response = requests.get(climb_url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    
    stats = {}
    # Find the statistics table specifically
    table = soup.find("table", class_="table-transparant")
    if table:
        rows = table.find_all("tr")
        for row in rows:
            label = row.find("th")
            value = row.find("td", class_="text-end")
            if label and value:
                key = label.text.strip()
                val = value.text.strip()
                stats[key] = val
    return stats

# Step 1 — get all climb links from page 1
print("Fetching climb links...")
climb_links = get_climb_links("https://climbfinder.com/en/ranking?s=popular&p=1")
print(f"Found {len(climb_links)} climbs")

# Step 2 — visit each climb page and get stats
all_climbs = []
for climb in climb_links:
    print(f"Scraping: {climb['name']}")
    stats = get_climb_stats(climb["url"])
    stats["name"] = climb["name"]
    stats["url"] = climb["url"]
    all_climbs.append(stats)
    time.sleep(1)  # be polite, wait 1 second between requests

# Step 3 — save to CSV
df = pd.DataFrame(all_climbs)
df.to_csv("climbs.csv", index=False)
print("Done! Saved to climbs.csv")
