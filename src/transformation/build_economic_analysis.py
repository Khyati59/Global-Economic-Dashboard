
import pandas as pd
from pathlib import Path

DATA = Path("data/processed")

# Load the existing datasets
vulnerability = pd.read_csv(DATA / "commodity_vulnerability.csv")
inflation = pd.read_csv(DATA / "growth_inflation.csv")
trade = pd.read_csv(DATA / "commodity_trade.csv")

# Standardize country codes and years
for df in [vulnerability, inflation, trade]:
    df["country_code"] = df["country_code"].astype(str).str.upper()
    df["year"] = df["year"].astype(int)

# Keep inflation values only
inflation = inflation[inflation["indicator"] == "inflation"]

inflation = inflation[
    ["country_code", "year", "value"]
].rename(columns={"value": "inflation_pct"})

# Merge inflation into the main dataset
analysis = vulnerability.merge(
    inflation,
    on=["country_code", "year"],
    how="left"
)

# Calculate trade balance only when both imports and exports exist
trade_wide = trade.pivot_table(
    index=["country_code", "year", "commodity"],
    columns="flow",
    values="trade_value_usd",
    aggfunc="sum"
).reset_index()

for flow in ["imports", "exports"]:
    if flow not in trade_wide.columns:
        trade_wide[flow] = float("nan")

trade_wide["net_trade_balance_usd"] = (
    trade_wide["exports"] - trade_wide["imports"]
)

trade_wide["trade_status"] = trade_wide.apply(
    lambda row: (
        "Net exporter" if row["net_trade_balance_usd"] > 0
        else "Net importer" if row["net_trade_balance_usd"] < 0
        else "Balanced" if pd.notna(row["net_trade_balance_usd"])
        else "Insufficient data"
    ),
    axis=1
)

# Add commodity trade results to each country-year
for commodity in ["crude_oil", "gold"]:
    part = trade_wide[trade_wide["commodity"] == commodity][
        [
            "country_code", "year", "imports", "exports",
            "net_trade_balance_usd", "trade_status"
        ]
    ].rename(columns={
        "imports": f"{commodity}_imports_usd",
        "exports": f"{commodity}_exports_usd",
        "net_trade_balance_usd": f"{commodity}_net_balance_usd",
        "trade_status": f"{commodity}_trade_status"
    })

    analysis = analysis.merge(
        part, on=["country_code", "year"], how="left"
    )

# Keep missing trade values as unavailable, not zero
for commodity in ["crude_oil", "gold"]:
    analysis[f"{commodity}_trade_status"] = (
        analysis[f"{commodity}_trade_status"]
        .fillna("Insufficient data")
    )

# Save final dataset
output = DATA / "economic_analysis.csv"
analysis.to_csv(output, index=False)

print("Economic analysis dataset created!")
print("Rows:", len(analysis))
print("Columns:", len(analysis.columns))
print("Saved to:", output)
print(analysis.head(10).to_string(index=False))
