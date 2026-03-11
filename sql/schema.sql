CREATE TABLE IF NOT EXISTS restoration_regions (
    id           SERIAL PRIMARY KEY,
    region_name  VARCHAR(100) UNIQUE NOT NULL,
    country      VARCHAR(100),
    biome        VARCHAR(100),
    project_type VARCHAR(100),
    total_area_ha NUMERIC(12,2),
    lat_center   NUMERIC(10,6),
    lon_center   NUMERIC(10,6),
    geometry     GEOMETRY(POLYGON, 4326),
    created_at   TIMESTAMP DEFAULT NOW()
);
 
-- Annual metrics (one row per region per year)
CREATE TABLE IF NOT EXISTS annual_metrics (
    id                    SERIAL PRIMARY KEY,
    region_id             INTEGER REFERENCES restoration_regions(id),
    year                  INTEGER NOT NULL CHECK (year BETWEEN 2010 AND 2030),
    tree_cover_pct        NUMERIC(6,2),
    tree_cover_ha         NUMERIC(12,2),
    tree_cover_ha_change  NUMERIC(12,2),
    total_area_ha         NUMERIC(12,2),
    data_quality_score    NUMERIC(5,2),
    UNIQUE(region_id, year)
);
 
-- Spatial index — makes geometry queries fast
CREATE INDEX IF NOT EXISTS idx_regions_geom
    ON restoration_regions USING GIST(geometry);
 
CREATE INDEX IF NOT EXISTS idx_metrics_year
    ON annual_metrics(year);
 

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text
 
DB_URL = "postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/forest_restoration"
engine = create_engine(DB_URL)
 
print("Loading data into PostgreSQL + PostGIS...")
 
# Load boundaries
boundaries = gpd.read_file("data/raw/boundaries/pilot_regions.geojson")
metrics    = pd.read_csv("data/processed/all_regions_metrics.csv")
 
with engine.begin() as conn:
    for _, row in boundaries.iterrows():
        conn.execute(text("""
            INSERT INTO restoration_regions
                (region_name, country, biome, project_type, total_area_ha,
                 lat_center, lon_center, geometry)
            VALUES
                (:name, :country, :biome, :ptype, :area, :lat, :lon,
                 ST_GeomFromText(:geom, 4326))
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
print(f"  Loaded {len(boundaries)} regions into restoration_regions")
 
# Load metrics 
with engine.begin() as conn:
    for _, row in metrics.iterrows():
        region = conn.execute(text(
            "SELECT id FROM restoration_regions WHERE region_name = :n"
        ), {"n": row["region_name"]}).fetchone()
        if not region:
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
 
print(f"  Loaded {len(metrics)} metric records into annual_metrics")
print("  Database load complete ✓")
 
# Quick verification query 
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT r.region_name, COUNT(m.id) AS years_of_data,
               MIN(m.tree_cover_pct) AS min_pct,
               MAX(m.tree_cover_pct) AS max_pct
        FROM restoration_regions r
        JOIN annual_metrics m ON r.id = m.region_id
        GROUP BY r.region_name
        ORDER BY r.region_name
    """))
    print()
    print("  Database verification:")
    print(f"  {'Region':<30} {'Years':>6} {'Min%':>6} {'Max%':>6}")
    print(f"  {'-'*50}")
    for row in result:
        print(f"  {row[0]:<30} {row[1]:>6} {row[2]:>6.1f} {row[3]:>6.1f}")
