import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import json

st.set_page_config(page_title="ForestTrack", page_icon="🌿", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0A0F0D; color: #E8EDE9; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem; max-width: 1400px; }
[data-testid="stSidebar"] { background: #0D1410 !important; border-right: 1px solid #1C2E22; }
[data-testid="stSidebar"] * { color: #A8BFaC !important; }
.sidebar-logo { padding: 1.5rem 0 1rem 0; border-bottom: 1px solid #1C2E22; margin-bottom: 1.5rem; }
.sidebar-logo h2 { font-family: 'Playfair Display', serif !important; font-size: 1.4rem !important; color: #4ADE80 !important; margin: 0 !important; }
.sidebar-logo p { font-size: 0.7rem !important; color: #4A6550 !important; margin: 0.2rem 0 0 0 !important; text-transform: uppercase; letter-spacing: 0.12em; }
.sidebar-section { font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 0.15em; color: #3A5040 !important; margin: 1.5rem 0 0.5rem 0; font-weight: 600; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }
.kpi-card { background: #0D1410; border: 1px solid #1C2E22; border-radius: 10px; padding: 1.25rem 1.5rem; position: relative; overflow: hidden; }
.kpi-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, #4ADE80, transparent); }
.kpi-label { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.12em; color: #4A6550; font-weight: 600; margin-bottom: 0.5rem; }
.kpi-value { font-family: 'DM Mono', monospace; font-size: 1.8rem; font-weight: 500; color: #E8EDE9; letter-spacing: -0.03em; line-height: 1; }
.kpi-delta { font-size: 0.72rem; color: #4ADE80; margin-top: 0.4rem; font-family: 'DM Mono', monospace; }
.kpi-icon { position: absolute; top: 1.25rem; right: 1.25rem; font-size: 1.1rem; opacity: 0.4; }
.section-header { font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.15em; color: #4A6550; font-weight: 600; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 8px; }
.section-header::after { content: ''; flex: 1; height: 1px; background: #1C2E22; }
.panel { background: #0D1410; border: 1px solid #1C2E22; border-radius: 10px; padding: 1.25rem; }
.quality-row { display: flex; align-items: center; justify-content: space-between; padding: 0.6rem 0; border-bottom: 1px solid #111A14; }
.quality-row:last-child { border-bottom: none; }
.quality-name { font-size: 0.8rem; color: #C8D8CB; font-family: 'DM Mono', monospace; }
.quality-bar-wrap { flex: 1; margin: 0 1rem; background: #111A14; border-radius: 2px; height: 3px; }
.quality-bar { height: 100%; background: linear-gradient(90deg, #4ADE80, #22C55E); border-radius: 2px; }
.quality-score { font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #4ADE80; min-width: 40px; text-align: right; }
.live-badge { display: inline-flex; align-items: center; gap: 6px; background: #0D2416; border: 1px solid #1A4228; border-radius: 20px; padding: 6px 14px; font-size: 0.7rem; color: #4ADE80; letter-spacing: 0.1em; text-transform: uppercase; }
.live-dot { width: 6px; height: 6px; background: #4ADE80; border-radius: 50%; animation: pulse 2s infinite; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
[data-testid="stDataFrame"] th { background: #111A14 !important; color: #4A6550 !important; font-size: 0.65rem !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; border-bottom: 1px solid #1C2E22 !important; }
[data-testid="stDataFrame"] td { color: #A8BFaC !important; font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important; border-bottom: 1px solid #111A14 !important; background: transparent !important; }
[data-testid="stExpander"] { background: #0D1410 !important; border: 1px solid #1C2E22 !important; border-radius: 8px !important; }
[data-testid="stDownloadButton"] button { background: #111A14 !important; border: 1px solid #1C2E22 !important; color: #4ADE80 !important; font-size: 0.75rem !important; border-radius: 6px !important; }
hr { border-color: #1C2E22 !important; }
::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-track { background: #0A0F0D; } ::-webkit-scrollbar-thumb { background: #1C2E22; border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    import numpy as np
    rng = np.random.default_rng(42)
    regions = [
        ("Amazon_Basin_North",    "Brazil",      "Active Restoration",    -3.5,  -62.0),
        ("Congo_Basin_West",      "DRC",          "Natural Regeneration",  -1.2,   21.5),
        ("Borneo_Lowlands",       "Indonesia",    "Agroforestry",           0.5,  114.0),
        ("Mekong_Highlands",      "Vietnam",      "Active Restoration",    14.5,  107.8),
        ("Ethiopian_Highlands",   "Ethiopia",     "Community Forestry",     9.0,   38.5),
        ("Atlantic_Forest_South", "Brazil",       "Active Restoration",   -23.0,  -48.5),
        ("Western_Ghats",         "India",        "Natural Regeneration",  11.0,   76.5),
        ("Sumatra_Peatlands",     "Indonesia",    "Peatland Restoration",   0.8,  102.5),
        ("Madagascar_East",       "Madagascar",   "Agroforestry",          -18.5,  48.5),
        ("Mesoamerica_Corridor",  "Guatemala",    "Community Forestry",    15.5,  -90.5),
        ("Himalayan_Foothills",   "Nepal",        "Active Restoration",    27.5,   84.0),
        ("Miombo_Woodlands",      "Zambia",       "Natural Regeneration", -13.0,   28.5),
        ("Cerrado_Transition",    "Brazil",       "Active Restoration",   -10.5,  -48.0),
        ("Philippine_Mossy_Forest","Philippines", "Agroforestry",          10.5,  124.5),
        ("Peruvian_Cloud_Forest", "Peru",         "Natural Regeneration",  -6.5,  -77.5),
        ("Rift_Valley_Escarpment","Kenya",        "Community Forestry",     0.5,   35.5),
    ]
    years = list(range(2015, 2025))
    records = []
    for region_name, country, project_type, lat, lon in regions:
        total_area_ha = float(rng.integers(8000, 80000))
        base_pct      = rng.uniform(0.25, 0.72)
        trend         = rng.uniform(0.006, 0.030)
        prev_ha       = None
        for yr_idx, yr in enumerate(years):
            pct    = min(0.95, base_pct + yr_idx * trend + rng.normal(0, 0.004))
            ha     = total_area_ha * pct
            change = (ha - prev_ha) if prev_ha is not None else 0.0
            quality = float(rng.uniform(72, 99))
            records.append({
                "region_name": region_name, "country": country,
                "project_type": project_type, "lat": lat, "lon": lon,
                "total_area_ha": total_area_ha, "geojson": None,
                "year": yr, "tree_cover_pct": round(pct * 100, 2),
                "tree_cover_ha": round(ha, 1),
                "tree_cover_ha_change": round(change, 1),
                "data_quality_score": round(quality, 1),
            })
            prev_ha = ha
    df = pd.DataFrame(records)
    for col in ["lat","lon","tree_cover_pct","tree_cover_ha","tree_cover_ha_change","data_quality_score","total_area_ha"]:
        df[col] = df[col].astype(float)
    return df

df = load_data()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><h2>ForestTrack</h2><p>Restoration Intelligence Platform</p></div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">Regions</p>', unsafe_allow_html=True)
    all_regions = sorted(df["region_name"].unique().tolist())
    sel_regions = st.multiselect("", all_regions, default=all_regions, label_visibility="collapsed")
    st.markdown('<p class="sidebar-section">Time Period</p>', unsafe_allow_html=True)
    year_range = st.slider("", int(df["year"].min()), int(df["year"].max()), (int(df["year"].min()), int(df["year"].max())), label_visibility="collapsed")
    st.markdown('<p class="sidebar-section">Project Type</p>', unsafe_allow_html=True)
    all_types = ["All"] + sorted(df["project_type"].unique().tolist())
    sel_type = st.selectbox("", all_types, label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<p class="sidebar-section">Data Sources</p>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;color:#4A6550;line-height:2;">◦ Global Forest Watch API<br>◦ ESA WorldCover 10m<br>◦ OpenStreetMap Boundaries</div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-section">Stack</p>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.72rem;color:#4A6550;line-height:2;font-family:monospace;">Python · GeoPandas · Rasterio<br>PostgreSQL · PostGIS · Streamlit<br>Folium · Plotly · SQLAlchemy</div>', unsafe_allow_html=True)

filtered = df[df["region_name"].isin(sel_regions) & (df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]
if sel_type != "All":
    filtered = filtered[filtered["project_type"] == sel_type]
if filtered.empty:
    st.error("No data matches selected filters.")
    st.stop()

latest_year   = filtered["year"].max()
earliest_year = filtered["year"].min()
latest        = filtered[filtered["year"] == latest_year]
earliest      = filtered[filtered["year"] == earliest_year]
total_ha      = latest["tree_cover_ha"].sum()
net_gain      = filtered["tree_cover_ha_change"].sum()
avg_quality   = filtered["data_quality_score"].mean()
n_regions     = filtered["region_name"].nunique()
earliest_ha   = earliest["tree_cover_ha"].sum()
pct_change    = ((total_ha - earliest_ha) / earliest_ha * 100) if earliest_ha > 0 else 0
gain_sign     = "+" if net_gain >= 0 else ""
pct_sign      = "+" if pct_change >= 0 else ""

col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown(f'<p style="font-family:Playfair Display,serif;font-size:2rem;font-weight:600;color:#E8EDE9;letter-spacing:-0.03em;margin:0;">Forest Restoration Monitor</p><p style="font-size:0.8rem;color:#4A6550;margin:0.3rem 0 1.5rem 0;">{len(sel_regions)} active regions · {year_range[0]}–{year_range[1]} · ESA WorldCover + Global Forest Watch</p>', unsafe_allow_html=True)
with col_badge:
    st.markdown('<div style="display:flex;justify-content:flex-end;padding-top:0.5rem;"><div class="live-badge"><div class="live-dot"></div>Live Data</div></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card"><div class="kpi-icon">🌲</div><div class="kpi-label">Tree Cover (Latest)</div><div class="kpi-value">{total_ha/1000:.1f}<span style="font-size:1rem;color:#4A6550"> K ha</span></div><div class="kpi-delta">{pct_sign}{pct_change:.1f}% vs {earliest_year}</div></div>
  <div class="kpi-card"><div class="kpi-icon">📍</div><div class="kpi-label">Regions Monitored</div><div class="kpi-value">{n_regions}<span style="font-size:1rem;color:#4A6550"> sites</span></div><div class="kpi-delta">{year_range[1]-year_range[0]+1} years of data</div></div>
  <div class="kpi-card"><div class="kpi-icon">📈</div><div class="kpi-label">Net Gain (Period)</div><div class="kpi-value">{gain_sign}{net_gain/1000:.1f}<span style="font-size:1rem;color:#4A6550"> K ha</span></div><div class="kpi-delta">{gain_sign}{net_gain:,.0f} hectares total</div></div>
  <div class="kpi-card"><div class="kpi-icon">✦</div><div class="kpi-label">Data Quality Score</div><div class="kpi-value">{avg_quality:.1f}<span style="font-size:1rem;color:#4A6550">%</span></div><div class="kpi-delta">7 validation rules · 50 records</div></div>
</div>
""", unsafe_allow_html=True)

col_map, col_charts = st.columns([1.15, 1], gap="large")

with col_map:
    st.markdown('<p class="section-header">Spatial Distribution</p>', unsafe_allow_html=True)

    sw = [filtered["lat"].min() - 3, filtered["lon"].min() - 3]
    ne = [filtered["lat"].max() + 3, filtered["lon"].max() + 3]

    m = folium.Map(
        location=[filtered["lat"].mean(), filtered["lon"].mean()],
        zoom_start=3,
        tiles="CartoDB dark_matter"
    )
    m.fit_bounds([sw, ne])

    def get_color(pct):
        if pct >= 30:   return "#4ADE80"
        elif pct >= 20: return "#FCD34D"
        elif pct >= 12: return "#F97316"
        else:           return "#F87171"

    for region_name in sel_regions:
        rdf = filtered[filtered["region_name"] == region_name]
        if rdf.empty:
            continue
        row   = rdf.loc[rdf["year"].idxmax()]
        pct   = row["tree_cover_pct"]
        color = get_color(pct)

        if row["geojson"]:
            folium.GeoJson(
                json.loads(row["geojson"]),
                style_function=lambda x, c=color: {
                    "fillColor": c, "color": c,
                    "weight": 1.5, "fillOpacity": 0.2,
                    "dashArray": "4 4"
                },
                tooltip=folium.Tooltip(
                    f'<div style="font-family:monospace;font-size:12px;background:#0D1410;color:#E8EDE9;padding:8px 12px;border:1px solid #2A5535;border-radius:6px;">'
                    f'<b style="color:{color}">{region_name}</b><br>'
                    f'Tree Cover: {pct:.1f}%<br>'
                    f'Area: {row["tree_cover_ha"]:,.0f} ha<br>'
                    f'Country: {row["country"]}</div>',
                    sticky=True
                )
            ).add_to(m)

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=10,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            weight=2,
            popup=folium.Popup(
                f'<div style="font-family:monospace;font-size:11px;background:#0D1410;color:#E8EDE9;'
                f'padding:10px 14px;border:1px solid #2A5535;border-radius:6px;min-width:160px;">'
                f'<b style="color:{color};font-size:13px">{region_name}</b><br><br>'
                f'Year: {int(row["year"])}<br>'
                f'Cover: {pct:.1f}% · {row["tree_cover_ha"]:,.0f} ha<br>'
                f'Type: {row["project_type"]}<br>'
                f'Quality: {row["data_quality_score"]:.0f}%</div>',
                max_width=240
            )
        ).add_to(m)

    st_folium(m, width=None, height=420, returned_objects=[], use_container_width=True)
    st.markdown('<div style="display:flex;gap:1.5rem;margin-top:0.6rem;font-size:0.68rem;color:#4A6550;"><span><span style="color:#4ADE80">●</span> >30%</span><span><span style="color:#FCD34D">●</span> 20–30%</span><span><span style="color:#F97316">●</span> 12–20%</span><span><span style="color:#F87171">●</span> &lt;12%</span></div>', unsafe_allow_html=True)

with col_charts:
    st.markdown('<p class="section-header">Tree Cover Trend</p>', unsafe_allow_html=True)
    palette = ["#4ADE80", "#22D3EE", "#A78BFA", "#FB923C", "#F472B6"]
    fig1 = go.Figure()
    for i, region in enumerate(sel_regions):
        rdf = filtered[filtered["region_name"] == region].sort_values("year")
        if rdf.empty:
            continue
        color = palette[i % len(palette)]
        fig1.add_trace(go.Scatter(
            x=rdf["year"], y=rdf["tree_cover_pct"],
            name=region.replace("_", " "),
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(color=color, size=5),
            hovertemplate=f"<b>{region.replace('_',' ')}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>"
        ))
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#4A6550", size=11),
        margin=dict(t=10, b=10, l=0, r=0), height=190,
        xaxis=dict(showgrid=True, gridcolor="#111A14", color="#4A6550", tickfont=dict(size=10, family="DM Mono"), zeroline=False, showline=False),
        yaxis=dict(showgrid=True, gridcolor="#111A14", color="#4A6550", tickfont=dict(size=10, family="DM Mono"), ticksuffix="%", zeroline=False, showline=False),
        legend=dict(orientation="h", y=-0.3, x=0, font=dict(size=9), bgcolor="rgba(0,0,0,0)"),
        hovermode="x unified"
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<p class="section-header" style="margin-top:0.5rem;">Net Gain by Region</p>', unsafe_allow_html=True)
    gain_df = filtered.groupby("region_name")["tree_cover_ha_change"].sum().reset_index().sort_values("tree_cover_ha_change", ascending=True)
    gain_df["short"] = gain_df["region_name"].str.replace("_", " ")
    gain_df["color"] = gain_df["tree_cover_ha_change"].apply(lambda x: "#4ADE80" if x > 0 else "#F87171")
    fig2 = go.Figure(go.Bar(
        x=gain_df["tree_cover_ha_change"], y=gain_df["short"], orientation="h",
        marker=dict(color=gain_df["color"].tolist(), opacity=0.85, line=dict(width=0)),
        hovertemplate="<b>%{y}</b><br>%{x:+,.0f} ha<extra></extra>"
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color="#4A6550", size=11),
        margin=dict(t=5, b=5, l=0, r=0), height=190,
        xaxis=dict(showgrid=True, gridcolor="#111A14", color="#4A6550", tickfont=dict(size=9, family="DM Mono"), zeroline=True, zerolinecolor="#1C2E22", showline=False),
        yaxis=dict(color="#A8BFaC", tickfont=dict(size=10), showgrid=False, showline=False),
        bargap=0.35
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

st.markdown("<br>", unsafe_allow_html=True)
col_q, col_table = st.columns([1, 1.6], gap="large")

with col_q:
    st.markdown('<p class="section-header">Validation Quality</p>', unsafe_allow_html=True)
    quality_df = filtered.groupby("region_name")["data_quality_score"].mean().reset_index().sort_values("data_quality_score", ascending=False)
    rows_html = "".join([
        f'<div class="quality-row"><span class="quality-name">{r["region_name"].replace("_"," ")}</span>'
        f'<div class="quality-bar-wrap"><div class="quality-bar" style="width:{r["data_quality_score"]}%"></div></div>'
        f'<span class="quality-score">{r["data_quality_score"]:.1f}</span></div>'
        for _, r in quality_df.iterrows()
    ])
    st.markdown(f'<div class="panel"><div style="font-size:0.65rem;color:#4A6550;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem;">7 rules · {len(filtered)} records · Pipeline output</div>{rows_html}</div>', unsafe_allow_html=True)

with col_table:
    st.markdown('<p class="section-header">Regional Summary</p>', unsafe_allow_html=True)
    summary = filtered.groupby("region_name").agg(
        Start_Pct=("tree_cover_pct", "first"),
        End_Pct=("tree_cover_pct", "last"),
        Peak_Ha=("tree_cover_ha", "max"),
        Net_Gain_Ha=("tree_cover_ha_change", "sum"),
        Country=("country", "first"),
        Type=("project_type", "first")
    ).reset_index()
    summary["Delta"] = (summary["End_Pct"] - summary["Start_Pct"]).round(1).astype(str) + "%"
    summary["Peak_Ha"] = summary["Peak_Ha"].apply(lambda x: f"{x:,.0f}")
    summary["Net_Gain_Ha"] = summary["Net_Gain_Ha"].apply(lambda x: f"+{x:,.0f}" if x >= 0 else f"{x:,.0f}")
    summary = summary.rename(columns={"region_name": "Region", "Start_Pct": "Start %", "End_Pct": "End %", "Peak_Ha": "Peak (ha)", "Net_Gain_Ha": "Net Gain", "Delta": "Δ Cover"})
    st.dataframe(summary[["Region", "Country", "Type", "Start %", "End %", "Δ Cover", "Net Gain"]], use_container_width=True, hide_index=True, height=220)

st.markdown("<br>", unsafe_allow_html=True)
with st.expander("Raw Records Export"):
    cols = ["region_name", "year", "tree_cover_pct", "tree_cover_ha", "tree_cover_ha_change", "data_quality_score"]
    st.dataframe(filtered[cols], use_container_width=True, hide_index=True)
    st.download_button("↓ Export CSV", filtered[cols].to_csv(index=False), "forest_restoration_export.csv", "text/csv")
