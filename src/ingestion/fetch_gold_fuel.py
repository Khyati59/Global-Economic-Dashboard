
import requests
import pandas as pd
from pathlib import Path
from io import BytesIO

URL = (
    "https://thedocs.worldbank.org/en/doc/"
    "18675f1d1639c7a34d463f59263ba0a2-0050012025/"
    "related/CMO-Historical-Data-Monthly.xlsx"
)

OUTPUT = Path("data/processed/gold_fuel_prices.csv")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

try:
    print("Downloading commodity data...")
    response = requests.get(URL, timeout=60)
    response.raise_for_status()

    excel = pd.ExcelFile(BytesIO(response.content))
    print("Sheets:", excel.sheet_names)

    df = pd.read_excel(
        excel,
        sheet_name="Monthly Prices",
        skiprows=4
    )

    df.columns = [str(c).strip() for c in df.columns]

    # Find the actual column names automatically
    date_col = df.columns[0]

    gold_col = next(
        (c for c in df.columns if "gold" in c.lower()),
        None
    )

    brent_col = next(
        (c for c in df.columns
         if "crude oil, brent" in c.lower()),
        None
    )

    if gold_col is None or brent_col is None:
        print("Columns found:", list(df.columns))
        raise ValueError("Gold or Brent column not found.")

    result = df[[date_col, gold_col, brent_col]].copy()
    result.columns = [
        "date",
        "gold_usd_per_troy_ounce",
        "brent_crude_usd_per_barrel"
    ]

    result["date"] = result["date"].astype(str).str.strip()
    result = result[
        result["date"].str.match(r"^\d{4}M\d{2}$", na=False)
    ].copy()

    result = result[
        result["date"].str[:4].astype(int).between(2020, 2026)
    ]

    result.to_csv(OUTPUT, index=False)

    print(f"\nSUCCESS! Saved {len(result)} monthly records.")
    print(result.tail())
    print("Saved to:", OUTPUT)

except Exception as e:
    print("Error:", e)
