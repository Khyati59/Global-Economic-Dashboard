
import requests
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed" / "exchange_rates.csv"
)

URL = (
    "https://api.worldbank.org/v2/country/all/"
    "indicator/PA.NUS.FCRF"
)

params = {
    "format": "json",
    "date": "2020:2026",
    "per_page": 20000
}


def fetch_exchange_rates():

    print("Fetching global exchange rates...")

    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()

    result = response.json()

    if len(result) < 2 or result[1] is None:
        print("No data received.")
        return

    records = []

    for item in result[1]:

        if item["value"] is None:
            continue

        code = item["countryiso3code"]

        if not code:
            continue

        records.append({
            "country": item["country"]["value"],
            "country_code": code,
            "year": int(item["date"]),
            "exchange_rate_lcu_per_usd": item["value"]
        })

    df = pd.DataFrame(records)

    df = df.sort_values(["country_code", "year"])

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nExchange rates fetched successfully!")
    print("Records:", len(df))
    print("Countries:", df["country_code"].nunique())
    print("Years:", sorted(df["year"].unique()))
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    fetch_exchange_rates()
