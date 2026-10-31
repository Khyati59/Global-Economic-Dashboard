
import requests
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "data" / "raw" / "world_bank"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "gdp_per_capita_usd.csv"

URL = (
    "https://api.worldbank.org/v2/country/all/"
    "indicator/NY.GDP.PCAP.CD"
)

params = {
    "format": "json",
    "date": "2020:2026",
    "per_page": 20000
}


def fetch_gdp_per_capita():

    print("Fetching GDP per capita data...")

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

        records.append({
            "country": item["country"]["value"],
            "country_code": item["countryiso3code"],
            "year": int(item["date"]),
            "gdp_per_capita_usd": item["value"]
        })

    df = pd.DataFrame(records)

# Keep only individual countries with valid country codes
    df = df.dropna(subset=["country_code"])

# Remove empty country codes, if any
    df = df[df["country_code"].str.strip() != ""]

    df = df.sort_values(
    ["country_code", "year"]
)

    df.to_csv(OUTPUT_FILE, index=False)

    print("Records saved:", len(df))
    print("Years:", sorted(df["year"].unique()))
    print("Countries:", df["country_code"].nunique())
    print("File:", OUTPUT_FILE)


if __name__ == "__main__":
    fetch_gdp_per_capita()
