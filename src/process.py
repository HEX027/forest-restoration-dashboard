import geopandas as gpd
import pandas as pd
from pathlib import Path
 
print("=" * 50)
print("STEP 1: Loading raw data")
print("=" * 50)
 
boundaries = gpd.read_file("data/raw/boundaries/pilot_regions.geojson")
metrics    = pd.read_csv("data/processed/all_regions_metrics.csv")
 
print(f"  Loaded {len(boundaries)} boundaries  |  CRS: {boundaries.crs}")
print(f"  Loaded {len(metrics)} metric records")
 
print()
print("=" * 50)
print("STEP 2: Reprojecting to UTM for area calculations")
print("=" * 50)
 
# EPSG:4326 = WGS84 lat/lon (what we store, what web maps use)
# EPSG:32636 = UTM Zone 36N — metric projection for accurate area in m²
boundaries_utm = boundaries.to_crs("EPSG:32636")
print(f"  Reprojected: EPSG:4326 → EPSG:32636 (UTM Zone 36N)")
 
# Verify area calculation (geometry.area gives m² in UTM, divide by 10000 for ha)
boundaries_utm["computed_area_ha"] = (boundaries_utm.geometry.area / 10000).round(0)
print(f"  Computed areas (ha): {boundaries_utm['computed_area_ha'].tolist()}")
 
print()
print("=" * 50)
print("STEP 3: Spatial join — attach metrics to boundaries")
print("=" * 50)
 
# Merge metrics (tabular) onto boundaries (spatial) using region_name as key
# This creates a GeoDataFrame where each row has both geometry AND metrics
metrics_gdf = boundaries.merge(metrics, on="region_name", how="inner")
print(f"  After spatial join: {len(metrics_gdf)} records with geometry")
 
print()
print("=" * 50)
print("STEP 4: Calculate year-over-year statistics")
print("=" * 50)
 
# Sort so diff() calculates correctly
metrics_gdf = metrics_gdf.sort_values(["region_name", "year"])
 
# Summary stats per region
summary = metrics.groupby("region_name").agg(
    start_pct    = ("tree_cover_pct", "first"),
    end_pct      = ("tree_cover_pct", "last"),
    total_gain_ha= ("tree_cover_ha_change", "sum"),
    avg_quality  = ("data_quality_score", "mean"),
).round(2).reset_index()
summary["pct_gained"] = (summary["end_pct"] - summary["start_pct"]).round(2)
 
print("  Regional Summary (2015–2024):")
print(summary[["region_name","start_pct","end_pct","pct_gained","total_gain_ha"]].to_string(index=False))
 
print()
print("=" * 50)
print("STEP 5: Save processed outputs")
print("=" * 50)
 
# Save as GeoJSON for database loading and dashboard
output_path = "data/processed/all_regions_processed.geojson"
metrics_gdf.to_file(output_path, driver="GeoJSON")
print(f"  Saved: {output_path}  ({len(metrics_gdf)} features)")
 
summary.to_csv("data/processed/regional_summary.csv", index=False)
print(f"  Saved: data/processed/regional_summary.csv")
 
print()
print("PROCESSING COMPLETE ✓")
