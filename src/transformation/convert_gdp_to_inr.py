
import pandas as pd
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Input files
GDP_FILE = (
    BASE_DIR / "data" / "raw" / "world_bank"
    / "gdp_usd_all_countries.csv"
)

FX_FILE = (
    BASE_DIR / "data" / "processed"
    / "exchange_rates.csv"
)

# Output file
OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "gdp_inr_all_countries.csv"
)


def convert_gdp_to_inr():

    print("Loading global GDP and exchange rate data...")

    # 1. Read GDP in USD
    gdp = pd.read_csv(GDP_FILE)

    # 2. Read exchange rates
    fx = pd.read_csv(FX_FILE)

    # 3. Select India's exchange rates
    fx = fx[fx["country_code"] == "IND"]

    fx = fx[
        ["year", "exchange_rate_lcu_per_usd"]
    ]

    # 4. Ensure year columns have the same data type
    gdp["year"] = gdp["year"].astype(int)
    fx["year"] = fx["year"].astype(int)

    # 5. Merge GDP and exchange rates using year
    df = pd.merge(
        gdp,
        fx,
        on="year",
        how="inner"
    )

    # 6. Rename exchange rate column
    df = df.rename(columns={
        "exchange_rate_lcu_per_usd": "inr_per_usd"
    })

    # 7. Convert GDP from USD to INR
    df["gdp_inr"] = (
        df["gdp_usd"] * df["inr_per_usd"]
    ).round(2)

    # 8. Sort records
    df = df.sort_values(
        ["country_code", "year"]
    )

    # 9. Save processed dataset
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(OUTPUT_FILE, index=False)

    # 10. Display results
    print("\nGDP conversion completed!")
    print("Records:", len(df))
    print("Countries:", df["country_code"].nunique())
    print("Years:", sorted(df["year"].unique()))

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nOutput:", OUTPUT_FILE)


if __name__ == "__main__":
    convert_gdp_to_inr()
