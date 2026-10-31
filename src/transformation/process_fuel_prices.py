import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

EXCEL_FILE = (
    BASE_DIR / "data" / "raw" / "fuel"
    / "Global_Fuel_Prices_Database.xlsx"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "fuel_prices.csv"
)


def extract_fuel_data(sheet_name, fuel_type):
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)

    # Keep the dataset's default country/price series
    if "Default MAP (1 to show)" in df.columns:
        df = df[df["Default MAP (1 to show)"] == 1].copy()

    # Identify monthly date columns
    date_columns = [
        col for col in df.columns
        if isinstance(col, pd.Timestamp)
        or isinstance(col, __import__("datetime").datetime)
    ]

    # Keep only 2020 onwards
    date_columns = [
        col for col in date_columns
        if col.year >= 2020
    ]

    # Convert monthly columns into individual rows
    result = df.melt(
        id_vars=["Country", "Country Code"],
        value_vars=date_columns,
        var_name="date",
        value_name="price_usd_per_litre"
    )

    result["date"] = pd.to_datetime(result["date"])
    result["price_usd_per_litre"] = pd.to_numeric(
        result["price_usd_per_litre"],
        errors="coerce"
    )

    result["fuel_type"] = fuel_type

    return result.dropna(subset=["price_usd_per_litre"])


def process_fuel_prices():
    print("Reading global fuel price data...")

    petrol = extract_fuel_data(
        "Reg Gasoline (below RON 95) USD",
        "Petrol"
    )

    diesel = extract_fuel_data(
        "Diesel USD",
        "Diesel"
    )

    fuel = pd.concat([petrol, diesel], ignore_index=True)

    print("Loading India's monthly exchange rates...")

    fx = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Monthly ER - LC to USD"
    )

    india_fx = fx[fx["Code"] == "IND"].copy()

    date_columns = [
        col for col in fx.columns
        if isinstance(col, pd.Timestamp)
        or isinstance(col, __import__("datetime").datetime)
    ]

    india_fx = india_fx.melt(
        id_vars=["Country", "Code"],
        value_vars=date_columns,
        var_name="date",
        value_name="inr_per_usd"
    )

    india_fx["date"] = pd.to_datetime(india_fx["date"])
    india_fx["inr_per_usd"] = pd.to_numeric(
        india_fx["inr_per_usd"],
        errors="coerce"
    )

    # Match each fuel month with India's exchange rate
    fuel = fuel.merge(
        india_fx[["date", "inr_per_usd"]],
        on="date",
        how="left"
    )

    fuel["price_inr_per_litre"] = (
        fuel["price_usd_per_litre"] * fuel["inr_per_usd"]
    )

    fuel = fuel.dropna(
        subset=["price_inr_per_litre"]
    )

    fuel = fuel.sort_values(
        ["Country", "date", "fuel_type"]
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fuel.to_csv(OUTPUT_FILE, index=False)

    print("\nFuel data processing completed!")
    print("Total records:", len(fuel))
    print("Countries:", fuel["Country Code"].nunique())
    print("Fuel types:", fuel["fuel_type"].unique())
    print("Date range:", fuel["date"].min(), "to", fuel["date"].max())
    print("\nMissing values:")
    print(fuel.isnull().sum())
    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    process_fuel_prices()