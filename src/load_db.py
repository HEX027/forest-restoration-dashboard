import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = "postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5433/forest_restoration"
engine = create_engine(DB_URL)

print("Connecting...")
with engine.connect() as conn:
    v = conn.execute(text("SELECT PostGIS_Version()")).fetchone()
    print(f"PostGIS: {v[0]}")

boundaries = gpd.read_file("data/raw/boundaries/pilot_regions.geojson")
metrics = pd.read_csv("data/processed/all_regions_metrics.csv")
print(f"Boundaries loaded: {len(boundaries)}")
print(f"Metrics loaded: {len(metrics)}")

print("\nLoading regions...")
with engine.begin() as conn:
    for _, row in boundaries.iterrows():
        conn.execute(text("""
            INSERT INTO restoration_regions
                (region_name, country, biome, project_type,
                 total_area_ha, lat_center, lon_center, geometry)
            VALUES
                (:name, :country, :biome, :ptype,
                 :area, :lat, :lon, ST_GeomFromText(:geom, 4326))
            ON CONFLICT (region_name) DO UPDATE SET
                geometry = EXCLUDED.geometry
        """), {
            "name":    row["region_name"],
            "country": row.get("country", "Unknown"),
            "biome":   row.get("biome", "Unknown"),
            "ptype":   row.get("project_type", "Reforestation"),
            "area":    float(row.get("total_area_ha", 0) or 0),
            "lat":     float(row.get("lat_center", 0) or 0),
            "lon":     float(row.get("lon_center", 0) or 0),
            "geom":    row.geometry.wkt
        })
print(f"  Loaded {len(boundaries)} regions")

print("\nLoading metrics...")
loaded = 0
with engine.begin() as conn:
    for _, row in metrics.iterrows():
        region = conn.execute(text(
            "SELECT id FROM restoration_regions WHERE region_name = :n"
        ), {"n": row["region_name"]}).fetchone()
        if not region:
            print(f"  SKIP: {row['region_name']}")
            continue
        conn.execute(text("""
            INSERT INTO annual_metrics
                (region_id, year, tree_cover_pct, tree_cover_ha,
                 tree_cover_ha_change, total_area_ha, data_quality_score)
            VALUES (:rid, :yr, :pct, :ha, :chg, :total, :dqs)
            ON CONFLICT (region_id, year) DO UPDATE SET
                tree_cover_pct = EXCLUDED.tree_cover_pct
        """), {
            "rid":   region[0],
            "yr":    int(row["year"]),
            "pct":   float(row["tree_cover_pct"]),
            "ha":    float(row["tree_cover_ha"]),
            "chg":   float(row.get("tree_cover_ha_change", 0) or 0),
            "total": float(row["total_area_ha"]),
            "dqs":   float(row.get("data_quality_score", 100))
        })
        loaded += 1
print(f"  Loaded {loaded} metric records")

print("\nVerifying database...")
with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT r.region_name, COUNT(m.id) as years,
               ROUND(MIN(m.tree_cover_pct)::numeric,1) as min_pct,
               ROUND(MAX(m.tree_cover_pct)::numeric,1) as max_pct
        FROM restoration_regions r
        JOIN annual_metrics m ON r.id = m.region_id
        GROUP BY r.region_name ORDER BY r.region_name
    """)).fetchall()
    print(f"\n  {'Region':<30} {'Years':>6} {'Min%':>6} {'Max%':>6}")
    print(f"  {'-'*52}")
    for row in rows:
        print(f"  {row[0]:<30} {row[1]:>6} {row[2]:>6} {row[3]:>6}")

print("\nDone!")
