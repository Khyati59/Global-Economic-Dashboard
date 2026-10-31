
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

GDP_FILE = (
    BASE_DIR / "data" / "raw" / "world_bank"
    / "gdp_usd_all_countries.csv"
)

FX_FILE = (
    BASE_DIR / "data" / "processed"
    / "exchange_rates.csv"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "gdp_inr_all_countries.csv"
)


def convert_gdp_to_inr():

    print("Loading global GDP and exchange rate data...")

    # Read GDP in USD
    gdp = pd.read_csv(GDP_FILE)

    # Read exchange rates
    fx = pd.read_csv(FX_FILE)

    # Keep India's exchange rate only
    fx = fx[fx["country_code"] == "IND"]

    # Select required columns
    fx = fx[["year", "exchange_rate_lcu_per_usd"]]

    # Match GDP and exchange rates by year
    df = pd.merge(
        gdp,
        fx,
        on="year",
        how="inner"
    )

    # Rename exchange rate column
    df = df.rename(columns={
        "exchange_rate_lcu_per_usd": "inr_per_usd"
    })

    # Convert GDP from USD to INR
    df["gdp_inr"] = df["gdp_usd"] * df["inr_per_usd"]

    df["gdp_inr"] = df["gdp_inr"].round(2)

    # Sort records
    df = df.sort_values(["country_code", "year"])

    # Save output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nGDP conversion completed!")
    print("Records:", len(df))
    print("Countries:", df["country_code"].nunique())
    print("Years:", sorted(df["year"].unique()))
    print("Missing values:\n", df.isnull().sum())
    print("Output:", OUTPUT_FILE)


if __name__ == "__main__":
    convert_gdp_to_inr()
