
import requests
import json
import csv
from pathlib import Path

# 1. World Bank country-list API
url = "https://api.worldbank.org/v2/country"

params = {
    "format": "json",
    "per_page": 300
}

# 2. Request country information
response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

# 3. Read the JSON response
result = response.json()
metadata = result[0]
countries = result[1] or []

print("Total entries received:", len(countries))

# 4. Create folders
raw_folder = Path("data/raw")
processed_folder = Path("data/processed")

raw_folder.mkdir(parents=True, exist_ok=True)
processed_folder.mkdir(parents=True, exist_ok=True)

# 5. Save the original response
with open(raw_folder / "countries_response.json", "w",
          encoding="utf-8") as file:
    json.dump(result, file, indent=2)

# 6. Keep country entries, excluding aggregates
country_rows = []

for country in countries:
    region = country.get("region", {})
    country_code = country.get("id", "")

    # Aggregates generally have region ID "NA"
    if region.get("id") == "NA":
        continue

    # Keep only entries with a three-character code
    if len(country_code) != 3:
        continue

    country_rows.append({
        "country_code": country_code,
        "country_name": country["name"],
        "region": region.get("value", ""),
        "latitude": country.get("latitude", ""),
        "longitude": country.get("longitude", "")
    })

# 7. Save the country catalogue
csv_path = processed_folder / "countries.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as file:
    columns = [
        "country_code",
        "country_name",
        "region",
        "latitude",
        "longitude"
    ]

    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(country_rows)

print("Country entries kept:", len(country_rows))
print("Country catalogue saved to:", csv_path)
print("First five countries:")

for country in country_rows[:5]:
    print(country)
