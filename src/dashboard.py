"""
Forest Restoration Monitoring Dashboard
Streamlit Cloud-ready version — no database required.
All data is generated synthetically at startup and cached.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
import json
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Forest Restoration Dashboard",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background-color: #F1F8E9; }
    .main-title { font-size: 2.4rem; font-weight: 800; color: #1B5E20; text-align: center; margin-bottom: 0.2rem; }
    .sub-title  { font-size: 1rem; color: #4CAF50; text-align: center; margin-bottom: 1.5rem; }
    .kpi-box {
        background: linear-gradient(135deg, #2E7D32, #66BB6A);
        border-radius: 12px; padding: 1.2rem 1rem;
        color: white; text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .kpi-val   { font-size: 1.9rem; font-weight: 800; }
    .kpi-lbl   { font-size: 0.82rem; opacity: 0.88; margin-top: 0.2rem; }
    .kpi-delta { font-size: 0.85rem; margin-top: 0.3rem; }
    .section-header { font-size: 1.3rem; font-weight: 700; color: #2E7D32;
                      border-left: 4px solid #4CAF50; padding-left: 0.6rem; margin: 1.2rem 0 0.8rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SYNTHETIC DATA GENERATION  (cached)
# ─────────────────────────────────────────────
REGIONS = [
    {"id": "R01", "name": "Amazon Basin North",    "country": "Brazil",       "lat": -3.5,  "lon": -62.0,  "type": "Active Restoration"},
    {"id": "R02", "name": "Congo Basin West",       "country": "DRC",          "lat": -1.2,  "lon": 21.5,   "type": "Natural Regeneration"},
    {"id": "R03", "name": "Borneo Lowlands",        "country": "Indonesia",    "lat":  0.5,  "lon": 114.0,  "type": "Agroforestry"},
    {"id": "R04", "name": "Mekong Highlands",       "country": "Vietnam",      "lat": 14.5,  "lon": 107.8,  "type": "Active Restoration"},
    {"id": "R05", "name": "Ethiopian Highlands",    "country": "Ethiopia",     "lat":  9.0,  "lon": 38.5,   "type": "Community Forestry"},
    {"id": "R06", "name": "Atlantic Forest South",  "country": "Brazil",       "lat": -23.0, "lon": -48.5,  "type": "Active Restoration"},
    {"id": "R07", "name": "Western Ghats",          "country": "India",        "lat": 11.0,  "lon": 76.5,   "type": "Natural Regeneration"},
    {"id": "R08", "name": "Sumatra Peatlands",      "country": "Indonesia",    "lat":  0.8,  "lon": 102.5,  "type": "Peatland Restoration"},
    {"id": "R09", "name": "Madagascar East",        "country": "Madagascar",   "lat": -18.5, "lon": 48.5,   "type": "Agroforestry"},
    {"id": "R10", "name": "Mesoamerica Corridor",   "country": "Guatemala",    "lat": 15.5,  "lon": -90.5,  "type": "Community Forestry"},
    {"id": "R11", "name": "Himalayan Foothills",    "country": "Nepal",        "lat": 27.5,  "lon": 84.0,   "type": "Active Restoration"},
    {"id": "R12", "name": "Miombo Woodlands",       "country": "Zambia",       "lat": -13.0, "lon": 28.5,   "type": "Natural Regeneration"},
    {"id": "R13", "name": "Cerrado Transition",     "country": "Brazil",       "lat": -10.5, "lon": -48.0,  "type": "Active Restoration"},
    {"id": "R14", "name": "Philippine Mossy Forest","country": "Philippines",  "lat": 10.5,  "lon": 124.5,  "type": "Agroforestry"},
    {"id": "R15", "name": "Peruvian Cloud Forest",  "country": "Peru",         "lat": -6.5,  "lon": -77.5,  "type": "Natural Regeneration"},
    {"id": "R16", "name": "Rift Valley Escarpment", "country": "Kenya",        "lat":  0.5,  "lon": 35.5,   "type": "Community Forestry"},
]

YEARS = list(range(2015, 2025))
LAND_CLASSES = ["Tree Cover", "Shrubland", "Grassland", "Cropland", "Urban", "Bare/Sparse", "Water"]

np.random.seed(42)


@st.cache_data
def generate_data():
    rng = np.random.default_rng(42)
    regions_df = pd.DataFrame(REGIONS)

    # Assign base metrics
    regions_df["base_area_ha"]        = rng.integers(8_000, 80_000, len(REGIONS))
    regions_df["base_tree_cover_pct"] = rng.uniform(0.25, 0.72, len(REGIONS))
    trend_map = {
        "Active Restoration":  rng.uniform(0.012, 0.030, len(REGIONS)),
        "Natural Regeneration":rng.uniform(0.006, 0.018, len(REGIONS)),
        "Agroforestry":        rng.uniform(0.005, 0.015, len(REGIONS)),
        "Community Forestry":  rng.uniform(0.008, 0.020, len(REGIONS)),
        "Peatland Restoration":rng.uniform(0.003, 0.010, len(REGIONS)),
    }
    regions_df["annual_trend"] = [
        trend_map[row.type][i] for i, row in regions_df.iterrows()
    ]

    # Time-series metrics
    records = []
    for _, row in regions_df.iterrows():
        for yr_idx, yr in enumerate(YEARS):
            noise        = rng.normal(0, 0.004)
            tree_pct     = min(0.95, row.base_tree_cover_pct + yr_idx * row.annual_trend + noise)
            tree_ha      = row.base_area_ha * tree_pct
            shrub_ha     = row.base_area_ha * rng.uniform(0.05, 0.15)
            grass_ha     = row.base_area_ha * rng.uniform(0.04, 0.12)
            crop_ha      = row.base_area_ha * rng.uniform(0.03, 0.10)
            urban_ha     = row.base_area_ha * rng.uniform(0.01, 0.05)
            bare_ha      = row.base_area_ha * max(0, 1 - tree_pct - 0.30) * rng.uniform(0.5, 1.0)
            water_ha     = row.base_area_ha * rng.uniform(0.005, 0.03)
            records.append({
                "region_id": row.id, "region_name": row["name"],
                "country": row.country, "project_type": row.type,
                "year": yr, "total_area_ha": row.base_area_ha,
                "tree_cover_ha": round(tree_ha, 1),
                "tree_cover_pct": round(tree_pct * 100, 2),
                "shrubland_ha": round(shrub_ha, 1),
                "grassland_ha": round(grass_ha, 1),
                "cropland_ha": round(crop_ha, 1),
                "urban_ha": round(urban_ha, 1),
                "bare_ha": round(bare_ha, 1),
                "water_ha": round(water_ha, 1),
            })

    ts_df = pd.DataFrame(records)

    # Year-over-year change
    ts_df = ts_df.sort_values(["region_id", "year"])
    ts_df["prev_tree_ha"] = ts_df.groupby("region_id")["tree_cover_ha"].shift(1)
    ts_df["yoy_change_ha"] = ts_df["tree_cover_ha"] - ts_df["prev_tree_ha"]
    ts_df["yoy_change_pct"] = (ts_df["yoy_change_ha"] / ts_df["prev_tree_ha"] * 100).round(2)

    # Land-use transitions (2015→2024)
    transition_records = []
    lc_pairs = [
        ("Cropland",    "Tree Cover"),
        ("Grassland",   "Tree Cover"),
        ("Bare/Sparse", "Tree Cover"),
        ("Tree Cover",  "Cropland"),
        ("Tree Cover",  "Urban"),
        ("Shrubland",   "Tree Cover"),
        ("Grassland",   "Cropland"),
    ]
    for _, row in regions_df.iterrows():
        for (fc, tc) in lc_pairs:
            area = rng.uniform(50, row.base_area_ha * 0.08)
            transition_records.append({
                "region_id": row.id, "region_name": row["name"],
                "country": row.country,
                "from_class": fc, "to_class": tc,
                "area_ha": round(area, 1),
                "period": "2015–2024"
            })
    trans_df = pd.DataFrame(transition_records)

    # Carbon estimates (rough: 1 ha tree cover ≈ 100–250 tCO2)
    ts_df["carbon_tco2"] = (ts_df["tree_cover_ha"] * rng.uniform(100, 250, len(ts_df))).round(0)

    return regions_df, ts_df, trans_df


@st.cache_data
def get_kpis(ts_df):
    latest = ts_df[ts_df.year == ts_df.year.max()]
    earliest = ts_df[ts_df.year == ts_df.year.min()]
    total_tree_now   = latest["tree_cover_ha"].sum()
    total_tree_start = earliest["tree_cover_ha"].sum()
    net_change       = total_tree_now - total_tree_start
    pct_change       = (net_change / total_tree_start) * 100
    carbon_now       = latest["carbon_tco2"].sum()
    regions_improved = (latest.set_index("region_id")["tree_cover_ha"] >
                        earliest.set_index("region_id")["tree_cover_ha"]).sum()
    return {
        "total_tree_now":    total_tree_now,
        "net_change":        net_change,
        "pct_change":        pct_change,
        "carbon_stock":      carbon_now,
        "regions_improved":  int(regions_improved),
        "total_regions":     len(latest),
        "countries":         latest["country"].nunique(),
    }


regions_df, ts_df, trans_df = generate_data()
kpis = get_kpis(ts_df)

# ─────────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Sylvain_Sonnet_Forest.jpg/320px-Sylvain_Sonnet_Forest.jpg",
             use_column_width=True)
    st.markdown("## 🌿 Filters")

    all_countries = sorted(ts_df["country"].unique())
    sel_countries = st.multiselect("Country", all_countries, default=all_countries)

    all_types = sorted(ts_df["project_type"].unique())
    sel_types = st.multiselect("Project Type", all_types, default=all_types)

    year_range = st.slider("Year Range", 2015, 2024, (2015, 2024))

    st.markdown("---")
    st.markdown("**About**")
    st.caption("Tracks tree cover change across 16 pilot restoration regions (2015–2024). "
               "Data is synthetic and generated for portfolio purposes.")

# ─────────────────────────────────────────────
# FILTER DATA
# ─────────────────────────────────────────────
filt = (
    ts_df["country"].isin(sel_countries) &
    ts_df["project_type"].isin(sel_types) &
    ts_df["year"].between(*year_range)
)
df = ts_df[filt]
regions_filt = regions_df[
    regions_df["country"].isin(sel_countries) &
    regions_df["type"].isin(sel_types)
]


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">🌳 Forest Restoration Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-title">16 Pilot Regions · {len(sel_countries)} Countries Selected · {year_range[0]}–{year_range[1]}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KPI CARDS
# ─────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpi_items = [
    (c1, f"{kpis['total_tree_now']:,.0f} ha",   "🌲 Current Tree Cover",   ""),
    (c2, f"{kpis['net_change']:+,.0f} ha",       "📈 Net Change (all years)", f"{'▲' if kpis['net_change']>0 else '▼'} {abs(kpis['pct_change']):.1f}%"),
    (c3, f"{kpis['carbon_stock']/1e6:.2f} MtCO₂","💨 Est. Carbon Stock",    ""),
    (c4, f"{kpis['regions_improved']} / {kpis['total_regions']}","✅ Regions Improving",""),
    (c5, f"{kpis['countries']}",                  "🌍 Countries",            ""),
]
for col, val, lbl, delta in kpi_items:
    with col:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-val">{val}</div>
            <div class="kpi-lbl">{lbl}</div>
            {'<div class="kpi-delta">' + delta + '</div>' if delta else ''}
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROW 1 : MAP + TREND CHART
# ─────────────────────────────────────────────
left, right = st.columns([1.1, 1], gap="medium")

with left:
    st.markdown('<div class="section-header">🗺️ Regional Map</div>', unsafe_allow_html=True)

    latest_map = df[df.year == df.year.max()].copy()
    m = folium.Map(location=[5, 20], zoom_start=2, tiles="CartoDB positron")

    color_map = {
        "Active Restoration":   "#2E7D32",
        "Natural Regeneration": "#66BB6A",
        "Agroforestry":         "#8BC34A",
        "Community Forestry":   "#FFA726",
        "Peatland Restoration": "#1565C0",
    }

    for _, row in regions_filt.iterrows():
        m_row = latest_map[latest_map.region_id == row.id]
        if m_row.empty:
            continue
        m_row = m_row.iloc[0]
        col = color_map.get(row.type, "#888")
        folium.CircleMarker(
            location=[row.lat, row.lon],
            radius=max(6, min(20, m_row.tree_cover_ha / 2500)),
            color=col, fill=True, fill_color=col, fill_opacity=0.75,
            tooltip=folium.Tooltip(f"""
                <b>{row['name']}</b><br>
                Country: {row.country}<br>
                Type: {row.type}<br>
                Tree Cover: {m_row.tree_cover_ha:,.0f} ha ({m_row.tree_cover_pct:.1f}%)<br>
                YoY Change: {m_row.yoy_change_ha:+,.0f} ha
            """),
        ).add_to(m)

    # Legend
    legend_html = """
    <div style="position:fixed;bottom:20px;left:20px;z-index:1000;background:white;
         padding:10px 14px;border-radius:8px;font-size:12px;box-shadow:0 2px 6px rgba(0,0,0,.25);">
    <b>Project Type</b><br>
    """
    for ptype, col in color_map.items():
        legend_html += f'<span style="color:{col};font-size:16px">●</span> {ptype}<br>'
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=None, height=420, returned_objects=[])

with right:
    st.markdown('<div class="section-header">📈 Tree Cover Trend</div>', unsafe_allow_html=True)

    trend_agg = df.groupby("year")["tree_cover_ha"].sum().reset_index()
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=trend_agg.year, y=trend_agg.tree_cover_ha,
        mode="lines+markers",
        line=dict(color="#2E7D32", width=3),
        marker=dict(size=7),
        fill="tozeroy", fillcolor="rgba(46,125,50,0.12)",
        name="Total Tree Cover"
    ))
    fig_trend.update_layout(
        xaxis_title="Year", yaxis_title="Tree Cover (ha)",
        plot_bgcolor="white", paper_bgcolor="white",
        height=200, margin=dict(l=10, r=10, t=10, b=30),
        showlegend=False,
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.markdown('<div class="section-header">📊 Year-over-Year Change</div>', unsafe_allow_html=True)
    yoy = df[df.year > year_range[0]].groupby("year")["yoy_change_ha"].sum().reset_index()
    fig_yoy = px.bar(
        yoy, x="year", y="yoy_change_ha",
        color="yoy_change_ha",
        color_continuous_scale=["#D32F2F", "#FFEB3B", "#2E7D32"],
        color_continuous_midpoint=0,
    )
    fig_yoy.update_layout(
        xaxis_title="Year", yaxis_title="Change (ha)",
        coloraxis_showscale=False,
        plot_bgcolor="white", paper_bgcolor="white",
        height=185, margin=dict(l=10, r=10, t=10, b=30),
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

# ─────────────────────────────────────────────
# ROW 2 : BY-REGION BAR + LAND USE TRANSITION
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">🏞️ Tree Cover by Region ({})'.format(df.year.max()) + '</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1.4, 1], gap="medium")

with col_a:
    latest_region = df[df.year == df.year.max()].sort_values("tree_cover_ha", ascending=True)
    fig_bar = px.bar(
        latest_region, x="tree_cover_ha", y="region_name",
        orientation="h",
        color="project_type",
        color_discrete_map=color_map,
        text=latest_region["tree_cover_pct"].apply(lambda x: f"{x:.1f}%"),
    )
    fig_bar.update_layout(
        xaxis_title="Tree Cover (ha)", yaxis_title="",
        legend_title="Project Type",
        plot_bgcolor="white", paper_bgcolor="white",
        height=460, margin=dict(l=10, r=10, t=10, b=30),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_b:
    st.markdown('<div class="section-header">🔄 Land-Use Transitions (2015→2024)</div>', unsafe_allow_html=True)
    trans_filt = trans_df[trans_df["country"].isin(sel_countries)]
    # Sankey
    labels = LAND_CLASSES
    label_idx = {l: i for i, l in enumerate(labels)}
    sankey_src, sankey_tgt, sankey_val = [], [], []
    for _, row in trans_filt.groupby(["from_class", "to_class"])["area_ha"].sum().reset_index().iterrows():
        if row.from_class in label_idx and row.to_class in label_idx:
            sankey_src.append(label_idx[row.from_class])
            sankey_tgt.append(label_idx[row.to_class])
            sankey_val.append(row.area_ha)

    fig_sankey = go.Figure(go.Sankey(
        node=dict(
            pad=12, thickness=16,
            label=labels,
            color=["#2E7D32","#8BC34A","#CDDC39","#FFA726","#E64A19","#BDBDBD","#1E88E5"],
        ),
        link=dict(source=sankey_src, target=sankey_tgt, value=sankey_val,
                  color="rgba(46,125,50,0.25)"),
    ))
    fig_sankey.update_layout(
        height=440, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_sankey, use_container_width=True)

# ─────────────────────────────────────────────
# ROW 3 : HEATMAP + PROJECT TYPE BREAKDOWN
# ─────────────────────────────────────────────
col_c, col_d = st.columns(2, gap="medium")

with col_c:
    st.markdown('<div class="section-header">🌡️ Tree Cover % Heatmap</div>', unsafe_allow_html=True)
    pivot = df.pivot_table(index="region_name", columns="year", values="tree_cover_pct", aggfunc="mean")
    fig_heat = px.imshow(
        pivot, color_continuous_scale="Greens",
        aspect="auto", text_auto=".1f",
    )
    fig_heat.update_layout(
        height=430, margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_colorbar=dict(title="% Cover"),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col_d:
    st.markdown('<div class="section-header">🌿 Restoration Type Performance</div>', unsafe_allow_html=True)
    type_agg = df.groupby(["year", "project_type"])["tree_cover_ha"].sum().reset_index()
    fig_type = px.line(
        type_agg, x="year", y="tree_cover_ha",
        color="project_type",
        color_discrete_map=color_map,
        markers=True,
    )
    fig_type.update_layout(
        xaxis_title="Year", yaxis_title="Tree Cover (ha)",
        legend_title="Type",
        plot_bgcolor="white", paper_bgcolor="white",
        height=200, margin=dict(l=10, r=10, t=10, b=30),
    )
    st.plotly_chart(fig_type, use_container_width=True)

    # Pie: share by type in latest year
    type_latest = df[df.year == df.year.max()].groupby("project_type")["tree_cover_ha"].sum().reset_index()
    fig_pie = px.pie(
        type_latest, names="project_type", values="tree_cover_ha",
        color="project_type", color_discrete_map=color_map, hole=0.4,
    )
    fig_pie.update_layout(
        height=200, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=True,
        legend=dict(font=dict(size=10)),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# ─────────────────────────────────────────────
# REGIONAL TABLE + EXPORT
# ─────────────────────────────────────────────
st.markdown('<div class="section-header">📋 Regional Summary Table</div>', unsafe_allow_html=True)

latest_all  = ts_df[ts_df.year == ts_df.year.max()]
earliest_all = ts_df[ts_df.year == ts_df.year.min()]

summary = latest_all.merge(
    earliest_all[["region_id", "tree_cover_ha"]].rename(columns={"tree_cover_ha": "tree_cover_2015"}),
    on="region_id",
)
summary["net_change_ha"]  = summary["tree_cover_ha"] - summary["tree_cover_2015"]
summary["change_pct"]     = (summary["net_change_ha"] / summary["tree_cover_2015"] * 100).round(1)
summary["status"] = summary["net_change_ha"].apply(lambda x: "✅ Gaining" if x > 0 else "⚠️ Declining")

display_cols = {
    "region_name": "Region", "country": "Country",
    "project_type": "Type", "tree_cover_ha": "Tree Cover (ha)",
    "tree_cover_pct": "Cover %",
    "net_change_ha": "Net Change (ha)", "change_pct": "Change %", "status": "Status",
}
table_df = summary[list(display_cols)].rename(columns=display_cols)
table_df["Tree Cover (ha)"] = table_df["Tree Cover (ha)"].map("{:,.0f}".format)
table_df["Net Change (ha)"] = table_df["Net Change (ha)"].map("{:+,.0f}".format)

st.dataframe(table_df, use_container_width=True, height=320)

csv = summary.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Full Data (CSV)", csv,
    "forest_restoration_summary.csv", "text/csv",
)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.85rem;'>"
    "Forest Restoration Monitoring Dashboard · Data: 2015–2024 (Synthetic) · "
    "Built with Streamlit, Plotly & Folium"
    "</div>",
    unsafe_allow_html=True,
)
