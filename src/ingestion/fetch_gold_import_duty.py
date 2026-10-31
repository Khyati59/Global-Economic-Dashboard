
import requests
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "gold_import_duty.csv"
)

COUNTRIES = {
    "IND": ("India", "356"),
    "CHN": ("China", "156"),
    "USA": ("United States", "840"),
    "GBR": ("United Kingdom", "826"),
    "ARE": ("United Arab Emirates", "784"),
    "CHE": ("Switzerland", "756"),
    "AUS": ("Australia", "036"),
    "JPN": ("Japan", "392"),
    "SGP": ("Singapore", "702"),
    "ZAF": ("South Africa", "710"),
}

PRODUCT_CODE = "710812"

URL = (
    "https://wits.worldbank.org/API/V1/SDMX/V21/"
    "datasource/TRN/reporter/{}/partner/000/"
    "product/" + PRODUCT_CODE +
    "/year/all/datatype/reported?format=JSON"
)


def fetch_country_tariff(country_code, country_name, reporter):
    url = URL.format(reporter)

    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=60
        )
        response.raise_for_status()

        data = response.json()

        structure = data.get("structure", {})
        time_values = (
            structure.get("dimensions", {})
            .get("observation", [{}])[0]
            .get("values", [])
        )

        series = (
            data.get("dataSets", [{}])[0]
            .get("series", {})
        )

        if not series:
            print("No tariff records:", country_name)
            return []

        observations = next(iter(series.values())).get(
            "observations", {}
        )

        records = []

        for index, year_info in enumerate(time_values):
            observation = observations.get(str(index))

            if not observation:
                continue

            rate = observation[0]
            year = year_info.get("id")

            if rate is None:
                continue

            records.append({
                "country": country_name,
                "country_code": country_code,
                "product_code": PRODUCT_CODE,
                "product_description": "Other unwrought non-monetary gold",
                "year": int(year),
                "gold_import_duty_pct": float(rate),
                "source": "World Bank WITS / UNCTAD TRAINS",
                "tariff_data_type": "Reported"
            })

        if records:
            latest = max(records, key=lambda x: x["year"])
            print(
                country_name,
                "Latest:", latest["year"],
                "Rate:", latest["gold_import_duty_pct"], "%"
            )

        return records

    except Exception as error:
        print("Skipped", country_name, ":", error)
        return []


def main():
    all_records = []

    for code, (name, reporter) in COUNTRIES.items():
        print("\nFetching:", name)

        records = fetch_country_tariff(
            code, name, reporter
        )

        all_records.extend(records)

    df = pd.DataFrame(all_records)

    if df.empty:
        print("\nNo tariff data retrieved.")
        return

    # Keep only the latest reported year per country
    df = (
        df.sort_values("year")
        .groupby("country_code", as_index=False)
        .tail(1)
        .sort_values("country")
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True, exist_ok=True
    )

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nGold import duty extraction completed!")
    print("Countries with data:", df["country_code"].nunique())
    print("\nFinal dataset:")
    print(df[[
        "country", "year", "gold_import_duty_pct"
    ]].to_string(index=False))

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
