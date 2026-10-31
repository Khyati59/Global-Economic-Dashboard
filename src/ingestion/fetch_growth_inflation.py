
import requests
import pandas as pd
from pathlib import Path
import time

BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/{}"

INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": "gdp_growth",
    "FP.CPI.TOTL.ZG": "inflation"
}

OUTPUT = Path("data/processed/growth_inflation.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

all_data = []

for code, name in INDICATORS.items():
    print(f"Fetching {name}...")

    try:
        url = BASE_URL.format(code)
        response = requests.get(
            url,
            params={
                "format": "json",
                "date": "2020:2024",
                "per_page": 20000
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()

        if not isinstance(result, list) or len(result) < 2:
            print(f"No data returned for {name}")
            continue

        for item in result[1] or []:
            if item["value"] is not None:
                all_data.append({
                    "country": item["country"]["value"],
                    "country_code": item["countryiso3code"],
                    "year": int(item["date"]),
                    "indicator": name,
                    "value": item["value"]
                })

        print(f"Collected {sum(r['indicator'] == name for r in all_data)} records.")

    except Exception as e:
        print(f"Failed to fetch {name}: {e}")

    time.sleep(2)

if all_data:
    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT, index=False)
    print(f"\nSaved {len(df)} records to {OUTPUT}")
else:
    print("\nNo data fetched. Existing files were not changed.")
