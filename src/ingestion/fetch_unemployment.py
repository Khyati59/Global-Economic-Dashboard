
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "processed" / "macro_indicators.csv"
OUTPUT_FILE = BASE_DIR / "data" / "processed" / "unemployment.csv"


def build_unemployment_data():

    print("Preparing global unemployment data...")

    df = pd.read_csv(INPUT_FILE)

    unemployment = df[
        ["country", "country_code", "year", "unemployment_pct"]
    ].copy()

    unemployment = unemployment.dropna(
        subset=["unemployment_pct"]
    )

    unemployment["year"] = unemployment["year"].astype(int)

    unemployment = unemployment.sort_values(
        ["country_code", "year"]
    )

    unemployment.to_csv(OUTPUT_FILE, index=False)

    print("Records saved:", len(unemployment))
    print("Countries:", unemployment["country_code"].nunique())
    print("Years:", sorted(unemployment["year"].unique()))
    print("File:", OUTPUT_FILE)


if __name__ == "__main__":
    build_unemployment_data()
