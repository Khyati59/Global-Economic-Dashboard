import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR / "data" / "raw" / "gold"
    / "World_official_gold_holdings_as_of_Oct2026_IFS.xlsx"
)

OUTPUT_FILE = (
    BASE_DIR / "data" / "processed"
    / "gold_reserves.csv"
)


def process_gold_reserves():
    df = pd.read_excel(INPUT_FILE, sheet_name="PDF", header=None)

    records = []

    # First table: ranks 1–50
    for _, row in df.iloc[6:56].iterrows():
        records.append({
            "rank": row[0],
            "country": row[1],
            "gold_reserves_tonnes": row[2],
            "gold_reserves_pct": row[3],
            "holdings_as_of": row[4]
        })

    # Second table: ranks 51–100
    for _, row in df.iloc[6:56].iterrows():
        records.append({
            "rank": row[5],
            "country": row[6],
            "gold_reserves_tonnes": row[7],
            "gold_reserves_pct": row[8],
            "holdings_as_of": row[9]
        })

    result = pd.DataFrame(records)

    # Remove non-country organisations and regional groups
    excluded = [
        "IMF", "ECB", "BIS", "WAEMU", "BEAC"
    ]

    result = result[
        result["country"].notna()
        & ~result["country"].astype(str).str.contains(
            "|".join(excluded), case=False, regex=True
        )
    ].copy()

    result["gold_reserves_tonnes"] = pd.to_numeric(
        result["gold_reserves_tonnes"], errors="coerce"
    )

    result["gold_reserves_pct"] = pd.to_numeric(
        result["gold_reserves_pct"], errors="coerce"
    )

    result["holdings_as_of"] = pd.to_datetime(
        result["holdings_as_of"], errors="coerce"
    )

    result = result.dropna(
        subset=["country", "gold_reserves_tonnes"]
    )

    result["rank"] = pd.to_numeric(
        result["rank"], errors="coerce"
    )

    result = result.sort_values("rank")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUTPUT_FILE, index=False)

    print("Gold reserves processing completed!")
    print("Records:", len(result))
    print("\nTop 10 countries:")
    print(result[[
        "country", "gold_reserves_tonnes", "holdings_as_of"
    ]].head(10).to_string(index=False))

    print("\nIndia record:")
    print(result[result["country"].str.contains(
        "India", case=False
    )].to_string(index=False))

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    process_gold_reserves()