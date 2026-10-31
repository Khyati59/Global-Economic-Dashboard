# Global Macro Economic Intelligence Platform

An interactive data engineering and analytics platform for exploring and comparing macroeconomic indicators across 10 major economies from 2020–2025.

## Overview

This project integrates economic and commodity datasets from multiple sources, processes them into structured formats, and presents insights through an interactive Streamlit dashboard.

It aims to simplify global economic comparison by transforming raw data into meaningful visual insights.

## Key Features

- **GDP Analysis:** Compare total GDP (in ₹ lakh crore) and annual GDP growth.
- **Inflation Analysis:** Explore inflation rates across countries.
- **Unemployment Analysis:** Compare unemployment trends over time.
- **Currency Analysis:** Track exchange rates and currency depreciation against the US Dollar.
- **Fuel Price Analysis:** Compare petrol and diesel prices.
- **Gold & Crude Oil Analysis:** Track global gold and Brent crude oil prices.
- **Gold Reserves & Import Duty:** Explore national gold holdings and reported import duties.

## Technology Stack

| Category | Tools |
|---|---|
| Programming | Python |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly |
| Dashboard | Streamlit |
| Data Storage | CSV |
| Development | VS Code |

## Data Sources

- World Bank – GDP, inflation, unemployment, exchange rates and commodity prices.
- WITS – Gold import duty data.
- Publicly available fuel price and gold reserve datasets.

## Project Structure

```text
macro-pipeline/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── database/
│   ├── ingestion/
│   └── transformation/
├── docs/
├── tests/
├── app.py
└── requirements.txt
```

## Getting Started

**1. Clone the repository**

```bash
git clone https://github.com/your-username/macro-pipeline.git
cd macro-pipeline
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the dashboard**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## Note on Data Availability

Data coverage varies by indicator, country, and year. Missing observations are kept unavailable rather than treated as zero. Some datasets, such as fuel prices and gold reserves, have different reporting periods.

## Future Scope

- Automated data pipeline scheduling.
- Integration of additional economic data sources.
- Economic risk and vulnerability analysis.
- Cloud deployment and improved reporting.

---

**Project Domain:** Data Engineering | Economic Analytics  
**Project Type:** Academic Microproject
