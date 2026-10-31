from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------------------------------
# Page setup
# ------------------------------------------------------------
st.set_page_config(
    page_title="Global Economic Comparison",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp { background:#F6F3EC; color:#26332F; }
    header[data-testid="stHeader"] { background:transparent; }
    .block-container { padding:3rem 3rem 3rem 3rem; max-width:1500px; }
    [data-testid="stVerticalBlock"] { gap:1.1rem; }

    /* banner */
    .banner { background:#1F4E4A; border-radius:16px; padding:26px 32px; }
    .banner h1 { color:#FFFFFF; font-size:2rem; font-weight:700; margin:0; line-height:1.25; }
    .banner p  { color:#CFE3DE; font-size:1rem; margin:6px 0 0 0; }

    /* section cards */
    [data-testid="stVerticalBlockBorderWrapper"] { background:#FFFFFF; border:1px solid #E4DED2 !important;
        border-radius:16px; box-shadow:0 2px 10px rgba(60,50,30,.06); padding:1.1rem 1.3rem; }
    h3 { font-size:1.3rem !important; font-weight:700; color:#26332F; margin:0 0 .4rem 0; padding:0; }

    /* KPI cards (no left border) */
    .kpi { background:#FFFFFF; border:1px solid #E4DED2; border-radius:14px; padding:18px 22px;
           box-shadow:0 2px 10px rgba(60,50,30,.06); min-height:128px; }
    .kpi .t { font-size:.85rem; color:#7A7468; text-transform:uppercase; letter-spacing:.06em; font-weight:600; }
    .kpi .c { display:flex; align-items:center; gap:12px; font-size:1.4rem; font-weight:700; margin-top:8px; color:#26332F; }
    .kpi .c img { width:38px; height:auto; border-radius:4px; box-shadow:0 0 0 1px #DDD6C8; }
    .kpi .v { font-size:1.05rem; color:#1F6F6B; font-weight:600; margin-top:6px; }

    .note { background:#FBF6E9; border:1px solid #EADFBF; border-radius:14px; padding:18px 22px;
            color:#4A4130; min-height:128px; font-size:.98rem; line-height:1.55; }
    .note b { color:#26332F; }

    /* ranking board */
    .rk { display:grid; grid-template-columns:30px 42px 150px 1fr 110px; align-items:center; gap:12px;
          height:50px; border-bottom:1px solid #F0EBE0; }
    .rk:last-child { border-bottom:none; }
    .rk .rn { color:#9A9385; font-weight:700; font-size:1rem; text-align:center; }
    .rk img { width:38px; height:auto; border-radius:4px; box-shadow:0 0 0 1px #DDD6C8; }
    .rk .rname { font-weight:600; font-size:1rem; color:#26332F; }
    .rk .rbar { background:#F0EBE0; border-radius:6px; height:14px; overflow:hidden; }
    .rk .rbar div { height:100%; border-radius:6px; }
    .rk .rval { font-weight:700; font-size:1rem; color:#26332F; text-align:right; white-space:nowrap; }

    /* legend chips */
    .chips { display:flex; flex-wrap:wrap; gap:10px; margin-bottom:6px; }
    .chip { display:flex; align-items:center; gap:8px; background:#FAF8F3; border:1px solid #E4DED2;
            border-radius:999px; padding:5px 14px 5px 10px; font-size:.92rem; font-weight:600; }
    .chip .dot { width:12px; height:12px; border-radius:50%; }
    .chip img { width:24px; height:auto; border-radius:3px; box-shadow:0 0 0 1px #DDD6C8; }

    div[data-baseweb="select"] > div { min-height:42px; background:#FFFFFF; border:1px solid #D8D1C2; }
    label[data-testid="stWidgetLabel"] p { font-size:.9rem; color:#26332F; font-weight:600; }
    </style>
    """,
    unsafe_allow_html=True,
)

DATA = Path("data/processed")
RAW = Path("data/raw/world_bank")
YEARS = [2020, 2021, 2022, 2023, 2024, 2025]

# code -> (ISO-2 code for the flag, country name)
COUNTRIES = {
    "IND": ("IN", "India"), "USA": ("US", "United States"),
    "CHN": ("CN", "China"), "JPN": ("JP", "Japan"),
    "DEU": ("DE", "Germany"), "GBR": ("GB", "United Kingdom"),
    "BRA": ("BR", "Brazil"), "IDN": ("ID", "Indonesia"),
    "SAU": ("SA", "Saudi Arabia"), "RUS": ("RU", "Russia"),
}
NAME_TO_CODE = {name: code for code, (_, name) in COUNTRIES.items()}


def cname(code):
    return COUNTRIES.get(str(code).upper(), ("", str(code)))[1]


def flag_url(code, w=80):
    iso2 = COUNTRIES.get(str(code).upper(), ("", ""))[0].lower()
    return f"https://flagcdn.com/w{w}/{iso2}.png" if iso2 else ""


def flag_img(code):
    url = flag_url(code)
    return f'<img src="{url}" alt="">' if url else ""


# kind: "series" (country x year) | "snapshot" (country, one point in time) | "global" (no country)
INDICATORS = {
    "GDP (₹ lakh crore)": dict(
        kind="series", col="gdp_inr_lakh_crore", unit="",
        help="Nominal GDP converted into Indian rupees. Bigger means a larger economy."),
    "Inflation rate (%)": dict(
        kind="series", col="inflation_pct", unit="%",
        help="How fast consumer prices are rising each year."),
    "Unemployment rate (%)": dict(
        kind="series", col="unemployment_pct", unit="%",
        help="Share of the labour force without a job."),
    "Currency depreciation (%)": dict(
        kind="series", col="currency_depreciation_pct", unit="%",
        help="Positive means the local currency became weaker against the US dollar."),
    "Fuel affordability": dict(
        kind="series", col="fuel_burden_pct", unit="%",
        help="Price of 1 litre of fuel as a % of one day's GDP per capita (both in ₹). "
             "Higher means fuel is less affordable."),
    "Gold reserves": dict(
        kind="snapshot", col="gold_reserves_tonnes", unit=" t",
        help="Official gold holdings of each country's central bank, in tonnes. "
             "This is a latest snapshot, not a yearly series."),
    "Standard gold rate": dict(
        kind="global", col="gold_usd_per_troy_ounce", unit=" USD/oz",
        help="World Bank Pink Sheet global benchmark in USD per troy ounce. "
             "It is not a country-specific retail price."),
}

# Pleasant, earthy palette: sand -> deep teal for scales, distinct warm/cool hues for lines.
MAP_SCALE = ["#E3EFEA", "#B9D8CE", "#85BBAC", "#4F9A8C", "#2A7872", "#17544F"]
LOW_RGB, HIGH_RGB = (0xCF, 0xE5, 0xDE), (0x17, 0x54, 0x4F)
LINE_COLORS = ["#1F6F6B", "#C8643B", "#D4A017", "#3D8FB5", "#6B8E23",
               "#B4506B", "#8B5E3C", "#475569", "#8FA88A", "#E08E45"]


def shade(t):
    """Interpolate between light and dark teal, t in 0..1."""
    return "#%02x%02x%02x" % tuple(int(a + (b - a) * t) for a, b in zip(LOW_RGB, HIGH_RGB))


# ------------------------------------------------------------
# Data loading
# ------------------------------------------------------------
@st.cache_data
def read_csv(path):
    p = Path(path)
    return pd.read_csv(p) if p.exists() else pd.DataFrame()


def clean_code(df, col="country_code"):
    if df.empty or col not in df.columns:
        return df
    df = df.copy()
    df[col] = df[col].astype(str).str.upper().str.strip()
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df


@st.cache_data
def build_main():
    """GDP, inflation, unemployment and currency depreciation (country x year)."""
    base = clean_code(read_csv(DATA / "economic_analysis.csv"))
    if base.empty:
        raise FileNotFoundError(
            "data/processed/economic_analysis.csv was not found. "
            "Run the existing transformation script first.")
    base = base[base["year"].isin(YEARS)].copy()

    gdp = clean_code(read_csv(DATA / "gdp_inr_all_countries.csv"))
    if not gdp.empty and {"country_code", "year", "gdp_inr"}.issubset(gdp.columns):
        gdp["gdp_inr"] = pd.to_numeric(gdp["gdp_inr"], errors="coerce")
        gdp = gdp[["country_code", "year", "gdp_inr"]].drop_duplicates(
            ["country_code", "year"], keep="last")
        base = base.merge(gdp, on=["country_code", "year"], how="left")
        base["gdp_inr_lakh_crore"] = base["gdp_inr"] / 1_000_000_000_000  # 1 lakh crore = 1e12

    gi = clean_code(read_csv(DATA / "growth_inflation.csv"))
    if not gi.empty and {"country_code", "year", "indicator", "value"}.issubset(gi.columns):
        txt = gi["indicator"].astype(str).str.lower()
        gi["value"] = pd.to_numeric(gi["value"], errors="coerce")
        is_inf = (txt.str.contains("fp.cpi.totl.zg", regex=False)
                  | txt.str.contains("inflation", regex=False)
                  | txt.str.contains("consumer price", regex=False))
        infl = (gi[is_inf][["country_code", "year", "value"]]
                .rename(columns={"value": "inflation_src"})
                .drop_duplicates(["country_code", "year"], keep="last"))
        base = base.merge(infl, on=["country_code", "year"], how="left")
        if "inflation_pct" in base.columns:
            base["inflation_pct"] = base["inflation_pct"].combine_first(base["inflation_src"])
        else:
            base["inflation_pct"] = base["inflation_src"]
        base = base.drop(columns=["inflation_src"], errors="ignore")

    un = clean_code(read_csv(DATA / "unemployment.csv"))
    if not un.empty and {"country_code", "year", "unemployment_pct"}.issubset(un.columns):
        un["unemployment_pct"] = pd.to_numeric(un["unemployment_pct"], errors="coerce")
        un = un[["country_code", "year", "unemployment_pct"]].drop_duplicates(
            ["country_code", "year"], keep="last")
        base = base.drop(columns=["unemployment_pct"], errors="ignore")
        base = base.merge(un, on=["country_code", "year"], how="left")

    base = base.sort_values(["country_code", "year"])
    if "exchange_rate_lcu_per_usd" in base.columns:
        base["currency_depreciation_pct"] = (
            base.groupby("country_code")["exchange_rate_lcu_per_usd"].pct_change() * 100)

    for spec in INDICATORS.values():
        if spec["kind"] == "series" and spec["col"] not in base.columns:
            base[spec["col"]] = float("nan")

    base = base.dropna(subset=["year"])
    base = base[base["country_code"].isin(COUNTRIES)].copy()
    base["year"] = base["year"].astype(int)
    return base


@st.cache_data
def build_fuel():
    """Fuel affordability = litre price / daily GDP per capita, both in INR."""
    fuel = read_csv(DATA / "fuel_prices.csv")
    gdp_pc = clean_code(read_csv(RAW / "gdp_per_capita_usd.csv"))
    fx = clean_code(read_csv(DATA / "exchange_rates.csv"))
    if fuel.empty or gdp_pc.empty or fx.empty:
        return pd.DataFrame()

    fuel = fuel.copy()
    fuel["country_code"] = fuel["Country Code"].astype(str).str.upper()
    fuel["year"] = pd.to_datetime(fuel["date"], errors="coerce").dt.year
    fuel["price_inr_per_litre"] = pd.to_numeric(fuel["price_inr_per_litre"], errors="coerce")
    fuel = fuel[fuel["country_code"].isin(COUNTRIES)]

    inr = (fx[fx.country_code.eq("IND")][["year", "exchange_rate_lcu_per_usd"]]
           .rename(columns={"exchange_rate_lcu_per_usd": "inr_per_usd"}))
    pc = gdp_pc.merge(inr, on="year", how="left")
    pc["gdp_pc_inr_daily"] = pc["gdp_per_capita_usd"] * pc["inr_per_usd"] / 365

    out = fuel.merge(pc[["country_code", "year", "gdp_pc_inr_daily"]],
                     on=["country_code", "year"], how="left")
    out["fuel_burden_pct"] = out["price_inr_per_litre"] / out["gdp_pc_inr_daily"] * 100
    out["fuel_type"] = out["fuel_type"].astype(str).str.title()
    out = out.dropna(subset=["fuel_burden_pct"])
    return (out.groupby(["country_code", "fuel_type", "year"], as_index=False)
               ["fuel_burden_pct"].mean())


@st.cache_data
def build_reserves():
    r = read_csv(DATA / "gold_reserves.csv")
    if r.empty:
        return r
    r = r.copy()
    r["country_code"] = r["country"].map(NAME_TO_CODE)
    r["gold_reserves_tonnes"] = pd.to_numeric(r["gold_reserves_tonnes"], errors="coerce")
    return r[r["country_code"].isin(COUNTRIES)].dropna(subset=["gold_reserves_tonnes"])


@st.cache_data
def build_gold():
    g = read_csv(DATA / "gold_fuel_prices.csv")
    if g.empty:
        return g
    g = g.copy()
    g["date"] = pd.to_datetime(g["date"], errors="coerce")
    g["gold_usd_per_troy_ounce"] = pd.to_numeric(g["gold_usd_per_troy_ounce"], errors="coerce")
    return g.dropna(subset=["date", "gold_usd_per_troy_ounce"]).sort_values("date")


try:
    main_df = build_main()
except Exception as exc:
    st.error(f"Could not prepare the dashboard data: {exc}")
    st.stop()
fuel_df = build_fuel()
reserves_df = build_reserves()
gold_df = build_gold()
duty_df = clean_code(read_csv(DATA / "gold_import_duty.csv"))


def fmt(v, unit):
    return f"{v:,.2f}{unit}" if pd.notna(v) else "n/a"


def card(title, main_html, sub):
    st.markdown(
        f'<div class="kpi"><div class="t">{title}</div>'
        f'<div class="c">{main_html}</div><div class="v">{sub}</div></div>',
        unsafe_allow_html=True)


def country_card(title, code, value_text):
    card(title, f'{flag_img(code)}<span>{cname(code)}</span>', value_text)


def note(title, text):
    st.markdown(f'<div class="note"><b>{title}</b><br>{text}</div>', unsafe_allow_html=True)


def chips(names_to_colors):
    html = "".join(
        f'<div class="chip"><span class="dot" style="background:{col}"></span>'
        f'{flag_img(NAME_TO_CODE.get(n, ""))}<span>{n}</span></div>'
        for n, col in names_to_colors.items())
    st.markdown(f'<div class="chips">{html}</div>', unsafe_allow_html=True)


def ranking_html(latest):
    r = latest.sort_values("value", ascending=False).reset_index(drop=True)
    vmax, vmin = r["value"].max(), r["value"].min()
    lo = min(0, vmin)
    span = (vmax - lo) or 1
    rows = []
    for i, row in r.iterrows():
        w = max((row["value"] - lo) / span, 0.03) * 100
        rows.append(
            f'<div class="rk"><div class="rn">{i + 1}</div>'
            f'<img src="{flag_url(row["country_code"])}" alt="">'
            f'<div class="rname">{row["country"]}</div>'
            f'<div class="rbar"><div style="width:{w:.1f}%;background:{shade(row["rank_color"])}"></div></div>'
            f'<div class="rval">{row["value_text"]}</div></div>')
    return "".join(rows)


def with_flags(df, code_col="country_code"):
    out = df.copy()
    out.insert(0, "Flag", out[code_col].map(lambda c: flag_url(c, 40)))
    out.insert(1, "Country", out[code_col].map(cname))
    return out


FLAG_COL = {"Flag": st.column_config.ImageColumn("", width="small")}

# ------------------------------------------------------------
# Banner + controls
# ------------------------------------------------------------
b1, b2, b3 = st.columns([2.4, 1.8, 1])
with b1:
    st.markdown(
        '<div class="banner"><h1>🌍 Global Economic Comparison</h1>'
        '<p>10 major economies · 2020–2025 </p></div>',
        unsafe_allow_html=True)
with b2:
    selected = st.selectbox("Indicator", list(INDICATORS.keys()))
cfg = INDICATORS[selected]
with b3:
    year = st.selectbox("Year", YEARS, index=len(YEARS) - 1,
                        disabled=(cfg["kind"] == "snapshot"),
                        help="Gold reserves are a latest snapshot, so the year does not apply."
                        if cfg["kind"] == "snapshot" else None)

unit, help_text = cfg["unit"], cfg["help"]

# ============================================================
# GLOBAL INDICATOR: Standard gold rate
# ============================================================
if cfg["kind"] == "global":
    gt = gold_df[gold_df["date"].dt.year <= year] if not gold_df.empty else gold_df
    if gt.empty:
        st.warning("Gold benchmark data is unavailable for this period.")
        st.stop()

    gcol = "gold_usd_per_troy_ounce"
    last, first = gt.iloc[-1], gt.iloc[0]
    hi, lo = gt.loc[gt[gcol].idxmax()], gt.loc[gt[gcol].idxmin()]
    change = (last[gcol] / first[gcol] - 1) * 100

    m1, m2, m3, m4 = st.columns([1, 1, 1, 1.8])
    with m1:
        card("Latest price", f'${last[gcol]:,.0f}', f'{last["date"]:%b %Y}')
    with m2:
        card("Highest", f'${hi[gcol]:,.0f}', f'{hi["date"]:%b %Y}')
    with m3:
        card("Lowest", f'${lo[gcol]:,.0f}', f'{lo["date"]:%b %Y}')
    with m4:
        note(selected, f"{help_text}<br>Change since {first['date']:%b %Y}: <b>{change:+.1f}%</b>.")

    with st.container(border=True):
        st.subheader("Gold price over time")
        fig = px.line(gt, x="date", y=gcol, markers=True,
                      labels={"date": "", gcol: "USD per troy ounce"})
        fig.update_traces(line=dict(color="#B8892B", width=3), marker=dict(size=7))
        fig.update_layout(height=460, paper_bgcolor="#FFFFFF", plot_bgcolor="#FBF9F4",
                          font=dict(color="#26332F", size=14), margin=dict(l=0, r=0, t=10, b=0),
                          xaxis=dict(gridcolor="#ECE6D9"), yaxis=dict(gridcolor="#ECE6D9"))
        st.plotly_chart(fig, use_container_width=True)
        with st.expander("View the data"):
            st.dataframe(gt.rename(columns={gcol: "USD per troy ounce"}),
                         hide_index=True, use_container_width=True, height=260)

    st.caption("Source: World Bank Pink Sheet. One worldwide price, so there is no country map or ranking.")
    st.stop()

# ============================================================
# COUNTRY-LEVEL INDICATORS
# ============================================================
series = pd.DataFrame()
if selected == "Fuel affordability":
    fuel_type = st.radio("Fuel type", ["Petrol", "Diesel"], horizontal=True)
    if not fuel_df.empty:
        series = (fuel_df[fuel_df.fuel_type == fuel_type]
                  .rename(columns={"fuel_burden_pct": "value"})[["country_code", "year", "value"]])
    else:
        st.warning("Fuel affordability needs fuel_prices.csv, gdp_per_capita_usd.csv and exchange_rates.csv.")
elif cfg["kind"] == "snapshot":
    if not reserves_df.empty:
        series = reserves_df.rename(columns={"gold_reserves_tonnes": "value"})[["country_code", "value"]]
        series["year"] = 0
else:
    series = main_df[["country_code", "year", cfg["col"]]].rename(columns={cfg["col"]: "value"})

series = series.dropna(subset=["value"]) if not series.empty else series

if series.empty:
    latest = pd.DataFrame()
elif cfg["kind"] == "snapshot":
    latest = series.copy()
    latest["observation_year"] = "Latest"
else:
    latest = (series[series["year"] <= year].sort_values("year")
              .groupby("country_code").tail(1)
              .rename(columns={"year": "observation_year"}))

if latest.empty:
    st.warning("No data is available for this indicator up to the selected year.")
    st.stop()

latest = latest.reset_index(drop=True)
latest["country"] = latest["country_code"].map(cname)
latest["value_text"] = latest["value"].map(lambda v: fmt(v, unit))
latest["rank_color"] = ((latest["value"].rank(method="first") - 1) / (len(latest) - 1)
                        if len(latest) > 1 else 0.5)

top, bottom = latest.loc[latest["value"].idxmax()], latest.loc[latest["value"].idxmin()]

m1, m2, m3, m4 = st.columns([1, 1, 1, 1.8])
with m1:
    country_card("Highest", top["country_code"], fmt(top["value"], unit))
with m2:
    country_card("Lowest", bottom["country_code"], fmt(bottom["value"], unit))
with m3:
    card("Average", fmt(latest["value"].mean(), unit), f"{len(latest)} of {len(COUNTRIES)} countries")
with m4:
    note(selected, help_text)

# Map + ranking
map_col, rank_col = st.columns([1.5, 1], gap="large")
with map_col:
    with st.container(border=True):
        st.subheader("World map")
        fig = px.choropleth(
            latest, locations="country_code", locationmode="ISO-3", color="rank_color",
            hover_name="country",
            hover_data={"value_text": True, "observation_year": True,
                        "rank_color": False, "country_code": False},
            color_continuous_scale=MAP_SCALE, range_color=(0, 1),
            labels={"value_text": "Value", "observation_year": "Data year"})
        fig.update_geos(projection_type="natural earth", projection_rotation=dict(lon=10),
                        lataxis_range=[-58, 85], showframe=False, showcoastlines=True,
                        coastlinecolor="#C9C2B2", showland=True, landcolor="#ECE7DB",
                        showcountries=True, countrycolor="#FFFFFF", showocean=True,
                        oceancolor="#EAF1F3", showlakes=False, bgcolor="rgba(0,0,0,0)")
        fig.update_traces(marker_line_color="#FFFFFF", marker_line_width=0.8)
        fig.update_layout(height=580, margin=dict(l=0, r=0, t=0, b=0), paper_bgcolor="#FFFFFF",
                          font=dict(color="#26332F", size=14),
                          coloraxis_colorbar=dict(title="", thickness=14, len=0.55, outlinewidth=0,
                                                  tickvals=[0, 1], ticktext=["Lowest", "Highest"]))
        st.plotly_chart(fig, use_container_width=True)

with rank_col:
    with st.container(border=True):
        st.subheader("Country ranking")
        st.markdown(ranking_html(latest), unsafe_allow_html=True)

missing = [COUNTRIES[c][1] for c in COUNTRIES if c not in set(latest["country_code"])]
if missing:
    st.caption("No data available for: " + ", ".join(missing) + ".")

# ------------------------------------------------------------
# Bottom panel
# ------------------------------------------------------------
if cfg["kind"] == "snapshot":
    with st.container(border=True):
        st.subheader("Reported gold import duty (HS 710812)")
        if duty_df.empty:
            st.info("Gold import duty data is unavailable.")
        else:
            dv = with_flags(duty_df[duty_df.country_code.isin(COUNTRIES)])
            dv = dv.rename(columns={"product_code": "HS code", "year": "Year",
                                    "gold_import_duty_pct": "Import duty (%)",
                                    "tariff_data_type": "Tariff type"})
            cols = [c for c in ["Flag", "Country", "HS code", "Year", "Import duty (%)", "Tariff type"]
                    if c in dv]
            st.dataframe(dv[cols].sort_values(["Country", "Year"]), hide_index=True,
                         use_container_width=True, column_config=FLAG_COL)
            st.caption("Only countries that reported a duty for this product are listed.")
else:
    series = series.copy()
    series["country"] = series["country_code"].map(cname)
    options = sorted(series["country"].unique())
    defaults = [c for c in ["India", "United States", "China", "Germany"] if c in options]

    with st.container(border=True):
        st.subheader("Trend over time")
        chosen = st.multiselect("Countries to compare", options, default=defaults)
        td = series[series["country"].isin(chosen)].sort_values(["country", "year"])
        if not chosen:
            st.info("Choose at least one country to see its trend.")
        elif td.empty:
            st.warning("No data is available for the selected countries.")
        else:
            color_map = {n: LINE_COLORS[i % len(LINE_COLORS)] for i, n in enumerate(chosen)}
            chips(color_map)
            trend = px.line(td, x="year", y="value", color="country", markers=True,
                            color_discrete_map=color_map,
                            labels={"year": "Year", "value": selected, "country": "Country"})
            trend.update_traces(line=dict(width=3.5), marker=dict(size=9))
            trend.update_layout(height=440, paper_bgcolor="#FFFFFF", plot_bgcolor="#FBF9F4",
                                font=dict(color="#26332F", size=14),
                                margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
                                xaxis=dict(dtick=1, gridcolor="#ECE6D9", title=""),
                                yaxis=dict(gridcolor="#ECE6D9", title=""),
                                hovermode="x unified")
            st.plotly_chart(trend, use_container_width=True)
        with st.expander("View the data"):
            tbl = with_flags(td if not td.empty else series).rename(
                columns={"year": "Year", "value": selected})
            st.dataframe(tbl[["Flag", "Country", "Year", selected]].sort_values(["Country", "Year"]),
                         hide_index=True, use_container_width=True, height=260,
                         column_config=FLAG_COL)

st.caption("Sources: World Bank, World Gold Council / IFS, World Bank Pink Sheet and WITS. "
           "Coverage differs by indicator.")
