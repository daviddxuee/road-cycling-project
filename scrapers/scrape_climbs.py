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
    table = soup.find("table", class_="table-transparant")
    if table:
        rows = table.find_all("tr")
        for row in rows:
            label = row.find("th")
            value = row.find("td", class_="text-end")
            if label and value:
                stats[label.text.strip()] = value.text.strip()
    return stats

# Step 1 — scrape links from pages 1 through 12
all_climb_links = []
for page_num in range(1, 13):
    print(f"Fetching page {page_num} of 12...")
    page_url = f"https://climbfinder.com/en/ranking?s=popular&p={page_num}"
    links = get_climb_links(page_url)
    all_climb_links.extend(links)
    time.sleep(1)

print(f"Found {len(all_climb_links)} climbs total")

# Step 2 — visit each climb page and get stats
all_climbs = []
for i, climb in enumerate(all_climb_links):
    print(f"Scraping {i+1}/{len(all_climb_links)}: {climb['name']}")
    stats = get_climb_stats(climb["url"])
    stats["name"] = climb["name"]
    stats["url"] = climb["url"]
    all_climbs.append(stats)
    time.sleep(1)

# Step 3 — save to CSV
df = pd.DataFrame(all_climbs)
df.to_csv("climbs.csv", index=False)
print(f"Done! Saved {len(df)} climbs to climbs.csv")
