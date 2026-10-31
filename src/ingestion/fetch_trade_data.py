
import requests
import pandas as pd
from pathlib import Path
import time

URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS"
OUTPUT = Path("data/processed/commodity_trade.csv")

COUNTRIES = {
    "India": "IND",
    "Saudi Arabia": "SAU",
    "Germany": "DEU",
    "Norway": "NOR",
    "Switzerland": "CHE"
}

REPORTER_CODES = {
    "IND": 356,
    "SAU": 682,
    "DEU": 276,
    "NOR": 579,
    "CHE": 756
}

COMMODITIES = {
    "crude_oil": "2709",
    "gold": "7108"
}

YEAR = 2023
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

# Preserve records from the previous run
if OUTPUT.exists():
    old = pd.read_csv(OUTPUT)
else:
    old = pd.DataFrame(columns=[
        "country", "country_code", "year",
        "commodity", "flow", "trade_value_usd"
    ])

records = old.to_dict("records")
session = requests.Session()

for country, country_code in COUNTRIES.items():
    for commodity, hs_code in COMMODITIES.items():

        # Skip a country/commodity already collected completely
        existing_flows = {
            r["flow"] for r in records
            if r["country_code"] == country_code
            and r["commodity"] == commodity
            and int(r["year"]) == YEAR
        }

        if {"imports", "exports"}.issubset(existing_flows):
            continue

        params = {
            "reporterCode": REPORTER_CODES[country_code],
            "period": YEAR,
            "cmdCode": hs_code,
            "partnerCode": 0
        }

        print(f"Fetching {country}: {commodity}...")

        for attempt in range(3):
            try:
                response = session.get(
                    URL, params=params, timeout=40
                )

                if response.status_code == 429:
                    wait = 30 * (attempt + 1)
                    print(f"Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                    continue

                response.raise_for_status()
                result = response.json()

                for item in result.get("data", []):
                    flow_code = str(item.get("flowCode", ""))
                    flow_desc = str(item.get("flowDesc", "")).lower()

                    if flow_code == "M" or "import" in flow_desc:
                        flow = "imports"
                    elif flow_code == "X" or "export" in flow_desc:
                        flow = "exports"
                    else:
                        continue

                    value = item.get("primaryValue")
                    if value is None:
                        value = item.get("tradeValue")

                    if value is None:
                        continue

                    records = [
                        r for r in records
                        if not (
                            r["country_code"] == country_code
                            and r["commodity"] == commodity
                            and int(r["year"]) == YEAR
                            and r["flow"] == flow
                        )
                    ]

                    records.append({
                        "country": country,
                        "country_code": country_code,
                        "year": YEAR,
                        "commodity": commodity,
                        "flow": flow,
                        "trade_value_usd": value
                    })

                # Save after each successful query
                pd.DataFrame(records).drop_duplicates(
                    subset=[
                        "country_code", "year",
                        "commodity", "flow"
                    ],
                    keep="last"
                ).to_csv(OUTPUT, index=False)

                print("Query completed.")
                break

            except Exception as e:
                print("Attempt failed:", e)
                if attempt < 2:
                    time.sleep(10 * (attempt + 1))

        time.sleep(8)

print("\nCurrent trade data saved to:", OUTPUT)
print(pd.read_csv(OUTPUT).to_string(index=False))
