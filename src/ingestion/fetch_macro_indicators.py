
import requests
import csv
from pathlib import Path

BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/"

INDICATORS = {
    "gdp_growth_pct": "NY.GDP.MKTP.KD.ZG",
    "inflation_pct": "FP.CPI.TOTL.ZG",
    "unemployment_pct": "SL.UEM.TOTL.ZS"
}

# Load country catalogue
with open("data/processed/countries.csv", encoding="utf-8") as file:
    country_codes = {
        row["country_code"]
        for row in csv.DictReader(file)
    }

data = {}

for column, indicator_code in INDICATORS.items():
    print("Fetching:", column)

    url = BASE_URL + indicator_code
    params = {
        "format": "json",
        "date": "2020:2026",
        "per_page": 20000,
        "page": 1
    }

    while True:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        result = response.json()
        print("API pagination:", result[0])

        if not result or result[1] is None:
            break

        metadata, records = result

        for item in records:
            code = item.get("countryiso3code", "")

            if code not in country_codes:
                continue

            key = (code, item["date"])

            if key not in data:
                data[key] = {
                    "country": item["country"]["value"],
                    "country_code": code,
                    "year": item["date"]
                }

            data[key][column] = item["value"]

        if params["page"] >= metadata["pages"]:
            break

        params["page"] += 1

# Save combined data
output = Path("data/processed/macro_indicators.csv")
output.parent.mkdir(parents=True, exist_ok=True)

columns = [
    "country", "country_code", "year",
    "gdp_growth_pct", "inflation_pct", "unemployment_pct"
]

with open(output, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(sorted(
        data.values(),
        key=lambda row: (row["country"], row["year"])
    ))

print("Records saved:", len(data))
print("File:", output)
