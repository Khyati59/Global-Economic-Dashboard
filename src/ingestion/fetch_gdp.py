
import requests
import json
import csv
from pathlib import Path

# 1. API URL
url = "https://api.worldbank.org/v2/country/IND/indicator/NY.GDP.MKTP.CN"

# 2. Request settings
params = {
    "format": "json",
    "date": "2020:2026",
    "per_page": 1000
}

# 3. Send the API request
response = requests.get(url, params=params, timeout=30)
response.raise_for_status()

# 4. Convert the JSON response into Python data
result = response.json()
metadata = result[0]
records = result[1] or []

print("API request successful!")
print("Records received:", len(records))

# 5. Create output folders if needed
raw_folder = Path("data/raw")
processed_folder = Path("data/processed")

raw_folder.mkdir(parents=True, exist_ok=True)
processed_folder.mkdir(parents=True, exist_ok=True)

# 6. Save the original response
with open(raw_folder / "gdp_response.json", "w",
          encoding="utf-8") as file:
    json.dump(result, file, indent=2)

# 7. Extract useful fields
rows = []

for item in records:
    rows.append({
    "country": item["country"]["value"],
    "country_code": item["countryiso3code"],
    "year": item["date"],
    "gdp_inr": item["value"]
})

# 8. Save the extracted data as CSV
csv_path = processed_folder / "gdp_data.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as file:
    columns = ["country", "country_code", "year", "gdp_inr"]
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print("Total records reported by API:", metadata["total"])
print("CSV saved to:", csv_path)
print("First five records:")

for row in rows[:5]:
    print(row)
