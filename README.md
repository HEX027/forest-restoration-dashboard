# Forest Restoration Monitoring Dashboard

A full-stack geospatial data platform tracking reforestation progress across pilot regions in Africa. Built with Python, PostGIS, and Streamlit.


---

![Dashboard Overview](assets/screenshot_dashboard.png)

---

## The Problem

Reforestation programs generate enormous amounts of satellite imagery, but the people running those programs have no easy way to see whether their interventions are actually working. This project bridges that gap.

---

## What It Tracks

5 pilot restoration regions across West and East Africa, 2015-2024:

| Region | Country | Biome | Project Type |
|--------|---------|-------|--------------|
| Sahel_Burkina_01 | Burkina Faso | Sahel | Reforestation |
| Kenya_Rift_01 | Kenya | Dry Forest | Agroforestry |
| Ethiopia_Highland | Ethiopia | Highland | Natural Regeneration |
| Ghana_Volta_01 | Ghana | Savanna | Reforestation |
| Tanzania_Usambara | Tanzania | Montane Forest | Reforestation |

332,456 ha monitored - +62,626 ha net gain - 97.6% data quality score

---

## Dashboard

![Map View](assets/screenshot_map.png)

The map shows each restoration site color-coded by tree cover percentage. Green is above 30%, yellow is 20-30%, orange is 12-20%, red is below 12%. Click any marker for a full breakdown.

![Charts](assets/screenshot_charts.png)

Time series showing tree cover trajectory from 2015 to 2024, and net hectares gained per site across the selected period.

![Quality Panel](assets/screenshot_quality.png)

Every record passed through a 7-rule validation pipeline. Score 97.6% - flagged records exported to JSON report, not silently dropped.

---

## How the Pipeline Works

**CRS handling**
Everything stored in EPSG:4326 for web maps. Area calculations reproject to UTM Zone 36N (EPSG:32636). Skipping this causes silent errors - areas wrong by a factor of 100.

**Windowed raster reading**
ESA WorldCover tiles are 2GB+. Rasterio clips to region bounding box before loading pixels into memory. Loading the full file crashes the pipeline.

**Validation rules**

| Rule | What it checks |
|------|----------------|
| valid_coordinates | Lat/lon within geographic bounds |
| valid_geometry | No self-intersections, auto-repair with make_valid() |
| no_missing_values | Required fields not null |
| no_duplicates | No duplicate region + year combinations |
| valid_year_range | Year between 2010 and 2030 |
| valid_pct_range | Tree cover percentage between 0 and 100 |
| area_consistency | Tree cover ha does not exceed total area ha |

**PostGIS spatial index**
GIST index on geometry column. ST_Intersects on 50K features without it takes 30 seconds. With it, under 50ms.

**Idempotent loading**
ON CONFLICT DO UPDATE means pipeline reruns safely without duplicates.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Geospatial | GeoPandas, Rasterio, Shapely, PyProj, Fiona |
| Database | PostgreSQL 16 + PostGIS 3.x |
| ORM | SQLAlchemy 2.0, psycopg2 |
| Dashboard | Streamlit, Folium, Plotly |

---

## Running Locally

1. Clone: git clone https://github.com/HEX027/forest-restoration-dashboard.git
2. Create environment: conda create -n forest_env python=3.11 -y
3. Activate: conda activate forest_env
4. Install geospatial: conda install -c conda-forge geopandas rasterio shapely pyproj fiona -y
5. Install rest: pip install -r requirements.txt
6. Create database and enable postgis extension
7. Run sql/schema.sql to create tables
8. Update DB_URL in src/dashboard.py and src/load_db.py
9. Run pipeline: python src/create_demo_data.py then process.py then validate.py then load_db.py
10. Launch: streamlit run src/dashboard.py

---

## Scaling to Production

- Dask for parallel raster processing across regions
- Apache Airflow for pipeline orchestration and scheduling
- PostgreSQL table partitioning by year
- pg_tileserv for large geometry tile serving

---

## About

https://github.com/HEX027
