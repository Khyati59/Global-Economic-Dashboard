
import pandas as pd
from pathlib import Path

files = [
    "macro_indicators.csv",
    "gdp_inr_all_countries.csv",
    "exchange_rates.csv",
    "economic_analysis.csv",
    "gold_fuel_prices.csv",
    "unemployment.csv"
]

for filename in files:
    path = Path("data/processed") / filename
    df = pd.read_csv(path)

    print("\n------------------------------")
    print(filename)
    print("------------------------------")
    print("Rows:", len(df))

    if "country_code" in df.columns:
        print("Countries:", df["country_code"].nunique())

    if "year" in df.columns:
        print("Years:", sorted(df["year"].dropna().unique()))
    elif "date" in df.columns:
        print("Date range:", df["date"].min(), "to", df["date"].max())
