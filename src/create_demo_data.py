# Save as: C:\forest_project\src\create_demo_data.py
 
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
import json
from pathlib import Path
 
np.random.seed(42)   # Reproducible results
 
# Define 5 realistic pilot regions with real-world coordinates 
REGIONS = [
    {"name": "Sahel_Burkina_01",  "lat": 12.5, "lon": 1.8,  "country": "Burkina Faso", "biome": "Sahel",         "project_type": "Reforestation"},
    {"name": "Kenya_Rift_01",     "lat": -0.5, "lon": 36.2, "country": "Kenya",         "biome": "Dry Forest",    "project_type": "Agroforestry"},
    {"name": "Ethiopia_Highland", "lat": 9.2,  "lon": 38.7, "country": "Ethiopia",      "biome": "Highland",      "project_type": "Natural Regeneration"},
    {"name": "Ghana_Volta_01",    "lat": 8.0,  "lon": -1.2, "country": "Ghana",         "biome": "Savanna",       "project_type": "Reforestation"},
    {"name": "Tanzania_Usambara", "lat": -4.6, "lon": 38.2, "country": "Tanzania",      "biome": "Montane Forest","project_type": "Reforestation"},
]
 
YEARS = list(range(2015, 2025))   # 2015–2024
 
# Build boundary polygons (0.5 x 0.5 degree boxes around each centroid) ─
def make_bbox_polygon(lat, lon, size=0.5):
    return Polygon([
        (lon - size, lat - size),
        (lon + size, lat - size),
        (lon + size, lat + size),
        (lon - size, lat + size),
        (lon - size, lat - size),
    ])
 
# Build boundaries GeoDataFrame 
boundary_records = []
for region in REGIONS:
    boundary_records.append({
        "region_name":  region["name"],
        "country":      region["country"],
        "biome":        region["biome"],
        "project_type": region["project_type"],
        "lat_center":   region["lat"],
        "lon_center":   region["lon"],
        "total_area_ha": 250000 + np.random.randint(-30000, 30000),
        "geometry":     make_bbox_polygon(region["lat"], region["lon"])
    })
 
boundaries_gdf = gpd.GeoDataFrame(boundary_records, crs="EPSG:4326")
boundaries_gdf.to_file("data/raw/boundaries/pilot_regions.geojson", driver="GeoJSON")
print(f"Saved {len(boundaries_gdf)} region boundaries")
 
# Build annual metrics with realistic forest recovery trend 
metric_records = []
for region in REGIONS:
    # Each region starts with a baseline tree cover and trends upward (restoration)
    # with some year-to-year variation (weather, drought events)
    base_pct  = 15 + np.random.uniform(0, 20)    # 15–35% starting cover
    trend     = np.random.uniform(0.5, 2.0)      # Annual gain: 0.5–2% per year
    total_ha  = 250000 + np.random.randint(-30000, 30000)
 
    prev_pct = base_pct
    for i, year in enumerate(YEARS):
        # Add noise: drought years can cause small dips
        noise    = np.random.normal(0, 0.4)
        tree_pct = max(5, prev_pct + trend + noise)
 
        # Simulate a drought in 2019-2020 for realism
        if year in [2019, 2020] and region["biome"] in ["Sahel", "Savanna"]:
            tree_pct -= np.random.uniform(0.5, 2.0)
 
        tree_ha      = (tree_pct / 100) * total_ha
        prev_pct_val = prev_pct if i > 0 else tree_pct
        ha_change    = tree_ha - (prev_pct_val / 100 * total_ha) if i > 0 else 0
 
        metric_records.append({
            "region_name":          region["name"],
            "country":              region["country"],
            "project_type":         region["project_type"],
            "year":                 year,
            "tree_cover_pct":       round(tree_pct, 2),
            "tree_cover_ha":        round(tree_ha, 0),
            "tree_cover_ha_change": round(ha_change, 0),
            "total_area_ha":        total_ha,
            "data_quality_score":   round(95 + np.random.uniform(0, 5), 1),
            "lat":                  region["lat"],
            "lon":                  region["lon"],
        })
        prev_pct = tree_pct
 
metrics_df = pd.DataFrame(metric_records)
metrics_df.to_csv("data/processed/all_regions_metrics.csv", index=False)
print(f"Saved {len(metrics_df)} metric records ({len(REGIONS)} regions × {len(YEARS)} years)")
print(metrics_df.groupby("region_name")[["tree_cover_pct","tree_cover_ha_change"]].mean().round(2))
