
import requests
import csv
import json
from pathlib import Path

url = "https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.CN"

params = {
    "format": "json",
    "date": "2020:2024",
    "per_page": 100
}

response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

result = response.json()
records = result[1] or []

Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)

with open("data/raw/gdp_inr_response.json", "w",
          encoding="utf-8") as file:
    json.dump(result, file, indent=2)

rows = []

for item in records:
    rows.append({
        "country": item["country"]["value"],
        "country_code": item["countryiso3code"],
        "year": item["date"],
        "gdp_inr": item["value"]
    })

with open("data/processed/gdp_inr.csv", "w",
          newline="", encoding="utf-8") as file:
    columns = ["country", "country_code", "year", "gdp_inr"]
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print("GDP records:", len(rows))
print("Saved to data/processed/gdp_inr.csv")

for row in rows:
    print(row)
